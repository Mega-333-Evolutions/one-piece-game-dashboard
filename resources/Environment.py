import os
from pathlib import Path

import constants as c

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

# --- CUSTOM REPLACEMENT FOR DISTUTILS ---
def strtobool(val):
    """Convert a string representation of truth to True or False."""
    return str(val).lower() in ("yes", "true", "t", "1", "on", "y")
# ----------------------------------------

_secrets_cache: dict | None = None


def _load_streamlit_secrets() -> dict:
    global _secrets_cache
    if _secrets_cache is not None:
        return _secrets_cache

    secrets_file = Path(__file__).resolve().parent.parent / '.streamlit' / 'secrets.toml'
    if not secrets_file.exists():
        _secrets_cache = {}
        return _secrets_cache

    try:
        with secrets_file.open('rb') as file:
            _secrets_cache = tomllib.load(file)
    except Exception:
        try:
            text = secrets_file.read_text(encoding='utf-8')
            parsed: dict[str, str] = {}
            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('['):
                    continue
                if '=' not in line:
                    continue
                key, value = line.split('=', 1)
                value = value.strip()
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                parsed[key.strip()] = value
            _secrets_cache = parsed
        except Exception:
            _secrets_cache = {}

    return _secrets_cache


class Environment:
    def __init__(self, name: str, default_value: str = None, can_be_empty: bool = False):
        self.name = name
        self.default_value = default_value
        self.can_be_empty = can_be_empty

    def get_or_none(self) -> str | None:
        """
        Get the environment variable or None if it is not set
        :return: The environment variable or None if it is not set
        :rtype: str | None
        """
        secrets = _load_streamlit_secrets()

        # If default value is set, return the environment variable, secrets value, or the default value
        if self.default_value is not None:
            return os.environ.get(self.name, secrets.get(self.name, self.default_value))

        # Get the environment variable or secret value, or return None if it is not set
        value = os.environ.get(self.name, secrets.get(self.name))

        # If the environment variable is not set and the environment variable can be empty, return None
        if value is None and self.can_be_empty:
            return None

        # If the environment variable is not set and the environment variable can not be empty, raise an exception
        if value is None:
            raise Exception(f"Environment variable {self.name} is not set")

        return value

    def get(self) -> str:
        """
        Get the environment variable
        :return: The environment variable
        """
        value = self.get_or_none()
        if value is None:
            raise Exception(f"Environment variable {self.name} is not set")

        return value

    def get_int(self) -> int:
        """
        Get the environment variable as an integer
        :return: The environment variable as an integer
        """
        return int(self.get())

    def get_float(self) -> float:
        """
        Get the environment variable as a float
        :return: The environment variable as a float
        """
        return float(self.get())

    def get_bool(self) -> bool:
        """
        Get the environment variable as a boolean
        :return: The environment variable as a boolean
        """
        return True if strtobool(self.get()) else False

    def get_list(self) -> list[str]:
        """
        Get the environment variable as a list
        :return: The environment variable as a list
        """
        return self.get().split(c.STANDARD_SPLIT_CHAR)


# Bot
OP_GROUP_BOT_ID = Environment('OP_GROUP_BOT_ID')
TG_REST_BOT_TOKEN = Environment('TG_REST_BOT_TOKEN')

# TgRest Channel ID
TG_REST_CHANNEL_ID = Environment('TG_REST_CHANNEL_ID')

# CONFIG
# Which timezone to use
TZ = Environment('TZ', default_value='Etc/UTC')

# DATABASE
# Database name
DB_NAME = Environment('DB_NAME')
# Database host
DB_HOST = Environment('DB_HOST')
# Database port
DB_PORT = Environment('DB_PORT')
# Database user
DB_USER = Environment('DB_USER')
# Database password
DB_PASSWORD = Environment('DB_PASSWORD')
# Log queries
DB_LOG_QUERIES = Environment('DB_LOG_QUERIES', default_value='False')

# Should refund wagers default option. Default: False
REFUND_WAGER_DEFAULT = Environment('REFUND_WAGER_DEFAULT', default_value='False')
# Should allow users to bet on multiple choices default option. Default: True
ALLOW_MULTIPLE_CHOICES_DEFAULT = Environment('ALLOW_MULTIPLE_CHOICES_DEFAULT', default_value='True')
# Should allow users to withdraw their bet default option. Default: False
CAN_WITHDRAW_BET_DEFAULT = Environment('CAN_WITHDRAW_BET_DEFAULT', default_value='False')
# Maximum refundable wager for prediction bets. Default: 100 million
PREDICTION_BET_MAX_REFUNDABLE_WAGER = Environment('PREDICTION_BET_MAX_REFUNDABLE_WAGER', default_value='100000000')

# Devil Fruit ability minimum value. Default: 0
DEVIL_FRUIT_ABILITY_MIN_VALUE = Environment('DEVIL_FRUIT_ABILITY_MIN_VALUE', default_value='0')
# Devil Fruit ability maximum value. Default: 100
DEVIL_FRUIT_ABILITY_MAX_VALUE = Environment('DEVIL_FRUIT_ABILITY_MAX_VALUE', default_value='100')
# Devil Fruit Zoan abilities sum. Default: 100
DEVIL_FRUIT_CATEGORY_ZOAN_SUM = Environment('DEVIL_FRUIT_CATEGORY_ZOAN_SUM', default_value='100')
# Devil Fruit Ancient Zoan abilities sum. Default: 150
DEVIL_FRUIT_CATEGORY_ANCIENT_ZOAN_SUM = Environment('DEVIL_FRUIT_CATEGORY_ANCIENT_ZOAN_SUM', default_value='150')
# Devil Fruit Mythical Zoan abilities sum. Default: 300
DEVIL_FRUIT_CATEGORY_MYTHICAL_ZOAN_SUM = Environment('DEVIL_FRUIT_CATEGORY_MYTHICAL_ZOAN_SUM', default_value='300')

# Maximum items displayed in a list. Default: 10
MAX_ITEMS_DISPLAYED_LIST = Environment('MAX_ITEMS_DISPLAYED_LIST', default_value='5')

# Maximum number of Warlords. Default: 7
MAX_WARLORDS = Environment('MAX_WARLORDS', default_value='7')

# Maximum number of Legendary Pirates. Default: 20
MAX_LEGENDARY_PIRATES = Environment('MAX_LEGENDARY_PIRATES', default_value='20')
