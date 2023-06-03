import uuid
from datetime import datetime

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, root_validator


class ChordType(str, Enum):
    main = "main"
    woman = "woman"
    man = "man"


class Chord(BaseModel):
    value: str = Field(...)
    type: Optional[ChordType]


class Song(BaseModel):
    id: Optional[str] = Field(alias="_id")
    title: str = Field(...)
    artist: Optional[str]
    chords: list[Chord] = Field(...)


class SongOrder(BaseModel):
    title: str = Field(...)
    order: int = Field(...)
    dayChord: str = Field(...)


def get_new_uuid() -> str:
    return str(uuid.uuid4())


class DaySong(BaseModel):
    id: str = Field(default_factory=get_new_uuid, alias="_id")
    day: str = Field(...)
    songsOrder: List[SongOrder]
    updateAt: datetime = datetime.now()

    @root_validator
    def day_song_validator(cls, values):
        values["updateAt"] = datetime.now()
        return values

