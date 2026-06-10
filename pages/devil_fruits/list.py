import streamlit as st

import resources.Environment as Env
from pages.commons.util import select_user_select_box, get_selected_user
from pages.devil_fruits.commons import show_and_get_abilities_multi_select, show_add_form, save
from src.model.DevilFruit import DevilFruit
from src.model.DevilFruitAbility import DevilFruitAbility
from src.model.DevilFruitTrade import DevilFruitTrade
from src.model.User import User
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.enums.devil_fruit.DevilFruitStatus import DevilFruitStatus
from src.model.tgrest.TgRestDevilFruitAward import TgRestDevilFruitAward
from src.model.tgrest.TgRestDevilFruitForceSchedule import TgRestDevilFruitForceSchedule
from src.service.tg_rest_service import send_tg_rest


def main() -> None:
    """
    View list function
    :return:
    """

    key_suffix = "_list"

    # Filter by status multiselect
    default_status = [DevilFruitStatus.NEW, DevilFruitStatus.COMPLETED, DevilFruitStatus.ENABLED]
    status_filter: list[str] = st.multiselect("Status filter", DevilFruitStatus.get_all_description(),
                                              [status.get_description() for status in default_status])

    selected_statuses = [DevilFruitStatus.get_by_description(status_str) for status_str in status_filter]

    # Filter by name text input
    name_filter = st.text_input("Name filter", "")

    # Get fruits
    devil_fruits: list[DevilFruit] = (DevilFruit.select()
                                      .where((DevilFruit.status.in_(selected_statuses))
                                             & ((DevilFruit.name.contains(name_filter))
                                                | (DevilFruit.model.contains(name_filter))))
                                      .order_by(DevilFruit.id.desc())
                                      .limit(Env.MAX_ITEMS_DISPLAYED_LIST.get_int()))

    for index, devil_fruit in enumerate(devil_fruits):
        key_suffix_list = f"{key_suffix}_{index}"
        status: DevilFruitStatus = DevilFruitStatus(devil_fruit.status)

        with st.expander(devil_fruit.get_full_name()):
            st.info(devil_fruit.get_status_description())
            abilities: list[DevilFruitAbility] = (DevilFruitAbility.select().where(
                DevilFruitAbility.devil_fruit == devil_fruit))

            # Get abilities from multi select
            abilities_type_value_dict: dict[DevilFruitAbilityType, int] = (
                show_and_get_abilities_multi_select(key_suffix_list, existing_abilities=abilities))

            with st.form(f"devil_fruit_edit_form{key_suffix_list}", clear_on_submit=False):
                show_add_form(key_suffix_list, abilities_type_value_dict, devil_fruit=devil_fruit)
                submitted = st.form_submit_button("Save")

                if submitted:
                    save(key_suffix_list, abilities_type_value_dict, devil_fruit=devil_fruit)

            if status is DevilFruitStatus.SCHEDULED:
                if st.button("Enable", key=f"enable{key_suffix_list}"):
                    devil_fruit.status = DevilFruitStatus.ENABLED
                    devil_fruit.save()
                    st.success("Devil fruit enabled, refresh the page")

            # Show if status is new, completed or enabled
            if status in [DevilFruitStatus.NEW, DevilFruitStatus.COMPLETED, DevilFruitStatus.ENABLED]:
                # Award to user section
                if status in [DevilFruitStatus.COMPLETED, DevilFruitStatus.ENABLED]:
                    st.subheader("Award to user")

                    selected_user_display_name, users_display_name_map = select_user_select_box(key_suffix_list)

                    # Reason input box
                    reason: str = st.text_input(label="Reason", key=f"reason{key_suffix_list}")
                    # Award button
                    if st.button("Award", key=f"award{key_suffix_list}", disabled=(selected_user_display_name is None)):
                        selected_user: User = get_selected_user(selected_user_display_name, users_display_name_map)
                        # Reason is required
                        if len(reason) == 0:
                            st.error("Reason is required")
                        else:
                            tg_rest_message = TgRestDevilFruitAward(selected_user.id, devil_fruit.id, reason)
                            send_tg_rest(tg_rest_message)

                            st.success("Devil fruit awarded, refresh the page")

                if status is DevilFruitStatus.ENABLED:
                    st.subheader("Force Schedule")
                    if st.button("Force Schedule", key=f"force_schedule{key_suffix_list}"):
                        tg_rest_message = TgRestDevilFruitForceSchedule(devil_fruit.id)
                        send_tg_rest(tg_rest_message, "Devil fruit scheduled for release, refresh the page")

                # Delete button
                st.subheader("Delete")
                if st.button("Delete", key=f"delete{key_suffix_list}"):
                    # Recheck status
                    if status not in [DevilFruitStatus.NEW, DevilFruitStatus.COMPLETED, DevilFruitStatus.ENABLED]:
                        st.error("Devil fruit is not in NEW, COMPLETED or ENABLED status")
                    else:
                        DevilFruitTrade.delete().where(DevilFruitTrade.devil_fruit_id == devil_fruit.id).execute()
                        devil_fruit.delete_instance()
                        st.success("Devil fruit deleted, refresh the page")
