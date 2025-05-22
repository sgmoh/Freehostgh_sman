import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import re
import shlex

class InviteCounter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='inv', help='Show how many invites a user has. Usage: .inv [user]')
    async def inv_command(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        invites = await ctx.guild.invites()
        count = sum(inv.uses for inv in invites if inv.inviter and inv.inviter.id == member.id)
        embed = discord.Embed(
            title=f"<:invite:1375130577933565952> Invites for {member.display_name}",
            description=f"{member.mention} has **{count}** invites.",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)

    @app_commands.command(name='inv', description='Show how many invites a user has.')
    @app_commands.describe(member='The user to check (optional)')
    async def inv_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        invites = await interaction.guild.invites()
        count = sum(inv.uses for inv in invites if inv.inviter and inv.inviter.id == member.id)
        embed = discord.Embed(
            title=f"<:invite:1375130577933565952> Invites for {member.display_name}",
            description=f"{member.mention} has **{count}** invites.",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)

    @commands.command(name='invleaderboard', help='Show the top inviters in the server. Usage: .invleaderboard')
    async def invleaderboard_command(self, ctx):
        invites = await ctx.guild.invites()
        counter = {}
        for inv in invites:
            if inv.inviter:
                counter[inv.inviter] = counter.get(inv.inviter, 0) + inv.uses
        top = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:10]
        desc = '\n'.join(f"**{i+1}.** {user.mention} — **{count}** invites" for i, (user, count) in enumerate(top))
        embed = discord.Embed(
            title=f"<:leaderboardd:1374502601269186680> Invite Leaderboard",
            description=desc or "No invites found.",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)

    @app_commands.command(name='invleaderboard', description='Show the top inviters in the server.')
    async def invleaderboard_slash(self, interaction: discord.Interaction):
        invites = await interaction.guild.invites()
        counter = {}
        for inv in invites:
            if inv.inviter:
                counter[inv.inviter] = counter.get(inv.inviter, 0) + inv.uses
        top = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:10]
        desc = '\n'.join(f"**{i+1}.** {user.mention} — **{count}** invites" for i, (user, count) in enumerate(top))
        embed = discord.Embed(
            title=f"<:leaderboardd:1374502601269186680> Invite Leaderboard",
            description=desc or "No invites found.",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)

    @commands.command(name='timer', help='Set a timer. Usage: .timer <duration>')
    async def timer_command(self, ctx, duration: str):
        seconds = self.parse_duration(duration)
        if seconds is None or seconds <= 0:
            await ctx.send('Invalid duration. Use formats like 10s, 5m, 2h.')
            return
        await ctx.send(f'Timer set for {duration}!')
        await asyncio.sleep(seconds)
        embed = discord.Embed(
            title='<:Timer:1375132027430633543> Timer Finished!',
            description=f'{ctx.author.mention}, your timer for **{duration}** is up!',
            color=discord.Color.orange()
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @app_commands.command(name='timer', description='Set a timer.')
    @app_commands.describe(duration='Duration (e.g., 10s, 5m, 2h)')
    async def timer_slash(self, interaction: discord.Interaction, duration: str):
        seconds = self.parse_duration(duration)
        if seconds is None or seconds <= 0:
            await interaction.response.send_message('Invalid duration. Use formats like 10s, 5m, 2h.', ephemeral=True)
            return
        await interaction.response.send_message(f'Timer set for {duration}!')
        await asyncio.sleep(seconds)
        embed = discord.Embed(
            title='<:Timer:1375132027430633543> Timer Finished!',
            description=f'{interaction.user.mention}, your timer for **{duration}** is up!',
            color=discord.Color.orange()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)

    @commands.command(name='poll', help='Create a poll. Usage: .poll Question? | Option 1 | Option 2 | ... (up to 10 options)')
    async def poll_command(self, ctx, *, args: str = None):
        if not args:
            await ctx.send('Usage: .poll Question? | Option 1 | Option 2 | ... (up to 10 options)')
            return
        # Try to split by | first
        parts = [part.strip() for part in args.split('|') if part.strip()]
        if len(parts) >= 3:
            question = parts[0]
            options = parts[1:]
        else:
            # Fallback: try quoted arguments
            try:
                tokens = shlex.split(args)
            except Exception:
                tokens = []
            if len(tokens) >= 3:
                question = tokens[0]
                options = tokens[1:]
            else:
                await ctx.send('You must provide a question and at least 2 options.\nExample: .poll What is your favorite color? | Red | Blue | Green')
                return
        if len(options) > 10:
            await ctx.send('You can provide up to 10 options only.')
            return
        emojis = [
            '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟'
        ]
        desc = '\n'.join(f'{emojis[i]} {opt}' for i, opt in enumerate(options))
        embed = discord.Embed(
            title='<:Poll:1375134172120748112> Poll',
            description=f'**{question}**\n\n{desc}',
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f'Poll by {ctx.author.display_name}', icon_url=ctx.author.display_avatar.url)
        msg = await ctx.send(embed=embed)
        for i in range(len(options)):
            await msg.add_reaction(emojis[i])

    @app_commands.command(name='poll', description='Create a poll with up to 10 options.')
    @app_commands.describe(question='The poll question', options='Comma-separated options (2-10)')
    async def poll_slash(self, interaction: discord.Interaction, question: str, options: str):
        option_list = [opt.strip() for opt in options.split(',') if opt.strip()]
        if len(option_list) < 2 or len(option_list) > 10:
            await interaction.response.send_message('You must provide between 2 and 10 options, separated by commas.', ephemeral=True)
            return
        emojis = [
            '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟'
        ]
        desc = '\n'.join(f'{emojis[i]} {opt}' for i, opt in enumerate(option_list))
        embed = discord.Embed(
            title='<:Poll:1375134172120748112> Poll',
            description=f'**{question}**\n\n{desc}',
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f'Poll by {interaction.user.display_name}', icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        for i in range(len(option_list)):
            await msg.add_reaction(emojis[i])

    def parse_duration(self, duration: str):
        match = re.match(r'^(\d+)\s*([smhSMH])$', duration.strip())
        if not match:
            return None
        value, unit = match.groups()
        value = int(value)
        unit = unit.lower()
        if unit == 's':
            return value
        elif unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
        return None

    async def cog_load(self):
        self.bot.tree.add_command(self.inv_slash)
        self.bot.tree.add_command(self.invleaderboard_slash)
        self.bot.tree.add_command(self.timer_slash)
        self.bot.tree.add_command(self.poll_slash)

async def setup(bot):
    await bot.add_cog(InviteCounter(bot)) 