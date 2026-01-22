from aiogram.fsm.state import State, StatesGroup

class CabinetState(StatesGroup):
    waiting_company_name = State()
