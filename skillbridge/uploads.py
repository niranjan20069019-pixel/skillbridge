"""uploads.py — Secure file upload validation."""
import os
from flask import current_app
from werkzeug.utils import secure_filename

# Magic bytes → allowed extension
_MAGIC = {
    b"%PDF":        ".pdf",
    b"PK\x03\x04":  ".docx",   # ZIP-based: .docx and .pptx
}


def allowed_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def validate_magic(stream) -> bool:
    """Read first 8 bytes and verify against known magic bytes."""
    header = stream.read(8)
    stream.seek(0)
    for magic in _MAGIC:
        if header.startswith(magic):
            return True
    # Plain text has no magic bytes — allow if extension is .txt
    return False


def save_upload(file, prefix: str) -> str:
    """
    Validate and save an uploaded file.
    Returns the saved filename.
    Raises ValueError on invalid file.
    """
    if not file or not file.filename:
        raise ValueError("No file provided.")

    if not allowed_file(file.filename):
        raise ValueError(
            f"File type not allowed. Permitted: "
            f"{', '.join(current_app.config['ALLOWED_EXTENSIONS'])}"
        )

    ext = os.path.splitext(file.filename)[1].lower()

    # Magic-byte check (skip for .txt — no reliable magic)
    if ext != ".txt" and not validate_magic(file.stream):
        raise ValueError("File content does not match its extension.")

    fname = secure_filename(f"{prefix}{ext}")
    dest  = os.path.join(current_app.config["UPLOAD_FOLDER"], fname)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    file.save(dest)
    return fname
