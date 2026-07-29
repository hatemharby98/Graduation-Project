import subprocess
import time
import json
from datetime import datetime
from scapy.all import *
import random

# ======== CONFIG ========
TARGET_IP = "192.168.17.153"
LOG_FILE = "portscan_timeline.json"

class PortScanGenerator:
    """Port Scan Attack Generator with Timeline"""
    
    def __init__(self, target_ip):
        self.target_ip = target_ip
        self.scans = []
    
    def log_scan_start(self, scan_type, description):
        """تسجيل بداية الفحص"""
        self.current_scan = {
            "scan_type": scan_type,
            "description": description,
            "target_ip": self.target_ip,
            "start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
            "start_timestamp": time.time(),
        }
        print(f"\n{'='*60}")
        print(f"[+] Scan Type: {scan_type}")
        print(f"[+] Description: {description}")
        print(f"[+] Target: {self.target_ip}")
        print(f"[+] Start: {self.current_scan['start_time']}")
        print(f"{'='*60}\n")
    
    def log_scan_end(self):
        """تسجيل نهاية الفحص"""
        self.current_scan['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.current_scan['end_timestamp'] = time.time()
        self.current_scan['duration_seconds'] = round(
            self.current_scan['end_timestamp'] - self.current_scan['start_timestamp'], 2
        )
        
        print(f"[✓] Scan completed")
        print(f"[✓] Duration: {self.current_scan['duration_seconds']}s\n")
        
        self.scans.append(self.current_scan)
    
    def save_timeline(self):
        """حفظ الـ timeline"""
        with open(LOG_FILE, 'w') as f:
            json.dump(self.scans, f, indent=2)
        
        print(f"\n[✓] Timeline saved to: {LOG_FILE}")
        self.print_summary()
    
    def print_summary(self):
        """طباعة ملخص"""
        print("\n" + "="*60)
        print("PORT SCAN TIMELINE SUMMARY")
        print("="*60)
        
        for i, scan in enumerate(self.scans, 1):
            print(f"\n#{i} - {scan['scan_type']}")
            print(f"   Start: {scan['start_time']}")
            print(f"   End:   {scan['end_time']}")
            print(f"   Duration: {scan['duration_seconds']}s")
        
        print("\n" + "="*60)
        print(f"Total scans: {len(self.scans)}")
        print("="*60)


# ======== NMAP-BASED SCANS ========
def run_nmap_scan(scanner, scan_type, description, nmap_args):
    """تشغيل Nmap scan"""
    scanner.log_scan_start(scan_type, description)
    
    cmd = ["nmap"] + nmap_args + [scanner.target_ip]
    
    try:
        print(f"[*] Executing: {' '.join(cmd)}")
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=120
        )
        print("[✓] Nmap scan completed")
    except subprocess.TimeoutExpired:
        print("[!] Scan timed out")
    except subprocess.CalledProcessError as e:
        print(f"[!] Error: {e}")
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
    
    scanner.log_scan_end()
