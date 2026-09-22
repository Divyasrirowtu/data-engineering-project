from decimal import Decimal

from psycopg2 import OperationalError

from app.db import get_connection
from app.errors import (
    AccountNotFoundError,
    DatabaseOperationError,
    InsufficientBalanceError,
    InvalidAmountError,
    SameAccountError,
)
from app.retry import database_retry


@database_retry
def check_database_connection():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            return cursor.fetchone()[0] == 1

    finally:
        connection.close()
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

                return cursor.fetchone()[0]

    except Exception as exc:
        raise DatabaseOperationError(
            f"Unable to create account: {exc}"
        ) from exc

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
                raise AccountNotFoundError(
                    f"Account {account_id} was not found"
                )

            return result[0]

    except AccountNotFoundError:
        raise

    except Exception as exc:
        raise DatabaseOperationError(
            f"Unable to retrieve account balance: {exc}"
        ) from exc

    finally:
        connection.close()


def transfer_money(from_account_id, to_account_id, amount):
    try:
        amount = Decimal(str(amount))
    except Exception as exc:
        raise InvalidAmountError(
            "Transaction amount must be numeric"
        ) from exc

    if amount <= 0:
        raise InvalidAmountError(
            "Transaction amount must be greater than zero"
        )

    if from_account_id == to_account_id:
        raise SameAccountError(
            "Source and destination accounts must be different"
        )

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
                    raise AccountNotFoundError(
                        "One or both accounts do not exist"
                    )

                balances = {
                    account_id: balance
                    for account_id, balance in accounts
                }

                if balances[from_account_id] < amount:
                    raise InsufficientBalanceError(
                        "Insufficient account balance"
                    )

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

                return cursor.fetchone()[0]

    except (
        AccountNotFoundError,
        InsufficientBalanceError,
        InvalidAmountError,
        SameAccountError,
    ):
        raise

    except Exception as exc:
        raise DatabaseOperationError(
            f"Ledger transaction failed: {exc}"
        ) from exc

    finally:
        connection.close()