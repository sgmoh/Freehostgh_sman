import discord
import os
import importlib.util
import re
import time
import logging
import asyncio
from discord.ext import commands
import sys
from dotenv import load_dotenv
# import asyncpg # type: ignore # Moved to database.py

# Load environment variables
load_dotenv()

# Enhanced logging setup for better debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import database functions
from database_configurations.database import create_db_pool_and_load_settings, close_db_pool, NOTIFICATION_CHANNELS, ensure_security_settings_table

# Get token from environment variable
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
PREFIX = '.'

# Performance monitoring
start_time = time.time()
logger.info(f"🚀 Bot startup initiated at {time.strftime('%Y-%m-%d %H:%M:%S')}")

intents = discord.Intents.default()
intents.message_content = True # Enable the message content intent
intents.members = True # Enable the members intent for caching members

def get_prefix(bot, message):
    return ['.', '/']

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

bot.user_data = {} # Keep user_data here for now, or consider moving it if it becomes database-backed
bot.NOTIFICATION_CHANNELS = NOTIFICATION_CHANNELS # Reference the imported settings dictionary
bot.pool = None # Initialize pool attribute here

# Define command categories and their commands
COMMAND_CATEGORIES = {
    'Moderation': {
        'emoji': '<:Prefix:1373605377609957426>',
        'commands': [
            {'name': '<:clear:1373370955279110245> purge', 'description': '<:clear:1373370955279110245> Bulk delete messages'},
            {'name': '<:Warn:1373605418315677807> warn', 'description': '<:Warn:1373605418315677807> Warns a user.'},
            {'name': '<:Warn:1373605418315677807> warnings', 'description': '<:Warn:1373605418315677807> Shows a user\'s warnings.'},
            {'name': '<:timeout:1373371114155413504> mute', 'description': '<:timeout:1373371114155413504> Mutes a user for a specified duration with an optional reason. Example: .mute @user 5m spam'},
            {'name': '<:timeout:1373371114155413504> unmute', 'description': '<:timeout:1373371114155413504> Removes timeout from a user.'},
            {'name': '<:slowmode:1374811642583322784> slowmode', 'description': '<:slowmode:1374811642583322784> Sets the slowmode for a channel. Requires Manage Channels permission. Usage: .slowmode #channel <duration (e.g., 5m, 1h, 30s)>'},
            {'name': '<:Level:1374468851525226584> set level', 'description': '<:Level:1374468851525226584> Sets the channel for level up notifications.'},
            {'name': '<:loked:1374846034542334006> lock', 'description': '<:loked:1374846034542334006> Locks the current channel or all channels.'},
            {'name': '<:unlock:1374832837349609503> unlock', 'description': '<:unlock:1374832837349609503> Unlocks the current channel or all channels.'},
            {'name': '<:role:1374834526005497998> role', 'description': '<:role:1374834526005497998> Assigns a role to a user. Usage: .role @user <role>'},
            {'name': '<:roleremove:1374831624482721823> removerole', 'description': '<:roleremove:1374831624482721823> Removes a role from a user. Usage: .removerole @user <role>'}
        ]
    },
    'Utility': {
        'emoji': '<:Briefcase:1374848333956255884>',
        'commands': [
            {'name': '<:user:1374846273706000434> usericon', 'description': '<:user:1374846273706000434> Displays a user\'s icon.'},
            {'name': '<:Exclmationmark:1374504177841082379> welcome', 'description': '<:Join:1373605236354056346> Sets the welcome channel.'},
            {'name': '<:Information:1374848638798397442> servericon', 'description': '<:Information:1374848638798397442> Displays the server\'s icon.'},
            {'name': '<:Information:1374848638798397442> serverinfo', 'description': '<:Information:1374848638798397442> Displays server information.'},
            {'name': '<:user:1374846273706000434> userinfo', 'description': '<:user:1374846273706000434> Displays user information.'}
        ]
    },
    'Fun': {
        'emoji': '<:Multipurpose:1373371000271409416>',
        'description': '''💫 **Fun Commands List**

> <:afk:1375111985821253763> **`AFK`**  
> Set your AFK status.  
> **Usage:** `.afk [reason]` or `/afk`  
> <:Multipurpose:1373371000271409416> *Category: Multipurpose*

> <:vc:1375112099801337856> **`VC Active`**  
> Shows the most active users in voice chat.  
> **Usage:** `.vcactive` or `/vcactive`  
> <:Chanels:1374849115644629202> *Category: Channels*

> <:Level:1374468851525226584> **`Level`**  
> Displays your level, XP, and progress.  
> **Usage:** `.level [user]` or `/level`  
> <:Golden:1374768659771428995> *Category: Golden*

> <:leaderboard:1374503230272442459> **`Leaderboard`**  
> Shows server ranking based on levels and messages.  
> **Usage:** `.leaderboard` or `/leaderboard`  
> <:Silver:1374504846216003596> *Category: Silver*

> <:invite:1375130577933565952> **`Invites`**  
> Shows how many invites a user has.  
> **Usage:** `.inv [user]` or `/inv`

> <:leaderboardd:1374502601269186680> **`Invite Leaderboard`**  
> View the top inviters in the server.  
> **Usage:** `.invleaderboard` or `/invleaderboard`

> <:Timer:1375132027430633543> **`Timer`**  
> Set a countdown timer that notifies you when it ends.  
> **Usage:** `.timer <duration>` or `/timer <duration>`  
> Example: `10s`, `5m`, `2h`

> <:Poll:1375134172120748112> **`Poll`**  
> Create a poll with up to 10 options.  
> **Usage:** `.poll Question? | Option 1 | Option 2` or `/poll`  
> Example: `.poll Best color? | Red | Blue | Green`
'''
    },
    'Logs': {
        'emoji': '<:Logs:1373372085866598550>',
        'commands': [
            {'name': 'setlog', 'description': 'Assign a log channel for a specific event type.\n**Usage:** `.setlog <type> #channel`\n**Types:** `messages`, `joins`, `voice`, `members`'}
        ],
        'description': '**<:Logs:1373372085866598550>・Logs Commands**\n\n> Track key server activities with real-time logging. Events include:\n> • <:Clipboard:1373605336820220097> Message Edits & Deletions  \n> • <:Join:1373605236354056346> Member Joins / <:leave:1373605302662070362> Leaves  \n> • <:timeout:1373371114155413504> Member / User Updates  \n> • <:mute:1373372051024248832> Voice State Changes  \n> • <:banned:1373370889235726407> Member Bans / Unbans  '
    },
    'Islamic': {
        'emoji': '<:Islamic:1374862588265103420>',
        'commands': [
            {'name': '<:Dua:1375096374013464696> dua', 'description': '<:Dua:1375096374013464696> Get a random dua with translation.'},
            {'name': '<:Hadith:1375097236517552199> hadith', 'description': '<:Hadith:1375097236517552199> Get a random or searched hadith.'},
            {'name': '<:Zikr:1375097279433801748> zikr', 'description': '<:Zikr:1375097279433801748> Get a random or searched zikr.'}
        ],
        'description': '<:Islamic:1374862588265103420> • **Islamic Commands**\nCommands for duas, hadith, and zikr with translation and search.'
    },
    'Security': {
        'emoji': '<:Security:1375118465668616212>',
        'commands': [
            {'name': '<:Security:1375118465668616212> automod', 'description': '<:Security:1375118465668616212> Toggle automod on or off for this server. Usage: .automod on/off or /automod on|off'},
            {'name': '<:Antinuke:1375119851299016756> antinuke', 'description': '<:Antinuke:1375119851299016756> Toggle antinuke on or off. If enabled, the bot will remove all roles from users who perform dangerous actions (mass channel/role deletion, spam mentions) and DM them a warning.'},
            {'name': '<:antispam:1375122762426880000> antispam', 'description': '<:antispam:1375122762426880000> Toggle anti-spam on or off. If enabled, users who send 6+ messages in less than 1 second are timed out for 10 seconds.'}
        ],
        'description': '<:Security:1375118465668616212> • **Security Commands**\nAutomated moderation to keep your server safe.'
    }
}

