from aiogram.fsm.state import State, StatesGroup

class CabinetState(StatesGroup):
    waiting_company_name = State()
    waiting_company_number = State()
    waiting_company_email = State()
