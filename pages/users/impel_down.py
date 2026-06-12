from datetime import datetime, timedelta

import streamlit as st

from src.model.ImpelDownLog import ImpelDownLog
from src.model.User import User
from src.model.enums.impel_down.ImpelDownBountyAction import ImpelDownBountyAction
from src.model.enums.impel_down.ImpelDownSentenceType import ImpelDownSentenceType
from src.model.exceptions.ValidationException import ValidationException
from src.model.tgrest.TgRestImpelDownNotification import TgRestImpelDownNotification
from src.service.tg_rest_service import send_tg_rest

# Quick-select durations (label -> total minutes). None = show custom inputs.
QUICK_DURATIONS = {
    "Custom": None,
    "30 minutes": 30,
    "1 hour": 60,
    "6 hours": 360,
    "12 hours": 720,
    "1 day": 1440,
    "3 days": 4320,
    "7 days": 10080,
}


def main(user: User) -> None:
    """
    Impel down function
    :return:
    """
    key_suffix = "_impel_down"
    sentence_radio_key = f"sentence_radio_{user.id}{key_suffix}"
    quick_duration_key = f"quick_duration_{user.id}{key_suffix}"

    # Display arrested status
    if user.is_arrested():
        arrested_status_text = "Arrested"
        if user.impel_down_is_permanent:
            arrested_status_text += " (permanent)"
        else:
            arrested_status_text += " until {}".format(user.impel_down_release_date)
    else:
        arrested_status_text = "Free"
    st.info(arrested_status_text)

    # Sentence type radio — OUTSIDE the form so its value is immediately
    # available in session_state to drive the conditional duration block.
    if user.impel_down_is_permanent:
        sentence_radio_index = 2
    elif user.is_arrested():
        sentence_radio_index = 1
    else:
        sentence_radio_index = 0

    sentence_type_value = st.radio(
        "Sentence",
        [e for e in ImpelDownSentenceType],
        index=sentence_radio_index,
        key=sentence_radio_key,
    )

    # -------------------------------------------------------------------------
    # Duration selector — only shown when Temporary is selected.
    # Also outside the form so Custom inputs appear instantly on selectbox change.
    # -------------------------------------------------------------------------
    total_duration_minutes = 0

    if ImpelDownSentenceType(sentence_type_value) is ImpelDownSentenceType.TEMPORARY:
        st.markdown("**Sentence Duration**")

        quick_label = st.selectbox(
            "Quick select",
            list(QUICK_DURATIONS.keys()),
            index=5,  # default: "1 day"
            key=quick_duration_key,
            help="Choose a preset duration, or pick Custom to enter days/hours/minutes manually.",
        )

        chosen_minutes = QUICK_DURATIONS[quick_label]

        if chosen_minutes is None:
            col_days, col_hours, col_mins = st.columns(3)
            duration_days = col_days.number_input(
                "Days",
                min_value=0,
                max_value=365,
                value=1,
                step=1,
                key=f"duration_days_{user.id}{key_suffix}",
            )
            duration_hours = col_hours.number_input(
                "Hours",
                min_value=0,
                max_value=23,
                value=0,
                step=1,
                key=f"duration_hours_{user.id}{key_suffix}",
            )
            duration_mins = col_mins.number_input(
                "Minutes",
                min_value=0,
                max_value=59,
                value=0,
                step=1,
                key=f"duration_minutes_{user.id}{key_suffix}",
            )
            total_duration_minutes = int(duration_days * 1440 + duration_hours * 60 + duration_mins)
        else:
            total_duration_minutes = chosen_minutes

        # Live preview
        if total_duration_minutes > 0:
            preview_release = datetime.now() + timedelta(minutes=total_duration_minutes)
            expected_bail = total_duration_minutes * 100_000
            st.info(
                f"⏱ Release at: **{preview_release.strftime('%Y-%m-%d %H:%M:%S')}**  \n"
                f"💰 Max bail: **฿{expected_bail:,}** ({total_duration_minutes:,} min × ฿100,000)"
            )
        else:
            st.warning("⚠️ Total duration is 0 — please set at least 1 minute.")

    # -------------------------------------------------------------------------
    # Rest of the form (bounty action, reason, save button)
    # -------------------------------------------------------------------------
    with st.form(f"impel_down_form_{user.id}{key_suffix}"):
        bounty_action = st.radio(
            "Bounty action",
            [e for e in ImpelDownBountyAction],
            index=0,
            key=f"bounty_action_{user.id}{key_suffix}",
        )

        # should_send_message = st.checkbox("Send message", key=f"send_message_{user.id}{key_suffix}")
        should_send_message = True  # Always send message

        reason = st.text_input("Reason", key=f"reason_{user.id}{key_suffix}")

        submitted = st.form_submit_button("Save")

        if submitted:
            # Read sentence_type and duration from session_state since they
            # live outside this form.
            sentence_type = ImpelDownSentenceType(
                st.session_state.get(sentence_radio_key, sentence_type_value)
            )
            duration = st.session_state.get(
                f"_total_duration_{user.id}{key_suffix}", total_duration_minutes
            )
            save(
                user,
                sentence_type,
                ImpelDownBountyAction(bounty_action),
                total_duration_minutes,
                should_send_message,
                reason,
            )


