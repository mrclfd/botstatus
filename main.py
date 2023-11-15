from logging import(
    basicConfig, 
    getLogger,
    INFO
)

from decouple import config

from time import time
from pytz import utc, timezone
from datetime import datetime

from asyncio import sleep

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.functions import messages

basicConfig(
    level=INFO, 
    format="%(message)s"
)
log = getLogger()


try:
    SSTR = config("SSTR")
    BOTS = config("BOTS").splitlines()
    CHID = config("CHID", cast=int)
    EDIT = config("EDIT", cast=int)
except BaseException as e:
    log.info(e)
    exit(1)
log.info("Connecting...")


try:
    client = TelegramClient(
        StringSession(SSTR), 
        api_id=2040, 
        api_hash="b18441a1ff607e10a989891a5462e627"
    ).start()
except BaseException as e:
    log.warning(e)
    exit(1)


async def _checkup():
    start = time()
    result = {}
    log.info("Checking...")
    for bot in BOTS:
        try:
            check = await client.send_message(
                bot, 
                "/start"
            )
            await sleep(5)
            history = await client(
                messages.GetHistoryRequest(
                    peer=bot,
                    offset_id=0,
                    offset_date=None,
                    add_offset=0,
                    limit=1,
                    max_id=0,
                    min_id=0,
                    hash=0,
                )
            )
            if check.id == history.messages[0].id:
                result[bot] = {"status": "OFF"}
            else:
                result[bot] = {"status": "ON"}
        except BaseException:
            result[bot] = {"status": "OFF"}
        await client.send_read_acknowledge(bot)

        log.info(f"[{result[bot]['status']}] {bot}")

    end = time()
    log.info("Completed!")
    
    msg = ""

    for bot, value in result.items():
        msg += (
            f"~~{bot}~~\n" 
            if result[bot]["status"] == "OFF"
            else f"{bot}\n"
        )
    
    utctime = datetime.now(utc)
    current = utctime.astimezone(timezone("Asia/Jakarta"))
    ftime = current.strftime("%b %-d, %-I:%M %p")
    
    msg += f"\n{ftime}"
    
    taken = end - start
    hours = int(taken // 3600)
    mins = int((taken % 3600) // 60)
    secs = int(taken % 60)
    
    msg += "\n" 
    
    if hours > 0:
        msg += f"{hours}h "
    if mins > 0:
        msg += f"{mins}m "
    if secs > 0:
        msg += f"{secs}s "


    try:
        await client.edit_message(
            CHID,
            EDIT,
            msg,
        )
    except BaseException:
        log.warning("Unable to edit message!")
        return


client.loop.run_until_complete(_checkup())