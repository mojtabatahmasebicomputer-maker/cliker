import tkinter as tk
from tkinter import messagebox
import threading
import time
import datetime

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    HAS_PAG = True
except ImportError:
    HAS_PAG = False

try:
    import keyboard
    HAS_KB = True
except ImportError:
    HAS_KB = False

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker — کلیک زمان‌بندی‌شده")
        self.root.geometry("480x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#12121f")

        self.running = False
        self.click_x = tk.IntVar(value=0)
        self.click_y = tk.IntVar(value=0)
        self.t_h  = tk.IntVar(value=8)
        self.t_m  = tk.IntVar(value=44)
        self.t_s  = tk.IntVar(value=59)
        self.t_ms = tk.IntVar(value=55)
        self.interval_ms = tk.IntVar(value=200)
        self.repeat_count = tk.IntVar(value=5)
        self.infinite = tk.BooleanVar(value=False)

        self._build()
        self._tick()
        self._track_mouse()

        if HAS_KB:
            keyboard.add_hotkey('space', self._space_pressed)

        missing = []
        if not HAS_PAG: missing.append("pyautogui")
        if not HAS_KB:  missing.append("keyboard")
        if missing:
            messagebox.showinfo(
                "نصب نیاز است",
                f"دستور زیر را در CMD اجرا کنید:\n\npip install {' '.join(missing)}\n\nسپس برنامه را دوباره باز کنید."
            )

    def _space_pressed(self):
        if self.running:
            self.root.after(0, self._stop)

    def _build(self):
        BG   = "#12121f"
        CARD = "#1e1e34"
        ACC  = "#7c5cbf"
        RED  = "#c0392b"
        GRN  = "#27ae60"
        FG   = "#dcdcf0"
        DIM  = "#7070a0"

        bar = tk.Frame(self.root, bg="#0d0d1a", pady=10)
        bar.pack(fill='x')
        self.clock_lbl = tk.Label(bar, text="", font=("Consolas", 28, "bold"),
                                  bg="#0d0d1a", fg=ACC)
        self.clock_lbl.pack()
        tk.Label(bar, text="ساعت سیستم   (HH:MM:SS:mmm)",
                 font=("Segoe UI", 8), bg="#0d0d1a", fg=DIM).pack()

        tk.Label(self.root, text="⌨️  کلید  SPACE  =  توقف فوری",
                 bg="#1a0a2e", fg="#b06eff",
                 font=("Segoe UI", 9, "bold"), pady=5).pack(fill='x')

        pad = dict(padx=18)

        def sec(title):
            tk.Label(self.root, text=title, bg=BG, fg=DIM,
                     font=("Segoe UI", 8, "bold"), anchor='w').pack(fill='x', **pad, pady=(10,2))

        def card():
            f = tk.Frame(self.root, bg=CARD, padx=14, pady=10)
            f.pack(fill='x', **pad)
            return f

        sec("⏰  زمان هدف برای اولین کلیک")
        tf = card()
        for col, (lbl, var, mx) in enumerate([
            ("ساعت", self.t_h, 23), ("دقیقه", self.t_m, 59),
            ("ثانیه", self.t_s, 59), ("میلی‌ثانیه", self.t_ms, 999)
        ]):
            fc = tk.Frame(tf, bg=CARD); fc.grid(row=0, column=col, padx=6)
            tk.Label(fc, text=lbl, bg=CARD, fg=DIM, font=("Segoe UI", 7)).pack()
            tk.Spinbox(fc, from_=0, to=mx, textvariable=var, width=5,
                       bg="#0d0d1a", fg=ACC, buttonbackground="#0d0d1a",
                       relief='flat', font=("Consolas", 15, "bold"),
                       justify='center', insertbackground='white').pack()
        tf.columnconfigure((0,1,2,3), weight=1)

        sec("🖱️  موقعیت کلیک روی صفحه")
        pf = card()
        for col, (lbl, var) in enumerate([("X", self.click_x), ("Y", self.click_y)]):
            fc = tk.Frame(pf, bg=CARD); fc.grid(row=0, column=col, padx=8)
            tk.Label(fc, text=lbl, bg=CARD, fg=DIM, font=("Segoe UI", 9)).pack(side='left', padx=3)
            tk.Entry(fc, textvariable=var, width=7, bg="#0d0d1a", fg=FG,
                     insertbackground='white', relief='flat',
                     font=("Consolas", 13), justify='center').pack(side='left')
        self.cap_btn = tk.Button(
            pf, text="📌 ثبت موقعیت  (3 ثانیه)",
            bg=ACC, fg='white', relief='flat', font=("Segoe UI", 9, "bold"),
            padx=10, pady=4, activebackground="#9b7ddf", command=self._capture)
        self.cap_btn.grid(row=0, column=2, padx=8)
        pf.columnconfigure((0,1,2), weight=1)

        self.mouse_lbl = tk.Label(self.root, text="موس: —", bg=BG, fg=DIM,
                                  font=("Segoe UI", 8))
        self.mouse_lbl.pack()

        sec("🔁  تنظیمات تکرار")
        rf = card()
        tk.Label(rf, text="فاصله بین کلیک‌ها (ms):", bg=CARD, fg=DIM,
                 font=("Segoe UI", 9)).grid(row=0, column=0, sticky='w', padx=4)
        tk.Spinbox(rf, from_=1, to=99999, textvariable=self.interval_ms, width=8,
                   bg="#0d0d1a", fg=FG, buttonbackground="#0d0d1a",
                   relief='flat', font=("Consolas", 11), justify='center').grid(row=0, column=1, padx=6)

        tk.Label(rf, text="تعداد تکرار:", bg=CARD, fg=DIM,
                 font=("Segoe UI", 9)).grid(row=1, column=0, sticky='w', padx=4, pady=(8,0))
        self.count_spin = tk.Spinbox(rf, from_=1, to=999999, textvariable=self.repeat_count, width=8,
                   bg="#0d0d1a", fg=FG, buttonbackground="#0d0d1a",
                   relief='flat', font=("Consolas", 11), justify='center')
        self.count_spin.grid(row=1, column=1, padx=6, pady=(8,0))

        tk.Checkbutton(rf, text="نامحدود (تا SPACE یا توقف)",
                       variable=self.infinite, bg=CARD, fg=DIM,
                       selectcolor="#0d0d1a", activebackground=CARD,
                       font=("Segoe UI", 9),
                       command=self._toggle_inf).grid(row=1, column=2, padx=10, pady=(8,0))

        bf = tk.Frame(self.root, bg=BG, padx=18, pady=10)
        bf.pack(fill='x')
        self.start_btn = tk.Button(bf, text="▶  شروع", bg=GRN, fg='white',
                                    font=("Segoe UI", 12, "bold"), relief='flat',
                                    padx=20, pady=8, activebackground="#2ecc71",
                                    command=self._start)
        self.start_btn.pack(side='left', expand=True, fill='x', padx=(0,6))
        self.stop_btn = tk.Button(bf, text="■  توقف", bg=RED, fg='white',
                                   font=("Segoe UI", 12, "bold"), relief='flat',
                                   padx=20, pady=8, activebackground="#e74c3c",
                                   state='disabled', command=self._stop)
        self.stop_btn.pack(side='left', expand=True, fill='x', padx=(6,0))

        self.status_var = tk.StringVar(value="آماده")
        self.prog_var   = tk.StringVar(value="")
        tk.Label(self.root, textvariable=self.prog_var,
                 bg=BG, fg=ACC, font=("Consolas", 10),
                 anchor='center').pack(fill='x', side='bottom', pady=2)
        tk.Label(self.root, textvariable=self.status_var,
                 bg="#0d0d1a", fg=FG, font=("Segoe UI", 9),
                 pady=7, anchor='center').pack(fill='x', side='bottom')

    def _tick(self):
        now = datetime.datetime.now()
        self.clock_lbl.config(
            text=f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}:{now.microsecond//1000:03d}"
        )
        self.root.after(8, self._tick)

    def _track_mouse(self):
        if HAS_PAG:
            try:
                x, y = pyautogui.position()
                self.mouse_lbl.config(text=f"موس: X={x},  Y={y}")
            except: pass
        self.root.after(50, self._track_mouse)

    def _capture(self):
        self.cap_btn.config(state='disabled', text="⏳ صبر کن...")
        self.status_var.set("3 ثانیه دیگر موقعیت موس ثبت می‌شود — موس را ببر روی هدف")
        self.root.after(3000, self._do_capture)

    def _do_capture(self):
        if HAS_PAG:
            x, y = pyautogui.position()
            self.click_x.set(x); self.click_y.set(y)
            self.status_var.set(f"✅ موقعیت ثبت شد: X={x}, Y={y}")
        else:
            self.status_var.set("❌ pyautogui نصب نیست")
        self.cap_btn.config(state='normal', text="📌 ثبت موقعیت  (3 ثانیه)")

    def _toggle_inf(self):
        self.count_spin.config(state='disabled' if self.infinite.get() else 'normal')

    def _start(self):
        if not HAS_PAG:
            messagebox.showerror("خطا", "pip install pyautogui keyboard")
            return
        self.running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_var.set("⏳ در انتظار زمان هدف...  (SPACE = توقف)")
        self.prog_var.set("")
        threading.Thread(target=self._worker, daemon=True).start()

    def _stop(self):
        self.running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')

    def _worker(self):
        th  = self.t_h.get();  tm_ = self.t_m.get()
        ts  = self.t_s.get();  tms = self.t_ms.get()
        x   = self.click_x.get(); y = self.click_y.get()
        gap = self.interval_ms.get() / 1000.0
        total = self.repeat_count.get()
        inf   = self.infinite.get()

        while self.running:
            now = datetime.datetime.now()
            ms  = now.microsecond // 1000
            if (now.hour == th and now.minute == tm_ and
                    now.second == ts and ms >= tms):
                break
            rem = self._ms_left(now, th, tm_, ts, tms)
            if   rem > 1000: time.sleep(0.2)
            elif rem > 100:  time.sleep(0.01)
            elif rem > 10:   time.sleep(0.001)
            else:            time.sleep(0.0001)

        if not self.running:
            self.root.after(0, lambda: self.status_var.set("⏹ متوقف شد (SPACE)"))
            return

        n = 0
        while self.running:
            try:
                pyautogui.click(x, y)
                n += 1
                label = "∞" if inf else f"{n}/{total}"
                self.root.after(0, lambda i=n, lb=label: (
                    self.status_var.set(f"✅ کلیک {i} انجام شد"),
                    self.prog_var.set(f"{lb} کلیک")
                ))
            except Exception as e:
                self.root.after(0, lambda err=e: self.status_var.set(f"❌ خطا: {err}"))
                break

            if not inf and n >= total:
                break
            time.sleep(gap)

        done = n
        self.root.after(0, self._stop)
        self.root.after(0, lambda: self.status_var.set(
            f"✅ تمام شد — {done} کلیک انجام شد"
        ))

    def _ms_left(self, now, th, tm_, ts, tms):
        t = now.replace(hour=th, minute=tm_, second=ts, microsecond=tms*1000)
        if t < now:
            t += datetime.timedelta(days=1)
        return max(0, (t - now).total_seconds() * 1000)

    def on_close(self):
        self.running = False
        if HAS_KB:
            try: keyboard.remove_hotkey('space')
            except: pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
