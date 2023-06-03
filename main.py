from typing import Optional, List

from dotenv import dotenv_values
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from fastapi.middleware.cors import CORSMiddleware

from models import DaySong, SongOrder
from models import Song

app = FastAPI()

origins = [
    "http://localhost",
    "http://192.168.100.130",
    "http://localhost:8080",
    "http://localhost:5173",
    "http://192.168.100.130:8000",
    "http://192.168.100.130:5173",
    "http://10.116.5.54:5173",
    "http://169.254.111.140:5173",
    "http://169.254.111.140"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = dotenv_values(".env")

client = MongoClient(config["ATLAS_URI"], server_api=ServerApi('1'))

db = client.KnowTheChord


@app.get("/autocomplete")
async def autocomplete_song(song):
    if song is None:
        return

    pipeline = [
        {"$search": {"autocomplete": {"query": song, "path": "title"}}},
        {"$limit": 5},
    ]

    return list(db["songs"].aggregate(pipeline))


@app.get("/day_songs")
async def get_day_songs(page_number: Optional[int] = 1, page_size: Optional[int] = 10):
    skips = page_size * (page_number - 1)
    cursor = db["day_songs"].find().skip(skips).limit(page_size)
    day_songs = [doc for doc in cursor]

    return sorted(day_songs, key=lambda day_song: day_song["updateAt"], reverse=True)


@app.get("/day_songs/{day_id}")
async def get_day_song(day_id):
    day_song = db["day_songs"].find_one({"_id": day_id})
    return day_song


@app.post("/day_songs")
async def create_update_day_song(day_song: DaySong):
    db["day_songs"].update_one({"_id": day_song.id}, {"$set": jsonable_encoder(day_song)}, upsert=True)
    return day_song


@app.post("/songs")
async def create_update_song(song: Song):
    song.id = song.title
    db["songs"].update_one({"_id": song.id}, {"$set": jsonable_encoder(song)}, upsert=True)
    return song


@app.put("/day_song_order/{day_id}")
async def update_song_order(day_id: str, song_orders: List[SongOrder]):
    song_orders_dicts = [song_order.dict() for song_order in song_orders]
    db["day_songs"].update_one({"_id": day_id}, {"$set": {"songsOrder": song_orders_dicts}})


@app.delete("/day_songs/{day_id}")
async def delete_day_song(day_id: str):
    db["day_songs"].delete_one({"_id": day_id})
