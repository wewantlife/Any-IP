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

LOCALES = {
    "ru": {
        "subtitle":      "AnyDesk IP Tracker  //  v1.0  //  by scashh_",
        "lang_select":   "  Выберите язык / Choose language\n\n  [ / ] 1   Русский\n  [ / ] 2   English",
        "lang_prompt":   "\n  >> ",
        "welcome_1":     "  Добро пожаловать в AnyDesk IP Tracker.",
        "welcome_2":     "  Узнайте, кто подключается к вашей машине в реальном времени.",
        "press_enter":   "\n  Нажмите Enter для продолжения...",
        "menu_title":    "  ГЛАВНОЕ МЕНЮ",
        "menu_1":        "  [ / ] 1   Сканировать подключения AnyDesk",
        "menu_2":        "  [ / ] 2   Режим непрерывного мониторинга",
        "menu_3":        "  [ / ] 3   О программе",
        "menu_0":        "  [ x ] 0   Выход",
        "menu_prompt":   "\n  >> ",
        "scanning":      "Сканирование активных подключений...",
        "no_conn":       "\n  [!]  Активных подключений AnyDesk не найдено.\n       Убедитесь, что AnyDesk запущен и есть активная сессия.",
        "found":         "\n  [+]  Найдено подключений: ",
        "conn_header":   "ПОДКЛЮЧЕНИЕ",
        "field_ip":      "IP         ",
        "field_port":    "Порт       ",
        "field_country": "Страна     ",
        "field_region":  "Регион     ",
        "field_city":    "Город      ",
        "field_isp":     "Провайдер  ",
        "back":          "  Нажмите Enter для возврата в меню...",
        "monitor_start": "\n  [~]  Режим мониторинга активен.  Нажмите CTRL+C для остановки.",
        "monitor_wait":  "Ожидание подключения AnyDesk...",
        "monitor_new":   "  [+]  Обнаружено новое подключение!",
        "monitor_stop":  "\n\n  [!]  Мониторинг остановлен.",
        "about_title":   "  О ПРОГРАММЕ",
        "about_body": (
            "  AnyDesk IP Tracker отслеживает активные сессии AnyDesk\n"
            "  и получает геолокационные данные подключённых IP-адресов.\n\n"
            "  Возможности:\n"
            "    [ + ]  Сканирование процессов в реальном времени (WMI)\n"
            "    [ + ]  Геолокация через ip-api.com\n"
            "    [ + ]  Фильтрация локальных и порт-80 подключений\n"
            "    [ + ]  Одиночное сканирование и режим мониторинга\n\n"
            "  Требования:\n"
            "    [ * ]  Windows OS\n"
            "    [ * ]  wmi, psutil, requests\n\n"
            "  Автор  :  scashh_"
        ),
        "goodbye": "\n  До свидания.",
        "invalid":  "\n  [!]  Неверная команда.",
        "unknown":  "Неизвестно",
    },
    "en": {
        "subtitle":      "AnyDesk IP Tracker  //  v1.0  //  by scashh_",
        "lang_select":   "  Выберите язык / Choose language\n\n  [ / ] 1   Русский\n  [ / ] 2   English",
        "lang_prompt":   "\n  >> ",
        "welcome_1":     "  Welcome to AnyDesk IP Tracker.",
        "welcome_2":     "  Find out who is connecting to your machine in real time.",
        "press_enter":   "\n  Press Enter to continue...",
        "menu_title":    "  MAIN MENU",
        "menu_1":        "  [ / ] 1   Scan AnyDesk Connections",
        "menu_2":        "  [ / ] 2   Continuous Monitor Mode",
        "menu_3":        "  [ / ] 3   About",
        "menu_0":        "  [ x ] 0   Exit",
        "menu_prompt":   "\n  >> ",
        "scanning":      "Scanning for active connections...",
        "no_conn":       "\n  [!]  No active AnyDesk connections found.\n       Make sure AnyDesk is running with an active session.",
        "found":         "\n  [+]  Connections found: ",
        "conn_header":   "CONNECTION",
        "field_ip":      "IP         ",
        "field_port":    "Port       ",
        "field_country": "Country    ",
        "field_region":  "Region     ",
        "field_city":    "City       ",
        "field_isp":     "ISP        ",
        "back":          "  Press Enter to return to menu...",
        "monitor_start": "\n  [~]  Monitor Mode active.  Press CTRL+C to stop.",
        "monitor_wait":  "Waiting for AnyDesk connection...",
        "monitor_new":   "  [+]  New connection detected!",
        "monitor_stop":  "\n\n  [!]  Monitor stopped.",
        "about_title":   "  ABOUT",
        "about_body": (
            "  AnyDesk IP Tracker monitors active AnyDesk sessions\n"
            "  and retrieves geolocation data on connected IPs.\n\n"
            "  Features:\n"
            "    [ + ]  Real-time process scanning via WMI\n"
            "    [ + ]  Geolocation via ip-api.com\n"
            "    [ + ]  Filters local and port-80 connections\n"
            "    [ + ]  Single scan & continuous monitor modes\n\n"
            "  Requirements:\n"
            "    [ * ]  Windows OS\n"
            "    [ * ]  wmi, psutil, requests\n\n"
            "  Author  :  scashh_"
        ),
        "goodbye": "\n  Goodbye.",
        "invalid":  "\n  [!]  Invalid option.",
        "unknown":  "Unknown",
    },
}

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

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def choose_language() -> dict:
    clear()
    print(BANNER)
    print(DLINE)
    print(LOCALES['ru']['lang_select'])
    print(f"\n{LINE}")
    choice = input(LOCALES['ru']['lang_prompt']).strip()
    return LOCALES['en'] if choice == '2' else LOCALES['ru']

