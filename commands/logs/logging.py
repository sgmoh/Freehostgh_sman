# commands/logs/logging.py
import discord
from discord.ext import commands
import asyncpg # Import asyncpg for database interaction

# We will now store log channels per guild and type within the cog instance
# LOG_CHANNELS = {}

class ServerLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Dictionary to store log channels: {guild_id: {log_type: channel_id}}
        self.guild_log_channels = {}
        # Mapping of log types to internal keys and descriptions
        self.log_types_map = {
            'messages': {'key': 'log_channel_messages', 'description': 'Message Edits/Deletions'},
            'joins': {'key': 'log_channel_joins', 'description': 'Member Joins/Leaves'},
            'voice': {'key': 'log_channel_voice', 'description': 'Voice State Changes'},
            'members': {'key': 'log_channel_members', 'description': 'Member/User Updates, Bans/Unbans'},
        }

    async def load_log_settings(self):
        # Load existing log channel settings from the database
        if self.bot.pool is not None:
            try:
                async with self.bot.pool.acquire() as connection:
                    settings = await connection.fetch("SELECT server_id, key, value FROM settings WHERE key LIKE 'log_channel_%'")
                    for setting in settings:
                        server_id = int(setting['server_id'])
                        key = setting['key']
                        channel_id = int(setting['value'])
                        log_type = None
                        for type_name, type_info in self.log_types_map.items():
                            if type_info['key'] == key:
                                log_type = type_name
                                break

                        if log_type:
                            if server_id not in self.guild_log_channels:
                                self.guild_log_channels[server_id] = {}
                            self.guild_log_channels[server_id][log_type] = channel_id
                            print(f"Loaded log channel for guild {server_id}, type {log_type}: {channel_id}")

            except Exception as e:
                print(f"Error loading log channel settings from database: {e}")

    @commands.command(name='setlog', help='Sets a specific channel for logging server events. Requires Administrator permission.')
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx, log_type: str, channel: discord.TextChannel):
        if self.bot.pool is None:
            await ctx.send("Database connection not available.")
            return

        if ctx.guild is None:
            await ctx.send("This command can only be used in a server.")
            return

        log_type = log_type.lower()
        if log_type not in self.log_types_map:
            await ctx.send(f"Invalid log type. Available types: {', '.join(self.log_types_map.keys())}. Example: .setlog messages #channel")
            return

        server_id = ctx.guild.id
        channel_id = channel.id
        db_key = self.log_types_map[log_type]['key']

        try:
            async with self.bot.pool.acquire() as connection:
                # Save the log channel ID to the settings table
                await connection.execute('''
                    INSERT INTO settings (key, server_id, value) VALUES ($1, $2, $3::TEXT)
                    ON CONFLICT (key, server_id) DO UPDATE SET value = $3::TEXT
                ''',
                db_key,
                server_id,
                str(channel_id)
                )

            # Update in-memory cache
            if server_id not in self.guild_log_channels:
                self.guild_log_channels[server_id] = {}
            self.guild_log_channels[server_id][log_type] = channel_id

            await ctx.send(f"{log_type.capitalize()} logs will now be sent to {channel.mention}.")

        except Exception as e:
            await ctx.send(f"An error occurred while saving the log channel: {e}")

    async def get_specific_log_channel(self, guild, log_type: str):
        """Helper function to get a specific log channel for a guild and type."""
        if guild and guild.id in self.guild_log_channels:
            channel_id = self.guild_log_channels[guild.id].get(log_type)
            if channel_id:
                return self.bot.get_channel(channel_id)
        return None

    # Event Listeners for Logging

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content == after.content or before.author.bot:
            return # Ignore if content didn't change or message is from a bot

        log_channel = await self.get_specific_log_channel(before.guild, 'messages')
        if log_channel:
            embed = discord.Embed(title='Message Edited', color=discord.Color.orange())
            embed.add_field(name='Original', value=before.content, inline=False)
            embed.add_field(name='Edited', value=after.content, inline=False)
            embed.add_field(name='Channel', value=before.channel.mention, inline=True)
            embed.add_field(name='Author', value=before.author.mention, inline=True)
            embed.set_footer(text=f'Message ID: {before.id}')
            if after.author.avatar:
                embed.set_thumbnail(url=after.author.avatar.url)
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return # Ignore bot messages

        log_channel = await self.get_specific_log_channel(message.guild, 'messages')
        if log_channel:
            embed = discord.Embed(title="Message Deleted", color=discord.Color.red())
            embed.add_field(name="Author", value=message.author.display_name, inline=True)
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            embed.add_field(name="Content", value=message.content or "No content", inline=False)
            if message.author.avatar:
                embed.set_thumbnail(url=message.author.avatar.url)
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return # Ignore if member is a bot

        log_channel = await self.get_specific_log_channel(member.guild, 'joins')
        if log_channel:
            embed = discord.Embed(title='Member Joined', color=discord.Color.green())
            embed.set_author(name=f'{member.display_name} ({member.id})', icon_url=member.avatar.url if member.avatar else discord.Embed.Empty)
            if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)
            embed.add_field(name='User', value=member.mention, inline=True)
            embed.add_field(name='Account Created', value=member.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
            embed.set_footer(text=f'Member Count: {member.guild.member_count}')
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return # Ignore if member is a bot

        log_channel = await self.get_specific_log_channel(member.guild, 'joins')
        if log_channel:
            embed = discord.Embed(title='Member Left', color=discord.Color.red())
            embed.set_author(name=f'{member.display_name} ({member.id})', icon_url=member.avatar.url if member.avatar else discord.Embed.Empty)
            if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)
            embed.add_field(name='User', value=member.mention, inline=True)
            embed.set_footer(text=f'Member Count: {member.guild.member_count}')
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        log_channel = await self.get_specific_log_channel(after.guild, 'members')
        if log_channel:
            # Nickname changed
            if before.nick != after.nick:
                embed = discord.Embed(title='Nickname Changed', color=discord.Color.blue())
                embed.add_field(name='User', value=after.mention, inline=True)
                embed.add_field(name='Before', value=before.nick or "None", inline=True)
                embed.add_field(name='After', value=after.nick or "None", inline=True)
                if after.avatar:
                    embed.set_thumbnail(url=after.avatar.url)
                await log_channel.send(embed=embed)

            # Roles changed
            if before.roles != after.roles:
                added_roles = [role.name for role in after.roles if role not in before.roles]
                removed_roles = [role.name for role in before.roles if role not in after.roles]

                if added_roles:
                    embed = discord.Embed(title='Roles Added', color=discord.Color.green())
                    embed.add_field(name='User', value=after.mention, inline=True)
                    embed.add_field(name='Roles', value=', '.join(added_roles), inline=False)
                    if after.avatar:
                        embed.set_thumbnail(url=after.avatar.url)
                    await log_channel.send(embed=embed)

                if removed_roles:
                    embed = discord.Embed(title='Roles Removed', color=discord.Color.red())
                    embed.add_field(name='User', value=after.mention, inline=True)
                    embed.add_field(name='Roles', value=', '.join(removed_roles), inline=False)
                    if after.avatar:
                        embed.set_thumbnail(url=after.avatar.url)
                    await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        # This event fires for global changes (username, avatar, discriminator)
        # Check if the user is in a guild where logging is enabled
        for guild in self.bot.guilds:
            log_channel = await self.get_specific_log_channel(guild, 'members')
            if log_channel:
                # Username changed (covers discriminator changes implicitly in new usernames)
                if before.name != after.name:
                    embed = discord.Embed(title='Username Changed', color=discord.Color.blue())
                    embed.add_field(name='User', value=after.mention, inline=True)
                    embed.add_field(name='Before', value=before.name, inline=True)
                    embed.add_field(name='After', value=after.name, inline=True)
                    if after.avatar:
                        embed.set_thumbnail(url=after.avatar.url)
                    await log_channel.send(embed=embed)

                # Avatar changed
                if before.avatar != after.avatar:
                    embed = discord.Embed(title='Avatar Changed', color=discord.Color.blue())
                    embed.set_author(name=f'{after.display_name} ({after.id})', icon_url=after.avatar.url if after.avatar else discord.Embed.Empty)
                    if after.avatar:
                        embed.set_thumbnail(url=after.avatar.url)
                    embed.add_field(name='User', value=after.mention, inline=True)
                    # embed.set_thumbnail(url=after.avatar.url) # Already set above
                    await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        log_channel = await self.get_specific_log_channel(member.guild, 'voice')
        if log_channel:
            # Joined a voice channel
            if before.channel is None and after.channel is not None:
                embed = discord.Embed(title='Voice Channel Joined', color=discord.Color.green())
                embed.add_field(name='User', value=member.mention, inline=True)
                embed.add_field(name='Channel', value=after.channel.mention, inline=True)
                if member.avatar:
                    embed.set_thumbnail(url=member.avatar.url)
                await log_channel.send(embed=embed)

            # Left a voice channel
            elif before.channel is not None and after.channel is None:
                embed = discord.Embed(title='Voice Channel Left', color=discord.Color.red())
                embed.add_field(name='User', value=member.mention, inline=True)
                embed.add_field(name='Channel', value=before.channel.mention, inline=True)
                if member.avatar:
                    embed.set_thumbnail(url=member.avatar.url)
                await log_channel.send(embed=embed)

            # Moved to a different voice channel
            elif before.channel is not None and after.channel is not None and before.channel != after.channel:
                embed = discord.Embed(title='Voice Channel Moved', color=discord.Color.blue())
                embed.add_field(name='User', value=member.mention, inline=True)
                embed.add_field(name='From', value=before.channel.mention, inline=True)
                embed.add_field(name='To', value=after.channel.mention, inline=True)
                if member.avatar:
                    embed.set_thumbnail(url=member.avatar.url)
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        log_channel = await self.get_specific_log_channel(guild, 'members')
        if log_channel:
            embed = discord.Embed(title='Member Banned', color=discord.Color.red())
            embed.set_author(name=f'{user.name} ({user.id})', icon_url=user.avatar.url if user.avatar else discord.Embed.Empty)
            if user.avatar:
                 embed.set_thumbnail(url=user.avatar.url)
            embed.add_field(name='User', value=user.mention, inline=True)
            # Note: Reason for ban is often in the audit log, not directly in this event
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        log_channel = await self.get_specific_log_channel(guild, 'members')
        if log_channel:
            embed = discord.Embed(title='Member Unbanned', color=discord.Color.green())
            embed.set_author(name=f'{user.name} ({user.id})', icon_url=user.avatar.url if user.avatar else discord.Embed.Empty)
            if user.avatar:
                embed.set_thumbnail(url=user.avatar.url)
            embed.add_field(name='User', value=user.mention, inline=True)
            # Note: Reason for unban is often in the audit log
            await log_channel.send(embed=embed)

    async def get_log_channel(self, guild):
        """Helper function to get the log channel for a guild."""
        # This function is now less specific, kept for potential broader use
        # Consider deprecating or renaming if get_specific_log_channel is preferred
        if guild and guild.id in self.guild_log_channels:
            # Return a default log channel if no specific type is requested?
            # For now, let's make it clear this needs a type.
            return None # Or raise an error, depending on desired behavior

async def setup(bot):
    # Instantiate the cog
    cog = ServerLogging(bot)
    # Add the cog to the bot
    await bot.add_cog(cog)
    # Load settings from the database after the cog is added
    await cog.load_log_settings() 