import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import time
import datetime
from database_configurations.database import get_security_settings, set_security_setting, get_all_security_settings

class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_message_times = {}  # (guild_id, user_id): [timestamps]
        self.spam_threshold = 2  # messages
        self.time_window = 1     # seconds
        self.timeout_duration = 10  # seconds
        self.antispam_enabled = {}  # guild_id: bool
        self.bot.loop.create_task(self.load_settings())

    async def load_settings(self):
        await self.bot.wait_until_ready()
        if not hasattr(self.bot, 'pool') or self.bot.pool is None:
            return
        all_settings = await get_all_security_settings(self.bot.pool)
        for guild_id, settings in all_settings.items():
            self.antispam_enabled[guild_id] = settings.get('antispam', False)

    @commands.command(name='antispam', help='Toggle anti-spam on or off for this server.')
    @commands.has_guild_permissions(administrator=True)
    async def antispam_command(self, ctx, mode: str = None):
        if mode is None:
            status = self.antispam_enabled.get(ctx.guild.id, False)
            await ctx.send(f"Antispam is currently {'ON' if status else 'OFF'}.")
            return
        mode = mode.lower()
        if mode in ('on', 'enable', 'enabled'):
            self.antispam_enabled[ctx.guild.id] = True
            await ctx.send('<:antispam:1375122762426880000> Antispam is now ON.')
            await set_security_setting(self.bot.pool, ctx.guild.id, 'antispam', True)
        elif mode in ('off', 'disable', 'disabled'):
            self.antispam_enabled[ctx.guild.id] = False
            await ctx.send('<:antispam:1375122762426880000> Antispam is now OFF.')
            await set_security_setting(self.bot.pool, ctx.guild.id, 'antispam', False)
        else:
            await ctx.send('Usage: .antispam on/off')

    @app_commands.command(name='antispam', description='Toggle anti-spam on or off for this server.')
    @app_commands.describe(mode='on or off')
    async def antispam_slash(self, interaction: discord.Interaction, mode: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message('You need Administrator permission to use this.', ephemeral=True)
            return
        mode = mode.lower()
        if mode in ('on', 'enable', 'enabled'):
            self.antispam_enabled[interaction.guild.id] = True
            await interaction.response.send_message('<:antispam:1375122762426880000> Antispam is now ON.')
            await set_security_setting(self.bot.pool, interaction.guild.id, 'antispam', True)
        elif mode in ('off', 'disable', 'disabled'):
            self.antispam_enabled[interaction.guild.id] = False
            await interaction.response.send_message('<:antispam:1375122762426880000> Antispam is now OFF.')
            await set_security_setting(self.bot.pool, interaction.guild.id, 'antispam', False)
        else:
            await interaction.response.send_message('Usage: /antispam mode:on|off', ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot:
            return
        # Exempt server owner
        if message.author.id == message.guild.owner_id:
            print(f"[ANTISPAM] Skipping server owner: {message.author} ({message.author.id})")
            return
        if not self.antispam_enabled.get(message.guild.id, False):
            print(f"[ANTISPAM] Antispam is OFF for guild {message.guild.name} ({message.guild.id})")
            return
        key = (message.guild.id, message.author.id)
        now = time.time()
        times = self.user_message_times.get(key, [])
        times = [t for t in times if now - t < self.time_window]
        times.append(now)
        self.user_message_times[key] = times
        print(f"[ANTISPAM] Message from {message.author} ({message.author.id}) in {message.guild.name} ({message.guild.id}): now={now}, count={len(times)}")
        if len(times) >= self.spam_threshold:
            print(f"[ANTISPAM] Triggered for user {message.author} ({message.author.id}) in guild {message.guild.name} ({message.guild.id})")
            try:
                print(f"[ANTISPAM] Attempting to timeout user {message.author} for {self.timeout_duration} seconds.")
                await message.author.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=self.timeout_duration), reason="Spamming messages")
                try:
                    await message.author.send('<:antispam:1375122762426880000> You have been timed out for 10 seconds for spamming.')
                except Exception as dm_exc:
                    print(f"[ANTISPAM] Failed to DM user: {dm_exc}")
            except Exception as exc:
                print(f"[ANTISPAM] Failed to timeout user: {exc}")
            self.user_message_times[key] = []  # Reset after timeout

    async def cog_load(self):
        self.bot.tree.add_command(self.antispam_slash)

async def setup(bot):
    await bot.add_cog(AntiSpam(bot)) 