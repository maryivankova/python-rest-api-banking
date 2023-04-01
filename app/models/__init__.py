from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from gino import Gino
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy import text

db = Gino()


class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    balance = Column(Float, default=0.0)


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    @classmethod
    async def get_by_id(cls, transaction_id: UUID):
        return await cls.query.where(cls.id == transaction_id).gino.first()


class Balance(db.Model):
    __tablename__ = "balances"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    balance = Column(Numeric(10, 2), nullable=False, default=0)

    async def update_balance(self, date=None):
        transaction_model = db.tables['transactions']
        balance = await db.select([func.coalesce(func.sum(transaction_model.c.amount), 0)]).where(
            (transaction_model.c.user_id == int(self.user_id)) & (
                    transaction_model.c.timestamp <= (date or datetime.utcnow()))
        ).gino.scalar()

        await db.update(Balance).where(Balance.id == self.id).values(balance=balance or 0).gino.status()
