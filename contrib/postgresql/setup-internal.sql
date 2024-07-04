/*
contrib/setup-internal.sql
--------------------------

This SQL script is responsible for the initial setup of the `internal` user and the related `internal` database in a PostgreSQL environment.
*/

\c postgres
CREATE USER internal WITH PASSWORD 'internal';
CREATE DATABASE internal;
-- GRANT ALL PRIVILEGES ON DATABASE internal TO internal;
ALTER USER internal WITH SUPERUSER;

\c internal;
CREATE SCHEMA personaflow;
ALTER SCHEMA personaflow OWNER TO internal;

CREATE EXTENSION IF NOT EXISTS pgcrypto;
