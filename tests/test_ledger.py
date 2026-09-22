from decimal import Decimal

import pytest

from app.ledger import (
    create_account,
    get_account_balance,
    transfer_money,
)


def test_create_account():
    account_name = "TestCreateAccount"

    account_id = create_account(
        account_name,
        Decimal("500.00"),
    )

    assert account_id is not None

    balance = get_account_balance(account_id)

    assert balance == Decimal("500.00")


def test_successful_transfer():
    sender = create_account(
        "TestSender",
        Decimal("1000.00"),
    )

    receiver = create_account(
        "TestReceiver",
        Decimal("100.00"),
    )

    transaction_id = transfer_money(
        sender,
        receiver,
        Decimal("250.00"),
    )

    assert transaction_id is not None

    assert get_account_balance(sender) == Decimal("750.00")

    assert get_account_balance(receiver) == Decimal("350.00")


def test_transfer_rejects_zero_amount():
    sender = create_account(
        "TestZeroSender",
        Decimal("1000.00"),
    )

    receiver = create_account(
        "TestZeroReceiver",
        Decimal("100.00"),
    )

    with pytest.raises(ValueError):
        transfer_money(
            sender,
            receiver,
            Decimal("0.00"),
        )


def test_transfer_rejects_insufficient_balance():
    sender = create_account(
        "TestLowBalanceSender",
        Decimal("100.00"),
    )

    receiver = create_account(
        "TestLowBalanceReceiver",
        Decimal("100.00"),
    )

    with pytest.raises(ValueError):
        transfer_money(
            sender,
            receiver,
            Decimal("500.00"),
        )