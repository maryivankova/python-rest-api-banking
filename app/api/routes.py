from .views import create_user, get_user_balance, add_transaction, get_transaction


def add_routes(app):
    app.router.add_route('POST', r'/v1/user', create_user, name='create_user')
    app.router.add_route('GET', r'/v1/user/{id:\d+}', get_user_balance, name='get_user_balance_by_id')
    app.router.add_route('POST', r'/v1/transaction', add_transaction, name='add_transaction')
    app.router.add_route('GET', r'/v1/transaction/{id}', get_transaction, name='get_transaction_by_id')
