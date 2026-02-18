"""FSM states for onboarding flow."""

from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    """States for the onboarding flow."""
    waiting_for_email = State()
    choosing_plan = State()
    confirming_payment = State()


class SupportStates(StatesGroup):
    """States for support ticket creation."""
    waiting_for_subject = State()
    waiting_for_description = State()
    confirming_ticket = State()