"""

# ======== SCAPY-BASED CUSTOM SCANS ========

def tcp_syn_scan_custom(scanner, ports=[80, 443, 22, 21, 25]):
    
    scanner.log_scan_start("CUSTOM_TCP_SYN", "Manual TCP SYN scan using Scapy")
    
    for port in ports:
        print(f"  [*] Scanning port {port}...")
        
        # إرسال SYN packet
        pkt = IP(dst=scanner.target_ip) / TCP(dport=port, flags="S")
        resp = sr1(pkt, timeout=2, verbose=False)
        
        if resp and resp.haslayer(TCP):
            if resp[TCP].flags == "SA":  # SYN-ACK
                print(f"      [+] Port {port} is OPEN")
                # إرسال RST لإغلاق الاتصال
                rst = IP(dst=scanner.target_ip) / TCP(dport=port, flags="R")
                send(rst, verbose=False)
            elif resp[TCP].flags == "RA":  # RST-ACK
                print(f"      [-] Port {port} is CLOSED")
        else:
            print(f"      [?] Port {port} - No response")
        
        time.sleep(0.5)
    
    scanner.log_scan_end()

"""
def tcp_connect_scan_custom(scanner, ports=[80, 443, 22]):
    """Custom TCP Connect Scan"""
    scanner.log_scan_start("CUSTOM_TCP_CONNECT", "Full TCP connection scan")
    
    import socket
    
    for port in ports:
        print(f"  [*] Connecting to port {port}...")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        
        try:
            result = sock.connect_ex((scanner.target_ip, port))
            if result == 0:
                print(f"      [+] Port {port} is OPEN")
            else:
                print(f"      [-] Port {port} is CLOSED")
        except socket.timeout:
            print(f"      [?] Port {port} - Timeout")
        except Exception as e:
            print(f"      [!] Port {port} - Error: {e}")
        finally:
            sock.close()
        
        time.sleep(0.5)
    
    scanner.log_scan_end()


def udp_scan_custom(scanner, ports=[53, 161, 123]):
    """Custom UDP Scan"""
    scanner.log_scan_start("CUSTOM_UDP", "UDP port scan using Scapy")
    
    for port in ports:
        print(f"  [*] Scanning UDP port {port}...")
        
        pkt = IP(dst=scanner.target_ip) / UDP(dport=port)
        resp = sr1(pkt, timeout=2, verbose=False)
        
        if resp is None:
            print(f"      [?] Port {port} - Open|Filtered")
        elif resp.haslayer(ICMP):
            if resp[ICMP].type == 3 and resp[ICMP].code == 3:
                print(f"      [-] Port {port} - Closed")
        elif resp.haslayer(UDP):
            print(f"      [+] Port {port} - Open")
        
        time.sleep(1)
    
    scanner.log_scan_end()


def fin_scan_custom(scanner, ports=[80, 443, 22]):
    """FIN Scan - لتخطي بعض Firewalls"""
    scanner.log_scan_start("CUSTOM_FIN", "TCP FIN scan to evade firewalls")
    
    for port in ports:
        print(f"  [*] FIN scan on port {port}...")
        
        pkt = IP(dst=scanner.target_ip) / TCP(dport=port, flags="F")
        resp = sr1(pkt, timeout=2, verbose=False)
        
        if resp is None:
            print(f"      [+] Port {port} - Open|Filtered")
        elif resp.haslayer(TCP):
            if resp[TCP].flags == "RA":
                print(f"      [-] Port {port} - Closed")
        
        time.sleep(0.5)
    
    scanner.log_scan_end()


def xmas_scan_custom(scanner, ports=[80, 443, 22]):
    """Xmas Scan - FIN, PSH, URG flags"""
    scanner.log_scan_start("CUSTOM_XMAS", "TCP Xmas scan (FIN+PSH+URG)")
    
    for port in ports:
        print(f"  [*] Xmas scan on port {port}...")
        
        pkt = IP(dst=scanner.target_ip) / TCP(dport=port, flags="FPU")
        resp = sr1(pkt, timeout=2, verbose=False)
        
        if resp is None:
            print(f"      [+] Port {port} - Open|Filtered")
        elif resp.haslayer(TCP):
            if resp[TCP].flags == "RA":
                print(f"      [-] Port {port} - Closed")
        
        time.sleep(0.5)
    
    scanner.log_scan_end()


def null_scan_custom(scanner, ports=[80, 443, 22]):
    """NULL Scan - بدون flags"""
    scanner.log_scan_start("CUSTOM_NULL", "TCP NULL scan (no flags)")
    
    for port in ports:
        print(f"  [*] NULL scan on port {port}...")
        
        pkt = IP(dst=scanner.target_ip) / TCP(dport=port, flags="")
        resp = sr1(pkt, timeout=2, verbose=False)
        
        if resp is None:
            print(f"      [+] Port {port} - Open|Filtered")
        elif resp.haslayer(TCP):
            if resp[TCP].flags == "RA":
                print(f"      [-] Port {port} - Closed")
        
        time.sleep(0.5)
    
    scanner.log_scan_end()


