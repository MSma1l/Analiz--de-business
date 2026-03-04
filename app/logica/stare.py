from aiogram.fsm.state import State, StatesGroup  # Importam clasele State si StatesGroup din aiogram pentru definirea starilor FSM (Finite State Machine)

class CabinetState(StatesGroup):  # Definim clasa CabinetState care mosteneste StatesGroup si contine starile pentru fluxul cabinetului
    waiting_company_name = State()  # Starea de asteptare a numelui companiei de la utilizator
    waiting_company_number = State()  # Starea de asteptare a numarului de telefon al companiei de la utilizator
    waiting_company_email = State()  # Starea de asteptare a adresei de email a companiei de la utilizator
