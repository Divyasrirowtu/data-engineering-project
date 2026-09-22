from decimal import Decimal

import pytest

from app.errors import (
    InsufficientBalanceError,
    InvalidAmountError,
    SameAccountError,
)
from app.ledger import (
    create_account,
    transfer_money,
)


def test_negative_amount_is_rejected():
    sender = create_account(
        "ErrorTestSender1",
        Decimal("1000.00"),
    )

    receiver = create_account(
        "ErrorTestReceiver1",
        Decimal("100.00"),
    )

    with pytest.raises(InvalidAmountError):
        transfer_money(
            sender,
            receiver,
            Decimal("-10.00"),
        )


def test_zero_amount_is_rejected():
    sender = create_account(
        "ErrorTestSender2",
        Decimal("1000.00"),
    )

    receiver = create_account(
        "ErrorTestReceiver2",
        Decimal("100.00"),
    )

    with pytest.raises(InvalidAmountError):
        transfer_money(
            sender,
            receiver,
            Decimal("0.00"),
        )


def test_same_account_is_rejected():
    account = create_account(
        "ErrorTestSameAccount",
        Decimal("1000.00"),
    )

    with pytest.raises(SameAccountError):
        transfer_money(
            account,
            account,
            Decimal("100.00"),
        )


def test_insufficient_balance_is_rejected():
    sender = create_account(
        "ErrorTestSender3",
        Decimal("50.00"),
    )

    receiver = create_account(
        "ErrorTestReceiver3",
        Decimal("100.00"),
    )

    with pytest.raises(InsufficientBalanceError):
        transfer_money(
            sender,
            receiver,
            Decimal("100.00"),
        )