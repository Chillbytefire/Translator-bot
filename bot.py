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
    
    if bot.user not in message.mentions:
        return

    if not message.reference:
        await message.reply("Mention me on a reply to translate.")
        return

    try:
        referenced = await message.channel.fetch_message(
            message.reference.message_id

        if referenced.author.bot:
            await message.reply("Reply to a user's message to translate.")
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
