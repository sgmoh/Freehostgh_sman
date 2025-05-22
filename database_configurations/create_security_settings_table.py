import asyncpg
import asyncio
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:npg_liP7Mms3jZtd@ep-flat-mud-a5m7n2l1-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require')

CREATE_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS security_settings (
    guild_id BIGINT PRIMARY KEY,
    antispam BOOLEAN DEFAULT FALSE,
    antinuke BOOLEAN DEFAULT FALSE,
    automod  BOOLEAN DEFAULT FALSE
);
'''

async def main():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute(CREATE_TABLE_SQL)
        print('✅ security_settings table ready.')
        await conn.close()
    except Exception as e:
        print('❌ Error creating table:', e)

if __name__ == '__main__':
    asyncio.run(main()) 