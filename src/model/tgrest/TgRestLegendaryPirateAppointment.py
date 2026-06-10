from src.model.tgrest.TgRest import TgRest
from src.model.tgrest.TgRestObjectType import TgRestObjectType


class TgRestLegendaryPirateAppointment(TgRest):
    """
    TgRestLegendaryPirateAppointment class is used to create a Telegram REST API request.
    """

    def __init__(self, user_id: int, legendary_pirate_id: int, days: int = None, is_permanent: bool = False):
        """
        Constructor

        :param user_id: The user id
        :param legendary_pirate_id: The legendary pirate id
        :param days: The number of days the user will be a legendary pirate
        :param is_permanent: Whether the appointment is permanent
        """

        super().__init__(TgRestObjectType.LEGENDARY_PIRATE_APPOINTMENT)

        self.user_id: int = user_id
        self.legendary_pirate_id: int = legendary_pirate_id
        self.days: int | None = days
        self.is_permanent: bool = is_permanent
