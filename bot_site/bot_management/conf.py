RABBITMQ_LOGIN = "guest"
RABBITMQ_PASSWORD = "guest"
RABBITMQ_QUEUE_NAME = "newsletter_queue_"
RABBITMQ_HOST_NAME = "rabbitmq"
RABBITMQ_CONNECT_RETRIES = 5
DELAY_BETWEEN_RETRIES = 0.5

initial_prompts = [
    {
        'prompt_name': 'greeting_phrase',
        'prompt': 'Добро пожаловать на нашу дачу!',
        'helper_text': 'Приветственное сообщение',
    },
    {
        'prompt_name': 'rules',
        'prompt': 'Правила нашей дачи:...',
        'helper_text': 'Правила дачи',
    },
    {
        'prompt_name': 'house_choose_text',
        'prompt': 'Пожалуйста, отправьте в ответ номер выбранного дома.',
        'helper_text': 'Приглашение к выбору дома',
    },
    {
        'prompt_name': 'incorrect_house_number',
        'prompt': 'Некорректный номер дома. Пожалуйста, попробуйте еще раз.',
        'helper_text': 'Некорректный номер дома',
    },
    {
        'prompt_name': 'answer_to_no_more_questions',
        'prompt': """Отлично, желаем вам хорошего отдыха! 
        Если появятся еще вопросы - просто отправьте мне номер интересующего. Список вопросов можно получить с помощью команды /questions_list.""",
        'helper_text': 'Сообщение в случае, если не осталось вопросов',
    },
    {
        'prompt_name': 'answer_to_more_questions',
        'prompt': 'Отправьте мне номер интересующего вас вопроса. Для получения списка вопросов воспользуйтесь командой /questions_list.',
        'helper_text': 'Сообщение в случае, если еще остались вопросы',
    },
    {
        'prompt_name': 'incorrect_question_number',
        'prompt': 'Некорректный номер вопроса. Пожалуйста, попробуйте еще раз.',
        'helper_text': 'Некорректный номер вопроса',
    },
]