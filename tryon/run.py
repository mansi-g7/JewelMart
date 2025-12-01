"""
Simple virtual try-on demo using MediaPipe Face Mesh and OpenCV.

Place this file at: JewelMart/tryon/run.py

API: expose run_tryon(product) where product is the product dict from data.py
The function will open the default webcam, overlay the product image based on face landmarks,
track movement, and allow taking photos by pressing 'c'. Press 'q' to quit.

Dependencies: opencv-python, mediapipe, Pillow, numpy
Install with:
    python -m pip install opencv-python mediapipe Pillow numpy

Notes:
- This is a simple demo. For production-quality AR you'd refine landmark selection,
  use higher-resolution assets, and handle different face orientations robustly.
"""
import os
import time
import tempfile
import base64
import math
from pathlib import Path

"""
Simple virtual try-on demo using MediaPipe Face Mesh and OpenCV.

Place this file at: JewelMart/tryon/run.py

API: expose run_tryon(product) where product is the product dict from data.py
The function will open the default webcam, overlay the product image based on face landmarks,
track movement, and allow taking photos by pressing 'c'. Press 'q' to quit.

Dependencies: opencv-python, mediapipe, Pillow, numpy
Install with:
    python -m pip install opencv-python mediapipe Pillow numpy

Notes:
- This is a simple demo. For production-quality AR you'd refine landmark selection,
  use higher-resolution assets, and handle different face orientations robustly.
"""

import os
import time
import tempfile
import base64
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


try:
    import mediapipe as mp
except Exception as e:
    raise ImportError("mediapipe is required for the try-on demo. Install with 'pip install mediapipe'") from e

mp_face = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils


def load_product_overlay(product, desired_width=None):
    """Load overlay image (with alpha) for the product. Returns BGRA numpy array or None."""
    # Prefer image_path
    img_path = product.get("image_path")
    if img_path:
        # If it's just a filename, look for it in assets directory
        if not os.path.isabs(img_path):
            assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
            full_path = os.path.join(assets_dir, img_path)
        else:
            full_path = img_path
            
        if os.path.exists(full_path):
            img = cv2.imread(full_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                return None
            # ensure BGRA
            if img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
            return img

    # fallback to base64 image in product['image']
    b64 = product.get("image")
    if b64:
        try:
            data = base64.b64decode(b64)
            pil = Image.open(tempfile.NamedTemporaryFile(delete=False, suffix='.png'))
        except Exception:
            return None
    return None


def overlay_transparent(background, overlay, x, y):
    """Overlay `overlay` (BGRA) onto `background` (BGR) at position (x, y) (top-left).
    Returns the resulting image.
    """
    bh, bw = background.shape[:2]
    oh, ow = overlay.shape[:2]
    if x >= bw or y >= bh:
        return background
    # Clip overlay region if it goes outside background
    x1 = max(x, 0)
    y1 = max(y, 0)
    x2 = min(x + ow, bw)
    y2 = min(y + oh, bh)
    ox1 = x1 - x
    oy1 = y1 - y
    ox2 = ox1 + (x2 - x1)
    oy2 = oy1 + (y2 - y1)
    if x2 <= x1 or y2 <= y1:
        return background
    roi = background[y1:y2, x1:x2]
    overlay_roi = overlay[oy1:oy2, ox1:ox2]
    # Split channels
    overlay_rgb = overlay_roi[..., :3].astype(float)
    overlay_alpha = overlay_roi[..., 3:].astype(float) / 255.0
    roi = roi.astype(float)
    inv_alpha = 1.0 - overlay_alpha
    for c in range(3):
        roi[..., c] = overlay_rgb[..., c] * overlay_alpha[..., 0] + roi[..., c] * inv_alpha[..., 0]
    background[y1:y2, x1:x2] = roi.astype(np.uint8)
    return background


def midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)


