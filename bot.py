import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import httpx

# Configuration
GLM_API_KEY = os.getenv("GLM_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# GLM 4.7 Coding Model
MODEL_NAME = "glm-4.7-coding"


async def call_glm_api(prompt: str) -> str:
    """Call GLM 4.7 Coding API with the given prompt."""
    headers = {
        "Authorization": f"Bearer {GLM_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 4096
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(GLM_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # Extract the response content
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                return "Error: No response from GLM API"
    except httpx.HTTPError as e:
        return f"HTTP Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    welcome_message = (
        "Hello! I'm a bot powered by GLM 4.7 Coding model.\n\n"
        "Just send me a message and I'll respond using the GLM API.\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show help message"
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_message = (
        "I can help you with coding questions using the GLM 4.7 Coding model.\n\n"
        "Just send me any coding question or request, and I'll do my best to help!\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages."""
    user_message = update.message.text

    # Send typing indicator
    await update.message.chat.send_action("typing")

    # Get response from GLM API
    response = await call_glm_api(user_message)

    # Send response (Telegram has a 4096 character limit per message)
    if len(response) > 4096:
        # Split into chunks if too long
        for i in range(0, len(response), 4096):
            await update.message.reply_text(response[i:i+4096])
    else:
        await update.message.reply_text(response)


def main() -> None:
    """Start the bot."""
    if not GLM_API_KEY:
        raise ValueError("GLM_API_KEY environment variable is not set")
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
