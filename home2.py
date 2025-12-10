# Updated code with clickable Shop Now button opening user_panel_main.py
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import cv2
import requests
from io import BytesIO
import os

# ---------------- Function to load images from URL ----------------
def load_image(url, size):
    response = requests.get(url)
    img_data = response.content
    img = Image.open(BytesIO(img_data))
    img = img.resize(size)
    return ImageTk.PhotoImage(img)

# ---------------- Function to open user panel ----------------
def open_user_panel():
    os.system("python user_panel.py")

# ---------------- MAIN WINDOW ----------------
root = Tk()
root.title("Jewellery Shop")
root.geometry("1000x900")
root.configure(bg="white")

# --------------------------------------------------------
#  CREATE SCROLLABLE CANVAS
# --------------------------------------------------------
main_canvas = Canvas(root, bg="white", highlightthickness=0)
main_canvas.pack(side=LEFT, fill=BOTH, expand=True)

scrollbar = Scrollbar(root, orient=VERTICAL, command=main_canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)

main_canvas.configure(yscrollcommand=scrollbar.set)

content_frame = Frame(main_canvas, bg="white")
main_canvas.create_window((0, 0), window=content_frame, anchor="nw")

def update_scroll_region(event=None):
    main_canvas.configure(scrollregion=main_canvas.bbox("all"))

content_frame.bind("<Configure>", update_scroll_region)

# Enable mousewheel scrolling
def _on_mouse_wheel(event):
    main_canvas.yview_scroll(-1 * int(event.delta / 120), "units")

root.bind_all("<MouseWheel>", _on_mouse_wheel)

# --------------------------------------------------------
#  HOME / WELCOME SECTION
# --------------------------------------------------------
home_frame = Frame(content_frame, bg="white")
home_frame.pack(fill="x", padx=20, pady=20)

title = Label(home_frame, text="Welcome to JewelMart",
              fg="#C8937E", bg="white",
              font=("Arial", 28, "bold"))
title.pack(pady=(6, 2))

tagline = Label(
    home_frame,
    text="Discover Luxury Jewelry | Premium Quality | Exquisite Designs",
    fg="#666666",
    bg="white",
    font=("Arial", 12, "italic")
)
tagline.pack(pady=(0, 12))

# --------------------------------------------------------
#  VIDEO BANNER
# --------------------------------------------------------
video_frame = Frame(content_frame, bg="white")
video_frame.pack(fill="x")

video_label = Label(video_frame, bg="white")
video_label.pack(fill="both")

video_path = "assets/JewelMart.mp4"
cap = cv2.VideoCapture(video_path)

def play_video():
    ret, frame = cap.read()
    if ret:
        win_width = root.winfo_width()
        frame = cv2.resize(frame, (win_width, 450))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(frame))
        video_label.img = img
        video_label.config(image=img)
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    video_label.after(20, play_video)

play_video()

# --------------------------------------------------------
#  SHOWCASE BANNER (MODERN GRADIENT + CLICKABLE BUTTON)
# --------------------------------------------------------
banner = Frame(content_frame, bg="white")
banner.pack(fill="x", padx=20, pady=(15, 10))

gradient_canvas = Canvas(banner, height=260, bd=0, highlightthickness=0)
gradient_canvas.pack(fill="both", expand=True)

def draw_gradient():
    gradient_canvas.delete("all")
    width = gradient_canvas.winfo_width()
    height = gradient_canvas.winfo_height()

    r1, g1, b1 = (232, 212, 204)
    r2, g2, b2 = (200, 147, 126)

    for i in range(height):
        r = int(r1 + (r2 - r1) * (i / height))
        g = int(g1 + (g2 - g1) * (i / height))
        b = int(b1 + (b2 - b1) * (i / height))
        color = f"#{r:02x}{g:02x}{b:02x}"
        gradient_canvas.create_line(0, i, width, i, fill=color)

    gradient_canvas.create_text(
        width/2, 60,
        text="Luxury Like Never Before",
        font=("Arial", 26, "bold"),
        fill="white"
    )

    gradient_canvas.create_text(
        width/2, 110,
        text="Handcrafted jewellery with timeless elegance",
        font=("Arial", 14),
        fill="#F8F1EF"
    )

    btn_w, btn_h = 150, 45
    x1 = width/2 - btn_w/2
    y1 = 150
    x2 = width/2 + btn_w/2
    y2 = 195

    gradient_canvas.create_rectangle(x1, y1, x2, y2, outline="", fill="white", tags="button_area")

    btn_text = gradient_canvas.create_text(
        width/2, 172,
        text="Shop Now",
        font=("Arial", 14, "bold"),
        fill="#C8937E",
        tags="button_area"
    )

    gradient_canvas.tag_bind("button_area", "<Button-1>", lambda e: open_user_panel())


gradient_canvas.bind("<Configure>", lambda e: draw_gradient())

# --------------------------------------------------------
#  STATS ROW
# --------------------------------------------------------
stats_frame = Frame(content_frame, bg="white")
stats_frame.pack(pady=12, fill="x")

stats = [("Collections", "50+"), ("Products", "500+"), ("Customers", "10K+")]

for name, val in stats:
    card = Frame(stats_frame, bg="white", relief="solid", bd=1)
    card.pack(side="left", expand=True, fill="both", padx=8, pady=6)

    Label(card, text=val, fg="#C8937E", bg="white",
          font=("Arial", 20, "bold")).pack(padx=12, pady=(12, 4))

    Label(card, text=name, fg="#666", bg="white",
          font=("Arial", 11)).pack(padx=12, pady=(0, 12))

# --------------------------------------------------------
#  CTA MESSAGE
# --------------------------------------------------------
Label(
    content_frame,
    text="Ready to explore? Use the categories below.",
    fg="#C8937E",
    bg="white",
    font=("Arial", 12, "bold")
).pack(pady=(8, 20))

root.mainloop()