@bot.event
async def on_ready():
    ready_start = time.time()
    logger.info(f'🎉 {bot.user.name} has connected to Discord!')
    logger.info(f'📊 Bot ID: {bot.user.id} | Servers: {len(bot.guilds)} | Users: {len(bot.users)}')

    # Create database pool and load settings with timing
    db_start = time.time()
    logger.info('🔄 Initializing database connection...')
    bot.pool, bot.NOTIFICATION_CHANNELS = await create_db_pool_and_load_settings()
    await ensure_security_settings_table(bot.pool)
    db_time = time.time() - db_start
    logger.info(f'✅ Database initialized in {db_time:.2f}s')

    # Load commands with enhanced debugging and timing
    cmd_start = time.time()
    logger.info('🔄 Loading command modules...')
    commands_dir = './commands'
    loaded_count = 0
    failed_count = 0
    
    for item_name in os.listdir(commands_dir):
        item_path = os.path.join(commands_dir, item_name)
        if os.path.isdir(item_path):
            logger.debug(f'📁 Processing category: {item_name}')
            for filename in os.listdir(item_path):
                if filename.endswith('.py'):
                    module_start = time.time()
                    module_name = filename[:-3]
                    full_module_path = f'commands.{item_name}.{module_name}'
                    file_path = os.path.join(item_path, filename)
                    try:
                        # Enhanced module loading with null checks
                        spec = importlib.util.spec_from_file_location(full_module_path, file_path)
                        if spec is None or spec.loader is None:
                            logger.error(f'❌ Failed to create spec for {full_module_path}')
                            failed_count += 1
                            continue
                            
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        if hasattr(module, 'setup'):
                            await module.setup(bot)
                            module_time = time.time() - module_start
                            logger.info(f'✅ Loaded {full_module_path} in {module_time:.3f}s')
                            loaded_count += 1
                        else:
                            logger.warning(f'⚠️ No setup function in {full_module_path}')
                    except Exception as e:
                        failed_count += 1
                        logger.error(f'❌ Failed to load {file_path}: {type(e).__name__}: {e}')

    cmd_time = time.time() - cmd_start
    total_time = time.time() - start_time
    
    logger.info(f'🏁 Bot fully ready! Loaded {loaded_count} modules, {failed_count} failed')
    logger.info(f'⏱️ Commands loaded in {cmd_time:.2f}s | Total startup: {total_time:.2f}s')
    logger.info(f'🌟 Bot is optimized and ready for action!')

