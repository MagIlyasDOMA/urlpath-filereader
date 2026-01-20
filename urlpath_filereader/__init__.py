import requests, chardet, os
from pathlib import Path
from typing import Literal, Optional
from urllib.parse import urlparse
from pathlike_typing import PathLike

__version__ = "1.2.0"
__all__ = ['__version__', 'detect_encoding', 'is_url', 'read_file', 'FileOpenMode', 'create_file_from_url', 'open_plus']

FileOpenMode = Literal[
    "r+", "+r", "rt+", "r+t", "+rt", "tr+", "t+r", "+tr", "w+", "+w", "wt+", "w+t", "+wt",
    "tw+", "t+w", "+tw", "a+", "+a", "at+", "a+t", "+at", "ta+", "t+a", "+ta", "x+", "+x",
    "xt+", "x+t", "+xt", "tx+", "t+x", "+tx", "w", "wt", "tw", "a", "at", "ta", "x", "xt",
    "tx", "r", "rt", "tr", "U", "rU", "Ur", "rtU", "rUt", "Urt", "trU", "tUr", "Utr"]


def detect_encoding(file_path: PathLike):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        return result['encoding']


def is_url(source: PathLike) -> bool:
    parsed = urlparse(str(source))
    return bool(parsed.scheme and parsed.netloc)


def read_file(source: PathLike) -> str:
    if is_url(source):
        response = requests.get(source)
        response.raise_for_status()
        return response.text
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {source}")
    return path.read_text(detect_encoding(path))

def create_file_from_url(source: PathLike, encoding: str) -> str:
    if is_url(source):
        source = source.replace('//', '_').replace('/', '_')
        with open(source, 'w', encoding=encoding) as file:
            file.write(requests.get(source).text)
    return source


def open_plus(source: PathLike, mode: FileOpenMode = 'r', buffering: int = -1, encoding: Optional[str] = None,
              errors: Optional[str] = None, newline: Optional[str] = None, closefd: bool = True,
              auto_detect_encoding: bool = False):
    source = create_file_from_url(source.replace('\\', '/'), encoding)
    auto_encoding = detect_encoding(source) if auto_detect_encoding else None
    encoding = encoding or auto_encoding or os.environ['DEFAULT_ENCODING']
    return open(source, mode, buffering, encoding, errors, newline, closefd)
