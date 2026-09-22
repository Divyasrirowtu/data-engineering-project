from decimal import Decimal

from app.ledger import (
    create_account,
    get_account_balance,
    transfer_money,
)
from app.logger import get_logger


logger = get_logger("ledger_application")


def main():
    logger.info("Ledger application started")

    try:
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

        logger.info(
            "Transaction completed: transaction_id=%s",
            transaction_id,
        )

        print("Transaction completed successfully")
        print("Transaction ID:", transaction_id)
        print(
            "Sender balance:",
            get_account_balance(sender),
        )
        print(
            "Receiver balance:",
            get_account_balance(receiver),
        )

    except Exception:
        logger.exception(
            "Ledger application failed"
        )
        raise

    finally:
        logger.info("Ledger application finished")


if __name__ == "__main__":
    main()