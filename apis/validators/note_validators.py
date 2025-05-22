from pydantic import BaseModel, Field, field_validator
from typing import Any, Optional
from uuid import UUID
from collections.abc import Iterable

# all the accepted cntent types
ACCEPTED_CONTENT_TYPES = [
    # Images
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/bmp",
    "image/svg+xml",
    # Videos
    "video/mp4",
    "video/webm",
    "video/ogg",
    "video/3gpp",
    "video/3gpp2",
    "video/x-msvideo",
    "video/x-matroska",
    "video/quicktime",
    # Audio
    "audio/mpeg",
    "audio/ogg",
    "audio/wav",
    "audio/webm",
    "audio/aac",
    "audio/mp4",
    "audio/3gpp",
    "audio/3gpp2",
    "audio/x-ms-wma",
]

# create note validator for the validation of the notes with coontent types, collaborators
class CreateNoteValidator(BaseModel):
    title: str = Field(max_length=300)
    note: str
    files: Any
    collaborators: Optional[list[UUID]] = None

    @field_validator("files")
    @classmethod
    def validate_files(cls, files):
        if not isinstance(files, Iterable):
            raise ValueError("Files must be iterable.")

        for file in files:
            # file type validation
            if file.content_type not in ACCEPTED_CONTENT_TYPES:
                raise ValueError("Not a valid file type.")

            # file size check of max 25mb
            if file.size > 25 * 1024 * 1024:
                raise ValueError("Image too large, max 25MB.")

        return files
