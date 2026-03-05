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
選択肢形式の回答はしないでください。
"""

MAX_HISTORY = 10


@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")


@client.event
async def on_message(message):

    # Botの発言は無視
    if message.author.bot:
        return

    # メンションされていなければ無視（2重返信防止）
    if f"<@{client.user.id}>" not in message.content:
        return

    user_id = message.author.id

    # 履歴リセット
    if message.content.strip() == "/reset":
        chat_history[user_id] = []
        await message.channel.send("会話履歴をリセットしました。")
        return

    # メンション削除
    prompt = message.content.replace(f"<@{client.user.id}>", "").strip()

    if prompt == "":
        return

    # 履歴初期化
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

            reply = response.text.strip()

    except Exception as e:
        print(e)
        await message.channel.send("エラーが発生しました。")
        return

    # 履歴保存
    chat_history[user_id].append(f"AI: {reply}")

    # Discord2000文字制限対策
    for i in range(0, len(reply), 2000):
        await message.channel.send(reply[i:i+2000])


client.run(DISCORD_TOKEN)
