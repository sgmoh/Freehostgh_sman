# commands/moderation/timeout.py
import discord
from discord.ext import commands
from datetime import timedelta
import re

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mute', help='Mutes a user for a specified duration with an optional reason. <:timeout:1373371114155413504> Requires Moderate Members permission. Format: <user> <duration (e.g., 10m, 1h, 1d)> [reason]')
    @commands.has_permissions(moderate_members=True)
    async def timeout_command(self, ctx, member: discord.Member, duration: str, *, reason: str = None):
        # Parse the duration string (e.g., 10m, 1h, 1d)
        time_pattern = re.compile(r'^(\d+)([smhd])$')
        match = time_pattern.match(duration.lower())

        if not match:
            await ctx.send("Invalid duration format. Use formats like 10s, 5m, 1h, 2d.")
            return

        value, unit = int(match.group(1)), match.group(2)

        if unit == 's':
            delta = timedelta(seconds=value)
            duration_text = f'{value} second(s)'
        elif unit == 'm':
            delta = timedelta(minutes=value)
            duration_text = f'{value} minute(s)'
        elif unit == 'h':
            delta = timedelta(hours=value)
            duration_text = f'{value} hour(s)'
        elif unit == 'd':
            delta = timedelta(days=value)
            duration_text = f'{value} day(s)'

        # Discord API has a maximum timeout duration
        if delta > timedelta(days=28):
            await ctx.send("Timeout cannot be longer than 28 days.")
            return

        try:
            await member.timeout(delta, reason=reason)
            await ctx.send(f'{member.mention} has been timed out for {duration_text}. <:timeout:1373371114155413504>')

            # Attempt to DM the user with the reason
            if reason:
                dm_message = f"You have been timed out in {ctx.guild.name} for {duration_text}. Reason: {reason}"
            else:
                dm_message = f"You have been timed out in {ctx.guild.name} for {duration_text}."

            try:
                await member.send(dm_message)
            except discord.Forbidden:
                print(f"Could not send DM to {member.display_name}. User may have DMs disabled.")

        except discord.Forbidden:
            await ctx.send("I don't have the necessary permissions to timeout this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

# This function is called to load the cog
async def setup(bot):
    await bot.add_cog(Timeout(bot)) 