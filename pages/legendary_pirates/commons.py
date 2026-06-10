from datetime import datetime

import streamlit as st

import resources.Environment as Env
from src.model.LegendaryPirate import LegendaryPirate
from src.model.User import User
from src.model.exceptions.ValidationException import ValidationException
from src.model.tgrest.TgRestLegendaryPirateAppointment import TgRestLegendaryPirateAppointment
from src.service.date_service import get_remaining_time_in_days, get_datetime_in_future_days
from src.service.form_service import get_session_state_key, validate_not_empty_fields
from src.service.tg_rest_service import send_tg_rest


def show_add_form(key_suffix: str, legendary_pirate: LegendaryPirate = None) -> None:
    """
    Show add form
    :param key_suffix: Key suffix
    :param legendary_pirate: The legendary pirate
    :return: None
    """

    is_disabled = legendary_pirate is not None and not legendary_pirate.is_active()

    epithet_value = legendary_pirate.epithet if legendary_pirate else ""
    st.text_input(label="Epithet", value=epithet_value, key=f"epithet{key_suffix}", max_chars=99,
                  disabled=is_disabled)

    reason_value = legendary_pirate.reason if legendary_pirate else ""
    st.text_input(label="Reason", value=reason_value, key=f"reason{key_suffix}", max_chars=999,
                  disabled=is_disabled)

    is_permanent_value = legendary_pirate.is_permanent if legendary_pirate else False
    if legendary_pirate and legendary_pirate.end_date is None and not legendary_pirate.is_permanent:
        is_permanent_value = True

    st.checkbox("Permanent", key=f"is_permanent{key_suffix}", value=is_permanent_value, disabled=is_disabled)

    is_permanent = get_session_state_key("is_permanent", key_suffix)
    duration_value = 7
    if legendary_pirate and legendary_pirate.end_date is not None:
        duration_value = get_remaining_time_in_days(legendary_pirate.end_date, legendary_pirate.date)

    st.number_input(label="Duration in days", value=duration_value, key=f"duration{key_suffix}",
                    min_value=0, max_value=365, disabled=(is_disabled or is_permanent))


def validate(key_suffix: str, user: User, legendary_pirate: LegendaryPirate) -> None:
    """
    Validate the legendary pirate, raise exception if not valid
    :param key_suffix: Key suffix
    :param user: The user
    :param legendary_pirate: The legendary pirate
    :return: None
    """

    validate_not_empty_fields(["epithet", "reason"], key_suffix)

    is_new = legendary_pirate is None
    is_permanent = get_session_state_key("is_permanent", key_suffix)

    if is_new:
        if user.is_legendary_pirate():
            raise ValidationException(f"User {user.get_display_name()} is already a Legendary Pirate")

        if LegendaryPirate.get_active_count() >= Env.MAX_LEGENDARY_PIRATES.get_int():
            raise ValidationException(
                f"Max number of Legendary Pirates reached: {Env.MAX_LEGENDARY_PIRATES.get_int()}")
    else:
        if not legendary_pirate.is_active():
            raise ValidationException("Expired Legendary Pirate cannot be updated")

        if not is_permanent and legendary_pirate.end_date is not None:
            duration = get_session_state_key("duration", key_suffix)
            if datetime.now() > legendary_pirate.get_end_date_by_duration(duration):
                elapsed_days = get_remaining_time_in_days(legendary_pirate.end_date, legendary_pirate.date)
                raise ValidationException(
                    f"Duration cannot be less than already elapsed days: {elapsed_days}")

    epithet: str = get_session_state_key("epithet", key_suffix)
    now = datetime.now()
    existing_legendary_pirate: LegendaryPirate = LegendaryPirate.get_or_none(
        ((LegendaryPirate.end_date.is_null()) | (LegendaryPirate.end_date > now))
        & (LegendaryPirate.user != user)
        & (LegendaryPirate.epithet == epithet))
    if existing_legendary_pirate:
        raise ValidationException(f"Legendary Pirate with epithet {epithet} already exists")

    if not is_permanent and is_new:
        validate_not_empty_fields(["duration"], key_suffix)


def save(key_suffix: str, user: User, legendary_pirate: LegendaryPirate | None) -> None:
    """
    Save the legendary pirate
    :param key_suffix: Key suffix
    :param user: The user
    :param legendary_pirate: The legendary pirate
    :return: None
    """

    is_new = legendary_pirate is None

    try:
        validate(key_suffix, user, legendary_pirate)
        try:
            is_permanent = get_session_state_key("is_permanent", key_suffix)
            duration = get_session_state_key("duration", key_suffix) if not is_permanent else None

            if is_new:
                legendary_pirate = LegendaryPirate()
                legendary_pirate.user = user
                legendary_pirate.is_permanent = is_permanent
                if is_permanent:
                    legendary_pirate.end_date = None
                    legendary_pirate.original_end_date = None
                else:
                    end_date = get_datetime_in_future_days(duration)
                    legendary_pirate.end_date = end_date
                    legendary_pirate.original_end_date = end_date
            elif is_permanent:
                legendary_pirate.is_permanent = True
                legendary_pirate.end_date = None
            else:
                end_date = legendary_pirate.get_end_date_by_duration(duration)
                legendary_pirate.is_permanent = False
                legendary_pirate.end_date = end_date

            legendary_pirate.epithet = get_session_state_key("epithet", key_suffix)
            legendary_pirate.reason = get_session_state_key("reason", key_suffix)
            legendary_pirate.save()

            if is_new:
                st.success(f"Legendary Pirate {legendary_pirate.epithet} successfully appointed")

                tg_rest_message = TgRestLegendaryPirateAppointment(
                    user.id, legendary_pirate.id, duration, is_permanent)
                send_tg_rest(tg_rest_message)
            else:
                st.success(f"Legendary Pirate {legendary_pirate.epithet} successfully updated")
        except Exception as e:
            st.error(f"Error saving Legendary Pirate: {e}")
    except ValidationException as ve:
        st.error(ve)
