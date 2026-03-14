import asyncio
import logging
import os
from collections import defaultdict
from typing import Any

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "Ты полезный AI-помощник для чата в Telegram. Отвечай кратко и по делу.",
)
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "10"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# История диалога по пользователям: role/content пары
history: dict[int, list[dict[str, str]]] = defaultdict(list)


async def ask_llm(user_id: int, text: str) -> str:
    """Отправляет сообщение в OpenAI-совместимый API и возвращает ответ модели."""
    if not OPENAI_API_KEY:
        return (
            "OPENAI_API_KEY не найден. Добавь его в переменные окружения, "
            "чтобы включить AI-ответы."
        )

    user_history = history[user_id]
    user_history.append({"role": "user", "content": text})

    # Ограничиваем историю, чтобы не переполнять контекст.
    history[user_id] = user_history[-MAX_HISTORY_MESSAGES:]

    payload: dict[str, Any] = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history[user_id],
        ],
        "temperature": 0.7,
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OPENAI_BASE_URL}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                data = await response.json()

                if response.status >= 400:
                    logger.error("LLM API error %s: %s", response.status, data)
                    return "Ошибка AI API. Проверь ключ, модель и base URL."

                answer = data["choices"][0]["message"]["content"].strip()
                history[user_id].append({"role": "assistant", "content": answer})
                history[user_id] = history[user_id][-MAX_HISTORY_MESSAGES:]
                return answer

    except asyncio.TimeoutError:
        return "AI не ответил вовремя. Попробуй ещё раз."
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected LLM request error: %s", exc)
        return "Неожиданная ошибка при запросе к AI."


async def start_handler(message: Message) -> None:
    await message.answer(
        "Привет! Я твой AI-чат 🤖\n"
        "Просто отправь текст, и я отвечу.\n"
        "Команда /clear — очистить историю диалога."
    )


async def clear_handler(message: Message) -> None:
    history.pop(message.from_user.id, None)
    await message.answer("История очищена ✅")


async def chat_handler(message: Message) -> None:
    if not message.from_user:
        return

    response = await ask_llm(message.from_user.id, message.text)
    await message.answer(response)


async def main() -> None:
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN не задан в переменных окружения.")

    bot = Bot(TELEGRAM_TOKEN)
    dp = Dispatcher()

    dp.message.register(start_handler, CommandStart())
    dp.message.register(clear_handler, F.text == "/clear")
    dp.message.register(chat_handler, F.text)

    logger.info("Bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
