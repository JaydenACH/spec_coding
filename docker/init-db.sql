-- Database initialization script for Respond IO Alternate Interface

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE respond_io_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'respond_io_db')\gexec

-- Connect to the database
\c respond_io_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types for enums
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('basic_user', 'manager', 'system_admin');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE customer_status AS ENUM ('assigned', 'unassigned');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE conversation_status AS ENUM ('active', 'closed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE message_sender_type AS ENUM ('customer', 'salesperson');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE message_type AS ENUM ('text', 'image', 'file');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE file_type AS ENUM ('image', 'pdf', 'document');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE notification_type AS ENUM ('assignment', 'tag', 'new_message');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance
-- These will be created by Django migrations, but we prepare the database

-- Grant permissions to application user
GRANT ALL PRIVILEGES ON DATABASE respond_io_db TO respond_user;
GRANT ALL ON SCHEMA public TO respond_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO respond_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO respond_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO respond_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO respond_user;

-- Optimize PostgreSQL settings for development
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Refresh configuration
SELECT pg_reload_conf(); 