import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import subprocess
import platform
import time
import winreg
import sys
import ctypes
import atexit

# --- IMPORTANT: External Libraries ---
# Run 'pip install keyboard pyautogui' before executing this script.
try:
    import keyboard
    HAS_KEYBOARD_LIB = True
except ImportError:
    HAS_KEYBOARD_LIB = False

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

# --- UI Color Palette (Premium Dark Mode) ---
BG_MAIN = "#020617"         
BG_CARD = "#0F172A"         
ACCENT_BLUE = "#38BDF8"     
ACCENT_INDIGO = "#6366F1"   
TEXT_PRIMARY = "#F8FAFC"    
TEXT_SECONDARY = "#94A3B8"  
TEXT_ERROR = "#F87171"      

class SetupWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gento Secure - Initial Setup")
        
        # Center the setup window on the screen
        window_width = 450
        window_height = 480
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        self.root.configure(bg=BG_CARD)
        self.root.resizable(False, False)

        self.target_coords = None # Will store custom (x, y)
        self.overlay = None

        # Fonts
        font_family = "Pretendard" if "Pretendard" in tkfont.families() else "맑은 고딕"
        self.title_font = tkfont.Font(family=font_family, size=24, weight="bold")
        self.label_font = tkfont.Font(family=font_family, size=12, weight="bold")
        self.input_font = tkfont.Font(family="Arial", size=14)

        self.setup_ui()

    def setup_ui(self):
        # Title
        tk.Label(self.root, text="LOCK SETUP", font=self.title_font, fg=ACCENT_BLUE, bg=BG_CARD).pack(pady=(30, 20))

        # Password Input
        tk.Label(self.root, text="Set Password:", font=self.label_font, fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", padx=50)
        self.pwd_entry = tk.Entry(self.root, font=self.input_font, bg="#1E293B", fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, relief="flat")
        self.pwd_entry.pack(fill="x", padx=50, pady=(5, 20), ipady=8)
        self.pwd_entry.insert(0, "1234") # Default password

        # Timer Input (Hours and Minutes)
        tk.Label(self.root, text="Auto-Terminate After:", font=self.label_font, fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", padx=50)
        
        time_frame = tk.Frame(self.root, bg=BG_CARD)
        time_frame.pack(fill="x", padx=50, pady=(5, 30))

        # Hours
        self.hour_entry = tk.Entry(time_frame, width=5, font=self.input_font, bg="#1E293B", fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, relief="flat", justify="center")
        self.hour_entry.pack(side="left", ipady=8)
        self.hour_entry.insert(0, "0")
        tk.Label(time_frame, text="Hours", font=self.label_font, fg=TEXT_SECONDARY, bg=BG_CARD).pack(side="left", padx=(5, 20))

        # Minutes
        self.minute_entry = tk.Entry(time_frame, width=5, font=self.input_font, bg="#1E293B", fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, relief="flat", justify="center")
        self.minute_entry.pack(side="left", ipady=8)
        self.minute_entry.insert(0, "30") # Default to 30 mins
        tk.Label(time_frame, text="Minutes", font=self.label_font, fg=TEXT_SECONDARY, bg=BG_CARD).pack(side="left", padx=(5, 0))

        # --- NEW: Coordinate Selection ---
        tk.Label(self.root, text="Click Target Coordinates:", font=self.label_font, fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", padx=50, pady=(10, 5))
        coord_frame = tk.Frame(self.root, bg=BG_CARD)
        coord_frame.pack(fill="x", padx=50, pady=(0, 20))
        
        self.coord_label = tk.Label(coord_frame, text="Default (Top-Right)", font=self.input_font, fg=TEXT_SECONDARY, bg=BG_CARD)
        self.coord_label.pack(side="left")
        
        coord_btn = ttk.Button(coord_frame, text="Set Coordinates", command=self.start_coordinate_selection)
        coord_btn.pack(side="right")

        # Start Button
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Start.TButton", font=self.label_font, foreground="white", background=ACCENT_INDIGO, borderwidth=0, padding=10)
        style.map("Start.TButton", background=[('active', ACCENT_BLUE)])

        self.start_btn = ttk.Button(self.root, text="START SECURE LOCK", style="Start.TButton", command=self.start_lock)
        self.start_btn.pack(fill="x", padx=50, pady=10)

    def start_coordinate_selection(self):
        if self.overlay:
            return
        
        # Create a fullscreen transparent overlay to catch the mouse click
        self.overlay = tk.Toplevel(self.root)
        self.overlay.attributes('-alpha', 0.6) # 60% opacity
        self.overlay.configure(bg='black')
        self.overlay.attributes('-topmost', True)
        self.overlay.overrideredirect(True)
        self.overlay.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.overlay.config(cursor="crosshair") # Change mouse cursor
        
        msg = tk.Label(self.overlay, text="화면의 원하는 위치를 클릭하세요.\n(Click anywhere to set coordinates)\n[Press ESC to cancel]", 
                       font=self.title_font, fg=ACCENT_BLUE, bg="black")
        msg.place(relx=0.5, rely=0.5, anchor="center")
        
        # Bind mouse click and ESC key
        self.overlay.bind("<Button-1>", self.on_coordinate_selected)
        self.overlay.bind("<Escape>", lambda e: self.close_overlay())

    def on_coordinate_selected(self, event):
        # Capture screen coordinates
        self.target_coords = (event.x_root, event.y_root)
        self.coord_label.config(text=f"X: {event.x_root}, Y: {event.y_root}", fg=ACCENT_BLUE)
        self.close_overlay()
        
    def close_overlay(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None

    def start_lock(self):
        password = self.pwd_entry.get()
        
        try:
            hours = int(self.hour_entry.get() or 0)
            minutes = int(self.minute_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for hours and minutes.")
            return

        total_seconds = (hours * 3600) + (minutes * 60)
        
        if total_seconds <= 0:
            messagebox.showerror("Invalid Input", "Time must be greater than 0.")
            return

        # Close the setup window
        self.root.destroy()

        # Use custom coordinates or default to top-right
        if self.target_coords:
            target_x, target_y = self.target_coords
        else:
            if HAS_PYAUTOGUI:
                screen_w, screen_h = pyautogui.size()
            else:
                screen_w, screen_h = 1920, 1080 # Fallback
            target_x = screen_w - 50
            target_y = 60

        # Launch the main lock screen
        app = GentoSecureLock(password=password, timeout_sec=total_seconds, click_coords=(target_x, target_y))
        app.run()

    def run(self):
        self.root.mainloop()


class GentoSecureLock:
    def __init__(self, password="1234", timeout_sec=30, click_coords=(100, 100)):
        """
        :param password: 잠금 해제 비밀번호
        :param timeout_sec: 자동 종료까지의 시간 (초)
        :param click_coords: 자동 종료 전 클릭할 화면 좌표 (x, y)
        """
        self.root = tk.Tk()
        self.target_password = password
        self.timeout_ms = timeout_sec * 1000
        self.click_coords = click_coords
        self.start_time = time.time()
        
        self.root.title("Gento Secure System")
        
        # 1. 시스템 보안 설정
        self.enforce_security()
        atexit.register(self.restore_security)
        
        # 2. 강력한 전체화면 및 최상단 설정
        self.root.overrideredirect(True)
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.root.attributes('-topmost', True)
        self.root.configure(bg=BG_MAIN)
        
        self.init_fonts()
        self.setup_styles()
        self.setup_layout()
        
        # 3. 보안 이벤트 및 입력 제한 설정
        self.bind_security_events()
        self.maintain_focus()
        
        # 4. 자동 종료 타이머 설정
        self.root.after(self.timeout_ms, self.auto_terminate)
        
        # 5. 실시간 업데이트 시작
        self.update_ui_loop()

    def enforce_security(self):
        """시스템 명령어를 통한 종료 시그널 가로채기 및 로우레벨 훅 설정"""
        if platform.system() == "Windows":
            try:
                subprocess.run(["shutdown", "/a"], capture_output=True)
            except: pass
            
            # --- 본체 전원 버튼 무력화 (제어판 전원 옵션 강제 수정) ---
            try:
                # 정책(Policy) 레지스트리를 통한 강제 제어 (0 = 아무것도 안 함)
                power_key_path = r"SOFTWARE\Policies\Microsoft\Power\PowerSettings\7648EFA3-DD9C-4E3E-B566-50F929386280"
                power_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, power_key_path)
                winreg.SetValueEx(power_key, "ACSettingIndex", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(power_key, "DCSettingIndex", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(power_key)
                
                # 즉시 적용을 위해 powercfg 새로고침
                CREATE_NO_WINDOW = 0x08000000
                subprocess.run(["powercfg", "-SetActive", "SCHEME_CURRENT"], capture_output=True, creationflags=CREATE_NO_WINDOW)
            except Exception as e:
                print(f"Power Button Disable Failed: {e}")
            
            # --- Ctrl+Alt+Delete 옵션 비활성화 ---
            try:
                # System 정책 (작업관리자, 잠금, 암호변경 비활성화)
                sys_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
                winreg.SetValueEx(sys_key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(sys_key, "DisableLockWorkstation", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(sys_key, "DisableChangePassword", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(sys_key)
                
                # Explorer 정책 (로그아웃 비활성화)
                exp_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer")
                winreg.SetValueEx(exp_key, "NoLogoff", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(exp_key)
                
                # 로컬 머신 정책 (사용자 전환 비활성화 - 관리자 권한 필요)
                try:
                    hklm_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System")
                    winreg.SetValueEx(hklm_key, "HideFastUserSwitching", 0, winreg.REG_DWORD, 1)
                    winreg.CloseKey(hklm_key)
                except: pass
            except Exception as e:
                print(f"Registry Edit Failed: {e}")

        if HAS_KEYBOARD_LIB:
            # 커널 수준에서 모든 키를 가로채고 숫자/제어키만 허용
            keyboard.hook(self.os_level_input_filter, suppress=True)

    def restore_security(self):
        """작업 관리자 비활성화 등 보안 설정 원상복구"""
        if platform.system() == "Windows":
            try:
                sys_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
                winreg.SetValueEx(sys_key, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(sys_key, "DisableLockWorkstation", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(sys_key, "DisableChangePassword", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(sys_key)
                
                exp_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer")
                winreg.SetValueEx(exp_key, "NoLogoff", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(exp_key)
                
                try:
                    hklm_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System")
                    winreg.SetValueEx(hklm_key, "HideFastUserSwitching", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(hklm_key)
                except: pass
                
                # --- 본체 전원 버튼 원상복구 ---
                try:
                    # 3 = 시스템 종료
                    power_key_path = r"SOFTWARE\Policies\Microsoft\Power\PowerSettings\7648EFA3-DD9C-4E3E-B566-50F929386280"
                    power_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, power_key_path)
                    winreg.SetValueEx(power_key, "ACSettingIndex", 0, winreg.REG_DWORD, 3)
                    winreg.SetValueEx(power_key, "DCSettingIndex", 0, winreg.REG_DWORD, 3)
                    winreg.CloseKey(power_key)
                    
                    CREATE_NO_WINDOW = 0x08000000
                    subprocess.run(["powercfg", "-SetActive", "SCHEME_CURRENT"], capture_output=True, creationflags=CREATE_NO_WINDOW)
                except Exception as e:
                    pass
                
            except Exception as e:
                print(f"Registry Restore Failed: {e}")

    def os_level_input_filter(self, event):
        """숫자 및 백스페이스만 허용하는 OS 레벨 필터"""
        allowed = ['0','1','2','3','4','5','6','7','8','9',
                   'kp_0','kp_1','kp_2','kp_3','kp_4','kp_5','kp_6','kp_7','kp_8','kp_9',
                   'backspace', 'delete', 'enter']
        
        if event.name in allowed:
            return True
        return False

    def init_fonts(self):
        font_family = "Pretendard" if "Pretendard" in tkfont.families() else "맑은 고딕"
        self.title_font = tkfont.Font(family=font_family, size=65, weight="bold")
        self.clock_font = tkfont.Font(family=font_family, size=28)
        self.label_font = tkfont.Font(family=font_family, size=14, weight="bold")
        self.input_font = tkfont.Font(family="Arial", size=22)
        self.status_font = tkfont.Font(family=font_family, size=11)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Premium.TButton", font=self.label_font, foreground="white",
                        background=ACCENT_INDIGO, borderwidth=0, padding=(20, 15))
        style.map("Premium.TButton", background=[('active', ACCENT_BLUE)])

    def setup_layout(self):
        # [RIGHT AREA] 인증 사이드바
        self.side_panel = tk.Frame(self.root, bg=BG_CARD, width=480)
        self.side_panel.pack(side="right", fill="y")
        self.side_panel.pack_propagate(False)
        tk.Frame(self.side_panel, bg=ACCENT_INDIGO, height=6).pack(fill="x")

        # [LEFT AREA] 메인 정보 표시 캔버스
        self.canvas = tk.Canvas(self.root, bg=BG_MAIN, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.info_frame = tk.Frame(self.canvas, bg=BG_MAIN)
        self.info_frame.place(relx=0.08, rely=0.45, anchor="w")

        self.time_label = tk.Label(self.info_frame, text="", font=self.clock_font, fg=ACCENT_BLUE, bg=BG_MAIN)
        self.time_label.pack(anchor="w")

        tk.Label(self.info_frame, text="SYSTEM", font=self.title_font, fg=TEXT_PRIMARY, bg=BG_MAIN).pack(anchor="w")
        tk.Label(self.info_frame, text="LOCKED.", font=self.title_font, fg=ACCENT_INDIGO, bg=BG_MAIN).pack(anchor="w")
        
        # 자동 종료 안내 문구 추가
        self.timer_label = tk.Label(self.info_frame, text="", font=("맑은 고딕", 15, "bold"), fg=ACCENT_BLUE, bg=BG_MAIN)
        self.timer_label.pack(anchor="w", pady=(20, 0))

        desc = "보안을 위해 장치가 잠겼습니다.\n지정된 시간 이후 자동으로 해제 및 클릭이 수행됩니다."
        tk.Label(self.info_frame, text=desc, font=("맑은 고딕", 13), fg=TEXT_SECONDARY, bg=BG_MAIN, justify="left").pack(anchor="w", pady=(20, 0))

        # 인증 컨테이너
        self.auth_container = tk.Frame(self.side_panel, bg=BG_CARD)
        self.auth_container.pack(expand=True, fill="x", padx=60)

        tk.Label(self.auth_container, text="ADMINISTRATOR LOGIN", font=self.label_font, fg=ACCENT_BLUE, bg=BG_CARD).pack(anchor="w")
        tk.Label(self.auth_container, text="Auto-termination Sequence Armed", font=self.status_font, fg=TEXT_SECONDARY, bg=BG_CARD).pack(anchor="w", pady=(5, 50))

        tk.Label(self.auth_container, text="PASSWORD", font=self.label_font, fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", pady=(0, 15))
        
        self.entry_frame = tk.Frame(self.auth_container, bg="#1E293B", padx=2, pady=2)
        self.entry_frame.pack(fill="x")
        
        self.password_entry = tk.Entry(self.entry_frame, show="●", font=self.input_font, 
                                      bg="#0F172A", fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
                                      relief="flat", borderwidth=12)
        self.password_entry.pack(fill="x")
        
        self.error_label = tk.Label(self.auth_container, text="비밀번호가 틀렸습니다.", 
                                    font=self.status_font, fg=TEXT_ERROR, bg=BG_CARD)
        
        self.unlock_btn = ttk.Button(self.auth_container, text="UNLOCK", style="Premium.TButton", command=self.validate_password)
        self.unlock_btn.pack(fill="x", pady=(50, 0))

        footer = tk.Frame(self.side_panel, bg=BG_CARD)
        footer.pack(side="bottom", fill="x", pady=40)
        tk.Label(footer, text=f"CLICK TARGET: {self.click_coords}", font=("Arial", 9, "bold"), fg=TEXT_SECONDARY, bg=BG_CARD).pack()

    def bind_security_events(self):
        self.root.grab_set()
        self.root.bind_all("<Tab>", lambda e: "break")
        self.password_entry.bind("<Return>", lambda e: self.validate_password())
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

    def maintain_focus(self):
        if self.root.focus_get() != self.password_entry:
            self.password_entry.focus_force()
        self.root.lift()
        self.root.attributes('-topmost', True)
        if self.root.state() == 'iconic': 
            self.root.deiconify()
        self.root.after(10, self.maintain_focus)

    def update_ui_loop(self):
        """시간 및 남은 타이머 업데이트"""
        now = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=now)
        
        # 남은 시간 계산
        elapsed = time.time() - self.start_time
        remaining = max(0, int((self.timeout_ms / 1000) - elapsed))
        
        # Format remaining seconds into HH:MM:SS
        m, s = divmod(remaining, 60)
        h, m = divmod(m, 60)
        time_string = f"{h:02d}:{m:02d}:{s:02d}"
        
        self.timer_label.config(text=f"자동 해제까지 남은 시간: {time_string}")
        
        self.root.after(1000, self.update_ui_loop)

    def auto_terminate(self):
        """특정 시간 후 클릭을 수행하고 잠금 화면 종료"""
        # 1. 키보드 훅 해제 (클릭 및 시스템 복구를 위해 우선 수행)
        if HAS_KEYBOARD_LIB:
            keyboard.unhook_all()
        
        self.restore_security()
            
        # 2. 지정된 좌표 클릭
        if HAS_PYAUTOGUI:
            # 잠금 화면이 꺼지기 직전 혹은 직후에 수행 (여기서는 직후로 처리하기 위해 윈도우 제거 후 실행)
            x, y = self.click_coords
            # 윈도우를 먼저 내리고 클릭 수행
            self.root.withdraw() 
            pyautogui.click(x, y)
            
        # 3. 프로그램 종료
        self.root.destroy()

    def validate_password(self):
        if self.password_entry.get() == self.target_password:
            if HAS_KEYBOARD_LIB:
                keyboard.unhook_all()
            self.restore_security()
            self.root.destroy()
        else:
            self.shake_ui()
            self.error_label.pack(pady=(15, 0))
            self.password_entry.delete(0, 'end')

    def shake_ui(self):
        orig_x = self.auth_container.winfo_x()
        def move_l(): self.auth_container.place(x=orig_x-10)
        def move_r(): self.auth_container.place(x=orig_x+10)
        def move_c(): self.auth_container.place(x=orig_x)
        for i in range(3):
            self.root.after(i*100, move_l)
            self.root.after(i*100+50, move_r)
        self.root.after(300, move_c)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # --- 관리자 권한 자동 취득 ---
    if platform.system() == "Windows":
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except:
            is_admin = False
            
        if not is_admin:
            # 관리자 권한이 없으면 UAC 창을 띄우고 재실행 (exe와 py 스크립트 모두 대응)
            if sys.argv[0].endswith('.py'):
                params = " ".join([f'"{arg}"' for arg in sys.argv])
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            else:
                params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            sys.exit(0)

    # Start the setup window first
    setup_app = SetupWindow()
    setup_app.run()