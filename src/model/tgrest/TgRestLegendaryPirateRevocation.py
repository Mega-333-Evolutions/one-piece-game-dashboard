from src.model.tgrest.TgRest import TgRest
from src.model.tgrest.TgRestObjectType import TgRestObjectType


class TgRestLegendaryPirateRevocation(TgRest):
    """
    TgRestLegendaryPirateRevocation class is used to create a Telegram REST API request.
    """

    def __init__(self, user_id: int, legendary_pirate_id: int):
        """
        Constructor

        :param user_id: The user id
        :param legendary_pirate_id: The legendary pirate id
        """

        super().__init__(TgRestObjectType.LEGENDARY_PIRATE_REVOCATION)

        self.user_id: int = user_id
        self.legendary_pirate_id: int = legendary_pirate_id
