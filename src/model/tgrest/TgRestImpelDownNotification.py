from datetime import datetime

from src.model.enums.impel_down.ImpelDownBountyAction import ImpelDownBountyAction
from src.model.enums.impel_down.ImpelDownSentenceType import ImpelDownSentenceType
from src.model.tgrest.TgRest import TgRest
from src.model.tgrest.TgRestObjectType import TgRestObjectType


class TgRestImpelDownNotification(TgRest):
    """
    TgRestImpelDownNotification class is used to create a Telegram REST API request.
    """

    def __init__(
        self,
        user_id: int,
        sentence_type: ImpelDownSentenceType,
        release_date_time: datetime,
        bounty_action: ImpelDownBountyAction,
        reason: str,
        log_id: int,
    ):
        """
        Constructor

        :param user_id: The user id
        :param sentence_type: The sentence type
        :param release_date_time: The release date time
        :param bounty_action: The bounty action
        :param reason: The reason
        :param log_id: The impel down log id
        """

        super().__init__(TgRestObjectType.IMPEL_DOWN_NOTIFICATION)

        self.user_id: int = user_id
        self.sentence_type: ImpelDownSentenceType = sentence_type
        self.release_date_time: str | None = (
            release_date_time.strftime("%Y-%m-%d %H:%M:%S") if release_date_time else None
        )
        self.bounty_action: ImpelDownBountyAction = bounty_action
        self.reason: str = reason
        self.log_id: int = log_id
