import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class AntiNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.antinuke_enabled = {}  # guild_id: bool
        self.user_actions = {}  # (guild_id, user_id): {'channels_deleted': int, 'roles_deleted': int, 'mentions': int, 'last_action': float}
        self.channel_delete_threshold = 3  # Number of channels deleted in 10s
        self.role_delete_threshold = 3     # Number of roles deleted in 10s
        self.mention_threshold = 8         # Number of mentions in 10s
        self.time_window = 10              # seconds

    @commands.command(name='antinuke', help='Toggle antinuke on or off for this server.')
    @commands.has_guild_permissions(administrator=True)
    async def antinuke_command(self, ctx, mode: str = None):
        if mode is None:
            status = self.antinuke_enabled.get(ctx.guild.id, False)
            await ctx.send(f"Antinuke is currently {'ON' if status else 'OFF'}.")
            return
        mode = mode.lower()
        if mode in ('on', 'enable', 'enabled'):
            self.antinuke_enabled[ctx.guild.id] = True
            await ctx.send('<:Antinuke:1375119851299016756> Antinuke is now ON.')
        elif mode in ('off', 'disable', 'disabled'):
            self.antinuke_enabled[ctx.guild.id] = False
            await ctx.send('<:Antinuke:1375119851299016756> Antinuke is now OFF.')
        else:
            await ctx.send('Usage: .antinuke on/off')

    @app_commands.command(name='antinuke', description='Toggle antinuke on or off for this server.')
    @app_commands.describe(mode='on or off')
    async def antinuke_slash(self, interaction: discord.Interaction, mode: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message('You need Administrator permission to use this.', ephemeral=True)
            return
        mode = mode.lower()
        if mode in ('on', 'enable', 'enabled'):
            self.antinuke_enabled[interaction.guild.id] = True
            await interaction.response.send_message('<:Antinuke:1375119851299016756> Antinuke is now ON.')
        elif mode in ('off', 'disable', 'disabled'):
            self.antinuke_enabled[interaction.guild.id] = False
            await interaction.response.send_message('<:Antinuke:1375119851299016756> Antinuke is now OFF.')
        else:
            await interaction.response.send_message('Usage: /antinuke mode:on|off', ephemeral=True)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild = channel.guild
        if not self.antinuke_enabled.get(guild.id, False):
            return
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            user = entry.user
            if user.bot:
                return
            await self._register_action(guild, user, 'channels_deleted')

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        guild = role.guild
        if not self.antinuke_enabled.get(guild.id, False):
            return
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            user = entry.user
            if user.bot:
                return
            await self._register_action(guild, user, 'roles_deleted')

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot:
            return
        if not self.antinuke_enabled.get(message.guild.id, False):
            return
        mention_count = len(message.mentions)
        if mention_count >= self.mention_threshold:
            await self._register_action(message.guild, message.author, 'mentions')

    async def _register_action(self, guild, user, action_type):
        key = (guild.id, user.id)
        now = asyncio.get_event_loop().time()
        data = self.user_actions.get(key, {'channels_deleted': 0, 'roles_deleted': 0, 'mentions': 0, 'last_action': now})
        # Reset if outside time window
        if now - data['last_action'] > self.time_window:
            data = {'channels_deleted': 0, 'roles_deleted': 0, 'mentions': 0, 'last_action': now}
        data[action_type] += 1
        data['last_action'] = now
        self.user_actions[key] = data
        # Check thresholds
        if (data['channels_deleted'] >= self.channel_delete_threshold or
            data['roles_deleted'] >= self.role_delete_threshold or
            data['mentions'] >= self.mention_threshold):
            await self._punish_user(guild, user)
            self.user_actions[key] = {'channels_deleted': 0, 'roles_deleted': 0, 'mentions': 0, 'last_action': now}

    async def _punish_user(self, guild, user):
        try:
            member = guild.get_member(user.id)
            if member:
                await member.edit(roles=[])
                try:
                    await member.send('<:Antinuke:1375119851299016756> We have removed your roles because we detected suspicious actions. Please DM the server owner or a staff member if this was a mistake.')
                except Exception:
                    pass
        except Exception:
            pass

    async def cog_load(self):
        self.bot.tree.add_command(self.antinuke_slash)

async def setup(bot):
    await bot.add_cog(AntiNuke(bot)) 