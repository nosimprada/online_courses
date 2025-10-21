from aiogram.fsm.state import State, StatesGroup

class RefCode(StatesGroup):
    get_ref_code = State()

class RenewalRefCode(StatesGroup):
    get_ref_code = State()
    
# ---------------------------- FSM States ----------------------------

class GrantSubscriptionState(StatesGroup):
    access_to = State()


class CreateLessonState(StatesGroup):
    title = State()
    video = State()
    pdf = State()


class UpdateLessonState(StatesGroup):
    title = State()
    video = State()
    pdf = State()
