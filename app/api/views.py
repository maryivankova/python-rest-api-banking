import json
import uuid

from aiohttp import web
from datetime import datetime

from sqlalchemy import func, and_

from models import User, Transaction, db, Balance
from decimal import Decimal


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


async def create_user(request):
    data = await request.json()
    user = await User.create(name=data['name'])
    balance = await Balance.create(user_id=user.id)
    await balance.update_balance()
    return web.json_response({
        'id': user.id,
        'name': user.name,
        'balance': str(balance.balance),
    }, status=201)


previous_txn_id = None


async def add_transaction(request):
    global previous_txn_id
    data = await request.json()
    user_id = data['user_id']
    amount = float(data['amount'])
    transaction_type = data['type']
    timestamp = datetime.utcnow()

    if previous_txn_id == data['uid']:
        return web.json_response({'error': f'Duplicate transaction with id {data["uid"]}'}, status=200)
    previous_txn_id = data['uid']

    async with db.transaction():
        # Fetch the user object
        user = await User.query.where(User.id == user_id).gino.first()

        if user is None:
            return web.json_response({'error': f'User with id {user_id} not found'}, status=404)

        if transaction_type == 'DEPOSIT':
            user.balance += amount
        elif transaction_type == 'WITHDRAW':
            if user.balance < amount:
                return web.json_response({'error': 'Insufficient funds'}, status=402)

            user.balance -= amount
        else:
            return web.json_response({'error': f'Invalid transaction type: {transaction_type}'}, status=400)

        await User.update.values(balance=user.balance).where(User.id == user_id).gino.status()

        # Create the transaction object
        transaction = await Transaction.create(id=str(data['uid']), user_id=user.id, type=data['type'],
                                               amount=float(data['amount']), timestamp=datetime.utcnow())

    if 'date' in request.query:
        date = datetime.fromisoformat(request.query['date'])
        balance = await db.select(func.sum(Transaction.amount)).where(and_(
            Transaction.user_id == user_id,
            Transaction.timestamp < date
        )).gino.scalar()
    else:
        balance = user.balance

    return web.json_response({'status': 200, 'balance': balance})


async def get_transaction(request):
    transaction_id = request.match_info['id']
    transaction = await Transaction.get_by_id(transaction_id)
    if not transaction:
        return web.Response(status=404, text=f'Transaction with id {transaction_id} not found')

    return web.json_response({
        'id': transaction.id,
        'user_id': transaction.user_id,
        'type': transaction.type,
        'amount': '{:.2f}'.format(transaction.amount),
        'timestamp': transaction.timestamp.isoformat(),
    }, dumps=CustomEncoder().encode)


async def get_user_balance(request):
    user_id = int(request.match_info['id'])

    user = await User.get(user_id)
    if not user:
        return web.Response(status=404, text=f'User with id {user_id} not found')

    return web.json_response({
        'user_id': user_id,
        'name': user.name,
        'balance': '{:.2f}'.format(user.balance),
    })
