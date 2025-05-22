from flask import Flask
from discord.ext import commands
from discord import app_commands
import discord
import bot

app = Flask(__name__)

PREFIX = '.'

def get_prefix(bot, message):
    return ['.', '/']

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

@app.route('/')
def home():
    return 'OK', 200

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send('Pong!')

    @app_commands.command(name='ping', description='Pong!')
    async def ping_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message('Pong!')

    @app_commands.command(name='zikr', description='Provides a reminder for Zikr or displays a specific Zikr.')
    @app_commands.describe(query='ID or keyword to search for a zikr (optional)')
    async def zikr_slash(self, interaction: discord.Interaction, query: str = None):
        await self.send_zikr(interaction, query)

    async def cog_load(self):
        self.bot.tree.add_command(self.zikr_slash)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        prefixes = self.bot.command_prefix(self.bot, message) if callable(self.bot.command_prefix) else [self.bot.command_prefix]
        if any(message.content.strip().lower().startswith(f'{p}afk') for p in prefixes):
            return

        # Don't remove AFK if the message is the .afk command itself
        if (
            message.author.id in self.afk and
            not (
                message.content.strip().lower().startswith(f"{self.bot.command_prefix}afk")
                or (hasattr(message, 'interaction') and getattr(message, 'command', None) and getattr(message.command, 'name', '') == 'afk')
            )
        ):
            pass  # TODO: implement AFK removal logic here

async def setup(bot):
    await bot.add_cog(MyCog(bot))

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

if __name__ == '__main__':
    bot.run_bot() 