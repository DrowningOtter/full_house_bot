import  psycopg2, os
from conf import DB_NAME, USER_ID, MEDIA_ROOT
from main import logging

db_params = {
    'dbname': 'full_house',
    'user': 'postgres',
    'password': 12345,
    'host': 'postgres_host',
    'port': 5432,
}

async def reg_user(reg_id):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    # cursor.execute("""
    #                 INSERT INTO bot_registeredusers (user_id, tg_user_id)
    #                 (SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM bot_registeredusers WHERE user_id = ? AND tg_user_id = ?))
    #                """, (USER_ID, reg_id, USER_ID, reg_id))
    try:
        cursor.execute("""
                        INSERT INTO bot_registeredusers (user_id, tg_user_id)
                        VALUES (%s, %s)
                        """, (USER_ID, reg_id))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        print(f"Error: {ex}")
    finally:
        cursor.close()
        conn.close()

async def get_prompt(prompt_name):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    cursor.execute(f"SELECT prompt FROM bot_prompt WHERE user_id = {USER_ID} AND prompt_name = '{prompt_name}'")
    logging.info(f"SELECT prompt FROM bot_prompt WHERE user_id = {USER_ID} AND prompt_name = '{prompt_name}'")
    res = cursor.fetchall()
    logging.info("-----------------res = ", " ".join(["("+", ".join(item)+")" for item in res]))
    if res == []:
        return ""
    prompt = res[0][0]
    conn.close()
    return prompt

# TODO fix query idiot
async def get_question_with_answer(number:int):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    cursor.execute(f'SELECT question_text, answer_text FROM bot_question ')
    conn.close()

async def get_house_list():
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    cursor.execute(f'SELECT house_number, house_name, address FROM bot_house WHERE user_id = {USER_ID}')
    rows = cursor.fetchall()
    rows = [f"{item[0]}. {item[1]} ({item[2]})" for item in rows]
    conn.close()
    return "\n".join(rows)

async def get_house_numbers():
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    cursor.execute(f'SELECT house_number FROM bot_house WHERE user_id = {USER_ID}')
    conn.close()
    return [int(num[0]) for num in cursor.fetchall()]

async def get_house_videos(house_number):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    cursor.execute(f'''SELECT video 
                             FROM bot_video
                             WHERE user_id = {USER_ID} AND house_id = 
                                (
                                    SELECT id FROM bot_house WHERE house_number = {house_number} AND user_id = {USER_ID}
                                )''')
    photos = cursor.fetchall()
    conn.close()
    return [os.path.join(MEDIA_ROOT, item[0]) for item in photos]

async def get_house_info(house_number):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    cursor.execute(f'''
                    SELECT house_name, address 
                    FROM bot_house
                    WHERE user_id = {USER_ID} AND house_number = {house_number}
                    ''')
    house_info = cursor.fetchall()[0]
    # return '\n'.join(row)
    conn.close()
    return f"Дом успешно выбран!\n<b>Название дома:</b> {house_info[0]}\n<b>Адрес:</b> {house_info[1]}"

async def get_house_photos(house_number):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    cursor.execute(f'''SELECT photo 
                        FROM bot_photo 
                        WHERE user_id = {USER_ID} AND house_id = (
                            SELECT id FROM bot_house WHERE house_number={house_number} AND user_id = {USER_ID}
                            )''')
    photos = cursor.fetchall()
    conn.close()
    return [os.path.join(MEDIA_ROOT, item[0]) for item in photos]

async def get_questions_list(house_number):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    cursor.execute(f'''
                    SELECT question_number, question_text
                    FROM bot_question
                    WHERE user_id = {USER_ID} AND house_id = (SELECT id FROM bot_house WHERE house_number = {house_number})
                    ''')
    questions = cursor.fetchall()
    conn.close()
    return [f"{item[0]}. {item[1]}" for item in questions]

async def get_answer_text(house_number, question_number):
    conn = psycopg2.connect(**db_params)
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
    conn.close()
    return f"{text[0]}. {text[1]}\n{text[2]}"

async def get_questions_numbers(house_number):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    cursor.execute(f'''
                    SELECT question_number FROM bot_question WHERE user_id = {USER_ID} AND house_id = (
                        SELECT id FROM bot_house WHERE 
                            house_number = {house_number} AND user_id = {USER_ID})
                    ''')
    conn.close()
    return [int(num[0]) for num in cursor.fetchall()]

async def get_question_photos(house_number, q_number):
    conn = psycopg2.connect(**db_params)
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
    conn.close()
    return [os.path.join(MEDIA_ROOT, item[0]) for item in rows]
   
async def get_question_videos(house_number, q_number):
    conn = psycopg2.connect(**db_params)
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
    conn.close()
    return [os.path.join(MEDIA_ROOT, item[0]) for item in rows]