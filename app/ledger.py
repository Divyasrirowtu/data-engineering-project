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
from app.logger import get_logger
from app.retry import database_retry


logger = get_logger()

@database_retry
def check_database_connection():
    logger.info("Checking database connection")

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")

            result = cursor.fetchone()[0] == 1

            if result:
                logger.info(
                    "Database connection check successful"
                )

            return result

    except OperationalError:
        logger.exception(
            "Temporary database connection failure"
        )
        raise

    finally:
        connection.close()

def create_account(account_name, balance=Decimal("0.00")):
    logger.info(
        "Creating account: name=%s balance=%s",
        account_name,
        balance,
    )

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

                logger.info(
                    "Account created successfully: account_id=%s",
                    account_id,
                )

                return account_id

    except Exception as exc:
        logger.exception(
            "Account creation failed: account_name=%s",
            account_name,
        )

        raise DatabaseOperationError(
            f"Unable to create account: {exc}"
        ) from exc

    finally:
        connection.close()

def get_account_balance(account_id):
    logger.info(
        "Retrieving account balance: account_id=%s",
        account_id,
    )

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
                logger.warning(
                    "Account not found: account_id=%s",
                    account_id,
                )

                raise AccountNotFoundError(
                    f"Account {account_id} was not found"
                )

            logger.info(
                "Balance retrieved: account_id=%s balance=%s",
                account_id,
                result[0],
            )

            return result[0]

    except AccountNotFoundError:
        raise

    except Exception as exc:
        logger.exception(
            "Balance retrieval failed: account_id=%s",
            account_id,
        )

        raise DatabaseOperationError(
            f"Unable to retrieve account balance: {exc}"
        ) from exc

    finally:
        connection.close()


def transfer_money(from_account_id, to_account_id, amount):
    logger.info(
        "Transfer requested: from=%s to=%s amount=%s",
        from_account_id,
        to_account_id,
        amount,
    )

    try:
        amount = Decimal(str(amount))
    except Exception as exc:
        logger.warning(
            "Invalid transaction amount: amount=%s",
            amount,
        )

        raise InvalidAmountError(
            "Transaction amount must be numeric"
        ) from exc

    if amount <= 0:
        logger.warning(
            "Rejected non-positive transaction: amount=%s",
            amount,
        )

        raise InvalidAmountError(
            "Transaction amount must be greater than zero"
        )

    if from_account_id == to_account_id:
        logger.warning(
            "Rejected same-account transfer: account_id=%s",
            from_account_id,
        )

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
                    logger.warning(
                        "Transfer rejected because account was not found"
                    )

                    raise AccountNotFoundError(
                        "One or both accounts do not exist"
                    )

                balances = {
                    account_id: balance
                    for account_id, balance in accounts
                }

                if balances[from_account_id] < amount:
                    logger.warning(
                        "Insufficient balance: account_id=%s balance=%s amount=%s",
                        from_account_id,
                        balances[from_account_id],
                        amount,
                    )

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

                transaction_id = cursor.fetchone()[0]

                logger.info(
                    "Transfer completed successfully: transaction_id=%s amount=%s",
                    transaction_id,
                    amount,
                )

                return transaction_id

    except (
        AccountNotFoundError,
        InsufficientBalanceError,
        InvalidAmountError,
        SameAccountError,
    ):
        raise

    except Exception as exc:
        logger.exception(
            "Ledger transaction failed: from=%s to=%s amount=%s",
            from_account_id,
            to_account_id,
            amount,
        )

        raise DatabaseOperationError(
            f"Ledger transaction failed: {exc}"
        ) from exc

    finally:
        connection.close()