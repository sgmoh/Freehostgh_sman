# commands/moderation/role.py
import discord
from discord.ext import commands

class RoleCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='role', help='Assigns a role to a user. Requires Manage Roles permission. <:role:1374834526005497998> Usage: .role @user <role>')
    @commands.has_permissions(manage_roles=True)
    async def role_command(self, ctx, member: discord.Member, *, role: discord.Role):
        # Check if the bot has permissions to manage roles and if the role is assignable
        if ctx.guild.me.top_role <= role:
            await ctx.send("I cannot assign this role as it is higher than or equal to my top role.")
            return

        # Check if the target member is the guild owner
        if member == ctx.guild.owner:
            await ctx.send("I cannot assign roles to the guild owner.")
            return
            
        # Check if the target member has a higher or equal role than the bot
        if member.top_role >= ctx.guild.me.top_role:
             await ctx.send("I cannot assign roles to members with a higher or equal role than mine.")
             return

        # Check if the target member has a higher or equal role than the author
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
             await ctx.send("You cannot assign roles to members with a higher or equal role than yours.")
             return

        if role in member.roles:
            await ctx.send(f"{member.display_name} already has the {role.name} role.")
            return

        try:
            await member.add_roles(role)
            await ctx.send(f"Successfully assigned the {role.name} role to {member.display_name}. <:role:1374834526005497998>")
        except discord.Forbidden:
            await ctx.send("I don't have the necessary permissions to assign this role.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(RoleCommand(bot)) 