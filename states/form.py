from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    waiting_for_contact = State()
    waiting_for_institution_type = State()
    waiting_for_institution_name = State()
    waiting_for_address = State()
    waiting_for_landmark = State()
    waiting_for_location = State()
    confirmation = State()