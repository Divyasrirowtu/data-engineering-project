from decimal import Decimal

from app.ledger import (
    create_account,
    get_account_balance,
    transfer_money,
)


def main():
    sender = create_account(
        "Sender",
        Decimal("1000.00"),
    )

    receiver = create_account(
        "Receiver",
        Decimal("100.00"),
    )

    transaction_id = transfer_money(
        sender,
        receiver,
        Decimal("250.00"),
    )

    print("Transaction completed successfully")
    print("Transaction ID:", transaction_id)
    print("Sender balance:", get_account_balance(sender))
    print("Receiver balance:", get_account_balance(receiver))


if __name__ == "__main__":
    main()