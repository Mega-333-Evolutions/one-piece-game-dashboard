from src.model.tgrest.TgRest import TgRest
from src.model.tgrest.TgRestObjectType import TgRestObjectType


class TgRestDevilFruitForceSchedule(TgRest):
    """
    TgRestDevilFruitForceSchedule class is used to create a Telegram REST API request.
    """

    def __init__(self, devil_fruit_id: int):
        """
        Constructor

        :param devil_fruit_id: The devil fruit id
        """

        super().__init__(TgRestObjectType.DEVIL_FRUIT_FORCE_SCHEDULE)

        self.devil_fruit_id: int = devil_fruit_id
