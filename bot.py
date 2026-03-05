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

SYSTEM_PROMPT = """
あなたはDiscordで動く親切なAIアシスタント「うちも」です。
自然な日本語で会話してください。
回答は必ず1つだけにしてください。
選択肢のような回答はしないでください。
"""

MAX_HISTORY = 10


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

    if client.user in message.mentions:

        prompt = message.content.replace(f"<@{client.user.id}>", "").strip()

        if prompt == "":
            return

        if user_id not in chat_history:
            chat_history[user_id] = []

        chat_history[user_id].append(f"User: {prompt}")

        # 履歴制限
        chat_history[user_id] = chat_history[user_id][-MAX_HISTORY:]

        conversation = SYSTEM_PROMPT + "\n" + "\n".join(chat_history[user_id])

        try:
            async with message.channel.typing():

                response = client_gemini.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=conversation,
                )

                reply = response.text

        except Exception as e:
            print(e)
            await message.channel.send("エラーが発生しました。")
            return

        chat_history[user_id].append(f"AI: {reply}")

        # Discordは2000文字制限
        for i in range(0, len(reply), 2000):
            await message.channel.send(reply[i:i+2000])


client.run(DISCORD_TOKEN)
