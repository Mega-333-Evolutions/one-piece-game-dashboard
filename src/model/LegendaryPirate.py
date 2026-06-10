import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.User import User


class LegendaryPirate(BaseModel):
    """
    Legendary Pirate class
    """
    id = PrimaryKeyField()
    user = ForeignKeyField(User, backref='legendary_pirates', on_delete='CASCADE', on_update='CASCADE')
    epithet = CharField(max_length=99, null=True)
    reason = CharField(max_length=999, null=True)
    date = DateTimeField(default=datetime.datetime.now)
    end_date = DateTimeField(null=True)
    original_end_date = DateTimeField(null=True)
    revoke_reason = CharField(max_length=999, null=True)
    is_permanent = BooleanField(default=False)

    class Meta:
        db_table = 'legendary_pirate'

    @staticmethod
    def get_active() -> list['LegendaryPirate']:
        """
        Get active legendary pirates
        :return: Active legendary pirates
        """

        now = datetime.datetime.now()
        return (LegendaryPirate
                .select()
                .where((LegendaryPirate.end_date.is_null()) | (LegendaryPirate.end_date > now)))

    @staticmethod
    def get_active_count() -> int:
        """
        Get active legendary pirates count
        :return: Active legendary pirates count
        """

        return len(LegendaryPirate.get_active())

    @staticmethod
    def get_by_string_filter(filter_by: str, only_active: bool = True) -> list['LegendaryPirate']:
        """
        Gets legendary pirates by string filter
        :param filter_by: Filter by
        :param only_active: Only active
        :return: Legendary pirates
        """

        query = (LegendaryPirate
                 .select()
                 .join(User)
                 .where((User.tg_first_name.contains(filter_by)) |
                        (User.tg_last_name.contains(filter_by)) |
                        (User.tg_username.contains(filter_by)) |
                        (User.tg_user_id.contains(filter_by)) |
                        (LegendaryPirate.epithet.contains(filter_by)) |
                        (LegendaryPirate.reason.contains(filter_by))
                        ).limit(10))

        if only_active:
            now = datetime.datetime.now()
            query = query.where((LegendaryPirate.end_date.is_null()) | (LegendaryPirate.end_date > now))

        return query.execute()

    @staticmethod
    def get_all(only_active: bool = True) -> list['LegendaryPirate']:
        """
        Gets all legendary pirates
        :param only_active: Only active
        :return: Legendary pirates
        """

        if only_active:
            return LegendaryPirate.get_active()

        return LegendaryPirate.select().order_by(LegendaryPirate.date.desc()).execute()

    def get_end_date_by_duration(self, duration_days: int) -> datetime.datetime:
        """
        Get end date by duration
        :param duration_days: Duration in days
        :return: End date
        """

        return self.date + datetime.timedelta(days=duration_days)

    def is_active(self) -> bool:
        """
        Returns True if the legendary pirate is active
        :return: True if the legendary pirate is active
        """

        return self.end_date is None or self.end_date > datetime.datetime.now()


def _ensure_legendary_pirate_schema() -> None:
    db = LegendaryPirate._meta.database
    columns = {
        'end_date': 'ALTER TABLE legendary_pirate ADD COLUMN end_date DATETIME NULL',
        'original_end_date': 'ALTER TABLE legendary_pirate ADD COLUMN original_end_date DATETIME NULL',
        'revoke_reason': 'ALTER TABLE legendary_pirate ADD COLUMN revoke_reason VARCHAR(999) NULL',
        'is_permanent': 'ALTER TABLE legendary_pirate ADD COLUMN is_permanent TINYINT(1) NOT NULL DEFAULT 0',
    }

    try:
        for column_name, alter_sql in columns.items():
            cursor = db.execute_sql(f"SHOW COLUMNS FROM legendary_pirate LIKE '{column_name}'")
            if not cursor.fetchall():
                db.execute_sql(alter_sql)

        db.execute_sql(
            'UPDATE legendary_pirate SET is_permanent = 1 '
            'WHERE end_date IS NULL AND revoke_reason IS NULL AND is_permanent = 0'
        )
    except Exception:
        pass


LegendaryPirate.create_table(safe=True)
_ensure_legendary_pirate_schema()
