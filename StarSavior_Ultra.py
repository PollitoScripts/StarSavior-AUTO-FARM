import tkinter as tk
from tkinter import scrolledtext
import threading, time, os, ctypes, pyautogui, pydirectinput

# --- CONFIGURACIÓN DE INTERFAZ ---
RECOMPENSA_POR_STAGE = 1  
COLOR_MAIN_BG = "#0b0e14"   
COLOR_CARD_OFF = "#161b22"  
COLOR_CARD_ON = "#1f2937"   
COLOR_ACCENT = "#00f2ff"    
COLOR_TEXT_OFF = "#57606a"  
COLOR_TEXT_ON = "#ffffff"   
COLOR_LOG_BG = "#080a0f"
COLOR_GOLD = "#f9e2af"
COLOR_WATERMARK = "#30363d" 

# Región de búsqueda (Top 75% para evitar la cruz inferior que borra selección)
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
REGION_SUPERIOR = (0, 0, SCREEN_WIDTH, int(SCREEN_HEIGHT * 0.75))

def ocultar_consola():
    try:
        hWnd = ctypes.WinDLL('kernel32').GetConsoleWindow()
        if hWnd: ctypes.WinDLL('user32').ShowWindow(hWnd, 0)
    except: pass

ocultar_consola()

class SkipperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StarSavior Ultra - PollitoScripts")
        self.root.geometry("400x880") 
        self.root.configure(bg=COLOR_MAIN_BG)
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        # --- RECURSOS (Asegúrate de tener estas imágenes en la misma carpeta) ---
        self.img_next = "next_stage.png"
        self.img_move = "Move.png"
        self.img_confirm = "Confirm.png"
        self.img_skip = "Skip_Text.png"
        self.img_reward = "reward.png"
        self.img_enter = "Enter.png"
        self.img_begin = "Begin_Battle.png"
        self.img_cruz = "Cruz.png"
        self.img_levelup = "LevelUp.png" 
        self.img_account_levelup = "AccLevelUp.png" 
        self.img_saltar_journey = "SaltarJourney.png"

        self.total_clicks = 0
        self.start_time = time.time()
        self.loot_estimado = 0
        self.vars = {"next": {"active": False}, "abyss": {"active": False}, "skip": {"active": False}}

        self.setup_ui()
        self.actualizar_dashboard_loop()
        self.log(">>> PollitoScripts: Sistema cargado correctamente.")

    def log(self, mensaje):
        hora = time.strftime("%H:%M:%S")
        self.txt_log.config(state='normal')
        self.txt_log.insert(tk.END, f"[{hora}] {mensaje}\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state='disabled')

    def setup_ui(self):
        tk.Label(self.root, text="STAR SAVIOR", font=("Orbitron", 22, "bold"), bg=COLOR_MAIN_BG, fg=COLOR_ACCENT).pack(pady=(15, 0))
        
        dash_frame = tk.Frame(self.root, bg=COLOR_MAIN_BG)
        dash_frame.pack(fill="x", padx=40, pady=10)
        self.lbl_timer = tk.Label(dash_frame, text="TIEMPO: 00:00:00", font=("Consolas", 10), bg=COLOR_MAIN_BG, fg=COLOR_TEXT_ON)
        self.lbl_timer.pack(side="left")
        self.lbl_apm = tk.Label(dash_frame, text="APM: 0.0", font=("Consolas", 10), bg=COLOR_MAIN_BG, fg=COLOR_ACCENT)
        self.lbl_apm.pack(side="right")

        self.f_stats = tk.Frame(self.root, bg=COLOR_CARD_OFF, padx=20, pady=10, highlightthickness=1, highlightbackground="#30363d")
        self.f_stats.pack(fill="x", padx=40, pady=5)
        self.lbl_num = tk.Label(self.f_stats, text="000", font=("Consolas", 35, "bold"), bg=COLOR_CARD_OFF, fg=COLOR_ACCENT)
        self.lbl_num.pack()
        self.lbl_loot = tk.Label(self.f_stats, text="NIVELES PASADOS: 0", font=("Segoe UI", 8, "bold"), bg=COLOR_CARD_OFF, fg=COLOR_GOLD)
        self.lbl_loot.pack()

        self.crear_card("FARM NIVELES", "Begin, Next & Dual LevelUp", self.toggle_next)
        self.crear_card("ABYSS TOWER", "Auto-TAB (Solo Abyss) + LevelUp", self.toggle_abyss)
        self.crear_card("AUTO LOOT", "Skip, Journey, Cruz & LevelUp", self.toggle_skip)

        tk.Label(self.root, text="LOG DE ACTIVIDAD", font=("Segoe UI", 7, "bold"), bg=COLOR_MAIN_BG, fg="#444d56").pack(pady=(10, 0), padx=45, anchor="w")
        self.txt_log = scrolledtext.ScrolledText(self.root, height=15, font=("Consolas", 8), bg=COLOR_LOG_BG, fg="#8b949e", bd=0, highlightthickness=1, highlightbackground="#1b1f23", state='disabled')
        self.txt_log.pack(fill="x", padx=40, pady=5)

        tk.Button(self.root, text="REINICIAR SESIÓN", command=self.reset_sesion, font=("Segoe UI", 8, "bold"), bg=COLOR_MAIN_BG, fg="#f85149", bd=1, relief="flat", highlightthickness=1, cursor="hand2").pack(pady=10)

        watermark_frame = tk.Frame(self.root, bg=COLOR_MAIN_BG)
        watermark_frame.pack(side="bottom", fill="x", pady=10)
        tk.Label(watermark_frame, text="PollitoScripts ak Pollito420", font=("Consolas", 9, "italic"), bg=COLOR_MAIN_BG, fg="#2a2e35").pack()

    def actualizar_dashboard_loop(self):
        def update():
            while True:
                seg_totales = int(time.time() - self.start_time)
                horas, rem = divmod(seg_totales, 3600)
                mins, segs = divmod(rem, 60)
                mins_totales = seg_totales / 60
                apm = self.total_clicks / mins_totales if mins_totales > 0 else 0
                try:
                    self.lbl_timer.config(text=f"TIEMPO: {horas:02d}:{mins:02d}:{segs:02d}")
                    self.lbl_apm.config(text=f"APM: {apm:.1f}")
                except: break
                time.sleep(1)
        threading.Thread(target=update, daemon=True).start()

    def crear_card(self, titulo, sub, comando):
        frame = tk.Frame(self.root, bg=COLOR_CARD_OFF, cursor="hand2", highlightthickness=1, highlightbackground="#30363d")
        frame.pack(fill="x", padx=40, pady=5)
        lbl_t = tk.Label(frame, text=titulo, font=("Segoe UI", 10, "bold"), bg=COLOR_CARD_OFF, fg=COLOR_TEXT_OFF)
        lbl_t.pack(pady=(8, 0), padx=20, anchor="w")
        lbl_s = tk.Label(frame, text=sub, font=("Segoe UI", 8), bg=COLOR_CARD_OFF, fg="#484f58")
        lbl_s.pack(pady=(0, 8), padx=20, anchor="w")
        for widget in [frame, lbl_t, lbl_s]:
            widget.bind("<Button-1>", lambda e, f=frame, lt=lbl_t, ls=lbl_s: comando(f, lt, ls))
        return frame

    def toggle_visual(self, active, frame, lbl_t, lbl_s, nombre):
        if active:
            frame.config(bg=COLOR_CARD_ON, highlightbackground=COLOR_ACCENT)
            lbl_t.config(bg=COLOR_CARD_ON, fg=COLOR_ACCENT)
            lbl_s.config(bg=COLOR_CARD_ON, fg="#8b949e")
            self.log(f"Módulo ON: {nombre}")
        else:
            frame.config(bg=COLOR_CARD_OFF, highlightbackground="#30363d")
            lbl_t.config(bg=COLOR_CARD_OFF, fg=COLOR_TEXT_OFF)
            lbl_s.config(bg=COLOR_CARD_OFF, fg="#484f58")
            self.log(f"Módulo OFF: {nombre}")

    def toggle_next(self, f, lt, ls):
        self.vars["next"]["active"] = not self.vars["next"]["active"]
        self.toggle_visual(self.vars["next"]["active"], f, lt, ls, "Farm")
        if self.vars["next"]["active"]: threading.Thread(target=self.hilo_next, daemon=True).start()

    def toggle_abyss(self, f, lt, ls):
        self.vars["abyss"]["active"] = not self.vars["abyss"]["active"]
        self.toggle_visual(self.vars["abyss"]["active"], f, lt, ls, "Abyss")
        if self.vars["abyss"]["active"]: threading.Thread(target=self.hilo_abyss, daemon=True).start()

    def toggle_skip(self, f, lt, ls):
        self.vars["skip"]["active"] = not self.vars["skip"]["active"]
        self.toggle_visual(self.vars["skip"]["active"], f, lt, ls, "Loot")
        if self.vars["skip"]["active"]: threading.Thread(target=self.hilo_skip, daemon=True).start()

    def registrar_accion(self, es_stage=False, msg=None):
        self.total_clicks += 1
        if es_stage: self.loot_estimado += RECOMPENSA_POR_STAGE
        self.lbl_num.config(text=str(self.total_clicks).zfill(3))
        self.lbl_loot.config(text=f"NIVELES PASADOS: {self.loot_estimado}")
        if msg: self.log(msg)

    def buscar_y_click(self, img, prec=0.7, gray=True, log_msg=None, es_stage=False, region=None):
        if os.path.exists(img):
            try:
                pos = pyautogui.locateOnScreen(img, confidence=prec, grayscale=gray, region=region)
                if pos:
                    pyautogui.click(pos)
                    self.registrar_accion(es_stage=es_stage, msg=log_msg)
                    return True
            except: pass
        return False

    def hilo_next(self):
        while self.vars["next"]["active"]:
            self.buscar_y_click(self.img_begin, gray=False, log_msg="Farm: Inicio Batalla")
            self.buscar_y_click(self.img_levelup, gray=False, log_msg="Farm: Level Up Personaje")
            self.buscar_y_click(self.img_account_levelup, gray=False, log_msg="Farm: Level Up Cuenta")
            self.buscar_y_click(self.img_next, gray=False, log_msg="Farm: Next Stage", es_stage=True)
            time.sleep(1.2)

    def hilo_abyss(self):
        while self.vars["abyss"]["active"]:
            self.buscar_y_click(self.img_levelup, gray=False, log_msg="Abyss: Level Up Personaje")
            self.buscar_y_click(self.img_account_levelup, gray=False, log_msg="Abyss: Level Up Cuenta")
            self.buscar_y_click(self.img_enter, gray=False)
            combat = False
            if self.buscar_y_click(self.img_begin, gray=False, log_msg="Abyss: Inicio"): combat = True
            elif self.buscar_y_click(self.img_next, gray=False, log_msg="Abyss: Siguiente", es_stage=True): combat = True
            
            if combat:
                time.sleep(2)
                while self.vars["abyss"]["active"]:
                    if self.buscar_y_click(self.img_confirm, gray=False, log_msg="Abyss: Piso OK"): break
                    pydirectinput.press('tab')
                    time.sleep(0.4)
            time.sleep(1)

    def hilo_skip(self):
        while self.vars["skip"]["active"]:
            self.buscar_y_click(self.img_levelup, gray=False, log_msg="Loot: Level Up Personaje")
            self.buscar_y_click(self.img_account_levelup, gray=False, log_msg="Loot: Level Up Cuenta")

            for img in [self.img_skip, self.img_saltar_journey, self.img_confirm, self.img_move, self.img_reward, self.img_cruz]:
                if not self.vars["skip"]["active"]: break
                # Región limitada SOLO para Cruz.png (Top 75%)
                region_actual = REGION_SUPERIOR if img == self.img_cruz else None
                if self.buscar_y_click(img, log_msg=f"Match: {img.split('.')[0]}", region=region_actual):
                    time.sleep(0.7)
            time.sleep(0.5)

    def reset_sesion(self):
        self.total_clicks = 0
        self.loot_estimado = 0
        self.start_time = time.time()
        self.lbl_num.config(text="000")
        self.lbl_loot.config(text="NIVELES PASADOS: 0")
        self.log(">>> Sesión reiniciada.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SkipperApp(root)
    root.mainloop()