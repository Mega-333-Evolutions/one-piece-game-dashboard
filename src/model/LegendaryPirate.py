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

        ensure_legendary_pirate_schema()
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


_schema_ensured = False


def ensure_legendary_pirate_schema() -> None:
    """
    Ensure legendary_pirate table has all required columns.
    """

    global _schema_ensured
    if _schema_ensured:
        return

    db = LegendaryPirate._meta.database
    db.connect(reuse_if_open=True)

    if not db.table_exists('legendary_pirate'):
        LegendaryPirate.create_table()
        _schema_ensured = True
        return

    existing_columns = {column.name for column in db.get_columns('legendary_pirate')}
    migrations = {
        'end_date': 'ALTER TABLE legendary_pirate ADD COLUMN end_date DATETIME NULL',
        'original_end_date': 'ALTER TABLE legendary_pirate ADD COLUMN original_end_date DATETIME NULL',
        'revoke_reason': 'ALTER TABLE legendary_pirate ADD COLUMN revoke_reason VARCHAR(999) NULL',
        'is_permanent': 'ALTER TABLE legendary_pirate ADD COLUMN is_permanent TINYINT(1) NOT NULL DEFAULT 0',
    }

    for column_name, alter_sql in migrations.items():
        if column_name not in existing_columns:
            db.execute_sql(alter_sql)

    if 'is_permanent' in existing_columns or 'is_permanent' in migrations:
        db.execute_sql(
            'UPDATE legendary_pirate SET is_permanent = 1 '
            'WHERE end_date IS NULL AND revoke_reason IS NULL AND is_permanent = 0'
        )

    _schema_ensured = True


LegendaryPirate.create_table(safe=True)
