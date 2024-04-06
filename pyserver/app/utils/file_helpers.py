import mimetypes
from langchain.document_loaders.parsers import BS4HTMLParser, PDFMinerParser
from langchain.document_loaders.parsers.generic import MimeTypeBasedParser
from langchain.document_loaders.parsers.msword import MsWordParser
from langchain.document_loaders.parsers.txt import TextParser

HANDLERS = {
    "application/pdf": PDFMinerParser(),
    "text/plain": TextParser(),
    "text/html": BS4HTMLParser(),
    "application/msword": MsWordParser(),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": MsWordParser(),
}

SUPPORTED_MIMETYPES = sorted(HANDLERS.keys())

MIMETYPE_BASED_PARSER = MimeTypeBasedParser(
    handlers=HANDLERS,
    fallback_parser=None,
)

def guess_mime_type(file_bytes: bytes) -> str:
    """Guess the mime-type of a file."""
    try:
        import magic
    except ImportError as e:
        raise ImportError(
            "magic package not found, please install it with `pip install python-magic`"
        ) from e
    return magic.from_buffer(file_bytes, mime=True)

def guess_file_extension(file_type: str) -> str:
    """Guess the file extension based on the file type."""
    extension = mimetypes.guess_extension(file_type)

    if extension:
        return extension.lstrip('.')  # Remove the leading dot from the extension
    else:
        # Fallback for common file types
        if 'PDF' in file_type.upper():
            return 'pdf'
        elif 'TEXT' in file_type.upper():
            return 'txt'
        elif 'HTML' in file_type.upper():
            return 'html'
        elif 'WORD' in file_type.upper():
            return 'doc' if 'Microsoft Word 2007+' in file_type else 'docx'
        else:
            raise ValueError(f"Unable to determine file extension for file type: {file_type}")

def get_file_handler(mime_type: str):
    """Get the appropriate file handler based on the mime type."""
    return HANDLERS.get(mime_type)

def is_mime_type_supported(mime_type: str) -> bool:
    """Check if the mime type is supported."""
    return mime_type in SUPPORTED_MIMETYPES




# import mimetypes
# from langchain.document_loaders.parsers import BS4HTMLParser, PDFMinerParser
# from langchain.document_loaders.parsers.generic import MimeTypeBasedParser
# from langchain.document_loaders.parsers.msword import MsWordParser
# from langchain.document_loaders.parsers.txt import TextParser

# HANDLERS = {
# #   PDFMinerParser handles parsing of everything in a pdf such as images, tables, etc.
#     "application/pdf": PDFMinerParser(),
#     "text/plain": TextParser(),
#     "text/html": BS4HTMLParser(),
#     "application/msword": MsWordParser(),
#     "application/vnd.openxmlformats-officedocument.wordprocessingml.document": (
#         MsWordParser()
#     ),
# }

# SUPPORTED_MIMETYPES = sorted(HANDLERS.keys())


# MIMETYPE_BASED_PARSER = MimeTypeBasedParser(
#     handlers=HANDLERS,
#     fallback_parser=None,
# )

# def guess_mime_type(file_bytes: bytes) -> str:
#     """Guess the mime-type of a file."""
#     try:
#         import magic
#     except ImportError as e:
#         raise ImportError(
#             "magic package not found, please install it with `pip install python-magic`"
#         ) from e

#     mime = magic.Magic(mime=True)
#     mime_type = mime.from_buffer(file_bytes)
#     return mime_type


# def guess_file_extension(file_bytes: bytes) -> str:
#     """Guess the file extension based on the file content."""
#     try:
#         import magic
#     except ImportError as e:
#         raise ImportError(
#             "magic package not found, please install it with `pip install python-magic`"
#         ) from e

#     magic_obj = magic.Magic()
#     file_type = magic_obj.from_buffer(file_bytes)
#     extension = mimetypes.guess_extension(file_type)

#     if extension:
#         return extension.lstrip('.')  # Remove the leading dot from the extension
#     else:
#         raise ValueError(f"Unable to determine file extension for file type: {file_type}")

