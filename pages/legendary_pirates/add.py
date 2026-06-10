import streamlit as st

from pages.commons.util import select_user_select_box, get_selected_user
from pages.legendary_pirates.commons import show_add_form, save
from src.model.User import User


def main() -> None:
    """
    Add legendary pirate function
    :return:
    """

    key_suffix = "_add"

    selected_user_display_name, users_display_name_map = select_user_select_box(key_suffix)
    selected_user: User = get_selected_user(selected_user_display_name, users_display_name_map)

    if selected_user:
        with st.form("legendary_pirate_add_form", clear_on_submit=False):
            show_add_form(key_suffix)

            submitted = st.form_submit_button("Save")
            if submitted:
                save(key_suffix, selected_user, None)