def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def run_tryon(product):
    """Main entry point called by the app. Opens webcam and overlays the product.
    Press 'c' to capture a photo, 'q' to quit.
    """
    overlay = load_product_overlay(product)
    if overlay is None:
        print("No overlay image available for this product.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam")
        return

    face_mesh = mp_face.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True,
                                 min_detection_confidence=0.5, min_tracking_confidence=0.5)

    window_name = f"Try-On: {product.get('name')}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    snapshot_dir = os.path.join(os.path.dirname(__file__), '..', 'snapshots')
    os.makedirs(snapshot_dir, exist_ok=True)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            h, w = frame.shape[:2]
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame_rgb)
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                pts = []
                for lm in landmarks.landmark:
                    pts.append((int(lm.x * w), int(lm.y * h)))

                # MediaPipe Face Mesh landmark indices:
                # chin: 152 (tip of chin)
                # nose: 1 (tip of nose)
                # forehead/top: 10 (upper forehead)
                # left ear lobe: 234 (bottom of left ear)
                # right ear lobe: 454 (bottom of right ear)
                # neck center: use chin + offset downward
                # throat area for necklace: around 152-170 range (lower neck)
                chin = pts[152] if len(pts) > 152 else None
                forehead = pts[10] if len(pts) > 10 else None
                
                # Better ear lobe positions for earrings (earlobe area)
                left_earlobe = pts[234] if len(pts) > 234 else None  # bottom of left ear
                right_earlobe = pts[454] if len(pts) > 454 else None  # bottom of right ear
                
                # Neck reference points
                left_jaw = pts[234] if len(pts) > 234 else None
                right_jaw = pts[454] if len(pts) > 454 else None

                # face width approx
                if left_jaw and right_jaw:
                    face_w = distance(left_jaw, right_jaw)
                else:
                    # fallback: bbox width from landmarks
                    xs = [p[0] for p in pts]
                    face_w = max(xs) - min(xs)

                category = (product.get('category') or '').lower()

                if 'necklace' in category:
                    # overlay centered on neck (lower than chin)
                    if chin:
                        target_w = int(1.0 * face_w)
                        scale = target_w / overlay.shape[1]
                        new_h = max(1, int(overlay.shape[0] * scale))
                        resized = cv2.resize(overlay, (target_w, new_h), interpolation=cv2.INTER_AREA)
                        x = int(chin[0] - target_w / 2)
                        # Position on neck area (below chin, not on chin itself)
                        y = int(chin[1] + int(face_w * 0.15))  # Offset down to neck area
                        frame = overlay_transparent(frame, resized, x, y)

                elif 'earring' in category or 'ear' in category:
                    # overlay earrings at ear lobe positions
                    target_w = int(face_w * 0.475)  # Increased from 0.25 (90% larger: 0.25 * 1.9 = 0.475)
                    scale = target_w / overlay.shape[1]
                    new_h = max(1, int(overlay.shape[0] * scale))
                    resized = cv2.resize(overlay, (target_w, new_h), interpolation=cv2.INTER_AREA)
                    
                    # Left earring
                    if left_earlobe:
                        x = int(left_earlobe[0] - target_w / 2)
                        # Position at earlobe (not above ear, at bottom of ear)
                        y = int(left_earlobe[1] - new_h * 0.2)
                        frame = overlay_transparent(frame, resized, x, y)
                    
                    # Right earring (mirror the left earring)
                    if right_earlobe:
                        x = int(right_earlobe[0] - target_w / 2)
                        # Position at earlobe
                        y = int(right_earlobe[1] - new_h * 0.2)
                        # flip horizontally for right ear
                        flipped = cv2.flip(resized, 1)
                        frame = overlay_transparent(frame, flipped, x, y)

                elif 'crown' in category or 'tiara' in category:
                    # overlay above forehead; scale to face_w * 1.2
                    if forehead:
                        target_w = int(face_w * 1.4)
                        scale = target_w / overlay.shape[1]
                        new_h = max(1, int(overlay.shape[0] * scale))
                        resized = cv2.resize(overlay, (target_w, new_h), interpolation=cv2.INTER_AREA)
                        x = int(forehead[0] - target_w / 2)
                        y = int(forehead[1] - new_h * 1.1)
                        frame = overlay_transparent(frame, resized, x, y)

                else:
                    # generic overlay near forehead
                    if forehead:
                        target_w = int(face_w * 1.0)
                        scale = target_w / overlay.shape[1]
                        new_h = max(1, int(overlay.shape[0] * scale))
                        resized = cv2.resize(overlay, (target_w, new_h), interpolation=cv2.INTER_AREA)
                        x = int(forehead[0] - target_w / 2)
                        y = int(forehead[1] - new_h / 2)
                        frame = overlay_transparent(frame, resized, x, y)

            # instructions overlay
            cv2.putText(frame, "Press 'c' to capture, 'q' to quit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            if key == ord('c'):
                # save snapshot with timestamp
                fname = os.path.join(snapshot_dir, f"snapshot_{int(time.time())}.png")
                cv2.imwrite(fname, frame)
                print("Saved snapshot:", fname)

    finally:
        cap.release()
        cv2.destroyAllWindows()
        face_mesh.close()


# Export expected function name
def launch(product):
    run_tryon(product)


if __name__ == '__main__':
    # Quick demo: pick the first product by loading data
    try:
        from ..data import products
        prod = products[0]
    except Exception:
        prod = None
    if prod:
        run_tryon(prod)