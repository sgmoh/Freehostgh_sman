# commands/moderation/reset.py
import discord
from discord.ext import commands

class ModerationReset(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='reset', help='Resets a user\'s level and data.')
    @commands.has_permissions(administrator=True)
    async def reset_user_data(self, ctx, member: discord.Member):
        # Access the database pool from bot instance
        db_pool = self.bot.pool

        if db_pool is None:
            await ctx.send("Database connection not available.")
            return

        user_id = member.id

        async with db_pool.acquire() as connection:
            # Delete user data from the users table
            await connection.execute(
                'DELETE FROM users WHERE user_id = $1',
                user_id
            )

        await ctx.send(f"Level and data for {member.display_name} have been reset and removed from the database.")

async def setup(bot):
    await bot.add_cog(ModerationReset(bot)) 