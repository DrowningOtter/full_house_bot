import asyncio
import logging
import sys
from os import getenv
import json
from aio_pika import connect, Message
from aiormq.exceptions import ChannelNotFoundEntity, ChannelInvalidStateError
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.utils.markdown import hbold
from aiogram.methods.send_message import SendMessage
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from conf import (API_TOKEN, MEDIA_ROOT, 
                  RABBITMQ_LOGIN, RABBITMQ_PASSWORD,
                  RABBITMQ_CONNECT_RETRIES, DELAY_BETWEEN_RETRIES,
                  RABBITMQ_QUEUE_NAME, RABBITMQ_HOST_NAME)
from filters import MyFilter
from states import Form
import message_templates
import db
import signal

# Bot token can be obtained via https://t.me/BotFather
TOKEN = API_TOKEN

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()
# Initialize Bot instance with a default parse mode which will be passed to all API calls
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

timer_name = "my_timer"

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    # await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")
    await state.set_state(Form.terms_of_use)
    # await state.update_data(have_sended=False)
    await message.answer(await db.get_prompt("greeting_phrase"),
                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                               InlineKeyboardButton(text=message_templates.terms_of_use_button_text, callback_data="terms_of_use")
                               ]]))
    await db.reg_user(message.from_user.id)

@dp.message(Command("help"))
async def send_help(message: Message):
    text = """
            Ответы на вопросы, которые вы не нашли здесь, можете задать по телефону.
Для смены дома используйте команду /start.
"""
    await bot.send_message(chat_id=message.chat.id, text=text)

@dp.message(Command("questions_list"), Form.house_choosen)
async def send_questions_list(message: Message, state:FSMContext):
    questions_list = await db.get_questions_list((await state.get_data())['selected_house_number'])
    text = "\n".join(questions_list)
    await bot.send_message(chat_id=message.chat.id, text=text)



@dp.message(Form.terms_of_use)
async def send_terms_of_use(message: Message, state: FSMContext):
    data = await state.get_data()
    if "sended_message_id" not in data:
        sended_message = await bot.send_message(chat_id=message.chat.id, text="Пожалуйста, нажмите на кнопку для получения списка правил")
        await state.update_data(sended_message_id=sended_message.message_id, sended_message_id_timestamp=datetime.now())
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@dp.callback_query(lambda query: query.data == "terms_of_use")
async def terms_of_use_handler(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, 
                                        message_id=query.message.message_id, 
                                        reply_markup=None)
    # await bot.edit_message_text(chat_id=query.message.chat.id,
    #                             message_id=query.message.message_id, text=query.message.text+"\n"+await db.get_prompt("rules")+message_templates.about_commands)
    await bot.send_message(chat_id=query.message.chat.id, text=await db.get_prompt("rules")+message_templates.about_commands)
    if "sended_message_id" in data and datetime.now() - data["sended_message_id_timestamp"] < timedelta(hours=48):
        await bot.delete_message(chat_id=query.message.chat.id, message_id=data.pop("sended_message_id"))
    data.pop("sended_message_id_timestamp", None)

    sended_message = await bot.send_message(chat_id=query.message.chat.id, text=await db.get_house_list()+"\n\n"+await db.get_prompt("house_choose_text"))
    data['house_select_message_id'] = sended_message.message_id
    data['house_select_message_id_timestamp'] = datetime.now()
    await state.set_data(data)
    await state.set_state(Form.house_choice)
    # await bot.pin_chat_message(chat_id=query.message.chat.id, message_id=query.message.message_id)

