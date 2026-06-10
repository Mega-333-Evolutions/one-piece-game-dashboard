from peewee import *

from src.model.BaseModel import BaseModel
from src.model.DevilFruit import DevilFruit


class DevilFruitTrade(BaseModel):
    """
    Devil Fruit Trade class
    """
    id = PrimaryKeyField()
    devil_fruit = ForeignKeyField(DevilFruit, backref='devil_fruit_trades', on_delete='RESTRICT',
                                  on_update='CASCADE')

    class Meta:
        db_table = 'devil_fruit_trade'


DevilFruitTrade.create_table(safe=True)
