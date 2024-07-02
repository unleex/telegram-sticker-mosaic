from aiogram.fsm.state import State, StatesGroup
class FSMStates(StatesGroup):
    init_mosaic = State()
    mosaic_setting_title = State()