@dp.message(Form.house_choice)
async def process_house_choice(message: Message, state: FSMContext):
    try:
        numbers_list = await db.get_house_numbers()
        house_number = int(message.text)
        assert house_number in numbers_list
        # Correct house number, proceess
        data = await state.get_data()
        if "incorrect_house_number_message_id" in data and datetime.now() - data['incorrect_house_number_message_id_timestamp'] < timedelta(hours=48):
            await bot.delete_message(chat_id=message.chat.id, message_id=data.pop("incorrect_house_number_message_id"))
        data.pop("incorrect_house_number_message_id_timestamp", None)
        await state.set_state(Form.house_choosen)
        # Добавить фотки и видео дома, текстовый ответ и отправить
        media_group = MediaGroupBuilder(caption=await db.get_house_info(house_number))
        photo_list = await db.get_house_photos(house_number)
        for photo in photo_list:
            media_group.add_photo(media=FSInputFile(photo))
        sended_message = await bot.send_message(chat_id=message.chat.id, text="Пожалуйста, подождите, медиа материалы загружаются...")
        if photo_list == []:
            await bot.send_message(chat_id=message.chat.id, text=await db.get_house_info(house_number))
        else:
            await bot.send_media_group(chat_id=message.chat.id, media=media_group.build())
        await bot.delete_message(chat_id=message.chat.id, message_id=sended_message.message_id)
        await bot.send_message(chat_id=message.chat.id, text="\n".join(await db.get_questions_list(house_number)))

        data['selected_house_number'] = house_number
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        if datetime.now() - data['house_select_message_id_timestamp'] < timedelta(hours=48):
            await bot.delete_message(chat_id=message.chat.id, message_id=data.pop('house_select_message_id'))
        data.pop('house_select_message_id_timestamp', None)
        await state.set_data(data)
        await state.set_state(Form.house_choosen)
    except (AssertionError, ValueError) as ex:
        if "incorrect_house_number_message_id" not in await state.get_data():
            sended_message = await bot.send_message(chat_id=message.chat.id, text=await db.get_prompt("incorrect_house_number"))
            await state.update_data(incorrect_house_number_message_id=sended_message.message_id, incorrect_house_number_message_id_timestamp=datetime.now())
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


async def timer_callback(message: types.Message, state: FSMContext):
    sended_message = await bot.send_message(chat_id=message.chat.id, text="Остались еще вопросы?", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="Да", callback_data="more_questions"),
            InlineKeyboardButton(text="Нет", callback_data="no_more_questions")
        ]]
    ))
    await state.update_data(ask_for_more_questions_message_id=sended_message.message_id, ask_for_more_questions_message_id_timestamp=datetime.now())

