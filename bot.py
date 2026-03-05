import discord
import os
from google import genai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client_gemini = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 会話履歴
chat_history = {}

MAX_HISTORY = 10

SYSTEM_PROMPT = """
あなたはDiscordで動くAIアシスタント「うちも」です。
変な人格は出さないように、親切で自然な日本語で会話してください。
自分のことは「私」と呼びます。
回答は必ず1つだけにしてください。
"""

@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")

@client.event
async def on_message(message):

    if message.author.bot:
        return

    user_id = message.author.id

    # 履歴リセット
    if message.content == "/reset":
        chat_history[user_id] = []
        await message.channel.send("会話履歴をリセットしました。")
        return

    # メンションされたときだけ反応
    if client.user in message.mentions:

        prompt = message.content.replace(f"<@{client.user.id}>", "").strip()

        if prompt == "":
            return

        if user_id not in chat_history:
            chat_history[user_id] = []

        # ユーザー履歴追加
        chat_history[user_id].append({
            "role": "user",
            "parts": [prompt]
        })

        # 履歴制限
        chat_history[user_id] = chat_history[user_id][-MAX_HISTORY:]

        contents = [
            {
                "role": "user",
                "parts": [SYSTEM_PROMPT]
            }
        ] + chat_history[user_id]

        try:
            async with message.channel.typing():

                response = client_gemini.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents
                )

                reply = response.text.strip()

        except Exception as e:
            print(e)
            await message.channel.send("エラーが発生しました。")
            return

        # AI履歴追加
        chat_history[user_id].append({
            "role": "model",
            "parts": [reply]
        })

        # Discord2000文字制限
        for i in range(0, len(reply), 2000):
            await message.channel.send(reply[i:i+2000])

client.run(DISCORD_TOKEN)
