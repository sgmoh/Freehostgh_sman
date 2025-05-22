# commands/moderation/removerole.py
import discord
from discord.ext import commands

class RemoveRoleCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='removerole', help='Removes a role from a user. Requires Manage Roles permission. <:Remove_Role:1374841199570165761> Usage: .removerole @user <role>')
    @commands.has_permissions(manage_roles=True)
    async def removerole_command(self, ctx, member: discord.Member, *, role: discord.Role):
        # Check if the bot has permissions to manage roles and if the role is lower than the bot's top role
        if ctx.guild.me.top_role <= role:
            await ctx.send("I cannot remove this role as it is higher than or equal to my top role.")
            return
            
        # Check if the target member has a higher or equal role than the bot
        if member.top_role >= ctx.guild.me.top_role:
             await ctx.send("I cannot remove roles from members with a higher or equal role than mine.")
             return

        # Check if the target member has a higher or equal role than the author
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
             await ctx.send("You cannot remove roles from members with a higher or equal role than yours.")
             return

        if role not in member.roles:
            await ctx.send(f"{member.display_name} does not have the {role.name} role.")
            return

        try:
            await member.remove_roles(role)
            await ctx.send(f"Successfully removed the {role.name} role from {member.display_name}. <:Remove_Role:1374841199570165761>")
        except discord.Forbidden:
            await ctx.send("I don't have the necessary permissions to remove this role.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(RemoveRoleCommand(bot)) 