from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    terms_of_use = State()
    terms_of_use_read = State()
    house_choice = State()
    house_choosen = State()