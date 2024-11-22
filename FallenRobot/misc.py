import socket
import time

import heroku3
from pyrogram import filters

import FallenRobot
from FallenRobot.utils.mongo import mongodb

from .logging import LOGGER

SUDOERS = filters.user()

HAPP = None
clonedb = None
_boot_ = time.time()


def is_heroku():
    return "heroku" in socket.getfqdn()


XCB = [
    "/",
    "@",
    ".",
    "com",
    ":",
    "git",
    "heroku",
    "push",
    str(FallenRobot.HEROKU_API_KEY),
    "https",
    str(FallenRobot.HEROKU_APP_NAME),
    "HEAD",
    "master",
]


def dbb():
    global db
    global clonedb
    clonedb = {}
    db = {}


async def sudo():
    global SUDOERS
    SUDOERS.add(FallenRobot.OWNER_ID)
    sudoersdb = FallenRobot.sudoers
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    sudoers = [] if not sudoers else sudoers["sudoers"]
    if FallenRobot.OWNER_ID not in sudoers:
        sudoers.append(FallenRobot.OWNER_ID)
        await sudoersdb.update_one(
            {"sudo": "sudo"},
            {"$set": {"sudoers": sudoers}},
            upsert=True,
        )
    if sudoers:
        for user_id in sudoers:
            SUDOERS.add(user_id)
    LOGGER(__name__).info(f"𝐎𝐰𝐧𝐞𝐫 + 𝐒𝐮𝐝𝐨 𝐔𝐬𝐞𝐫𝐬 𝐋𝐨𝐚𝐝𝐞𝐝...")


def heroku():
    global HAPP
    if is_heroku:
        if FallenRobot.HEROKU_API_KEY and FallenRobot.HEROKU_APP_NAME:
            try:
                Heroku = heroku3.from_key(FallenRobot.HEROKU_API_KEY)
                HAPP = Heroku.app(FallenRobot.HEROKU_APP_NAME)
                LOGGER(__name__).info(f"𝐇𝐞𝐫𝐨𝐤𝐮 𝐀𝐩𝐩 𝐍𝐚𝐦𝐞 𝐋𝐨𝐚𝐝𝐞𝐝...")
            except BaseException:
                LOGGER(__name__).warning(
                    f"𝐘𝐨𝐮 𝐇𝐚𝐯𝐞 𝐍𝐨𝐭 𝐅𝐢𝐥𝐥𝐞𝐝 𝐇𝐞𝐫𝐨𝐤𝐮 𝐀𝐩𝐢 𝐊𝐞𝐲 𝐀𝐧𝐝 𝐇𝐞𝐫𝐨𝐤𝐮 𝐀𝐩𝐩 𝐍𝐚𝐦𝐞 𝐂𝐨𝐫𝐫𝐞𝐜𝐭... "
                )
