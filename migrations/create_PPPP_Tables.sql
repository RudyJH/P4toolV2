-- create all PPPP_Table tables
--- This SQL script creates the necessary tables for the PPPP application, 
--- including user_table and pundent_table. It also sets up a trigger to automatically 
--- update the updated_at timestamp whenever a record is updated in the users table.
--- need to consider first time setup and how to handle that with the trigger, as well 
--- as potential issues with the trigger on updates to the users table.


--- 
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

--- Person Base tables


CREATE TABLE IF NOT EXISTS user_table (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(100) NOT NULL UNIQUE,
    first_name    VARCHAR(100),
    last_name     VARCHAR(100),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);




CREATE TABLE IF NOT EXISTS pundent_table (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),  -- Handle the case where a pundent might also be a user
    pundent       VARCHAR(50)  UNIQUE NOT NULL,

    username      VARCHAR(50)  NOT NULL UNIQUE,
    first_name    VARCHAR(100),
    last_name     VARCHAR(100),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS PPPprofile_table (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),  -- Handle the case where a pundent might also be a user
    test_ver      VARCHAR(10)  NOT NULL, -- version of the test.
    username      VARCHAR(50)  NOT NULL UNIQUE,
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