@dp.callback_query(lambda query: query.data in ["no_more_questions", "more_questions"])
async def no_more_questions(query: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    if datetime.now() - state_data["ask_for_more_questions_message_id_timestamp"] < timedelta(hours=48):
        await bot.delete_message(chat_id=query.message.chat.id, message_id=state_data.pop("ask_for_more_questions_message_id"))
    state_data.pop("ask_for_more_questions_message_id_timestamp", None)
    sended_message = await bot.send_message(
        chat_id=query.message.chat.id,
        text=await db.get_prompt("answer_to_no_more_questions") \
            if query.data == "no_more_questions" else await db.get_prompt("answer_to_more_questions")
        )
    if query.data == "more_questions":
        state_data["ask_to_more_questions_message_id"] = sended_message.message_id
        state_data["ask_to_more_questions_message_id_timestamp"] = datetime.now()
    elif query.data == "no_more_questions":
        state_data["wish_nice_rest_message_id"] = sended_message.message_id
        state_data["wish_nice_rest_message_id_timestamp"] = datetime.now()
    await state.set_data(state_data)

@dp.message(Form.house_choosen)
async def echo_handler(message: types.Message, state: FSMContext) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    sleep_time = 3
    if not hasattr(echo_handler, "timer_task") or echo_handler.timer_task.done():
        print("Starting a new timer...")
        echo_handler.timer_task = asyncio.create_task(asyncio.sleep(sleep_time))
    else:
        echo_handler.timer_task.cancel()
    state_data = await state.get_data()
    # Получить номер вопроса и отправить ответ
    try:
        if "ask_for_more_questions_message_id" in state_data and datetime.now() - state_data["ask_for_more_questions_message_id_timestamp"] < timedelta(hours=48):
            await bot.delete_message(chat_id=message.chat.id, message_id=state_data.pop("ask_for_more_questions_message_id"))
            state_data.pop("ask_for_more_questions_message_id_timestamp", None)
        if "ask_to_more_questions_message_id" in state_data and datetime.now() - state_data["ask_to_more_questions_message_id_timestamp"] < timedelta(hours=48):
            await bot.delete_message(chat_id=message.chat.id, message_id=state_data.pop("ask_to_more_questions_message_id"))
            state_data.pop("ask_to_more_questions_message_id_timestamp", None)
        if "wish_nice_rest_message_id" in state_data and datetime.now() - state_data["wish_nice_rest_message_id_timestamp"] < timedelta(hours=48):
            await bot.delete_message(chat_id=message.chat.id, message_id=state_data.pop("wish_nice_rest_message_id"))
            state_data.pop("wish_nice_rest_message_id_timestamp", None)
        await state.set_data(state_data)

        house_number = (await state.get_data())['selected_house_number']
        q_no = int(message.text)
        # logging.info(f"ques num: {q_no}\nques list: {await db.get_questions_numbers(house_number)}")
        if q_no not in await db.get_questions_numbers(house_number):
            # logging.info("question number not in ques list")
            raise ValueError
        media_group_list = []
        photos_list = await db.get_question_photos(house_number, q_no)
        videos_list = await db.get_question_videos(house_number, q_no)
        for i in range((len(photos_list) + len(videos_list)) // 10):
            media_group_list.append(MediaGroupBuilder())
        media_group_list.append(MediaGroupBuilder(caption=await db.get_answer_text(house_number, q_no)))
        for ind, photo in enumerate(photos_list):
            media_group_list[ind // 10].add_photo(media=FSInputFile(photo))
        for ind, video in enumerate(videos_list):
            media_group_list[ind // 10].add_video(media=FSInputFile(video))
        # Исключений нет - нужно удалить сообщение об ошибке
        if "error_message_id" in state_data and datetime.now() - state_data["error_message_id_timestamp"] < timedelta(hours=48):
            await bot.delete_message(chat_id=message.chat.id, message_id=state_data.pop("error_message_id"))
            state_data.pop("error_message_id_timestamp", None)
            await state.set_data(state_data)
        sended_message = await bot.send_message(chat_id=message.chat.id, text="Пожалуйста, подождите, медиа материалы загружаются...")
        if photos_list == [] and videos_list == []:
            await bot.send_message(chat_id=message.chat.id, text=await db.get_answer_text(house_number, q_no))
        else:
            for group in media_group_list:
                await bot.send_media_group(chat_id=message.chat.id, media=group.build())
        await bot.delete_message(chat_id=message.chat.id, message_id=sended_message.message_id)
        await echo_handler.timer_task
        await timer_callback(message, state)
    except (KeyError, ValueError) as ex:
        # logging.info(str(ex))
        text = await db.get_prompt("incorrect_question_number")
        if "error_message_id" not in state_data:
            sended_message = await bot.send_message(chat_id=message.chat.id, text=await db.get_prompt("incorrect_question_number"))
            await state.update_data(error_message_id=sended_message.message_id, error_message_id_timestamp=datetime.now())
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        else:
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except asyncio.CancelledError:
        # print("Restarting the timer...")
        echo_handler.timer_task = asyncio.create_task(asyncio.sleep(sleep_time))

async def send_newsletter(text, user_id_list):
    for user in user_id_list:
        await bot.send_message(chat_id=user, text=text)

async def newsletter_update_handler():
    for attempt_number in range(1, RABBITMQ_CONNECT_RETRIES + 1):
        try:
            connection = await connect(f"amqp://{RABBITMQ_LOGIN}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST_NAME}/")
            if connection:
                logging.info("Successfully connected to RabbitMQ")
                break
        except Exception as ex:
            await asyncio.sleep(DELAY_BETWEEN_RETRIES)
            logging.error(ex)
            logging.info(f"Failed to connect to RabbitMQ. Retrying...(attempt number {attempt_number})")
    else:
        logging.error("Failed to connect... Exiting task")
        return
    
    channel = await connection.channel()
    for attempt_number in range(1, RABBITMQ_CONNECT_RETRIES + 1):
        try:
            queue = await channel.get_queue(RABBITMQ_QUEUE_NAME)
            if queue:
                logging.info("Successfully got queue")
                break
        except (ChannelNotFoundEntity, ChannelInvalidStateError) as ex:
            await asyncio.sleep(DELAY_BETWEEN_RETRIES)
            logging.info(f"Failed to get queue. Retrying...(attempt number {attempt_number})")
            # logging.error(type(ex), ex)
    else:
        logging.error("Failed to get queue... Exiting")
        return

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    json_data = json.loads(message.body.decode("utf-8"))
                except Exception as ex:
                    logging.error(ex)
                    break
                await send_newsletter(json_data["newsletter_text"], json_data["user_list"])
    await connection.close()

def register_got_queue_handler():
    loop = asyncio.get_event_loop()

    async def try_to_connect(sig) -> None:
        logging.info(f"got signal{sig}")
        await newsletter_update_handler()

    for sig in [signal.SIGUSR1]:
        loop.add_signal_handler(sig, lambda: asyncio.create_task(try_to_connect(sig)))


async def main() -> None:
    # And the run events dispatching
    # await newsletter_update_handler()
    task_one = asyncio.create_task(dp.start_polling(bot))
    task_two = asyncio.create_task(newsletter_update_handler())
    register_got_queue_handler()
    await asyncio.gather(task_one, task_two)
    # await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())