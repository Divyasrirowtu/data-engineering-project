from app.db import get_connection


def test_accounts_table_exists():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'accounts'
                );
                """
            )

            assert cursor.fetchone()[0] is True

    finally:
        connection.close()


def test_ledger_transactions_table_exists():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'ledger_transactions'
                );
                """
            )

            assert cursor.fetchone()[0] is True

    finally:
        connection.close()


def test_accounts_balance_constraint_exists():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.table_constraints
                    WHERE table_name = 'accounts'
                    AND constraint_name =
                        'accounts_balance_non_negative'
                );
                """
            )

            assert cursor.fetchone()[0] is True

    finally:
        connection.close()