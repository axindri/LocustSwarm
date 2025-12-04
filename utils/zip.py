import io
import zipfile
from pathlib import Path


def make_zip(results_dir: Path):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in results_dir.iterdir():
            if file_path.is_file():
                arcname = file_path.name
                zip_file.write(file_path, arcname)

    zip_buffer.seek(0)
    return zip_buffer
