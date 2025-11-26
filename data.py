"""JewelMart product data and configuration."""

import base64
import os

# Tiny valid 1x1 PNG (transparent) base64used to create demo asset files.
SMALL_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVQImWNgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII="
)

# Map of sample asset filename -> base64 contents
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

# Ensure assets exist on disk
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
            pass

# Products
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

# Home video URL
HOME_VIDEO_URL = os.path.normpath(r"E:\JM\JewelMart\assets\JewelMart.mp4")


def get_products(category=None):
    """Get all products or filter by category."""
    if category:
        return [p for p in products if p["category"] == category]
    return list(products)


def get_product_by_id(pid):
    """Get product by ID."""
    for p in products:
        if p["id"] == pid:
            return p
    return None


# Auto-wire images from assets directory
try:
    existing_files = [f for f in os.listdir(ASSETS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if existing_files:
        def score_filename_for_product(fname, product):
            s = 0
            name = fname.lower()
            for token in [product.get('material', ''), product.get('category', ''), product.get('name', '')]:
                for word in str(token).lower().split():
                    if word and word in name:
                        s += 2
            if product.get('material', '').lower() in name:
                s += 3
            if product.get('category', '').lower() in name:
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
