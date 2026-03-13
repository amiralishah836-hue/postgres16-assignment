-- Task 3 - Roles & Permissions

-- Create dedicated database
CREATE DATABASE sdl_db
    WITH ENCODING='UTF8'
    LC_COLLATE='ru_RU.UTF-8'
    LC_CTYPE='ru_RU.UTF-8'
    TEMPLATE template0;

-- Create non-admin user
CREATE USER sdl_user
    WITH PASSWORD 'sdl_secret'
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    NOINHERIT
    LOGIN;

-- Grant privileges
GRANT CONNECT ON DATABASE sdl_db TO sdl_user;

\c sdl_db

GRANT USAGE ON SCHEMA public TO sdl_user;

GRANT SELECT, INSERT, UPDATE
ON ALL TABLES IN SCHEMA public
TO sdl_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE ON TABLES TO sdl_user;

