import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Crew import Crew


class User(BaseModel):
    """
    User class
    """
    id: int | PrimaryKeyField = PrimaryKeyField()
    tg_user_id: str | CharField = CharField(max_length=99, unique=True)
    tg_first_name: str | CharField = CharField(max_length=99)
    tg_last_name: str | CharField = CharField(max_length=99)
    tg_username: str | CharField = CharField(max_length=99)
    bounty: int | BigIntegerField = BigIntegerField(default=0)
    total_gained_bounty: int | BigIntegerField = BigIntegerField(
        default=0, constraints=[Check("total_gained_bounty >= 0")]
    )
    total_gained_bounty_unmodified: int | BigIntegerField = BigIntegerField(
        default=0, constraints=[Check("total_gained_bounty_unmodified >= 0")]
    )
    pending_bounty: int | BigIntegerField = BigIntegerField(default=0)
    doc_q_cooldown_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    game_cooldown_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    bounty_poster_limit: int | SmallIntegerField = SmallIntegerField(default=0)
    location_level: int | SmallIntegerField = SmallIntegerField(default=0)
    should_propose_new_world: bool | BooleanField = BooleanField(default=True)
    can_change_region: bool | BooleanField = BooleanField(default=True)
    fight_immunity_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    fight_cooldown_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    plunder_immunity_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    plunder_cooldown_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    impel_down_release_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    impel_down_is_permanent: bool | BooleanField = BooleanField(default=False)
    crew: Crew | ForeignKeyField = ForeignKeyField(Crew, backref="crew_members", null=True)
    crew_join_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    crew_role: int | SmallIntegerField = SmallIntegerField(null=True)
    crew_promotion_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    conscription_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    can_create_crew: bool | BooleanField = BooleanField(default=True)
    can_join_crew: bool | BooleanField = BooleanField(default=True)
    crew_davy_back_fight_priority: int | IntegerField = IntegerField(null=True)
    last_message_date: datetime.datetime | DateTimeField = DateTimeField(
        default=datetime.datetime.now
    )
    last_system_interaction_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    private_screen_list: str | CharField | None = CharField(max_length=99)
    private_screen_step: int | SmallIntegerField | None = SmallIntegerField()
    private_screen_in_edit_id: int | IntegerField | None = IntegerField(null=True)
    bounty_gift_tax: int | IntegerField = IntegerField(default=0)
    is_admin: bool | BooleanField = BooleanField(default=False)
    devil_fruit_collection_cooldown_end_date: datetime.datetime | DateTimeField = DateTimeField(
        null=True
    )
    timezone: str | CharField = CharField(max_length=99, null=True)
    is_active: bool | BooleanField = BooleanField(default=True)
    prediction_creation_cooldown_end_date: datetime.datetime | DateTimeField = DateTimeField(
        null=True
    )
    bounty_loan_issue_cool_down_end_date: datetime.datetime | DateTimeField = DateTimeField(
        null=True
    )
    # For Legendary Pirate
    is_exempt_from_global_leaderboard_requirements: bool | BooleanField = BooleanField(
        default=True
    )
    can_collect_daily_reward: bool | BooleanField = BooleanField(default=True)

    class Meta:
        db_table = 'user'

    def get_bounty_formatted(self) -> str:
        """
        Returns a formatted string of the bounty
        :return: The formatted string e.g. 1,000,000
        """

        return '{0:,}'.format(self.bounty)

    def is_arrested(self):
        """
        Returns True if the user is arrested
        :return: True if the user is arrested
        """

        return ((self.impel_down_release_date is not None and self.impel_down_release_date > datetime.datetime.now())
                or self.impel_down_is_permanent)

    def get_display_name(self, add_user_id: bool = False) -> str:
        """
        Gets the user display name
        :param add_user_id: Add user id
        :return: User display name
        """
        return "{}{}{}{}".format(self.tg_first_name,
                                 " " + self.tg_last_name if self.tg_last_name is not None else "",
                                 " (@" + self.tg_username + ")" if self.tg_username is not None else "",
                                 " - " + self.tg_user_id if add_user_id else "")

    @staticmethod
    def get_by_string_filter(filter_by: str) -> list['User']:
        """
        Gets users by string filter, searching by first name, last name, username or user id
        :param filter_by: Filter by
        :return: Users
        """

        return User.select().where((User.tg_first_name.contains(filter_by)) |
                                   (User.tg_last_name.contains(filter_by)) |
                                   (User.tg_username.contains(filter_by)) |
                                   (User.tg_user_id.contains(filter_by))
                                   ).order_by(User.tg_first_name.desc()).limit(10)

    def is_warlord(self) -> bool:
        """
        Returns True if the user is a Warlord
        :return: True if the user is a Warlord
        """
        from src.model.Warlord import Warlord

        return self.warlords.where(Warlord.end_date > datetime.datetime.now()).count() > 0


User.create_table()
