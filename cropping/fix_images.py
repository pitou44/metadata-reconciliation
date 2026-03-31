import os
from pathlib import Path
import cv2
import numpy as np

# ============== CHANGE THESE ==============
SOURCE_FOLDER = "jpgs"
OUTPUT_FOLDER = "fixed_options"
# ==========================================

source_path = Path(SOURCE_FOLDER)
output_path = Path(OUTPUT_FOLDER)
output_path.mkdir(parents=True, exist_ok=True)


def find_art_contour(img):
    """Find the largest non-black contour (the art piece)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)

    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    return max(contours, key=cv2.contourArea)


def method_simple_crop(img):
    """Method 1: Simple threshold and bounding box crop."""
    contour = find_art_contour(img)
    if contour is None:
        return None

    x, y, w, h = cv2.boundingRect(contour)

    # Add small padding
    pad = 5
    x = max(0, x - pad)
    y = max(0, y - pad)
    w = min(img.shape[1] - x, w + 2 * pad)
    h = min(img.shape[0] - y, h + 2 * pad)

    return img[y:y + h, x:x + w]


def method_rotated_crop(img):
    """Method 2: Find rotated bounding box, deskew, then crop."""
    contour = find_art_contour(img)
    if contour is None:
        return None

    rect = cv2.minAreaRect(contour)
    center, size, angle = rect

    # Adjust angle
    if angle < -45:
        angle += 90
        size = (size[1], size[0])
    elif angle > 45:
        angle -= 90
        size = (size[1], size[0])

    # Skip if rotation is minimal
    if abs(angle) < 0.5:
        return None  # Will use simple crop instead

    # Rotate image
    h, w = img.shape[:2]
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, rotation_matrix, (w, h),
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

    # Crop the rotated image
    size = (int(size[0]), int(size[1]))
    x = int(center[0] - size[0] / 2)
    y = int(center[1] - size[1] / 2)

    # Clamp to image bounds
    x = max(0, x)
    y = max(0, y)
    x2 = min(w, x + size[0])
    y2 = min(h, y + size[1])

    cropped = rotated[y:y2, x:x2]

    if cropped.size == 0:
        return None

    return cropped


def method_aggressive_crop(img):
    """Method 3: More aggressive thresholding for stubborn borders."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)  # Higher threshold

    kernel = np.ones((10, 10), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(contour)

    return img[y:y + h, x:x + w]


def method_edge_detection_crop(img):
    """Method 4: Use edge detection to find art boundaries."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    kernel = np.ones((5, 5), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=2)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(contour)

    pad = 10
    x = max(0, x - pad)
    y = max(0, y - pad)
    w = min(img.shape[1] - x, w + 2 * pad)
    h = min(img.shape[0] - y, h + 2 * pad)

    return img[y:y + h, x:x + w]


def method_rotated_aggressive(img):
    """Method 5: Aggressive threshold + rotation correction."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)

    kernel = np.ones((10, 10), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    contour = max(contours, key=cv2.contourArea)
    rect = cv2.minAreaRect(contour)
    center, size, angle = rect

    if angle < -45:
        angle += 90
        size = (size[1], size[0])
    elif angle > 45:
        angle -= 90
        size = (size[1], size[0])

    if abs(angle) < 0.5:
        return None

    h, w = img.shape[:2]
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(img, rotation_matrix, (w, h),
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

    # Re-detect contour on rotated image
    gray_rot = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
    _, thresh_rot = cv2.threshold(gray_rot, 30, 255, cv2.THRESH_BINARY)
    thresh_rot = cv2.morphologyEx(thresh_rot, cv2.MORPH_CLOSE, kernel)

    contours_rot, _ = cv2.findContours(thresh_rot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours_rot:
        return None

    contour_rot = max(contours_rot, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(contour_rot)

    cropped = rotated[y:y + h, x:x + w]

    if cropped.size == 0:
        return None

    return cropped


def method_percentage_crop(img):
    """Method 6: Crop fixed percentage from all sides as fallback."""
    h, w = img.shape[:2]
    crop_percent = 0.03  # 3% from each side

    x1 = int(w * crop_percent)
    x2 = int(w * (1 - crop_percent))
    y1 = int(h * crop_percent)
    y2 = int(h * (1 - crop_percent))

    return img[y1:y2, x1:x2]


METHODS = {
    "simple": method_simple_crop,
    "rotated": method_rotated_crop,
    "aggressive": method_aggressive_crop,
    "edge": method_edge_detection_crop,
    "rotated_aggressive": method_rotated_aggressive,
    "percent": method_percentage_crop,
}

# Process all images
jpg_files = list(source_path.glob("*.jpg")) + list(source_path.glob("*.JPG")) + \
            list(source_path.glob("*.jpeg")) + list(source_path.glob("*.JPEG"))

print(f"Found {len(jpg_files)} image(s) to process")

for img_file in jpg_files:
    print(f"\nProcessing: {img_file.name}")

    img = cv2.imread(str(img_file))
    if img is None:
        print(f"  Could not read image, skipping")
        continue

    # Create subfolder for this image's options
    img_output_folder = output_path / img_file.stem
    img_output_folder.mkdir(parents=True, exist_ok=True)

    # Save original for reference
    cv2.imwrite(str(img_output_folder / "original.jpg"), img)

    # Apply each method
    for method_name, method_func in METHODS.items():
        try:
            result = method_func(img)
            if result is not None and result.size > 0:
                # Check result is reasonable size (at least 10% of original)
                if result.shape[0] * result.shape[1] > img.shape[0] * img.shape[1] * 0.1:
                    output_file = img_output_folder / f"{method_name}.jpg"
                    cv2.imwrite(str(output_file), result)
                    print(f"  ✓ {method_name}")
                else:
                    print(f"  ✗ {method_name} (result too small)")
            else:
                print(f"  ✗ {method_name} (no result)")
        except Exception as e:
            print(f"  ✗ {method_name} (error: {e})")

print("\n\nDone! Run checker.py to review and select the best versions.")