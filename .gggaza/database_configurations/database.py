# database_configurations/database.py
import asyncpg
import os
import datetime

# Initialize bot.NOTIFICATION_CHANNELS here as well, or ensure it's passed/accessed correctly
NOTIFICATION_CHANNELS = {}

async def create_db_pool_and_load_settings():
    """Creates a database connection pool and loads settings."""
    print('Attempting to connect to database...')
    try:
        # Your database URL
        DATABASE_URL = 'postgresql://neondb_owner:npg_liP7Mms3jZtd@ep-flat-mud-a5m7n2l1-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require' # Replace YOUR_DATABASE_URL_HERE with your actual URL
        if not DATABASE_URL:
            print('DATABASE_URL environment variable not set. Database features will be disabled.')
            return None, NOTIFICATION_CHANNELS # Return None for pool if URL is missing
        else:
            # Create a connection pool
            pool = await asyncpg.create_pool(DATABASE_URL)
            print('Database connection pool created successfully.')

            # Create users table if it doesn't exist
            async with pool.acquire() as connection:
                await connection.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        xp INT DEFAULT 0,
                        messages INT DEFAULT 0
                    )
                ''')
                print('Users table checked/created.')

                # Create settings table if it doesn't exist
                await connection.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key VARCHAR(255) NOT NULL,
                        server_id BIGINT NOT NULL,
                        value TEXT,
                        PRIMARY KEY (key, server_id)
                    )
                ''')
                print('Settings table checked/created.')

                # Load settings from database into NOTIFICATION_CHANNELS
                settings_data = await connection.fetch('SELECT key, server_id, value FROM settings')
                NOTIFICATION_CHANNELS = {}
                for row in settings_data:
                    server_id = row['server_id']
                    key = row['key']
                    value = row['value']
                    if server_id not in NOTIFICATION_CHANNELS:
                        NOTIFICATION_CHANNELS[server_id] = {}
                    try:
                        # Store channel ID as integer for easier use later
                        NOTIFICATION_CHANNELS[server_id][key] = int(value)
                    except (ValueError, TypeError):
                        print(f"Warning: Could not convert setting value for key {key} on server {server_id} to integer: {value}")
                        pass # Skip loading this setting if value is invalid
                print(f'Loaded {len(settings_data)} settings from database into per-server cache.')

            # Ensure security_settings table exists before returning pool
            await ensure_security_settings_table(pool)

            return pool, NOTIFICATION_CHANNELS

    except Exception as e:
        print(f'Failed to connect to database or create table: {e}')
        return None, NOTIFICATION_CHANNELS # Return None for pool on failure

async def close_db_pool(pool):
    """Closes the database connection pool."""
    if pool:
        print('Closing database connection pool...')
        await pool.close()
        print('Database connection pool closed.')

async def get_security_settings(pool, guild_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow('SELECT * FROM security_settings WHERE guild_id = $1', guild_id)
        if row:
            return dict(row)
        return None

async def set_security_setting(pool, guild_id, setting, value):
    async with pool.acquire() as conn:
        await conn.execute(f'''
            INSERT INTO security_settings (guild_id, {setting})
            VALUES ($1, $2)
            ON CONFLICT (guild_id) DO UPDATE SET {setting} = $2
        ''', guild_id, value)

async def get_all_security_settings(pool):
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM security_settings')
        return {row['guild_id']: dict(row) for row in rows}

async def ensure_security_settings_table(pool):
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS security_settings (
                guild_id BIGINT PRIMARY KEY,
                antispam BOOLEAN DEFAULT FALSE,
                antinuke BOOLEAN DEFAULT FALSE,
                automod  BOOLEAN DEFAULT FALSE
            )
        ''') 