def print_header(L: dict):
    clear()
    print(BANNER)
    print(f"  {L['subtitle']}")
    print(DLINE)

def print_menu(L: dict):
    print(f"\n{L['menu_title']}\n")
    print(L['menu_1'])
    print(L['menu_2'])
    print(L['menu_3'])
    print(L['menu_0'])
    print(f"\n{LINE}")
    print(L['menu_prompt'], end='')

def print_result_block(infos: dict, idx: int, L: dict):
    print(f"""
  ┌── {L['conn_header']} #{idx} {'─' * 33}
  │
  │   {L['field_ip']}  :  {infos['IP']}
  │   {L['field_port']}  :  {infos['Port']}
  │   {L['field_country']}  :  {infos['Country']}
  │   {L['field_region']}  :  {infos['Region']}
  │   {L['field_city']}  :  {infos['City']}
  │   {L['field_isp']}  :  {infos['ISP']}
  │
  └{'─' * 48}""")

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

def get_ip_info(ip: str, port: int, unknown: str) -> dict:
    try:
        j = requests.get(f'http://ip-api.com/json/{ip}', timeout=5).json()
    except Exception:
        j = {}
    return dict(
        IP      = ip,
        Port    = port,
        Country = j.get('country',    unknown),
        Region  = j.get('regionName', unknown),
        City    = j.get('city',       unknown),
        ISP     = j.get('isp',        unknown),
    )

def scan_once(L: dict):
    frames = ['|', '/', '-', '\\']
    stop   = threading.Event()

    def spin():
        i = 0
        while not stop.is_set():
            print(f"\r  [{frames[i % 4]}]  {L['scanning']}", end='', flush=True)
            time.sleep(0.1)
            i += 1

    t = threading.Thread(target=spin, daemon=True)
    t.start()
    connections = get_ips()
    stop.set()
    t.join()
    print(f"\r  {' ' * 60}", end='\r')

    if not connections:
        print(L['no_conn'])
    else:
        print(f"{L['found']}{len(connections)}\n")
        for i, conn in enumerate(connections, 1):
            print_result_block(get_ip_info(conn['ip'], conn['port'], L['unknown']), i, L)

    print()
    input(L['back'])

def monitor_mode(L: dict):
    print(L['monitor_start'])
    print(f"\n{LINE}")

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
                        print(f"\r  {' ' * 60}", end='\r')
                        print(L['monitor_new'])
                        print_result_block(get_ip_info(conn['ip'], conn['port'], L['unknown']), len(seen), L)
            else:
                print(f"\r  [{frames[i % 4]}]  {L['monitor_wait']}", end='', flush=True)
            i += 1
            time.sleep(0.3)
    except KeyboardInterrupt:
        print(L['monitor_stop'])
        print()
        input(L['back'])

def about(L: dict):
    print_header(L)
    print(f"\n{L['about_title']}\n{LINE}\n")
    print(L['about_body'])
    print(f"\n{LINE}")
    input(f"\n{L['back']}")

def try_exit():
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

def greeting(L: dict):
    clear()
    print(BANNER)
    print(f"  {L['subtitle']}")
    print(DLINE)
    print()
    time.sleep(0.2)
    print(L['welcome_1'])
    time.sleep(0.3)
    print(L['welcome_2'])
    time.sleep(0.3)
    print(f"\n{LINE}")
    input(L['press_enter'])

def main():
    L = choose_language()
    greeting(L)

    while True:
        print_header(L)
        print_menu(L)
        choice = input().strip()

        if choice == '1':
            print_header(L)
            scan_once(L)
        elif choice == '2':
            print_header(L)
            monitor_mode(L)
        elif choice == '3':
            about(L)
        elif choice == '0':
            clear()
            print(BANNER)
            print(L['goodbye'])
            print()
            time.sleep(0.6)
            try_exit()
        else:
            print(L['invalid'])
            time.sleep(0.8)

if __name__ == '__main__':
    main()
