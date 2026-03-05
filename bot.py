import discord
import os
from google import genai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client_gemini = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

chat_history = {}

@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")

@client.event
async def on_message(message):

    if message.author.bot:
        return

    user_id = message.author.id

    if message.content == "/reset":
        chat_history[user_id] = []
        await message.channel.send("会話履歴をリセットしました。")
        return

    if client.user in message.mentions:

        prompt = message.content.replace(f"<@{client.user.id}>", "").strip()

        if prompt == "":
            return

        if user_id not in chat_history:
            chat_history[user_id] = []

        chat_history[user_id].append(f"User: {prompt}")

        conversation = "\n".join(chat_history[user_id])

        response = client_gemini.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=conversation,
        )

        reply = response.text

        chat_history[user_id].append(f"AI: {reply}")

        for i in range(0, len(reply), 2000):
            await message.channel.send(reply[i:i+2000])

client.run(DISCORD_TOKEN)