def ack_scan_custom(scanner, ports=[80, 443, 22]):
    """ACK Scan - لاكتشاف Firewall rules"""
    scanner.log_scan_start("CUSTOM_ACK", "TCP ACK scan for firewall detection")
    
    for port in ports:
        print(f"  [*] ACK scan on port {port}...")
        
        pkt = IP(dst=scanner.target_ip) / TCP(dport=port, flags="A")
        resp = sr1(pkt, timeout=2, verbose=False)
        
        if resp is None:
            print(f"      [?] Port {port} - Filtered")
        elif resp.haslayer(TCP):
            if resp[TCP].flags == "R":
                print(f"      [+] Port {port} - Unfiltered")
        elif resp.haslayer(ICMP):
            print(f"      [-] Port {port} - Filtered")
        
        time.sleep(0.5)
    
    scanner.log_scan_end()


def window_scan_custom(scanner, ports=[80, 443, 22]):
    """Window Scan - فحص TCP window"""
    scanner.log_scan_start("CUSTOM_WINDOW", "TCP Window scan")
    
    for port in ports:
        print(f"  [*] Window scan on port {port}...")
        
        pkt = IP(dst=scanner.target_ip) / TCP(dport=port, flags="A")
        resp = sr1(pkt, timeout=2, verbose=False)
        
        if resp and resp.haslayer(TCP):
            if resp[TCP].window > 0:
                print(f"      [+] Port {port} - Open")
            else:
                print(f"      [-] Port {port} - Closed")
        
        time.sleep(0.5)
    
    scanner.log_scan_end()


def idle_scan_simulation(scanner):
    """Idle Scan Simulation - باستخدام zombie host"""
    scanner.log_scan_start("IDLE_SCAN_SIM", "Idle scan simulation (zombie scan)")
    
    # ملاحظة: هذا simulation فقط - idle scan حقيقي محتاج zombie host
    print("  [*] This is a simulation of idle scan traffic pattern")
    print("  [*] In real scenario, you'd use: nmap -sI <zombie_host> <target>")
    
    # إرسال packets تشبه idle scan pattern
    for port in [80, 443, 22]:
        print(f"  [*] Simulating idle scan on port {port}...")
        
        # إرسال SYN/ACK للزومبي (simulation)
        pkt1 = IP(dst=scanner.target_ip) / TCP(dport=port, flags="S")
        send(pkt1, verbose=False)
        
        time.sleep(0.3)
        
        # إرسال spoofed packet
        pkt2 = IP(src=scanner.target_ip, dst=scanner.target_ip) / \
               TCP(sport=port, dport=port, flags="SA")
        send(pkt2, verbose=False)
        
        time.sleep(0.5)
    
    scanner.log_scan_end()


def decoy_scan_custom(scanner, ports=[80, 443]):
    """Decoy Scan - استخدام IPs وهمية"""
    scanner.log_scan_start("CUSTOM_DECOY", "Decoy scan with fake source IPs")
    
    # IPs وهمية
    decoys = [
        "192.168.1.100",
        "192.168.1.101",
        "192.168.1.102",
        "192.168.1.103"
    ]
    
    for port in ports:
        print(f"  [*] Decoy scan on port {port}...")
        
        # إرسال من IPs مختلفة
        for decoy_ip in decoys:
            pkt = IP(src=decoy_ip, dst=scanner.target_ip) / \
                  TCP(dport=port, flags="S")
            send(pkt, verbose=False)
            time.sleep(0.1)
        
        # الطلب الحقيقي
        real_pkt = IP(dst=scanner.target_ip) / TCP(dport=port, flags="S")
        send(real_pkt, verbose=False)
        
        time.sleep(1)
    
    scanner.log_scan_end()


