import os
import random
import tkinter as tk
import subprocess
import shutil

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

WINDOWS_COUNT = 30
SMALL_SIZE = 220
LIFETIME_MS = 1000
SPREAD_MS = 12000
SHAKE_POWER = 30
SHAKE_INTERVAL_MS = 30 # Чуть увеличили для Linux, чтобы система не лагала от вызовов

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")

def find_image():
    for ext in IMAGE_EXTS:
        path = os.path.join(BASE_DIR, "image" + ext)
        if os.path.exists(path):
            return path
    for name in sorted(os.listdir(BASE_DIR)):
        if name.lower().endswith(IMAGE_EXTS):
            return os.path.join(BASE_DIR, name)
    raise FileNotFoundError("Положи картинку (например image.png) в папку со скриптом")

def load_photo(path, width, height):
    if HAS_PIL:
        img = Image.open(path).convert("RGB")
        img = img.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    photo = tk.PhotoImage(file=path)
    scale_x = max(1, photo.width() // width)
    scale_y = max(1, photo.height() // height)
    return photo.subsample(scale_x, scale_y)

class WindowShaker:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.window_id = None
        self.origin = (0, 0)
        
        # Проверяем, есть ли xdotool в системе (работает в X11)
        self.enabled = shutil.which("xdotool") is not None
        
        if not self.enabled:
            print("ВНИМАНИЕ: 'xdotool' не найден. Тряска активного окна отключена.")
            print("Установите его командой: sudo apt install xdotool")
            return

        if os.environ.get("XDG_SESSION_TYPE") == "wayland":
            print("ВНИМАНИЕ: Вы используете Wayland. xdotool работает только в X11. Тряска отключена.")
            self.enabled = False
            return

    def start(self):
        if not self.enabled:
            return
        try:
            # Получаем ID активного окна
            self.window_id = subprocess.check_output(["xdotool", "getactivewindow"]).decode().strip()
            if not self.window_id:
                return
            
            # Получаем текущие координаты окна
            geo = subprocess.check_output(["xdotool", "getwindowgeometry", "--shell", self.window_id]).decode()
            x = int([line for line in geo.split('\n') if line.startswith("X=")][0].split('=')[1])
            y = int([line for line in geo.split('\n') if line.startswith("Y=")][0].split('=')[1])
            self.origin = (x, y)
            
            self.root.after(200, self._begin)
        except Exception as e:
            print(f"Ошибка получения активного окна: {e}")
            self.enabled = False

    def _begin(self):
        self.running = True
        self._shake()

    def _move(self, x, y):
        try:
            subprocess.run(["xdotool", "windowmove", self.window_id, str(x), str(y)], check=False)
        except Exception:
            pass

    def _shake(self):
        if not self.running:
            return
        ox, oy = self.origin
        dx = random.randint(-SHAKE_POWER, SHAKE_POWER)
        dy = random.randint(-SHAKE_POWER, SHAKE_POWER)
        self._move(ox + dx, oy + dy)
        self.root.after(SHAKE_INTERVAL_MS, self._shake)

    def stop(self):
        self.running = False
        if self.enabled and self.window_id:
            self._move(*self.origin)

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw() # Скрываем главное окно
        self.image_path = find_image()
        self.closed = 0
        self.photos = []
        self.shaker = WindowShaker(self.root)

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.small_photo = load_photo(self.image_path, SMALL_SIZE, SMALL_SIZE)

    def run(self):
        self.shaker.start()
        for _ in range(WINDOWS_COUNT):
            delay = random.randint(0, SPREAD_MS)
            self.root.after(delay, self.open_small_window)
        self.root.mainloop()

    def open_small_window(self):
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        x = random.randint(0, max(0, self.screen_w - SMALL_SIZE))
        y = random.randint(0, max(0, self.screen_h - SMALL_SIZE))
        win.geometry(f"{SMALL_SIZE}x{SMALL_SIZE}+{x}+{y}")
        tk.Label(win, image=self.small_photo, borderwidth=0).pack()
        win.bind("<Escape>", lambda e: self.emergency_exit())
        self.root.after(LIFETIME_MS, lambda: self.close_small_window(win))

    def close_small_window(self, win):
        win.destroy()
        self.closed += 1
        if self.closed >= WINDOWS_COUNT:
            self.finish()

    def finish(self):
        self.shaker.stop()
        full = tk.Toplevel(self.root)
        full.configure(bg="black")
        full.attributes("-fullscreen", True)
        full.attributes("-topmost", True)
        photo = load_photo(self.image_path, self.screen_w, self.screen_h)
        self.photos.append(photo) # Ссылка, чтобы Python не удалил картинку из памяти
        tk.Label(full, image=photo, bg="black", borderwidth=0).pack(expand=True, fill="both")
        full.bind("<Escape>", lambda e: self.emergency_exit())
        full.bind("<Button-1>", lambda e: self.emergency_exit())
        full.focus_force() # Принудительный фокус для Linux

    def emergency_exit(self):
        self.shaker.stop()
        self.root.destroy()

if __name__ == "__main__":
    App().run()
