# JewelMart (demo)

JewelMart is a demo desktop application built with Python and PyQt5 that showcases a jewelry catalog with login/registration, categories, product pages, wishlist and cart functionality. The virtual try-on button is a placeholder (no real AR implemented).

## Requirements
- Python 3.8+
- PyQt5
- Pillow

Install dependencies (recommended in a virtualenv):

```powershell
python -m pip install -r requirements.txt
```

## Run

From the workspace root (where `requirements.txt` is), run:

```powershell
python .\JewelMart\ui.py
```

or

```powershell
python .\JewelMart\app.py
```

## Notes
- This is a minimal demo; user passwords are stored in `JewelMart/users.json` without hashing — do not use for production.
- The virtual try-on button shows a placeholder message.
- You can add product images in `data.py` as base64 strings.
