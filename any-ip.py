import os
import sys
import time
import threading

try:
    import wmi
    import psutil
    import requests
except ImportError:
    os.system("pip install requests psutil wmi -q")
    import wmi
    import psutil
    import requests

# ─────────────────────────────────────────────────────────────────────────────

BANNER = """
  ░█████╗░███╗░░██╗██╗░░░██╗        ██╗██████╗░
  ██╔══██╗████╗░██║╚██╗░██╔╝        ██║██╔══██╗
  ███████║██╔██╗██║░╚████╔╝░ █████╗ ██║██████╔╝
  ██╔══██║██║╚████║░░╚██╔╝░░ ╚════╝ ██║██╔═══╝░
  ██║░░██║██║░╚███║░░░██║░░░        ██║██║░░░░░
  ╚═╝░░╚═╝╚═╝░░╚══╝░░░╚═╝░░░        ╚═╝╚═╝░░░░░
"""

LINE  = "  " + "─" * 52
DLINE = "  " + "═" * 52

# ─────────────────────────────────────────────────────────────────────────────

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear()
    print(BANNER)
    print(f"  AnyDesk Connection IP Tracker  //  v1.0")
    print(DLINE)

def print_menu():
    print(f"""
  MAIN MENU

  [ / ] 1   Scan AnyDesk Connections
  [ / ] 2   Continuous Monitor Mode
  [ / ] 3   About
  [ x ] 0   Exit

{LINE}

  >> """, end='')

def print_result_block(infos: dict, idx: int):
    print(f"""
  ┌── CONNECTION #{idx} {'─' * 34}
  │
  │   IP          :  {infos['IP']}
  │   Port        :  {infos['Port']}
  │   Country     :  {infos['Country']}
  │   Region      :  {infos['Region']}
  │   City        :  {infos['City']}
  │   ISP         :  {infos['ISP']}
  │
  └{'─' * 48}""")

# ─────────────────────────────────────────────────────────────────────────────

def get_ips() -> list:
    wmi_obj = wmi.WMI()
    connections = []
    for process in wmi_obj.Win32_Process():
        try:
            if 'anydesk' in process.Name.lower():
                for conn in psutil.Process(process.ProcessId).connections():
                    if conn.status in ('SYN_SENT', 'ESTABLISHED'):
                        ip   = conn.raddr.ip
                        port = conn.raddr.port
                        if port != 80 and not ip.startswith('192.168.'):
                            if not any(c['ip'] == ip for c in connections):
                                connections.append({'ip': ip, 'port': port})
        except (psutil.NoSuchProcess, AttributeError):
            pass
    return connections

def get_ip_info(ip: str, port: int) -> dict:
    try:
        j = requests.get(f'http://ip-api.com/json/{ip}', timeout=5).json()
    except Exception:
        j = {}
    return dict(
        IP      = ip,
        Port    = port,
        Country = j.get('country',    'Unknown'),
        Region  = j.get('regionName', 'Unknown'),
        City    = j.get('city',       'Unknown'),
        ISP     = j.get('isp',        'Unknown')
    )

# ─────────────────────────────────────────────────────────────────────────────

def scan_once():
    frames = ['|', '/', '-', '\\']
    stop   = threading.Event()

    def spin():
        i = 0
        while not stop.is_set():
            print(f"\r  [{frames[i % 4]}]  Scanning for active connections...", end='', flush=True)
            time.sleep(0.1)
            i += 1

    t = threading.Thread(target=spin, daemon=True)
    t.start()
    connections = get_ips()
    stop.set()
    t.join()
    print(f"\r  {' ' * 55}", end='\r')

    if not connections:
        print(f"\n  [!]  No active AnyDesk connections found.")
        print(f"       Make sure AnyDesk is running with an active session.\n")
    else:
        print(f"\n  [+]  Found {len(connections)} connection(s).\n")
        for i, conn in enumerate(connections, 1):
            print_result_block(get_ip_info(conn['ip'], conn['port']), i)

    print()
    input(f"  Press Enter to return to menu...")

def monitor_mode():
    print(f"\n  [~]  Monitor Mode active.  Press CTRL+C to stop.\n")
    print(LINE)

    frames = ['|', '/', '-', '\\']
    seen   = set()
    i      = 0

    try:
        while True:
            connections = get_ips()
            if connections:
                for conn in connections:
                    key = (conn['ip'], conn['port'])
                    if key not in seen:
                        seen.add(key)
                        print(f"\r  {' ' * 55}", end='\r')
                        print(f"  [+]  New connection detected!")
                        print_result_block(get_ip_info(conn['ip'], conn['port']), len(seen))
            else:
                print(f"\r  [{frames[i % 4]}]  Waiting for AnyDesk connection...", end='', flush=True)
            i += 1
            time.sleep(0.3)
    except KeyboardInterrupt:
        print(f"\n\n  [!]  Monitor stopped.\n")
        input(f"  Press Enter to return to menu...")

def about():
    print_header()
    print(f"""
  ABOUT
{LINE}

  AnyDesk IP Tracker monitors active AnyDesk sessions
  and retrieves geolocation data on connected IPs.

  Features:
    [ + ]  Real-time process scanning via WMI
    [ + ]  Geolocation via ip-api.com
    [ + ]  Filters local and port-80 connections
    [ + ]  Single scan & continuous monitor modes

  Requirements:
    [ * ]  Windows OS
    [ * ]  wmi, psutil, requests

{LINE}""")
    input(f"\n  Press Enter to return to menu...")

# ─────────────────────────────────────────────────────────────────────────────

def greeting():
    clear()
    print(BANNER)
    print(f"  AnyDesk Connection IP Tracker  //  v1.0")
    print(DLINE)

    lines = [
        "",
        "  Welcome to AnyDesk IP Tracker.",
        "  Identify who connects to your machine in real time.",
        "",
    ]
    for line in lines:
        print(line)
        time.sleep(0.3)

    print(LINE)
    input(f"\n  Press Enter to continue...")

def try_exit():
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

def main():
    greeting()
    while True:
        print_header()
        print_menu()
        choice = input().strip()

        if choice == '1':
            print_header()
            scan_once()
        elif choice == '2':
            print_header()
            monitor_mode()
        elif choice == '3':
            about()
        elif choice == '0':
            clear()
            print(BANNER)
            print(f"\n  Goodbye.\n")
            time.sleep(0.6)
            try_exit()
        else:
            print(f"\n  [!]  Invalid option.\n")
            time.sleep(0.8)

if __name__ == '__main__':
    main()
