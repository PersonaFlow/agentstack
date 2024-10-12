import mimetypes
import json
import csv
import io
from langchain.document_loaders.parsers import BS4HTMLParser, PDFMinerParser
from langchain.document_loaders.parsers.generic import MimeTypeBasedParser
from langchain.document_loaders.parsers.msword import MsWordParser
from langchain.document_loaders.parsers.txt import TextParser
import structlog

logger = structlog.get_logger()

HANDLERS = {
    "application/pdf": PDFMinerParser(),
    "text/plain": TextParser(),
    "text/html": BS4HTMLParser(),
    "text/markdown": TextParser(),
    "text/csv": TextParser(),
    "application/json": TextParser(),
    "application/rtf": TextParser(),
    "application/msword": MsWordParser(),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": MsWordParser(),
}

SUPPORTED_MIMETYPES = sorted(HANDLERS.keys())

MIMETYPE_BASED_PARSER = MimeTypeBasedParser(
    handlers=HANDLERS,
    fallback_parser=None,
)


def guess_mime_type(file_name: str, file_bytes: bytes) -> str:
    """Guess the mime-type of a file based on its name or bytes."""
    # Guess based on the file extension
    mime_type, _ = mimetypes.guess_type(file_name)

    # Return detected mime type from mimetypes guess, unless it's None
    if mime_type:
        return mime_type

    # Signature-based detection for common types
    if file_bytes.startswith(b"%PDF"):
        return "application/pdf"
    elif file_bytes.startswith(
        (b"\x50\x4B\x03\x04", b"\x50\x4B\x05\x06", b"\x50\x4B\x07\x08")
    ):
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif file_bytes.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        return "application/msword"
    elif file_bytes.startswith(b"\x09\x00\xff\x00\x06\x00"):
        return "application/vnd.ms-excel"

    # Check for JSON-like content
    try:
        decoded = file_bytes[:1024].decode("utf-8", errors="ignore")
        stripped = decoded.strip()
        if (stripped.startswith("{") and stripped.endswith("}")) or (
            stripped.startswith("[") and stripped.endswith("]")
        ):
            return "application/json"
    except UnicodeDecodeError:
        pass

    # Check for CSV-like plain text content (commas, tabs, newlines)
    try:
        decoded = file_bytes[:1024].decode("utf-8", errors="ignore")
        if all(char in decoded for char in (",", "\n")) or all(
            char in decoded for char in ("\t", "\n")
        ):
            return "text/csv"
        elif decoded.isprintable() or decoded == "":
            return "text/plain"
    except UnicodeDecodeError:
        pass

    return "application/octet-stream"


def guess_file_extension(file_name: str, file_bytes: bytes) -> str:
    """Guess the file extension based on the file type."""
    mime_type = guess_mime_type(file_name, file_bytes)
    extension = mimetypes.guess_extension(mime_type)

    if extension:
        return extension.lstrip(".")  # Remove the leading dot from the extension
    else:
        # Fallback for common file types
        mime_to_ext = {
            "application/pdf": "pdf",
            "application/msword": "doc",
            "text/rtf": "rtf",
            "text/markdown": "md",
            "application/json": "json",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
            "text/csv": "csv",
            "text/plain": "txt",
            "text/html": "html",
            "application/octet-stream": "bin",
        }
        return mime_to_ext.get(mime_type, "bin")


def get_file_handler(mime_type: str):
    """Get the appropriate file handler based on the mime type."""
    return HANDLERS.get(mime_type)


def is_mime_type_supported(mime_type: str) -> bool:
    """Check if the mime type is supported."""
    return mime_type in SUPPORTED_MIMETYPES


def parse_json_file(file_content: bytes) -> list:
    try:
        data = json.loads(file_content.decode("utf-8"))
        if isinstance(data, list):
            return data
        else:
            raise ValueError("JSON file must contain an array of objects")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON file")


def parse_csv_file(file_content: bytes) -> list:
    try:
        csv_content = file_content.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        return list(csv_reader)
    except csv.Error:
        raise ValueError("Invalid CSV file")
