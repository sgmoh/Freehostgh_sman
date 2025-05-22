# commands/fun/level.py
import discord
from discord.ext import commands
import math
import datetime
import re
from discord import app_commands

# Basic leveling formula (you can customize this)
def get_level_from_xp(xp):
    return math.floor(0.1 * math.sqrt(xp))

def get_xp_for_level(level):
    return math.ceil((level / 0.1)**2)

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk = {}  # user_id: (reason, timestamp)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Don't remove AFK if the message is the .afk command itself
        prefixes = self.bot.command_prefix(self.bot, message) if callable(self.bot.command_prefix) else [self.bot.command_prefix]
        if any(message.content.strip().lower().startswith(f'{p}afk') for p in prefixes):
            return

        # Remove AFK if user was AFK and they send a message (but not the afk command)
        if message.author.id in self.afk:
            del self.afk[message.author.id]
            try:
                if message.guild:
                    member = message.guild.get_member(message.author.id)
                    if member and member.display_name.endswith(' | AFK'):
                        await member.edit(nick=member.display_name[:-6])
            except Exception:
                pass
            try:
                await message.channel.send(f"Welcome back, {message.author.mention}! Your AFK status has been removed.", delete_after=10)
            except Exception:
                pass

        # Notify if mentioned user is AFK
        if message.mentions:
            for user in message.mentions:
                if user.id in self.afk:
                    reason, since = self.afk[user.id]
                    since_str = since.strftime('%Y-%m-%d %H:%M UTC')
                    await message.channel.send(f"{user.mention} is AFK: {reason} (since {since_str})", delete_after=10)

        user_id = message.author.id

        # Access the database pool and notification channels from bot instance
        db_pool = self.bot.pool
        notification_channels = self.bot.NOTIFICATION_CHANNELS

        if db_pool is None:
            # If database is not connected, fall back to in-memory (optional, or handle error)
            # For now, we'll just skip tracking if DB is down
            print("Database connection not available for level tracking.")
            return

        async with db_pool.acquire() as connection:
            # Fetch user data
            user_data = await connection.fetchrow(
                'SELECT xp, messages FROM users WHERE user_id = $1',
                user_id
            )

            if user_data:
                # User exists, update data
                current_xp = user_data['xp']
                current_messages = user_data['messages']
                previous_level = get_level_from_xp(current_xp)

                xp_to_add = 15
                new_xp = current_xp + xp_to_add
                new_messages = current_messages + 1

                await connection.execute(
                    'UPDATE users SET xp = $1, messages = $2 WHERE user_id = $3',
                    new_xp,
                    new_messages,
                    user_id
                )
                current_level = get_level_from_xp(new_xp)

            else:
                # User does not exist, insert new user
                new_xp = 15
                new_messages = 1
                await connection.execute(
                    'INSERT INTO users (user_id, xp, messages) VALUES ($1, $2, $3)',
                    user_id,
                    new_xp,
                    new_messages
                )
                previous_level = get_level_from_xp(0) # Assume level 0 before first message
                current_level = get_level_from_xp(new_xp)

            # Check for level up (logic remains similar, but uses new_xp)
            if current_level > previous_level:
                print(f"Debug: Level up detected for user {user_id}. New level: {current_level}, Previous level: {previous_level}") # Debug print
                # Retrieve the notification channel ID for the specific server
                server_id = message.guild.id if message.guild else None
                print(f"Debug: Checking for notification channel in server ID: {server_id}") # Debug print
                print(f"Debug: Available notification channels in bot.NOTIFICATION_CHANNELS: {notification_channels}") # Debug print

                if server_id and server_id in notification_channels:
                    print(f"Debug: Settings found for server ID {server_id}: {notification_channels[server_id]}") # Debug print
                    level_notification_channel_id = notification_channels[server_id].get('level')
                    print(f"Debug: Retrieved level notification channel ID: {level_notification_channel_id}") # Debug print

                    if level_notification_channel_id:
                        try:
                            channel = self.bot.get_channel(level_notification_channel_id)
                            if channel:
                                await channel.send(f'🎉 Congratulations {message.author.mention}! You leveled up to Level {current_level}! 🎉')
                            else:
                                # Fallback to the original channel if the set channel is not found
                                await message.channel.send(f'🎉 Congratulations {message.author.mention}! You leveled up to Level {current_level}! 🎉')
                        except discord.errors.NotFound:
                             # Fallback to the original channel if the set channel is not found
                             await message.channel.send(f'🎉 Congratulations {message.author.mention}! You leveled up to Level {current_level}! 🎉')

                    else:
                        # Send to the original channel if no notification channel is set
                        await message.channel.send(f'🎉 Congratulations {message.author.mention}! You leveled up to Level {current_level}! 🎉')

    @commands.command(name='level', help='Shows a user\'s level, XP, and progress.')
    async def level_command(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author # Default to the command author if no user is mentioned

        user_id = member.id

        # Access the database pool from bot instance
        db_pool = self.bot.pool

        if db_pool is None:
            await ctx.send("Database connection not available.")
            return

        async with db_pool.acquire() as connection:
            # Fetch user data from the database
            user_data = await connection.fetchrow(
                'SELECT xp, messages FROM users WHERE user_id = $1',
                user_id
            )

            user_xp = 0
            user_messages = 0
            user_level = 0
            xp_for_current_level = 0
            xp_for_next_level = get_xp_for_level(1)
            xp_in_current_level = 0
            xp_needed_for_next_level = get_xp_for_level(1)
            progress_bar = '░' * 20
            percentage = 0

            if user_data:
                user_xp = user_data['xp']
                user_messages = user_data['messages']
                user_level = get_level_from_xp(user_xp)
                xp_for_current_level = get_xp_for_level(user_level)
                xp_for_next_level = get_xp_for_level(user_level + 1)
                xp_in_current_level = user_xp - xp_for_current_level
                xp_needed_for_next_level = xp_for_next_level - xp_for_current_level

                # Calculate progress bar (simple text representation)
                bar_length = 20
                progress = xp_in_current_level / xp_needed_for_next_level if xp_needed_for_next_level > 0 else 0
                filled_length = round(bar_length * progress)
                progress_bar = '█' * filled_length + '░' * (bar_length - filled_length)
                percentage = round(progress * 100)

            embed = discord.Embed(
                title=f'{member.display_name}\'s Level Stats',
                color=discord.Color.gold()
            )

            # Set user profile picture as thumbnail
            if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)

            embed.add_field(name='Level', value=user_level, inline=True)
            embed.add_field(name='XP', value=user_xp, inline=True)
            embed.add_field(name='Messages', value=user_messages, inline=True)
            
            embed.add_field(name=f'Progress to Level {user_level + 1}', value=f'{progress_bar} {percentage}%', inline=False)

            await ctx.send(embed=embed)

    @commands.group(name='set', invoke_without_command=True)
    async def set_command(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Invalid set command. Use `{self.bot.command_prefix}set level <channel>`.")

    @set_command.command(name='level')
    async def set_level_notification_channel(self, ctx, channel: discord.TextChannel):
        # Access the database pool and notification channels from bot instance
        db_pool = self.bot.pool
        notification_channels = self.bot.NOTIFICATION_CHANNELS

        if db_pool is None:
            await ctx.send("Database connection not available.")
            return

        # Ensure the command is used in a guild
        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.")
            return

        server_id = ctx.guild.id
        channel_id = channel.id

        print(f"Attempting to save setting: key='level', server_id={server_id}, channel_id={channel_id}") # Debug print

        async with db_pool.acquire() as connection:
            # Save the channel ID to the settings table with the server ID
            await connection.execute('''
                INSERT INTO settings (key, server_id, value) VALUES ($1, $2, $3::TEXT)
                ON CONFLICT (key, server_id) DO UPDATE SET value = $3::TEXT
            ''',
            'level',
            server_id,
            str(channel_id)
            )

        # Update in-memory cache (nested structure)
        if server_id not in notification_channels:
            notification_channels[server_id] = {}
        notification_channels[server_id]['level'] = channel_id

        await ctx.send(f"Level up notifications will now be sent to {channel.mention} in this server.")

    @commands.command(name='afk', help='Set your AFK status. Usage: .afk [reason]')
    async def afk_command(self, ctx, *, reason: str = "No reason provided."):
        self.afk[ctx.author.id] = (reason, datetime.datetime.utcnow())
        await ctx.send(f"{ctx.author.mention} is now AFK: {reason}")
        try:
            new_nick = ctx.author.display_name
            if not new_nick.endswith(' | AFK'):
                new_nick = (new_nick + ' | AFK')[:32]
                await ctx.author.edit(nick=new_nick)
        except Exception:
            pass  # Ignore if can't change nickname

    @app_commands.command(name='afk', description='Set your AFK status.')
    @app_commands.describe(reason='Reason for going AFK (optional)')
    async def afk_slash(self, interaction: discord.Interaction, reason: str = "No reason provided."):
        self.afk[interaction.user.id] = (reason, datetime.datetime.utcnow())
        await interaction.response.send_message(f"{interaction.user.mention} is now AFK: {reason}", ephemeral=True)
        try:
            member = interaction.guild.get_member(interaction.user.id)
            if member:
                new_nick = member.display_name
                if not new_nick.endswith(' | AFK'):
                    new_nick = (new_nick + ' | AFK')[:32]
                    await member.edit(nick=new_nick)
        except Exception:
            pass

    @commands.command(name='funhelp', help='Shows this help message for fun commands.')
    async def funhelp_command(self, ctx):
        embed = discord.Embed(title='Fun Commands', color=discord.Color.purple())
        embed.add_field(name='<:afk:1375111985821253763> afk', value='Set your AFK status. Usage: `.afk [reason]` or `/afk`', inline=False)
        embed.add_field(name='<:vc:1375112099801337856> vcactive', value='Show the most active users in voice chat. Usage: `.vcactive` or `/vcactive`', inline=False)
        embed.add_field(name='level', value='Shows your level, XP, and progress. Usage: `.level [user]`', inline=False)
        embed.add_field(name='leaderboard', value='Shows the top members by level and XP. Usage: `.leaderboard`', inline=False)
        embed.set_footer(text='You can use these as slash commands too!')
        await ctx.send(embed=embed)

    async def cog_load(self):
        self.bot.tree.add_command(self.afk_slash)

# This function is called to load the cog
async def setup(bot):
    print("Attempting to add Fun cog")
    await bot.add_cog(Fun(bot)) 