import streamlit as st

import constants as c
from src.model.ImpelDownLog import ImpelDownLog
from src.model.exceptions.ValidationException import ValidationException
from src.service.impel_down_service import get_logs_by_string_filter, get_log_display_text, reverse_bounty_action


def main():
    """
    Main function
    :return:
    """

    st.title("Impel Down Records")
    st.markdown(c.HIDE_ST_STYLE, unsafe_allow_html=True)

    key_suffix = "_impel_down_logs"

    # Filter records by first name, last name, username or user id, sentence reason
    filter_by = st.text_input(
        label="Search", key=f"filter_by{key_suffix}",
        help="Search by first name, last name, username, user id, bounty action, sentence reason or type")

    # Filter logs limit 10
    if len(filter_by) > 1:
        logs: list[ImpelDownLog] = get_logs_by_string_filter(filter_by)
    else:
        logs: list[ImpelDownLog] = ImpelDownLog.select().order_by(ImpelDownLog.id.desc()).limit(10)

    for index, log in enumerate(logs):
        expander_text = get_log_display_text(log)

        with st.expander(expander_text):
            # Basic information
            col0 = st.columns(1)[0]
            col_1, col_2 = st.columns(2)

            # Reason (if applicable)
            if log.reason is not None:
                col0.info(log.reason)

            # Sentence type and release datetime (if applicable)
            if log.sentence_type is not None:
                col_1.text_input("Sentence Type", value=log.sentence_type, disabled=True,
                                 key=f"sentence_type{key_suffix}{index}")
                release_datetime_string = log.release_date_time if log.release_date_time is not None else "Undefined"
                col_2.text_input("Release Datetime", value=release_datetime_string, disabled=True,
                                 key=f"release_datetime{key_suffix}{index}")

            # Bounty action and lost bounty (if applicable)
            if log.bounty_action is not None:
                col_1.text_input("Bounty Action", value=log.bounty_action, disabled=True,
                                 key=f"bounty_action{key_suffix}{index}")
                lost_bounty_string = '{0:,}'.format(log.previous_bounty - log.new_bounty)
                col_2.text_input("Lost Bounty", value=lost_bounty_string, disabled=True,
                                 key=f"lost_bounty{key_suffix}{index}")

                # Reverse bounty action and lost bounty
                reverse_button_is_enabled = not log.is_reversed

                if col_1.button("Reverse", key=f"reverse_button{key_suffix}{index}",
                                disabled=not reverse_button_is_enabled):
                    try:
                        reverse_bounty_action(log)

                        st.success("Bounty action reversed successfully")
                    except ValidationException as e:
                        st.error(e.message)


main()
