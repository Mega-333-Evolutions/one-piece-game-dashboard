from enum import IntEnum


class DevilFruitAbilityType(IntEnum):
    """
    Enum for the type of Devil Fruit ability type.
    """

    DOC_Q_COOLDOWN_DURATION = 1
    GAME_COOLDOWN_DURATION = 2
    FIGHT_COOLDOWN_DURATION = 3
    FIGHT_IMMUNITY_DURATION = 4
    FIGHT_DEFENSE_BOOST = 5
    PREDICTION_WAGER_REFUND = 6
    GIFT_LOAN_TAX = 7
    INCOME_TAX = 8
    PLUNDER_COOLDOWN_DURATION = 9
    PLUNDER_IMMUNITY_DURATION = 10
    PLUNDER_SENTENCE_DURATION = 11
    FIGHT_SCOUT_FEE = 12
    PLUNDER_SCOUT_FEE = 13
    GAME_GLOBAL_ACCEPT_COOLDOWN_DURATION = 14

    def get_description(self) -> str:
        """
        Get the description of the devil fruit ability type
        :return: The description of the devil fruit ability type
        """
        return DEVIL_FRUIT_ABILITY_TYPE_DESCRIPTION_MAP[self]

    @staticmethod
    def get_all_description():
        """
        Get all the descriptions of the devil fruit ability types
        :return: All the descriptions of the devil fruit ability types
        """
        return [DevilFruitAbilityType.DOC_Q_COOLDOWN_DURATION.get_description(),
                DevilFruitAbilityType.GAME_COOLDOWN_DURATION.get_description(),
                DevilFruitAbilityType.FIGHT_COOLDOWN_DURATION.get_description(),
                DevilFruitAbilityType.FIGHT_IMMUNITY_DURATION.get_description(),
                DevilFruitAbilityType.FIGHT_DEFENSE_BOOST.get_description(),
                DevilFruitAbilityType.PREDICTION_WAGER_REFUND.get_description(),
                DevilFruitAbilityType.GIFT_LOAN_TAX.get_description(),
                DevilFruitAbilityType.INCOME_TAX.get_description(),
                DevilFruitAbilityType.PLUNDER_COOLDOWN_DURATION.get_description(),
                DevilFruitAbilityType.PLUNDER_IMMUNITY_DURATION.get_description(),
                DevilFruitAbilityType.PLUNDER_SENTENCE_DURATION.get_description(),
                DevilFruitAbilityType.FIGHT_SCOUT_FEE.get_description(),
                DevilFruitAbilityType.PLUNDER_SCOUT_FEE.get_description(),
                DevilFruitAbilityType.GAME_GLOBAL_ACCEPT_COOLDOWN_DURATION.get_description()]

    @staticmethod
    def get_by_description(description: str) -> 'DevilFruitAbilityType':
        """
        Get the devil fruit ability type by its description
        :param description: The description of the devil fruit ability type
        :return: The devil fruit ability type
        """
        for devil_fruit_ability_type in DevilFruitAbilityType:
            if devil_fruit_ability_type.get_description() == description:
                return devil_fruit_ability_type

        raise ValueError("Invalid devil fruit ability type description: " + description)


DEVIL_FRUIT_ABILITY_TYPE_DESCRIPTION_MAP = {
    DevilFruitAbilityType.DOC_Q_COOLDOWN_DURATION: "Doc Q Cooldown Duration",
    DevilFruitAbilityType.GAME_COOLDOWN_DURATION: "Challenge Cooldown Duration",
    DevilFruitAbilityType.FIGHT_COOLDOWN_DURATION: "Fight Cooldown Duration",
    DevilFruitAbilityType.FIGHT_IMMUNITY_DURATION: "Fight Immunity Duration",
    DevilFruitAbilityType.FIGHT_DEFENSE_BOOST: "Fight Defense Boost",
    DevilFruitAbilityType.PREDICTION_WAGER_REFUND: "Prediction Wager Refund",
    DevilFruitAbilityType.GIFT_LOAN_TAX: "Tax",
    DevilFruitAbilityType.INCOME_TAX: "Income Tax",
    DevilFruitAbilityType.PLUNDER_COOLDOWN_DURATION: "Plunder Cooldown Duration",
    DevilFruitAbilityType.PLUNDER_IMMUNITY_DURATION: "Plunder Immunity Duration",
    DevilFruitAbilityType.PLUNDER_SENTENCE_DURATION: "Plunder Sentence Duration",
    DevilFruitAbilityType.FIGHT_SCOUT_FEE: "Fight Scout Fee",
    DevilFruitAbilityType.PLUNDER_SCOUT_FEE: "Plunder Scout Fee",
    DevilFruitAbilityType.GAME_GLOBAL_ACCEPT_COOLDOWN_DURATION: "Game Global Accept Cooldown Duration"
}
