from decimal import Decimal

import pytest

from app.errors import InsufficientBalanceError
from app.ledger import (
    create_account,
    get_account_balance,
    transfer_money,
)


def test_failed_transfer_does_not_change_balances():
    sender = create_account(
        "RollbackSender",
        Decimal("100.00"),
    )

    receiver = create_account(
        "RollbackReceiver",
        Decimal("50.00"),
    )

    sender_before = get_account_balance(sender)
    receiver_before = get_account_balance(receiver)

    with pytest.raises(InsufficientBalanceError):
        transfer_money(
            sender,
            receiver,
            Decimal("500.00"),
        )

    sender_after = get_account_balance(sender)
    receiver_after = get_account_balance(receiver)

    assert sender_after == sender_before
    assert receiver_after == receiver_before