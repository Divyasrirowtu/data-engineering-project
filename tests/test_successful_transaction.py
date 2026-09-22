from decimal import Decimal

from app.db import get_connection
from app.ledger import (
    create_account,
    get_account_balance,
    transfer_money,
)


def test_successful_transfer_creates_ledger_record():
    sender = create_account(
        "SuccessSender",
        Decimal("1000.00"),
    )

    receiver = create_account(
        "SuccessReceiver",
        Decimal("100.00"),
    )

    transaction_id = transfer_money(
        sender,
        receiver,
        Decimal("200.00"),
    )

    assert transaction_id is not None

    assert get_account_balance(sender) == Decimal("800.00")
    assert get_account_balance(receiver) == Decimal("300.00")

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT amount, transaction_type
                FROM ledger_transactions
                WHERE id = %s;
                """,
                (transaction_id,),
            )

            result = cursor.fetchone()

        assert result is not None
        assert result[0] == Decimal("200.00")
        assert result[1] == "TRANSFER"

    finally:
        connection.close()