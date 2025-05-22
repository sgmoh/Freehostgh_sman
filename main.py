#!/usr/bin/env python3
"""
Combined Discord Bot + Dashboard for Render deployment
This runs both the Discord bot and web dashboard in one service
"""

import os
import threading
import subprocess
import time
from flask import Flask, render_template
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

# Bot stats storage
bot_stats = {
    'name': '.gg/gazaguild',
    'uptime': '0h 0m 0s', 
    'servers': 1,
    'commands': 25,
    'status': 'Starting...'
}

start_time = time.time()

def run_discord_bot():
    """Run the Discord bot in a separate thread"""
    try:
        print("🤖 Starting Discord bot...")
        subprocess.run(['python', 'bot.py'])
    except Exception as e:
        print(f"Bot error: {e}")

def get_bot_info():
    """Get bot information safely"""
    global bot_stats
    
    time.sleep(5)  # Wait for bot to start
    
    try:
        # Count commands from the bot structure
        command_count = 0
        commands_dir = './commands'
        if os.path.exists(commands_dir):
            for category in os.listdir(commands_dir):
                category_path = os.path.join(commands_dir, category)
                if os.path.isdir(category_path):
                    for file in os.listdir(category_path):
                        if file.endswith('.py'):
                            command_count += 3  # Approximate commands per file
        
        bot_stats['commands'] = max(command_count, 25)
        bot_stats['status'] = 'Online'
        
        # Try to get bot name from Discord token (safely)
        token = os.getenv('DISCORD_BOT_TOKEN')
        if token:
            try:
                headers = {'Authorization': f'Bot {token}'}
                response = requests.get('https://discord.com/api/v9/users/@me', headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    bot_stats['name'] = data.get('username', '.gg/gazaguild')
                    
                # Get guild count
                response = requests.get('https://discord.com/api/v9/users/@me/guilds', headers=headers, timeout=5)
                if response.status_code == 200:
                    guilds = response.json()
                    bot_stats['servers'] = len(guilds)
            except:
                pass
                
    except Exception as e:
        print(f"Info fetch error: {e}")

@app.route('/')
def dashboard():
    global bot_stats, start_time
    
    # Calculate uptime
    uptime_seconds = int(time.time() - start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    
    bot_stats['uptime'] = uptime_str
    
    return render_template('dashboard.html', stats=bot_stats)

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return {'status': 'healthy', 'uptime': bot_stats['uptime'], 'bot_status': bot_stats['status']}, 200

if __name__ == '__main__':
    print("🚀 Starting combined Discord Bot + Dashboard service...")
    
    # Start Discord bot in background thread
    bot_thread = threading.Thread(target=run_discord_bot, daemon=True)
    bot_thread.start()
    
    # Start bot info fetching in background
    info_thread = threading.Thread(target=get_bot_info, daemon=True)
    info_thread.start()
    
    # Start Flask dashboard
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Dashboard starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)