def fragmented_scan_custom(scanner, ports=[80, 443]):
    """Fragmented Scan - تجزئة الـ packets"""
    scanner.log_scan_start("CUSTOM_FRAGMENTED", "Fragmented packet scan to evade IDS")
    
    for port in ports:
        print(f"  [*] Fragmented scan on port {port}...")
        
        # إنشاء packet كبير
        pkt = IP(dst=scanner.target_ip) / TCP(dport=port, flags="S") / ("X" * 1000)
        
        # تجزئة الـ packet
        frags = fragment(pkt, fragsize=8)
        
        for frag in frags:
            send(frag, verbose=False)
            time.sleep(0.05)
        
        time.sleep(1)
    
    scanner.log_scan_end()


# ======== MAIN ========
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Port Scan Generator')
    parser.add_argument('-t', '--target', default=TARGET_IP, help='Target IP')
    parser.add_argument('-m', '--mode', 
                       choices=['nmap', 'custom', 'all'], 
                       default='all',
                       help='Scan mode')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("COMPREHENSIVE PORT SCAN GENERATOR")
    print("="*60)
    print(f"Target: {args.target}")
    print(f"Mode: {args.mode}")
    print(f"Timeline: {LOG_FILE}")
    print("="*60 + "\n")
    
    print("⚠️  WARNING: Authorized testing only!")
    print("⚠️  Port scanning without permission is illegal!\n")
    
    input("Press ENTER to start scans...")
    
    scanner = PortScanGenerator(args.target)
    
    try:
        if args.mode in ['nmap', 'all']:
            print("\n>>> NMAP-BASED SCANS <<<\n")
            
            # قائمة Nmap scans
            nmap_scans = [
                ("TCP_SYN", "TCP SYN Stealth Scan", ["-sS"]),
                ("TCP_CONNECT", "TCP Connect Scan", ["-sT"]),
                ("UDP", "UDP Scan", ["-sU", "--max-retries", "1"]),
                ("FIN", "FIN Scan", ["-sF"]),
                ("NULL", "NULL Scan", ["-sN"]),
                ("XMAS", "Xmas Scan", ["-sX"]),
                ("ACK", "ACK Scan", ["-sA"]),
                ("STEALTH_SLOW", "Stealth Slow Scan (T1)", ["-sS", "-T1"]),
                ("AGGRESSIVE", "Aggressive Fast Scan (T4)", ["-sS", "-T4"]),
                ("VERSION", "Service Version Detection", ["-sV"]),
                ("OS_DETECTION", "OS Detection", ["-O"]),
                ("SCRIPT_VULN", "Vulnerability Scripts", ["--script", "vuln"]),
            ]
            
            for scan_type, desc, args_list in nmap_scans:
                run_nmap_scan(scanner, scan_type, desc, args_list)
                print("[*] Waiting 5 seconds...\n")
                time.sleep(5)
        
        if args.mode in ['custom', 'all']:
            print("\n>>> CUSTOM SCAPY-BASED SCANS <<<\n")
            
            # قائمة Custom scans
            custom_scans = [
                #tcp_syn_scan_custom,
                tcp_connect_scan_custom,
                udp_scan_custom,
                fin_scan_custom,
                xmas_scan_custom,
                null_scan_custom,
                ack_scan_custom,
                window_scan_custom,
                idle_scan_simulation,
                decoy_scan_custom,
                fragmented_scan_custom,
            ]
            
            for scan_func in custom_scans:
                scan_func(scanner)
                print("[*] Waiting 5 seconds...\n")
                time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n\n[!] Stopped by user")
    
    finally:
        scanner.save_timeline()
        
        print("\n[✓] All scans completed!")
        print(f"[✓] You can now stop tcpdump capture")


if __name__ == "__main__":
    main()
