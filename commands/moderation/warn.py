# commands/warn.py
import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_warnings = {} # Dictionary to store user warnings: {user_id: [warning_reason1, warning_reason2, ...]}

    @commands.command(name='warn', help='Warns a user. <:Warn:1373605418315677807> Requires Kick Members permission.')
    @commands.has_permissions(kick_members=True)
    async def warn_command(self, ctx, member: discord.Member, *, reason: str = "No reason provided."):
        # Add warning to storage
        if member.id not in self.user_warnings:
            self.user_warnings[member.id] = []
        self.user_warnings[member.id].append(reason)

        # In a real bot, you would likely want to log this warn, maybe store it in a database,
        # or send a DM to the user. For this example, we'll just send a message to the channel.

        # Send a DM to the warned user
        try:
            dm_embed = discord.Embed(
                title='You have been warned!',
                description=f'You were warned in {ctx.guild.name}.',
                color=discord.Color.orange()
            )
            dm_embed.add_field(name='Reason', value=reason, inline=False)
            dm_embed.set_footer(text=f'Warning issued by {ctx.author}')
            await member.send(embed=dm_embed)
            # Optionally, inform the moderator if the DM was sent successfully (or if it failed)
            # await ctx.send(f"DM sent to {member.display_name}.")
        except discord.Forbidden:
            # Optionally, inform the moderator if the DM failed
            # await ctx.send(f"Could not send a DM to {member.display_name}. They may have DMs disabled.")
            pass # Ignore if DM fails

        embed = discord.Embed(
            title='User Warned',
            description=f'<:Multipurpose:1373371000271409416> {member.mention} has been warned.',
            color=discord.Color.orange()
        )
        embed.add_field(name='Reason', value=reason, inline=False)
        embed.set_footer(text=f'Warned by {ctx.author}')

        await ctx.send(embed=embed)

    @commands.command(name='warnings', help='Shows a user\'s warnings. <:Warn:1373605418315677807>')
    @commands.has_permissions(kick_members=True)
    async def show_warnings(self, ctx, member: discord.Member):
        warnings = self.user_warnings.get(member.id, [])
        num_warnings = len(warnings)

        embed = discord.Embed(
            title=f"<:Multipurpose:1373371000271409416> {member.display_name}'s Warnings",
            color=discord.Color.blue()
        )

        if num_warnings == 0:
            embed.description = f'<:Multipurpose:1373371000271409416> {member.display_name} has no warnings.'
        else:
            embed.description = f'{member.display_name} has {num_warnings} warning(s).'
            for i, warning_reason in enumerate(warnings, 1):
                embed.add_field(name=f'Warning {i}', value=warning_reason, inline=False)

        await ctx.send(embed=embed)

# This function is called to load the cog
async def setup(bot):
    await bot.add_cog(Moderation(bot)) 