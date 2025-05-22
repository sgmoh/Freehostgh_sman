# commands/purge.py
import discord
from discord.ext import commands

class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='purge', help='Deletes a specified number of messages. Requires Manage Messages permission. <:clear:1373370955279110245>')
    @commands.has_permissions(manage_messages=True)
    async def purge_command(self, ctx, amount: int):
        if amount <= 0:
            await ctx.send("Please specify a positive number of messages to delete.")
            return

        try:
            # Add 1 to amount to also delete the command message itself
            deleted_messages = await ctx.channel.purge(limit=amount + 1)
            # Subtract 1 because the command message itself is deleted
            await ctx.send(f'Successfully deleted {len(deleted_messages) - 1} messages. <:clear:1373370955279110245>', delete_after=5) # Delete confirmation after 5 seconds
        except discord.Forbidden:
            await ctx.send("I don't have the necessary permissions to delete messages.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred while deleting messages: {e}")

# This function is called to load the cog
async def setup(bot):
    await bot.add_cog(Purge(bot)) 