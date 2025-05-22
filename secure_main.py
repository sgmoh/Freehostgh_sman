from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import time
import requests
import threading

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure random secret key

# Bot stats storage
bot_stats = {
    'name': 'Not Connected',
    'uptime': '0h 0m 0s', 
    'servers': 0,
    'commands': 25,
    'status': 'Waiting for Token...'
}

start_time = time.time()

def get_bot_info_with_token(token):
    """Get bot information using provided token"""
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
        
        # Try to get bot info from Discord API
        if token:
            try:
                headers = {'Authorization': f'Bot {token}'}
                response = requests.get('https://discord.com/api/v9/users/@me', headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    bot_stats['name'] = data.get('username', 'Unknown Bot')
                    bot_stats['status'] = 'Online'
                    
                    # Get guild count
                    response = requests.get('https://discord.com/api/v9/users/@me/guilds', headers=headers, timeout=10)
                    if response.status_code == 200:
                        guilds = response.json()
                        bot_stats['servers'] = len(guilds)
                    else:
                        bot_stats['servers'] = 1  # Default
                        
                    return True
                else:
                    bot_stats['status'] = 'Invalid Token'
                    return False
            except Exception as e:
                bot_stats['status'] = 'Connection Error'
                return False
                
    except Exception as e:
        bot_stats['status'] = 'System Error'
        return False
    
    return False

@app.route('/')
def index():
    if 'discord_token' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        token = request.form.get('discord_token', '').strip()
        
        if token:
            # Test the token
            if get_bot_info_with_token(token):
                session['discord_token'] = token
                flash('Successfully connected to Discord!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid Discord token. Please check and try again.', 'error')
        else:
            flash('Please enter a Discord token.', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'discord_token' not in session:
        return redirect(url_for('login'))
    
    global bot_stats, start_time
    
    # Calculate uptime
    uptime_seconds = int(time.time() - start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    
    bot_stats['uptime'] = uptime_str
    
    # Refresh bot info periodically
    token = session.get('discord_token')
    if token:
        threading.Thread(target=get_bot_info_with_token, args=(token,), daemon=True).start()
    
    return render_template('dashboard.html', stats=bot_stats)

@app.route('/logout')
def logout():
    session.clear()
    flash('Successfully logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return {'status': 'healthy', 'uptime': bot_stats['uptime'], 'bot_status': bot_stats['status']}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🔐 Secure Discord Dashboard starting on port {port}")
    print("🌐 Visit the website to enter your Discord token securely!")
    app.run(host='0.0.0.0', port=port, debug=False)