from datetime import datetime

import streamlit as st

from src.model.ImpelDownLog import ImpelDownLog
from src.model.User import User
from src.model.enums.impel_down.ImpelDownBountyAction import ImpelDownBountyAction
from src.model.enums.impel_down.ImpelDownSentenceType import ImpelDownSentenceType
from src.model.exceptions.ValidationException import ValidationException
from src.model.tgrest.TgRestImpelDownNotification import TgRestImpelDownNotification
from src.service.tg_rest_service import send_tg_rest


def main(user: User) -> None:
    """
    Impel down function
    :return:
    """
    key_suffix = "_impel_down"

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

    # Impel down status form
    with st.form(f"impel_down_form_{user.id}{key_suffix}"):
        # Sentence type  radio
        if user.impel_down_is_permanent:
            sentence_radio_index = 2
        elif user.is_arrested():
            sentence_radio_index = 1
        else:
            sentence_radio_index = 0

        sentence_type = st.radio("Sentence", [e for e in ImpelDownSentenceType], index=sentence_radio_index,
                                 key=f"sentence_radio_{user.id}{key_suffix}")

        # Release date and time
        col_release_date, col_release_time = st.columns(2)
        release_date = col_release_date.date_input("Release date", value=user.impel_down_release_date,
                                                   key=f"release_date_{user.id}{key_suffix}")
        release_time = col_release_time.time_input("Release time", value=user.impel_down_release_date,
                                                   key=f"release_time_{user.id}{key_suffix}")

        # Bounty action radio
        bounty_action = st.radio("Bounty action", [e for e in ImpelDownBountyAction], index=0,
                                 key=f"bounty_action_{user.id}{key_suffix}")

        # Send message checkbox
        # should_send_message = st.checkbox("Send message", key=f"send_message_{user.id}{key_suffix}")
        should_send_message = True  # Always send message

        # Reason input
        reason = st.text_input("Reason", key=f"reason_{user.id}{key_suffix}")

        # Save button
        submitted = st.form_submit_button("Save")

        if submitted:
            save(user, ImpelDownSentenceType(sentence_type), ImpelDownBountyAction(bounty_action), release_date,
                 release_time, should_send_message, reason)


def save(user: User, sentence_type: ImpelDownSentenceType, bounty_action: ImpelDownBountyAction, release_date: datetime,
         release_time: datetime.time, should_send_message, reason) -> None:
    """
    Save impel down status
    :param user: User
    :param sentence_type: Sentence type
    :param bounty_action: Bounty action
    :param release_date: Release date
    :param release_time: Release time
    :param should_send_message: If a message should be sent
    :param reason: Reason. Must be set if should_send_message is True
    :return:
    """
    try:
        # Validation
        validate(sentence_type, release_date, release_time, should_send_message, reason)

        impel_down_log: ImpelDownLog = ImpelDownLog()
        impel_down_log.user = user

        # Save
        user.impel_down_is_permanent = sentence_type is ImpelDownSentenceType.PERMANENT

        impel_down_log.sentence_type = sentence_type if sentence_type is not ImpelDownSentenceType.NONE else None

        if sentence_type is ImpelDownSentenceType.NONE or sentence_type is ImpelDownSentenceType.PERMANENT:
            user.impel_down_release_date = None

            if sentence_type is ImpelDownSentenceType.PERMANENT:
                impel_down_log.is_permanent = True
        else:
            user.impel_down_release_date = datetime.combine(release_date, release_time)
            impel_down_log.release_date_time = user.impel_down_release_date

        impel_down_log.bounty_action = bounty_action if bounty_action is not ImpelDownBountyAction.NONE else None
        impel_down_log.previous_bounty = user.bounty

        if bounty_action is ImpelDownBountyAction.HALVE:
            user.bounty = user.bounty // 2
        elif bounty_action is ImpelDownBountyAction.ERASE:
            user.bounty = 0

        impel_down_log.new_bounty = user.bounty
        impel_down_log.reason = reason if len(reason) > 0 else None

        user.save()
        impel_down_log.save()

        # Send notification message
        if should_send_message:
            if sentence_type is ImpelDownSentenceType.TEMPORARY:
                release_date_time = datetime.combine(release_date, release_time)
            else:
                release_date_time = None
            notification = TgRestImpelDownNotification(
                user.id,
                sentence_type,
                release_date_time,
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


def validate(sentence_type: ImpelDownSentenceType, release_date: datetime, release_time: datetime.time,
             should_send_message: bool, reason: str) -> None:
    """
    Validate impel down status
    :param sentence_type: Sentence type
    :param release_date: Release date
    :param release_time: Release time
    :param should_send_message: If a message should be sent
    :param reason: Reason. Must be set if should_send_message is True
    :return:
    """

    # If sentence is temporary, release date and time must be in the future
    if sentence_type is ImpelDownSentenceType.TEMPORARY:
        release_date_time = datetime.combine(release_date, release_time)
        if release_date < datetime.now().date():
            raise ValidationException("Release date cannot be earlier than today")
        if release_date_time < datetime.now():
            raise ValidationException("Release time cannot be earlier than now")

    # If you should send message, reason must be set
    if should_send_message:
        if reason == "":
            raise ValidationException("Reason must be set")
