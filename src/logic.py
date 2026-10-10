from pathlib import Path
from PIL import Image, UnidentifiedImageError

def resize_image(input_path, output_path, width, height):
    if not isinstance(width, int) or not isinstance(height, int) or width < 1 or height < 1:
        return False
    try:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(input_path) as image:
            resized = image.convert("RGB") if image.mode not in ("RGB", "RGBA") else image.copy()
            resized = resized.resize((width, height), Image.Resampling.LANCZOS)
            fmt = output.suffix.lower()
            if fmt in (".jpg", ".jpeg") and resized.mode == "RGBA":
                resized = resized.convert("RGB")
            resized.save(output)
        return True
    except (OSError, UnidentifiedImageError, ValueError):
        return False