@bot.event
async def on_close():
    print('Bot is shutting down. Closing database connection pool...')
    # Close the database pool
    await close_db_pool(bot.pool)

@bot.event
async def on_command_error(ctx, error):
    error_start = time.time()
    command_name = getattr(ctx.command, "name", "Unknown")
    
    if isinstance(error, commands.MissingRequiredArgument):
        command_signature = ctx.command.signature
        logger.warning(f'⚠️ Missing argument in {command_name} by {ctx.author}')
        await ctx.send(f"Incorrect usage. Proper usage: `{PREFIX}{command_name} {command_signature}`")
    elif isinstance(error, commands.BadArgument):
        command_signature = ctx.command.signature
        logger.warning(f'⚠️ Bad argument in {command_name} by {ctx.author}')
        await ctx.send(f"Invalid argument provided. Proper usage: `{PREFIX}{command_name} {command_signature}`")
    elif isinstance(error, commands.TooManyArguments):
        command_signature = ctx.command.signature
        logger.warning(f'⚠️ Too many arguments in {command_name} by {ctx.author}')
        await ctx.send(f"Too many arguments provided. Proper usage: `{PREFIX}{command_name} {command_signature}`")
    elif isinstance(error, commands.CommandOnCooldown):
        logger.info(f'⏱️ {command_name} on cooldown for {ctx.author}')
        await ctx.send(f"Command is on cooldown. Try again in {error.retry_after:.1f}s")
    elif isinstance(error, commands.MissingPermissions):
        logger.warning(f'🔒 Permission denied for {command_name} by {ctx.author}')
        await ctx.send("You don't have permission to use this command.")
    else:
        error_time = time.time() - error_start
        logger.error(f'❌ Exception in {command_name}: {type(error).__name__}: {error} (handled in {error_time:.3f}s)')

@bot.before_invoke
async def before_any_command(ctx):
    logger.debug(f'🎯 Command {ctx.command.name} invoked by {ctx.author} in {ctx.guild}')

# Performance and debugging commands
@bot.command(name='hello', help='Says hello')
async def hello(ctx):
    cmd_start = time.time()
    await ctx.send('Hello! 👋')
    cmd_time = time.time() - cmd_start
    logger.debug(f'⚡ Hello command executed in {cmd_time:.3f}s')

@bot.command(name='ping', help='Responds with pong and latency')
async def ping(ctx):
    cmd_start = time.time()
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! 🏓 Latency: {latency}ms')
    cmd_time = time.time() - cmd_start
    logger.debug(f'⚡ Ping command executed in {cmd_time:.3f}s (latency: {latency}ms)')

