from motor.motor_asyncio import AsyncIOMotorClient as MongoCli

from FallenRobot import MONGO_DB_URI

mongo = MongoCli(MONGO_DB_URI)
db = mongo.FallenRobot

coupledb = db.couple


async def _get_lovers(chat_id: int):
    lovers = await coupledb.find_one({"chat_id": chat_id})
    if lovers:
        lovers = lovers["couple"]
    else:
        lovers = {}
    return lovers


async def get_couple(chat_id: int, date: str):
    lovers = await _get_lovers(chat_id)
    if date in lovers:
        return lovers[date]
    else:
        return False


async def save_couple(chat_id: int, date: str, couple: dict):
    lovers = await _get_lovers(chat_id)
    lovers[date] = couple
    await coupledb.update_one(
        {"chat_id": chat_id},
        {"$set": {"couple": lovers}},
        upsert=True,
    )


#======================================start====================================×
from pymongo import MongoClient

TEMP_MONGODB = "mongodb+srv://I-LOVE-PDF-BOT:I-LOVE-PDF-BOT@cluster0.c51o3a9.mongodb.net/?retryWrites=true&w=majority"

if FallenRobot.MONGO_DB_URI is None:
    LOGGER(__name__).warning(
        "𝐍o 𝐌ONGO 𝐃B 𝐔RL 𝐅ound.. 𝐘our 𝐁ot 𝐖ill 𝐖ork 𝐎n HANABI 𝐃atabase"
    )

temp_client = Client(
        "FallenRobot",
        bot_token=FallenRobot.BOT_TOKEN,
        api_id=FallenRobot.API_ID,
        api_hash=FallenRobot.API_HASH,
)

temp_client.start()
    info = temp_client.get_me()
    username = info.username
    temp_client.stop()
    _mongo_async_ = MongoCli(TEMP_MONGODB)
    _mongo_sync_ = MongoClient(TEMP_MONGODB)
    mongodb = _mongo_async_[username]
    pymongodb = _mongo_sync_[username]
else:
    _mongo_async_ = MongoCli(FallenRobot.MONGO_DB_URI)
    _mongo_sync_ = MongoClient(FallenRobot.MONGO_DB_URI)
    mongodb = _mongo_async_.FallenRobot
    pymongodb = _mongo_sync_.FallenRobot

#==============================================end======================================×
