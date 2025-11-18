# setup/PNG-ICO.py
from wand.image import Image
from pathlib import Path

def convert_png_to_ico(png_path, ico_path=None, sizes=None):
    """
    Convert a PNG image to ICO format using Wand.
    
    Args:
        png_path (str): Path to the source PNG file
        ico_path (str, optional): Path to save the ICO file. If None, replaces .png with .ico
        sizes (list, optional): List of icon sizes to include. Defaults to [16, 32, 48, 64, 128, 256]
    """
    if sizes is None:
        sizes = [16, 32, 48, 64, 128, 256]
    
    if ico_path is None:
        ico_path = str(Path(png_path).with_suffix('.ico'))
    
    try:
        # Create a new image list for the ICO
        with Image() as ico_image:
            # Read the source image
            with Image(filename=png_path) as img:
                # Add each size to the ICO
                for size in sizes:
                    # Create a copy and resize
                    with img.clone() as resized:
                        resized.resize(size, size)
                        ico_image.sequence.append(resized.sequence[0])
            
            # Save as ICO
            ico_image.format = 'ico'
            ico_image.save(filename=ico_path)
            print(f"Successfully converted {png_path} to {ico_path}")
            return True
    except Exception as e:
        print(f"Error converting image: {e}")
        return False

if __name__ == "__main__":
    # Paths
    base_dir = Path(__file__).parent.parent
    png_path = base_dir / "assets" / "icon.png"
    ico_path = base_dir / "assets" / "icon.ico"

    # Convert the icon
    if png_path.exists():
        convert_png_to_ico(str(png_path), str(ico_path))
    else:
        print(f"Error: {png_path} not found")