from PIL import Image
import os

def resize_image(input_path, output_path, width, height):
    try:
        with Image.open(input_path) as img:
            # Use LANCZOS for high-quality downsampling
            resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
            resized_img.save(output_path)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False