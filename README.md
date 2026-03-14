# second_flowers_bot

Telegram AI-чат бот на `aiogram 3`.

## Что умеет
- отвечает на сообщения через OpenAI-совместимый API;
- хранит краткую историю диалога по каждому пользователю;
- очищает историю командой `/clear`.

## Быстрый старт

1. Установи зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Создай `.env` на основе примера:
   ```bash
   cp .env.example .env
   ```
3. Заполни переменные:
   - `TELEGRAM_BOT_TOKEN` — токен из @BotFather;
   - `OPENAI_API_KEY` — API ключ;
   - `OPENAI_BASE_URL` — URL совместимого API (по умолчанию OpenAI);
   - `OPENAI_MODEL` — модель (например `gpt-4o-mini`).
4. Запусти бота:
   ```bash
   python bot.py
   ```

## Переменные окружения
- `TELEGRAM_BOT_TOKEN` (обязательно)
- `OPENAI_API_KEY` (обязательно для AI ответов)
- `OPENAI_BASE_URL` (по умолчанию `https://api.openai.com/v1`)
- `OPENAI_MODEL` (по умолчанию `gpt-4o-mini`)
- `SYSTEM_PROMPT` (системный промпт)
- `MAX_HISTORY_MESSAGES` (по умолчанию `10`)
