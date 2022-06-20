#=================================================================================================
# Copyright (C) 2022 by szsupunma 
# Released under the "GNU v3.0 License Agreement".
# All rights reserved. © Asad Ali #Rocks
#=================================================================================================
import os
import json
import asyncio
import requests

from pyrogram.errors import UserNotParticipant
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from RocksAlexaRobot import pbot as app

from RocksAlexaRobot.function.dbfunctions import get_served_users
    

#********************************************************************************
API1='https://api.proxyscrape.com/v2/?request=proxyinfo&protocol='
API2='https://api.proxyscrape.com/v2/?request=getproxies&protocol'
#********************************************************************************

create = InlineKeyboardMarkup(
            [[InlineKeyboardButton("ᴀsᴀᴅ ᴀʟɪ 🇵🇰", url="https://t.me/AsadSupport")]])

#********************************************************************************
@app.on_message(filters.command("socks4"))
async def proxy(_, message: Message):
    try:
       await message._client.get_chat_member(-1001717283097, message.from_user.id)
    except UserNotParticipant:
       await app.send_message(
			chat_id=message.from_user.id,
			text=f"""
🚧 **Access Denied** {message.from_user.mention}
You must,
🔹 : [join Our Telegram Group](https://t.me/Alexa_Help).

@AsadSupport
""")
       return
    name = message.from_user.id
    m =  await app.send_message(name,text=f"♻️ Creating Proxy....",reply_markup = create)
    req=requests.get(f'{API2}=socks4&timeout=10000&country=all').text
    with open(f"SOCKS4.txt", "w") as txt:
     txt.write(req)
     txt.close()
    info=json.loads(requests.get(f'{API1}socks4').text)
    last = info['last_updated'] 
    await app.send_document(name, f"SOCKS4.txt", caption=f"""
**✅ SUCCESSFULLY CREATED ✅**

※ Proxy count : `{str(len(req))}`
※ Lasted Updated : `{last}`

**Powered by** : @AsadSupport """,reply_markup = create)
    await m.delete()
    os.remove(f"SOCKS4.txt")

#********************************************************************************
@app.on_message(filters.command("socks5"))
async def proxy(_, message: Message):
    try:
       await message._client.get_chat_member(-1001717283097, message.from_user.id)
    except UserNotParticipant:
       await app.send_message(
			chat_id=message.from_user.id,
			text=f"""
🚧 **Access Denied** {message.from_user.mention}
You must,
🔹 : [join Our Telegram Group](https://t.me/Alexa_Help).

@AsadSupport
""")
       return
    name = message.from_user.id
    m =  await app.send_message(name,text=f"♻️ Creating Proxy....",reply_markup = create)
    req=requests.get(f'{API2}=socks5&timeout=10000&country=all').text
    with open(f"SOCKS5.txt", "w") as txt:
     txt.write(req)
     txt.close()
    info=json.loads(requests.get(f'{API1}socks5').text)
    last = info['last_updated'] 
    await app.send_document(name, f"SOCKS5.txt", caption=f"""
**✅ SUCCESSFULLY CREATED ✅**

※ Proxy count : `{str(len(req))}`
※ Lasted Updated : `{last}`

**Powered by** : @AsadSupport """ ,reply_markup = create )
    await m.delete()
    os.remove(f"SOCKS5.txt")

#********************************************************************************
@app.on_message(filters.command("http"))
async def proxy(_, message: Message):
    try:
       await message._client.get_chat_member(-1001717283097, message.from_user.id)
    except UserNotParticipant:
       await app.send_message(
			chat_id=message.from_user.id,
			text=f"""
🚧 **Access Denied** {message.from_user.mention}
You must,
🔹 : [join Our Telegram Group](https://t.me/Alexa_Help).

@AsadSupport
""")
       return
    name = message.from_user.id
    m =  await app.send_message(name,text=f"♻️ Creating Proxy....",reply_markup = create)
    req=requests.get(f'{API2}=http&timeout=10000&country=all').text
    with open(f"http.txt", "w") as txt:
     txt.write(req)
     txt.close()
    info=json.loads(requests.get(f'{API1}http').text)
    last = info['last_updated'] 
    await app.send_document(name, f"http.txt", caption=f"""
**✅ SUCCESSFULLY CREATED ✅**

※ Proxy count : `{str(len(req))}`
※ Lasted Updated : `{last}`

**Powered by** : @AsadSupport """,reply_markup = create)
    await m.delete()
    os.remove(f"http.txt")


@app.on_message(filters.private & filters.command("bcast") & filters.user([2042185317,1452370643]) & filters.reply)
async def broadcast_message(_, message):
    b_msg = message.reply_to_message
    chats = await get_served_users() 
    m = await message.reply_text("Broadcast in progress")
    for chat in chats:
        try:
            await broadcast_messages(int(chat['bot_users']), b_msg)
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(int(e.x))
        except Exception:
            pass  
    await m.edit(f"""
Broadcast Completed:.""")


__help__ = """This module can Generate free API base proxies for you! ✅ Https(s) | Socks5 | Socks4 proxies Available.
 *Commands...*
 - `/http` for http.
 - `/socks5` for Sicks5
 - `/socks4` fot Socks4
"""

__mod_name__ = "📱 ᴘʀᴏxʏ"