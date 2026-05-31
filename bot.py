import os
import requests
import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)


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

    data = requests.get(url, params=params).json()

    return data["translation"]


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
        await message.reply(
            "Reply to a message and mention me."
        )
        return

    try:
        referenced = await message.channel.fetch_message(
            message.reference.message_id
        )

        translated = translate(referenced.content)

        await message.reply(
            f" **Translation:**\n{translated}"
        )

    except Exception as e:
        await message.reply(
            f"Translation failed: {e}"
        )


bot.run(TOKEN)