def save(
    user: User,
    sentence_type: ImpelDownSentenceType,
    bounty_action: ImpelDownBountyAction,
    duration_minutes: int,
    should_send_message: bool,
    reason: str,
) -> None:
    """
    Save impel down status.

    :param user: User
    :param sentence_type: Sentence type
    :param bounty_action: Bounty action
    :param duration_minutes: Sentence length in minutes (from now). Only used for TEMPORARY.
    :param should_send_message: If a notification should be sent to the bot
    :param reason: Reason (required when should_send_message is True)
    :return:
    """
    try:
        validate(sentence_type, duration_minutes, should_send_message, reason)

        impel_down_log: ImpelDownLog = ImpelDownLog()
        impel_down_log.user = user

        user.impel_down_is_permanent = sentence_type is ImpelDownSentenceType.PERMANENT
        impel_down_log.sentence_type = (
            sentence_type if sentence_type is not ImpelDownSentenceType.NONE else None
        )

        if sentence_type is ImpelDownSentenceType.NONE or sentence_type is ImpelDownSentenceType.PERMANENT:
            user.impel_down_release_date = None
            if sentence_type is ImpelDownSentenceType.PERMANENT:
                impel_down_log.is_permanent = True
        else:
            # Compute release_date_time from duration — 1 day = exactly 1440 minutes from now
            release_date_time = datetime.now() + timedelta(minutes=duration_minutes)
            user.impel_down_release_date = release_date_time
            impel_down_log.release_date_time = release_date_time

        impel_down_log.bounty_action = (
            bounty_action if bounty_action is not ImpelDownBountyAction.NONE else None
        )
        impel_down_log.previous_bounty = user.bounty

        if bounty_action is ImpelDownBountyAction.HALVE:
            user.bounty = user.bounty // 2
        elif bounty_action is ImpelDownBountyAction.ERASE:
            user.bounty = 0

        impel_down_log.new_bounty = user.bounty
        impel_down_log.reason = reason if len(reason) > 0 else None

        user.save()
        impel_down_log.save()

        if should_send_message:
            notification = TgRestImpelDownNotification(
                user.id,
                sentence_type,
                user.impel_down_release_date,
                bounty_action,
                reason,
                impel_down_log.id,
            )
            send_tg_rest(notification)
            impel_down_log.message_sent = True
            impel_down_log.save()

        st.success("Saved")

    except ValidationException as ve:
        st.error(ve)
        return


def validate(
    sentence_type: ImpelDownSentenceType,
    duration_minutes: int,
    should_send_message: bool,
    reason: str,
) -> None:
    """
    Validate impel down status.

    :param sentence_type: Sentence type
    :param duration_minutes: Total sentence length in minutes
    :param should_send_message: If a notification should be sent
    :param reason: Reason (required when should_send_message is True)
    :return:
    """
    if sentence_type is ImpelDownSentenceType.TEMPORARY:
        if duration_minutes <= 0:
            raise ValidationException(
                "Sentence duration must be at least 1 minute for a temporary sentence."
            )

    if should_send_message:
        if reason == "":
            raise ValidationException("Reason must be set")
