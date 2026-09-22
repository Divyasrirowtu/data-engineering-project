from decimal import Decimal

from app.db import get_connection


def create_account(account_name, balance=Decimal("0.00")):
    connection = get_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO accounts (account_name, balance)
                    VALUES (%s, %s)
                    RETURNING id;
                    """,
                    (account_name, balance),
                )

                account_id = cursor.fetchone()[0]

        return account_id

    finally:
        connection.close()


def get_account_balance(account_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT balance
                FROM accounts
                WHERE id = %s;
                """,
                (account_id,),
            )

            result = cursor.fetchone()

            if result is None:
                raise ValueError("Account not found")

            return result[0]

    finally:
        connection.close()


def transfer_money(from_account_id, to_account_id, amount):
    amount = Decimal(str(amount))

    if amount <= 0:
        raise ValueError("Transfer amount must be greater than zero")

    if from_account_id == to_account_id:
        raise ValueError("Source and destination accounts must be different")

    connection = get_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT id, balance
                    FROM accounts
                    WHERE id IN (%s, %s)
                    FOR UPDATE;
                    """,
                    (from_account_id, to_account_id),
                )

                accounts = cursor.fetchall()

                if len(accounts) != 2:
                    raise ValueError("One or both accounts do not exist")

                balances = {
                    account_id: balance
                    for account_id, balance in accounts
                }

                if balances[from_account_id] < amount:
                    raise ValueError("Insufficient account balance")

                cursor.execute(
                    """
                    UPDATE accounts
                    SET balance = balance - %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                    """,
                    (amount, from_account_id),
                )

                cursor.execute(
                    """
                    UPDATE accounts
                    SET balance = balance + %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                    """,
                    (amount, to_account_id),
                )

                cursor.execute(
                    """
                    INSERT INTO ledger_transactions (
                        from_account_id,
                        to_account_id,
                        amount,
                        transaction_type
                    )
                    VALUES (%s, %s, %s, 'TRANSFER')
                    RETURNING id;
                    """,
                    (
                        from_account_id,
                        to_account_id,
                        amount,
                    ),
                )

                transaction_id = cursor.fetchone()[0]

        return transaction_id

    finally:
        connection.close()