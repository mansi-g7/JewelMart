import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, Image
import cv2
import os
import sys

# ----------------- Configuration -----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
VIDEO_FILE = os.path.join(ASSETS_DIR, "JewelMart.mp4")

# ----------------- App -----------------
class JewelMartApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JewelMart — Luxury Jewelry Store")
        self.geometry("1200x800")
        self.configure(bg="white")
        self.minsize(900, 600)

        # top-level frames
        self.create_header()
        self.create_video_banner()
        self.create_home_section()
        self.create_category_tabs()

        # start video loop (if available)
        self.cap = None
        if os.path.exists(VIDEO_FILE):
            self.cap = cv2.VideoCapture(VIDEO_FILE)
            self.after(20, self._video_loop)
        else:
            # show missing video notice inside banner
            self._show_banner_placeholder("Video not found: assets/JewelMart.mp4")

    # ----------------- Header -----------------
    def create_header(self):
        header = tk.Frame(self, bg="white", height=80)
        header.pack(side="top", fill="x")

        left = tk.Frame(header, bg="white")
        left.pack(side="left", padx=18, pady=10)

        logo = tk.Label(left, text="✨ JewelMart", fg="#C8937E", bg="white",
                        font=("Poppins", 22, "bold"))
        logo.pack(side="left")

        # nav buttons
        nav_names = ["Home", "About Us", "Contact Us"]
        for name in nav_names:
            b = tk.Button(left, text=name, bg="white", bd=0, fg="#333333",
                          font=("Poppins", 11, "bold"), activeforeground="#C8937E")
            b.pack(side="left", padx=8)

        # right area
        right = tk.Frame(header, bg="white")
        right.pack(side="right", padx=18)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(right, textvariable=self.search_var, width=30,
                                relief="solid", bd=1)
        search_entry.pack(side="left", padx=(0,8))
        search_entry.insert(0, "Search...")

        tk.Button(right, text="Search", bg="white", bd=0).pack(side="left", padx=6)
        tk.Button(right, text="Refresh", bg="white", bd=0, command=self._on_refresh).pack(side="left", padx=6)

        # small colored buttons
        def colored_btn(text, bg):
            return tk.Button(right, text=text, bg=bg, fg="white", bd=0, padx=8, pady=4)
        colored_btn("🛒 View Cart", "#C8937E").pack(side="left", padx=6)
        colored_btn("📦 My Orders", "#B8D4E8").pack(side="left", padx=6)
        colored_btn("👤 Login", "#E8C5C9").pack(side="left", padx=6)

    # ----------------- Video banner (Tkinter + OpenCV) -----------------
    def create_video_banner(self):
        self.banner_frame = tk.Frame(self, bg="white")
        self.banner_frame.pack(fill="both", expand=False)

        # Label that will display frames
        self.video_label = tk.Label(self.banner_frame, bg="white")
        self.video_label.pack(fill="both", expand=True)

        # Keep a reference for PhotoImage to avoid GC
        self._current_banner_image = None

    def _show_banner_placeholder(self, text="No video available"):
        # Clear label and show a placeholder
        self.video_label.config(text=text, fg="#8A6E63", font=("Arial", 18), image="", compound="center",
                                bg="#E7D4CC", padx=10, pady=60)

    def _video_loop(self):
        """Read frame from OpenCV capture, convert and display in Tkinter Label."""
        if not self.cap or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            # loop video
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if not ret:
                # cannot read
                self._show_banner_placeholder("Unable to play video")
                return

        # compute resize dimensions based on current window width
        win_w = max(self.winfo_width(), 800)
        target_h = 420
        try:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_h, frame_w = frame.shape[:2]
            scale = win_w / frame_w
            new_w = int(frame_w * scale)
            new_h = int(frame_h * scale)
            # limit height to target_h
            if new_h > target_h:
                new_h = target_h
                new_w = int(frame_w * (target_h / frame_h))
            resized = cv2.resize(frame, (new_w, new_h))
            img = Image.fromarray(resized)
            photo = ImageTk.PhotoImage(img)
            self._current_banner_image = photo
            self.video_label.config(image=photo, text="")
        except Exception as e:
            # fallback to placeholder text
            self._show_banner_placeholder(f"Video error: {e}")

        # schedule next frame
        self.banner_frame.after(30, self._video_loop)

    # ----------------- Home content -----------------
    def create_home_section(self):
        self.home_frame = tk.Frame(self, bg="white")
        self.home_frame.pack(fill="both", expand=True, padx=20, pady=18)

        title = tk.Label(self.home_frame, text="Welcome to JewelMart",
                         fg="#C8937E", bg="white", font=("Arial", 28, "bold"))
        title.pack(pady=(6,2))

        tagline = tk.Label(self.home_frame, text="Discover Luxury Jewelry | Premium Quality | Exquisite Designs",
                           fg="#666666", bg="white", font=("Arial", 12, "italic"))
        tagline.pack(pady=(0,12))

        # banner-like image placeholder (below the video)
        banner = tk.Frame(self.home_frame, bg="#E7D4CC", height=220)
        banner.pack(fill="x", padx=10, pady=(6,10))
        banner.pack_propagate(False)
        tk.Label(banner, text="Showcase Banner", bg="#E7D4CC", fg="#8A6E63", font=("Arial", 18)).pack(expand=True)

        # stats row
        stats_frame = tk.Frame(self.home_frame, bg="white")
        stats_frame.pack(pady=12, fill="x")
        stats = [("Collections", "50+"), ("Products", "500+"), ("Customers", "10K+")]
        for name, val in stats:
            card = tk.Frame(stats_frame, bg="white", relief="solid", bd=1)
            card.pack(side="left", expand=True, fill="both", padx=8, pady=6)
            tk.Label(card, text=val, fg="#C8937E", bg="white", font=("Arial", 20, "bold")).pack(padx=12, pady=(12,4))
            tk.Label(card, text=name, fg="#666", bg="white", font=("Arial", 11)).pack(padx=12, pady=(0,12))

        # CTA
        tk.Label(self.home_frame, text="Ready to explore? Use the categories below.", fg="#C8937E", bg="white",
                 font=("Arial", 12, "bold")).pack(pady=(8,20))

    # ----------------- Category tabs (simple) -----------------
    def create_category_tabs(self):
        # Example: not a true ttk.Notebook; simple buttons switching content
        tabs_frame = tk.Frame(self, bg="white")
        tabs_frame.pack(fill="x", padx=20)

        btn_names = ["Home", "Earring", "Necklace", "Diamond Necklace", "Earrings"]
        self.tab_buttons = []
        for i, name in enumerate(btn_names):
            b = tk.Button(tabs_frame, text=name, relief="raised" if i==0 else "flat",
                          padx=10, pady=6, bg="#F5F5F5" if i!=0 else "white")
            b.pack(side="left", padx=4, pady=6)
            self.tab_buttons.append(b)

    # alias to keep compatibility with prior names
    create_category_tabs = create_category_tabs

    # ----------------- Callbacks -----------------
    def _on_refresh(self):
        # placeholder refresh action
        print("Refresh requested")

    # ----------------- Cleanup -----------------
    def on_close(self):
        if self.cap:
            try:
                self.cap.release()
            except:
                pass
        self.destroy()


if __name__ == "__main__":
    app = JewelMartApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
