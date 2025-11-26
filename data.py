import base64
# In your data.py file:
import os

# --- IMPORTANT ---
# 1. Replace 'your_video.mp4' with the actual file name of your video.
# 2. Adjust the second argument (e.g., "assets") if the video is in a different folder.
# -----------------

# Get the absolute path to the directory containing this data.py file.
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 

# Construct the absolute path to the video file.
# Example: If your structure is main_script/data.py and main_script/assets/my_jewel_video.mp4
HOME_VIDEO_URL = os.path.join(BASE_DIR, "assets", "my_jewel_video.mp4")

# If the video is in the SAME folder as data.py:
# HOME_VIDEO_URL = os.path.join(BASE_DIR, "my_jewel_video.mp4")

# If you are using a network URL, just ensure it's correct:
# HOME_VIDEO_URL = "https://example.com/videos/jewel_promo.mp4"

# INSIDE MainWindow.create_home, replacing the block near the QtMultimedia fallback

            # --- START DEBUG CODE BLOCK ---
            def player_error_debug(error_code):
                # Print the error to your console/terminal
                print(f"\n!!! QMediaPlayer FAILED !!!")
                print(f"Error Code: {error_code.name}")
                print(f"Error String: {player.errorString()}")
                print(f"Video URL (Attempted): {url_obj.toString()}")
                print(f"!!! QMediaPlayer FAILED !!!\n")
                show_poster_and_message() # This will show the fallback message/poster
                
            try:
                # Connect the custom debug function
                player.error.connect(player_error_debug)
            except Exception:
                # Fallback connection if the above fails
                player.error.connect(show_poster_and_message)
            # --- END DEBUG CODE BLOCK ---
import os
# HOME_VIDEO_URL = os.path.join(BASE_DIR, "assets", "E:\JM\JewelMart\assets\JewelMart.mp4")

# Tiny valid 1x1 PNG (transparent) base64 used to create demo asset files.
SMALL_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVQImWNgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII="
)

# Map of sample asset filename -> base64 contents. We'll write these to the assets/ folder
# if they don't already exist. You can replace these with real images later.
ASSET_FILES = {
    "necklace_gold.png": SMALL_PNG_B64,
    "necklace_silver.png": SMALL_PNG_B64,
    "necklace_diamond.png": SMALL_PNG_B64,
    "earring_gold.png": SMALL_PNG_B64,
    "earring_diamond.png": SMALL_PNG_B64,
    "crown_gold.png": SMALL_PNG_B64,
    "crown_silver.png": SMALL_PNG_B64,
    "nosepin_gold.png": SMALL_PNG_B64,
}


# Ensure assets exist on disk next to this module
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
if not os.path.exists(ASSETS_DIR):
    try:
        os.makedirs(ASSETS_DIR, exist_ok=True)
    except Exception:
        pass

for fname, b64 in ASSET_FILES.items():
    path = os.path.join(ASSETS_DIR, fname)
    if not os.path.exists(path):
        try:
            with open(path, "wb") as f:
                f.write(base64.b64decode(b64))
        except Exception:
            # if writing fails, ignore; ui will still generate thumbnails
            pass


# Products: multiple variants (Gold, Silver, Diamond) for Necklace, Earring, Crown
products = [
    {
        "id": 1,
        "name": "Elegant Pearl Necklace (Gold)",
        "category": "Necklace",
        "material": "Gold",
        "price": 12999,
        "image_path": os.path.join(ASSETS_DIR, "necklace_gold.png"),
        "description": "Classic pearl necklace with gold plating and sterling clasp.",
    },
    {
        "id": 2,
        "name": "Elegant Pearl Necklace (Silver)",
        "category": "Necklace",
        "material": "Silver",
        "price": 8999,
        "image_path": os.path.join(ASSETS_DIR, "necklace_silver.png"),
        "description": "Classic pearl necklace with silver finish.",
    },
    {
        "id": 3,
        "name": "Opal Choker Necklace (Diamond Accent)",
        "category": "Necklace",
        "material": "Diamond",
        "price": 24999,
        "image_path": os.path.join(ASSETS_DIR, "necklace_diamond.png"),
        "description": "Short choker with opal centerpiece and diamond accents.",
    },
    {
        "id": 4,
        "name": "Stud Earrings (Gold)",
        "category": "Earring",
        "material": "Gold",
        "price": 7599,
        "image_path": os.path.join(ASSETS_DIR, "earring_gold.png"),
        "description": "Tiny gold stud earrings for daily wear.",
    },
    {
        "id": 5,
        "name": "Stud Earrings (Diamond)",
        "category": "Earring",
        "material": "Diamond",
        "price": 19999,
        "image_path": os.path.join(ASSETS_DIR, "earring_diamond.png"),
        "description": "Sparkling diamond studs with certified stones.",
    },
    {
        "id": 6,
        "name": "Delicate Nose Pin (Gold)",
        "category": "Nose Pin",
        "material": "Gold",
        "price": 1999,
        "image_path": os.path.join(ASSETS_DIR, "nosepin_gold.png"),
        "description": "Simple and elegant gold nose pin for daily wear.",
    },
]

categories = ["Necklace", "Earring", "Nose Pin"]

# Optional home video URL (set to a hosted video page or YouTube link). Leave empty to hide.
# Use a raw string and normalize the path so backslashes don't act as escape sequences
HOME_VIDEO_URL = os.path.normpath(r"E:\JM\JewelMart\assets\JewelMart.mp4")


def get_products(category=None):
    if category:
        return [p for p in products if p["category"] == category]
    return list(products)


def get_product_by_id(pid):
    for p in products:
        if p["id"] == pid:
            return p
    return None


def image_bytes_from_b64(b64str):
    return base64.b64decode(b64str)


# Auto-wire any images the user placed into the assets directory.
# This will look for files in ASSETS_DIR and, for each product, try to find
# the best matching file by checking keywords (material, category, name).
try:
    existing_files = [f for f in os.listdir(ASSETS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    existing_paths = [os.path.join(ASSETS_DIR, f) for f in existing_files]
    if existing_paths:
        # helper to score filenames for a product
        def score_filename_for_product(fname, product):
            s = 0
            name = fname.lower()
            for token in [product.get('material',''), product.get('category',''), product.get('name','')]:
                for word in str(token).lower().split():
                    if word and word in name:
                        s += 2
            # small bonus for exact category/material substring
            if product.get('material','').lower() in name:
                s += 3
            if product.get('category','').lower() in name:
                s += 3
            return s

        for p in products:
            best = None
            best_score = 0
            for f in existing_files:
                sc = score_filename_for_product(f, p)
                if sc > best_score:
                    best_score = sc
                    best = f
            if best and best_score > 0:
                p['image_path'] = os.path.join(ASSETS_DIR, best)
except Exception:
    pass
