import os
import requests
import discord
import logging
from flask import Flask
from threading import Thread


TOKEN = os.environ["DISCORD_TOKEN"]

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()


# ✅ FIXED TRANSLATE (safe + no crash on bad response)
def translate(text):
    url = "https://translate-pa.googleapis.com/v1/translate"

    params = {
        "params.client": "gtx",
        "dataTypes": "TRANSLATION",
        "key": "AIzaSyDLEeFI5OtFBwYBIoK_jj5m32rZK5CkCXA",
        "query.sourceLanguage": "auto",
        "query.targetLanguage": "en",
        "query.text": text,
    }

    try:
        data = requests.get(url, params=params, timeout=10).json()

        # safer extraction (API sometimes changes structure)
        return data.get("translation") or "⚠️ Translation unavailable"

    except Exception:
        return "⚠️ Translation failed"


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # ✅ CLEAN TRIGGER LOGIC (FIXED)
    is_mentioned = bot.user in message.mentions
    is_reply = message.reference is not None

    # must be either mention OR reply
    if not (is_mentioned or is_reply):
        return

    try:
        # ✅ If reply → translate replied message
        if message.reference:
            referenced = await message.channel.fetch_message(
                message.reference.message_id
            )
        else:
            # if only mention but no reply
            await message.reply("Reply to a message to translate it.")
            return

        translated = translate(referenced.content)

        embed = discord.Embed(
            title="Translation",
            description=translated,
        )

        embed.set_author(
            name=referenced.author.display_name,
            icon_url=referenced.author.display_avatar.url
        )

        embed.add_field(
            name="Original Message",
            value=referenced.content[:1024],
            inline=False
        )

        embed.set_footer(
            text=f"Requested by {message.author.display_name}",
            icon_url=message.author.display_avatar.url
        )

        await message.reply(embed=embed)

    except Exception:
        await message.reply("⚠️ Couldn't translate that message.")


keep_alive()
bot.run(TOKEN, reconnect=True)
