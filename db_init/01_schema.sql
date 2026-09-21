CREATE EXTENSION IF NOT EXISTS pgcrypto;


CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_name VARCHAR(100) NOT NULL UNIQUE,
    balance NUMERIC(18, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT accounts_balance_non_negative
        CHECK (balance >= 0)
);


CREATE TABLE IF NOT EXISTS ledger_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    from_account_id UUID,
    to_account_id UUID NOT NULL,

    amount NUMERIC(18, 2) NOT NULL,

    transaction_type VARCHAR(50) NOT NULL DEFAULT 'TRANSFER',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ledger_amount_positive
        CHECK (amount > 0),

    CONSTRAINT ledger_different_accounts
        CHECK (
            from_account_id IS NULL
            OR from_account_id <> to_account_id
        ),

    CONSTRAINT ledger_from_account_fk
        FOREIGN KEY (from_account_id)
        REFERENCES accounts(id),

    CONSTRAINT ledger_to_account_fk
        FOREIGN KEY (to_account_id)
        REFERENCES accounts(id)
);


CREATE INDEX IF NOT EXISTS idx_ledger_transactions_from_account
    ON ledger_transactions(from_account_id);


CREATE INDEX IF NOT EXISTS idx_ledger_transactions_to_account
    ON ledger_transactions(to_account_id);


CREATE INDEX IF NOT EXISTS idx_ledger_transactions_created_at
    ON ledger_transactions(created_at);


CREATE INDEX IF NOT EXISTS idx_ledger_transactions_type
    ON ledger_transactions(transaction_type);