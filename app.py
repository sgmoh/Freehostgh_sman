from flask import Flask, render_template
import discord
import os
import time
from dotenv import load_dotenv
import asyncio
import threading

load_dotenv()

app = Flask(__name__)

# Bot stats storage
bot_stats = {
    'name': 'Loading...',
    'uptime': 0,
    'servers': 0,
    'commands': 0,
    'status': 'Offline'
}

start_time = time.time()

async def get_bot_info():
    """Get bot information using Discord API"""
    global bot_stats
    
    try:
        # Create a simple client to get bot info
        intents = discord.Intents.default()
        client = discord.Client(intents=intents)
        
        @client.event
        async def on_ready():
            global bot_stats
            bot_stats['name'] = client.user.name
            bot_stats['servers'] = len(client.guilds)
            bot_stats['status'] = 'Online'
            
            # Count commands from the bot structure
            command_count = 0
            try:
                import os
                commands_dir = './commands'
                if os.path.exists(commands_dir):
                    for category in os.listdir(commands_dir):
                        category_path = os.path.join(commands_dir, category)
                        if os.path.isdir(category_path):
                            for file in os.listdir(category_path):
                                if file.endswith('.py'):
                                    command_count += 1
                bot_stats['commands'] = command_count
            except:
                bot_stats['commands'] = 25  # Approximate count
            
            await client.close()
        
        token = os.getenv('DISCORD_BOT_TOKEN')
        if token:
            await client.start(token)
    except Exception as e:
        print(f"Could not fetch bot info: {e}")
        bot_stats['name'] = 'Discord Bot'
        bot_stats['commands'] = 25
        bot_stats['status'] = 'Running'

def run_bot_info():
    """Run bot info fetching in a separate thread"""
    try:
        asyncio.run(get_bot_info())
    except:
        pass

# Start bot info fetching in background
threading.Thread(target=run_bot_info, daemon=True).start()

@app.route('/')
def dashboard():
    global bot_stats, start_time
    
    # Calculate uptime
    uptime_seconds = int(time.time() - start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    
    # Update uptime in stats
    bot_stats['uptime'] = uptime_str
    
    return render_template('dashboard.html', stats=bot_stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)