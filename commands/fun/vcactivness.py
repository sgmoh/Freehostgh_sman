import discord
from discord.ext import commands
from discord import app_commands
import datetime

class VCActivity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vc_sessions = {}  # user_id: join_time (datetime)
        self.vc_total = {}     # user_id: total_seconds

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # User joins a voice channel
        if before.channel is None and after.channel is not None:
            self.vc_sessions[member.id] = datetime.datetime.utcnow()
        # User leaves a voice channel
        elif before.channel is not None and after.channel is None:
            join_time = self.vc_sessions.pop(member.id, None)
            if join_time:
                seconds = (datetime.datetime.utcnow() - join_time).total_seconds()
                self.vc_total[member.id] = self.vc_total.get(member.id, 0) + seconds
        # User switches channels
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            join_time = self.vc_sessions.pop(member.id, None)
            if join_time:
                seconds = (datetime.datetime.utcnow() - join_time).total_seconds()
                self.vc_total[member.id] = self.vc_total.get(member.id, 0) + seconds
            self.vc_sessions[member.id] = datetime.datetime.utcnow()

    def get_leaderboard(self, guild, top_n=10):
        # Only show users in this guild
        members = {m.id: m for m in guild.members}
        leaderboard = [
            (members[uid], secs)
            for uid, secs in self.vc_total.items() if uid in members
        ]
        # Add currently in-VC users
        now = datetime.datetime.utcnow()
        for uid, join_time in self.vc_sessions.items():
            if uid in members:
                secs = (now - join_time).total_seconds()
                total = self.vc_total.get(uid, 0) + secs
                leaderboard.append((members[uid], total))
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        return leaderboard[:top_n]

    @commands.command(name='vcactive', help='Show the most active users in voice chat (session only).')
    async def vcactive_command(self, ctx):
        leaderboard = self.get_leaderboard(ctx.guild)
        if not leaderboard:
            await ctx.send('No voice chat activity recorded this session.')
            return
        desc = '\n'.join([
            f"{i+1}. {member.display_name}: {int(secs//60)} min {int(secs%60)} sec"
            for i, (member, secs) in enumerate(leaderboard)
        ])
        embed = discord.Embed(title='Voice Chat Activity Leaderboard', description=desc, color=discord.Color.blue())
        await ctx.send(embed=embed)

    @app_commands.command(name='vcactive', description='Show the most active users in voice chat (session only).')
    async def vcactive_slash(self, interaction: discord.Interaction):
        leaderboard = self.get_leaderboard(interaction.guild)
        if not leaderboard:
            await interaction.response.send_message('No voice chat activity recorded this session.', ephemeral=True)
            return
        desc = '\n'.join([
            f"{i+1}. {member.display_name}: {int(secs//60)} min {int(secs%60)} sec"
            for i, (member, secs) in enumerate(leaderboard)
        ])
        embed = discord.Embed(title='Voice Chat Activity Leaderboard', description=desc, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    async def cog_load(self):
        self.bot.tree.add_command(self.vcactive_slash)

async def setup(bot):
    await bot.add_cog(VCActivity(bot)) 