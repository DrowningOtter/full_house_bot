import sqlite3, os
from conf import DB_NAME, USER_ID, MEDIA_ROOT
from main import logging

async def reg_user(reg_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
                    INSERT INTO bot_registeredusers (user_id, tg_user_id)
                    SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM bot_registeredusers WHERE user_id = ? AND tg_user_id = ?)
                   ''', (USER_ID, reg_id, USER_ID, reg_id))
    conn.commit()
    conn.close()

async def get_prompt(prompt_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'SELECT prompt FROM bot_prompt WHERE user_id = {USER_ID} AND prompt_name = "{prompt_name}"')
    logging.info(f'SELECT prompt FROM bot_prompt WHERE user_id = {USER_ID} AND prompt_name = "{prompt_name}"')
    res = cursor.fetchall()
    logging.info("-----------------res = ", res)
    if res == []:
        return ""
    prompt = res[0][0]
    conn.close()
    return prompt

# TODO fix query idiot
async def get_question_with_answer(number:int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'SELECT question_text, answer_text FROM bot_question ')

async def get_house_list():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'SELECT house_number, house_name, address FROM bot_house WHERE user_id = {USER_ID}')
    rows = cursor.fetchall()
    rows = [f"{item[0]}. {item[1]} ({item[2]})" for item in rows]
    return "\n".join(rows)

async def get_house_numbers():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'SELECT house_number FROM bot_house WHERE user_id = {USER_ID}')
    return [int(num[0]) for num in cursor.fetchall()]

async def get_house_videos(house_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'''SELECT video 
                             FROM bot_video
                             WHERE user_id = {USER_ID} AND house_id = 
                                (
                                    SELECT id FROM bot_house WHERE house_number = {house_number} AND user_id = {USER_ID}
                                )''')
    photos = cursor.fetchall()
    return [os.path.join(MEDIA_ROOT, item[0]) for item in photos]

async def get_house_info(house_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'''
                    SELECT house_name, address 
                    FROM bot_house
                    WHERE user_id = {USER_ID} AND house_number = {house_number}
                    ''')
    house_info = cursor.fetchall()[0]
    # return '\n'.join(row)
    return f"Дом успешно выбран!\n<b>Название дома:</b> {house_info[0]}\n<b>Адрес:</b> {house_info[1]}"

async def get_house_photos(house_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'''SELECT photo 
                        FROM bot_photo 
                        WHERE user_id = {USER_ID} AND house_id = (
                            SELECT id FROM bot_house WHERE house_number={house_number} AND user_id = {USER_ID}
                            )''')
    photos = cursor.fetchall()
    return [os.path.join(MEDIA_ROOT, item[0]) for item in photos]

async def get_questions_list(house_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'''
                    SELECT question_number, question_text
                    FROM bot_question
                    WHERE user_id = {USER_ID} AND house_id = (SELECT id FROM bot_house WHERE house_number = {house_number})
                    ''')
    questions = cursor.fetchall()
    return [f"{item[0]}. {item[1]}" for item in questions]

async def get_answer_text(house_number, question_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'''
                    SELECT question_number, question_text, answer_text
                    FROM bot_question
                    WHERE house_id = (
                        SELECT id FROM bot_house 
                        WHERE house_number = {house_number} 
                            AND user_id = {USER_ID}) 
                    AND question_number = {question_number}
                    ''')
    text = cursor.fetchall()[0]
    return f"{text[0]}. {text[1]}\n{text[2]}"

async def get_questions_numbers(house_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'''
                    SELECT question_number FROM bot_question WHERE user_id = {USER_ID} AND house_id = (
                        SELECT id FROM bot_house WHERE 
                            house_number = {house_number} AND user_id = {USER_ID})
                    ''')
    return [int(num[0]) for num in cursor.fetchall()]

async def get_question_photos(house_number, q_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'''
                    SELECT photo
                    FROM bot_photo 
                    WHERE question_id = (
                        SELECT id
                        FROM bot_question
                        WHERE house_id = (
                                SELECT id FROM bot_house WHERE house_number = {house_number} AND user_id = {USER_ID}
                        ) AND question_number = {q_number}
                    )
                    ''')
    rows = cursor.fetchall()
    return [os.path.join(MEDIA_ROOT, item[0]) for item in rows]
   
async def get_question_videos(house_number, q_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'''
                    SELECT video
                    FROM bot_video 
                    WHERE question_id = (
                        SELECT id
                        FROM bot_question
                        WHERE house_id = (
                                SELECT id FROM bot_house WHERE house_number = {house_number} AND user_id = {USER_ID}
                        ) AND question_number = {q_number}
                    )
                    ''')
    rows = cursor.fetchall()
    return [os.path.join(MEDIA_ROOT, item[0]) for item in rows]