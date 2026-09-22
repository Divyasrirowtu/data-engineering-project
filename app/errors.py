class LedgerError(Exception):
    """Base exception for ledger processing."""


class AccountNotFoundError(LedgerError):
    """Raised when an account does not exist."""


class InsufficientBalanceError(LedgerError):
    """Raised when an account does not have enough balance."""


class InvalidAmountError(LedgerError):
    """Raised when a transaction amount is invalid."""


class SameAccountError(LedgerError):
    """Raised when source and destination accounts are the same."""


class DatabaseOperationError(LedgerError):
    """Raised when a database operation fails."""