import discord
from discord.ext import commands
from discord import app_commands
import json
import os

BAD_WORDS_PATH = os.path.join(os.path.dirname(__file__), 'bad_words.json')

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.automod_enabled = {}  # guild_id: bool
        with open(BAD_WORDS_PATH, 'r', encoding='utf-8') as f:
            self.bad_words = set(json.load(f))

    @commands.command(name='automod', help='Toggle automod on or off for this server.')
    @commands.has_guild_permissions(administrator=True)
    async def automod_command(self, ctx, mode: str = None):
        if mode is None:
            status = self.automod_enabled.get(ctx.guild.id, False)
            await ctx.send(f"Automod is currently {'ON' if status else 'OFF'}.")
            return
        mode = mode.lower()
        if mode in ('on', 'enable', 'enabled'):
            self.automod_enabled[ctx.guild.id] = True
            await ctx.send('<:Security:1375118465668616212> Automod is now ON.')
        elif mode in ('off', 'disable', 'disabled'):
            self.automod_enabled[ctx.guild.id] = False
            await ctx.send('<:Security:1375118465668616212> Automod is now OFF.')
        else:
            await ctx.send('Usage: .automod on/off')

    @app_commands.command(name='automod', description='Toggle automod on or off for this server.')
    @app_commands.describe(mode='on or off')
    async def automod_slash(self, interaction: discord.Interaction, mode: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message('You need Administrator permission to use this.', ephemeral=True)
            return
        mode = mode.lower()
        if mode in ('on', 'enable', 'enabled'):
            self.automod_enabled[interaction.guild.id] = True
            await interaction.response.send_message('<:Security:1375118465668616212> Automod is now ON.')
        elif mode in ('off', 'disable', 'disabled'):
            self.automod_enabled[interaction.guild.id] = False
            await interaction.response.send_message('<:Security:1375118465668616212> Automod is now OFF.')
        else:
            await interaction.response.send_message('Usage: /automod mode:on|off', ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot:
            return
        if not self.automod_enabled.get(message.guild.id, False):
            return
        content = message.content.lower()
        if any(bad in content for bad in self.bad_words):
            try:
                await message.delete()
            except Exception:
                pass
            try:
                await message.author.send('<:Security:1375118465668616212> Your message was deleted for inappropriate language. Please follow the server rules.')
            except Exception:
                pass

    async def cog_load(self):
        self.bot.tree.add_command(self.automod_slash)

async def setup(bot):
    await bot.add_cog(Security(bot)) 