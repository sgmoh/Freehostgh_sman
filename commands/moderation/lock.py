# commands/moderation/lock.py
import discord
from discord.ext import commands

class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='lock', help='Locks the current channel or all channels. Requires Manage Channels permission. <:lock:1374832805334483134> Usage: .lock [all]')
    @commands.has_permissions(manage_channels=True)
    async def lock_command(self, ctx, scope: str = None):
        if scope and scope.lower() == 'all':
            # Lock all text channels
            locked_channels = []
            for channel in ctx.guild.text_channels:
                try:
                    # Deny send_messages permission for @everyone role
                    await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                    locked_channels.append(channel.mention)
                except discord.Forbidden:
                    await ctx.send(f"Could not lock {channel.mention} due to insufficient permissions.")
                except Exception as e:
                    await ctx.send(f"An error occurred while locking {channel.mention}: {e}")
            if locked_channels:
                await ctx.send(f"Locked the following channels: {', '.join(locked_channels)} <:lock:1374832805334483134>")
            else:
                await ctx.send("No text channels were locked.")
        elif scope is None:
            # Lock the current channel
            channel = ctx.channel
            try:
                await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                await ctx.send(f"Channel {channel.mention} has been locked. <:lock:1374832805334483134>")
            except discord.Forbidden:
                await ctx.send("I don't have the necessary permissions to lock this channel.")
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")
        else:
            await ctx.send("Invalid scope specified. Use `.lock` to lock the current channel or `.lock all` to lock all text channels.")

    @commands.command(name='unlock', help='Unlocks the current channel or all channels. Requires Manage Channels permission. <:unlock:1374832837349609503> Usage: .unlock [all]')
    @commands.has_permissions(manage_channels=True)
    async def unlock_command(self, ctx, scope: str = None):
        if scope and scope.lower() == 'all':
            # Unlock all text channels
            unlocked_channels = []
            for channel in ctx.guild.text_channels:
                try:
                    # Allow send_messages permission for @everyone role
                    await channel.set_permissions(ctx.guild.default_role, send_messages=True)
                    unlocked_channels.append(channel.mention)
                except discord.Forbidden:
                    await ctx.send(f"Could not unlock {channel.mention} due to insufficient permissions.")
                except Exception as e:
                    await ctx.send(f"An error occurred while unlocking {channel.mention}: {e}")
            if unlocked_channels:
                await ctx.send(f"Unlocked the following channels: {', '.join(unlocked_channels)} <:unlock:1374832837349609503>")
            else:
                await ctx.send("No text channels were unlocked.")
        elif scope is None:
            # Unlock the current channel
            channel = ctx.channel
            try:
                await channel.set_permissions(ctx.guild.default_role, send_messages=True)
                await ctx.send(f"Channel {channel.mention} has been unlocked. <:unlock:1374832837349609503>")
            except discord.Forbidden:
                await ctx.send("I don't have the necessary permissions to unlock this channel.")
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")
        else:
            await ctx.send("Invalid scope specified. Use `.unlock` to unlock the current channel or `.unlock all` to unlock all text channels.")

async def setup(bot):
    await bot.add_cog(Lock(bot)) 