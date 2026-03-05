import discord
import os
from google import genai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client_gemini = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 履歴保存
chat_history = {}

SYSTEM_PROMPT = """
あなたはDiscordで動く親切なAIアシスタント「うちも」です。
自然な日本語で会話してください。
回答は必ず1つだけにしてください。
選択肢形式は使わないでください。
"""

# 履歴最大数
MAX_HISTORY = 10


@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")


@client.event
async def on_message(message):

    if message.author.bot:
        return

    # ======================
    # 履歴キー
    # ======================
    guild_id = message.guild.id if message.guild else "dm"
    user_id = message.author.id
    history_key = f"{guild_id}-{user_id}"

    # ======================
    # リセットコマンド
    # ======================
    if message.content == "/reset":
        chat_history[history_key] = []
        await message.channel.send("会話履歴をリセットしました。")
        return

    # ======================
    # メンション確認
    # ======================
    if not message.content.startswith(f"<@{client.user.id}>") and not message.content.startswith(f"<@!{client.user.id}>"):
        return

    prompt = message.content.replace(f"<@{client.user.id}>", "").replace(f"<@!{client.user.id}>", "").strip()

    if prompt == "":
        return

    # ======================
    # 履歴初期化
    # ======================
    if history_key not in chat_history:
        chat_history[history_key] = []

    chat_history[history_key].append(f"User: {prompt}")

    # ======================
    # 履歴制限
    # ======================
    chat_history[history_key] = chat_history[history_key][-MAX_HISTORY:]

    conversation = SYSTEM_PROMPT + "\n" + "\n".join(chat_history[history_key])

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

    chat_history[history_key].append(f"AI: {reply}")

    # ======================
    # Discord文字制限
    # ======================
    for i in range(0, len(reply), 2000):
        await message.channel.send(reply[i:i+2000])


client.run(DISCORD_TOKEN)
