import logging
import sys

import streamlit as st

import constants as c
import resources.Environment as Env

st.set_page_config(
    page_title="One Piece Deluxe Tools",
    page_icon="👋",
)

st.title("Main Page")

# --- HIDE STREAMLIT STYLE ---
st.markdown(c.HIDE_ST_STYLE, unsafe_allow_html=True)

if Env.DB_LOG_QUERIES.get_bool():
    # Set Peewee logger
    logger = logging.getLogger('peewee')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, stream=sys.stdout)
