from dataclasses import dataclass
from io import BytesIO


@dataclass
class DownloadResult:
    contents: bytes


@dataclass
class UploadBody:
    user_id: int
    id: int
    contents: bytes
