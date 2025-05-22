# commands/untimeout.py
import discord
from discord.ext import commands
from datetime import timedelta

class Untimeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='unmute', help='Removes mute from a user. <:timeout:1373371114155413504> Requires Moderate Members permission.')
    @commands.has_permissions(moderate_members=True)
    async def untimeout_command(self, ctx, member: discord.Member):
        try:
            await member.timeout(timedelta(seconds=0)) # Setting timeout to 0 seconds removes it
            await ctx.send(f'Mute removed for {member.mention}. <:timeout:1373371114155413504>')
        except discord.Forbidden:
            await ctx.send("I don't have the necessary permissions to remove timeout from this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

# This function is called to load the cog
async def setup(bot):
    await bot.add_cog(Untimeout(bot)) 