@bot.command(name='status', help='Shows bot performance stats')
async def status(ctx):
    if ctx.author.id == 930131254106550333:  # Bot owner only
        uptime = time.time() - start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        
        embed = discord.Embed(title="🤖 Bot Performance Stats", color=0x00ff00)
        embed.add_field(name="⏰ Uptime", value=f"{hours}h {minutes}m {seconds}s", inline=True)
        embed.add_field(name="📊 Servers", value=len(bot.guilds), inline=True)
        embed.add_field(name="👥 Users", value=len(bot.users), inline=True)
        embed.add_field(name="🏓 Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
        
        await ctx.send(embed=embed)
        logger.info(f'📊 Status command used by {ctx.author}')

@bot.command(name='restart')
async def restart_bot(ctx):
    # Check if the user is the specified owner
    if ctx.author.id == 930131254106550333:
        await ctx.send("Restarting bot...")
        # Attempt to self-restart using os.execv
        try:
            # Close the bot's connection first
            await bot.close()
            # Get the path to the Python executable
            python = sys.executable
            # Get the arguments used to start the current script
            os.execv(python, [python] + sys.argv)
        except Exception as e:
            await ctx.send(f"Error during self-restart: {e}")
            # If self-restart fails, close the bot as a fallback
            await bot.close()
    else:
        await ctx.send("You do not have permission to use this command.")

class HelpMenuDropdown(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = []
        # Iterate over a copy of keys to avoid issues while modifying the dictionary
        for category_name in list(COMMAND_CATEGORIES.keys()):
            category_info = COMMAND_CATEGORIES[category_name]
            emoji_string = category_info.get('emoji', '') # Get emoji string, default to empty if not found
            emoji_obj = None
            # Attempt to parse the emoji string if it looks like a custom emoji
            if emoji_string.startswith('<:') and emoji_string.endswith('>'):
                match = re.match(r'<:(\w+):(\d+)>', emoji_string)
                if match:
                    emoji_name = match.group(1)
                    emoji_id = int(match.group(2))
                    emoji_obj = discord.PartialEmoji(name=emoji_name, id=emoji_id)
            # Also handle standard emojis (e.g., '🔧')
            if emoji_string and not emoji_obj:
                emoji_obj = emoji_string

            # Use the category name as the label
            label = category_name

            # Add the option, including the parsed emoji if available
            options.append(discord.SelectOption(label=label, value=category_name, emoji=emoji_obj))

        super().__init__(placeholder='Select a category...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_category_name = self.values[0]
        print(f"[DEBUG] HelpMenuDropdown callback: Selected category: {selected_category_name}")

        # Get category info from dictionary (might be needed for description/emoji)
        selected_category_info = COMMAND_CATEGORIES.get(selected_category_name, {})
        # Check if a cog with this name exists
        cog = self.bot.get_cog(selected_category_name)
        print(f"[DEBUG] HelpMenuDropdown callback: Found cog '{selected_category_name}': {cog is not None}")

        embed = None

        # 1. Handle Logs as a special case using COMMAND_CATEGORIES dictionary
        if selected_category_name == 'Logs':
            print("[DEBUG] HelpMenuDropdown callback: Handling Logs category.")
            category_description_content = selected_category_info.get('description', '')
            commands_list = selected_category_info.get('commands', [])
            command_info = commands_list[0] if commands_list else None # Assuming only one command for Logs

            if command_info:
                full_log_content = f"{category_description_content}\n\n**<:Multipurpose:1373371000271409416>・Command:**\n`.{command_info['name']}` – {command_info['description']}"
            else:
                full_log_content = category_description_content + "\n\nNo commands found for this category.\""

            embed = discord.Embed(
                title=None, # Logs has title in description
                description=full_log_content,
                color=discord.Color.blue()
            )

        # 2. Check if the category is in COMMAND_CATEGORIES and has a non-empty commands list (Moderation, Fun).
        #    Prioritize displaying these as defined in the dictionary.
        elif selected_category_name in COMMAND_CATEGORIES and selected_category_name != 'Logs':
            print(f"[DEBUG] HelpMenuDropdown callback: Handling category '{selected_category_name}' from COMMAND_CATEGORIES.")
            embed = discord.Embed(
                description=selected_category_info.get('description', f'Commands in the {selected_category_name} category:'),
                color=discord.Color.blue()
            )
            commands_list = selected_category_info.get('commands', [])
            if commands_list:
                for command_info in commands_list:
                    embed.add_field(name=f'{PREFIX}{command_info["name"]}', value=command_info['description'], inline=False)
                print(f"[DEBUG] HelpMenuDropdown callback: Added {len(commands_list)} commands from COMMAND_CATEGORIES.")

        # 3. If not handled above (not Logs, not in COMMAND_CATEGORIES with commands), check if a cog exists.
        elif cog:
            print(f"[DEBUG] HelpMenuDropdown callback: Handling category '{selected_category_name}' as a cog.")

            if selected_category_name == 'Utility':
                # Custom formatting for Utility cog
                # Using the custom text provided by the user
                description_content = """
<:Multipurpose:1373371000271409416> • **Utility Commands**  
Useful tools to manage your server and fetch important info:

> 💡 **Commands in this category include:**
> • <:Exclmationmark:1374504177841082379> **.welcome** – Set a welcome channel for new members.  
> • <:Logs:1373372085866598550> **.servericon** – Display the server's icon.  
> • <:Information:1374848638798397442> **.serverinfo** – View detailed server information.  
> • <:user:1374846273706000434> **.userinfo** – Show info about a user.

<:Clipboard:1373605336820220097> **• Command Details:**

> <:Exclmationmark:1374504177841082379> **.welcome**  
> <:Join:1373605236354056346> Set a welcome channel for new members.  
> **Usage:** `.welcome #channel`

> <:Logs:1373372085866598550> **.servericon**  
> <:Clipboard:1373605336820220097> Display the server's icon.  
> **Usage:** `.servericon`

> <:Information:1374848638798397442> **.serverinfo**  
> <:Briefcase:1374848333956255884> View server name, ID, creation date & more.  
> **Usage:** `.serverinfo`

> <:user:1374846273706000434> **.userinfo**  
> <:role:1374834526005497998> View avatar, join date, roles & status of any user.  
> **Usage:** `.userinfo [user]`
"""
                embed = discord.Embed(
                    title=None, # Using custom formatting in description
                    description=description_content.strip(), # Remove trailing newlines
                    color=discord.Color.blue()
                )
                print(f"[DEBUG] HelpMenuDropdown callback: Constructed custom embed for Utility.")

            else:
                # Standard formatting for other cogs (if any)
                embed = discord.Embed(
                    title=f'{selected_category_name} Commands', # Use cog name directly in title
                    description=f'Commands in the {selected_category_name} category:', # Default description for cogs
                    color=discord.Color.blue()
                )
                commands_list = list(cog.get_commands()) # Convert to list to get length
                for command in commands_list:
                    # Fetch name and help text from the cog's command objects
                    embed.add_field(name=f'{self.bot.command_prefix}{command.name}', value=command.help or 'No description provided.', inline=False)
                print(f"[DEBUG] HelpMenuDropdown callback: Added {len(commands_list)} commands from cog using standard format.")

        # If embed is still None, it means the category was not found or had no commands/cog to display
        if embed is None:
            print("[DEBUG] HelpMenuDropdown callback: No commands/category found, showing error.")
            embed = discord.Embed(
                title='Error',
                description='Could not find commands for this category or no commands available.',
                color=discord.Color.red()
            )

        await interaction.response.edit_message(embed=embed, view=HelpMenuView(self.bot))

class HelpMenuView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot # Store bot instance
        self.add_item(HelpMenuDropdown(bot)) # Pass bot to dropdown
        back_button = discord.ui.Button(label="Back to Main", style=discord.ButtonStyle.secondary, custom_id='back_to_main_button')
        back_button.callback = self.back_to_main
        self.add_item(back_button)

    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
         embed = discord.Embed(
            title='Bot Help Menu',
            description=f'Created by gh_sman\nMy prefix is {PREFIX}\nUse the dropdown menu below to browse commands.',
            color=discord.Color.blue()
        )
         # Pass the bot instance when creating a new HelpMenuView
         await interaction.response.edit_message(embed=embed, view=HelpMenuView(self.bot))

@bot.command(name='help', help='Displays the help menu')
async def help_command(ctx):
    embed = discord.Embed(
        title='Bot Help Menu',
        description=f'Created by gh_sman\nMy prefix is {PREFIX}\nUse the dropdown menu below to browse commands.',
        color=discord.Color.blue()
    )
    # Pass the bot instance when creating the initial HelpMenuView
    await ctx.send(embed=embed, view=HelpMenuView(bot))

# Run the bot
bot.run(TOKEN) 
bot.run(TOKEN) 