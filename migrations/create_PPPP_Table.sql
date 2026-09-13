-- Migration 001 — create PPPP_Table table
CREATE EXTENSION IF NOT EXISTS "pgcrypto";



CREATE TABLE IF NOT EXISTS pppp_table (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    pundent       VARCHAR(50)  NOT NULL,
    question1     VARCHAR() TEXT         NOT NULL,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash TEXT         NOT NULL,
    first_name    VARCHAR(100),
    last_name     VARCHAR(100),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);


BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();