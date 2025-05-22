# commands/moderation/slowmode.py
import discord
from discord.ext import commands
import re

class Slowmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def parse_duration(self, duration_str):
        """Parses a duration string (e.g., 5m, 1h, 30s) into seconds."""
        if not duration_str:
            return None

        # Regex to match digits followed by a time unit (s, m, h) case-insensitive
        match = re.match(r'(\d+)([smh])', duration_str.lower())

        if not match:
            return None # Invalid format

        value, unit = match.groups()
        value = int(value)

        if unit == 's':
            return value
        elif unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 60 * 60
        else:
            return None # Should not happen with the current regex

    @commands.command(name='slowmode', help='Sets the slowmode for a channel. Requires Manage Channels permission. <:slowmode:1374811642583322784> Usage: .slowmode #channel <duration (e.g., 5m, 1h, 30s)>')
    @commands.has_permissions(manage_channels=True)
    async def slowmode_command(self, ctx, channel: discord.TextChannel, duration_str: str):
        seconds = self.parse_duration(duration_str)

        if seconds is None:
            await ctx.send("Invalid duration format. Use formats like `5m`, `1h`, or `30s`.")
            return

        if seconds < 0:
            await ctx.send("Slowmode duration cannot be negative.")
            return
        if seconds > 21600:
             await ctx.send("Slowmode duration cannot exceed 6 hours (21600 seconds).")
             return

        try:
            await channel.edit(slowmode_delay=seconds)
            if seconds == 0:
                await ctx.send(f"Slowmode removed in {channel.mention}.")
            else:
                await ctx.send(f"Slowmode set to {duration_str} in {channel.mention}. <:slowmode:1374811642583322784>")
        except discord.Forbidden:
            await ctx.send("I don't have the necessary permissions to set slowmode in that channel.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Slowmode(bot)) 