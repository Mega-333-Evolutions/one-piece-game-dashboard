from datetime import datetime

import streamlit as st

from pages.legendary_pirates.commons import show_add_form, save
from src.model.LegendaryPirate import LegendaryPirate
from src.model.User import User
from src.model.tgrest.TgRestLegendaryPirateRevocation import TgRestLegendaryPirateRevocation
from src.service.tg_rest_service import send_tg_rest


def main() -> None:
    """
    View list function
    :return:
    """

    key_suffix = "_list"

    only_active = st.checkbox("Only active", value=True)

    filter_by = st.text_input(
        label="Search", key=f"filter_by{key_suffix}",
        help="Search by first name, last name, username, user id, epithet, reason")

    if len(filter_by) > 1:
        legendary_pirates: list[LegendaryPirate] = LegendaryPirate.get_by_string_filter(
            filter_by, only_active=only_active)
    else:
        legendary_pirates: list[LegendaryPirate] = LegendaryPirate.get_all(only_active=only_active)

    for index, legendary_pirate in enumerate(legendary_pirates):
        key_suffix_list = f"{key_suffix}_{index}"

        user: User = legendary_pirate.user
        with st.expander(user.get_display_name()):

            if not only_active:
                if legendary_pirate.is_active():
                    st.info("Active")
                else:
                    st.error("Inactive")

            col_start_date, col_end_date = st.columns(2)
            col_start_date.text_input("Start date", value=legendary_pirate.date, disabled=True,
                                      key=f"start_date{key_suffix_list}")

            if legendary_pirate.is_permanent or legendary_pirate.end_date is None:
                end_date_display = "Permanent"
            else:
                end_date_display = legendary_pirate.end_date

            col_end_date.text_input("End date", value=end_date_display, disabled=True,
                                    key=f"end_date{key_suffix_list}")

            with st.form(f"legendary_pirate_edit_form{key_suffix_list}", clear_on_submit=False):
                show_add_form(key_suffix_list, legendary_pirate=legendary_pirate)
                submitted = st.form_submit_button("Save")

                if submitted:
                    save(key_suffix_list, user, legendary_pirate)

            if legendary_pirate.is_active():
                st.subheader("Revoke membership")

                reason: str = st.text_input(label="Reason", key=f"revoke_reason_{key_suffix_list}")
                if st.button("Revoke membership", key=f"revoke{key_suffix_list}"):
                    if len(reason) == 0:
                        st.error("Reason is required")
                    else:
                        legendary_pirate.end_date = datetime.now()
                        legendary_pirate.is_permanent = False
                        legendary_pirate.revoke_reason = reason
                        legendary_pirate.save()

                        st.success("Legendary Pirate membership revoked, refresh the page")

                        tg_rest_message = TgRestLegendaryPirateRevocation(user.id, legendary_pirate.id)
                        send_tg_rest(tg_rest_message)
