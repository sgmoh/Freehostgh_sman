from flask import Flask, render_template
import os
import time
from dotenv import load_dotenv
import requests
import threading

load_dotenv()

app = Flask(__name__)

# Bot stats storage
bot_stats = {
    'name': '.gg/gazaguild',  # Default bot name
    'uptime': '0h 0m 0s',
    'servers': 1,
    'commands': 25,
    'status': 'Online'
}

start_time = time.time()

def get_bot_info():
    """Get bot information safely"""
    global bot_stats
    
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
                # Use Discord API to get bot info
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
                pass  # Keep defaults if API fails
                
    except Exception as e:
        print(f"Info fetch error: {e}")
        # Keep defaults

# Start bot info fetching in background
threading.Thread(target=get_bot_info, daemon=True).start()

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

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return {'status': 'healthy', 'uptime': bot_stats['uptime']}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)