import streamlit as st
from streamlit_option_menu import option_menu

import constants as c
from pages.legendary_pirates.add import main as add_main
from pages.legendary_pirates.list import main as list_main
from src.model.LegendaryPirate import ensure_legendary_pirate_schema

ensure_legendary_pirate_schema()


def main():
    """
    Main function
    :return:
    """

    st.title("Legendary Pirates")
    st.markdown(c.HIDE_ST_STYLE, unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=["Add", "List"],
        icons=["plus-square", "list-ul"],
        orientation="horizontal",
    )

    if selected == "Add":
        add_main()
    elif selected == "List":
        list_main()


main()
