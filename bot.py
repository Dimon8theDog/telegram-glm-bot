import os
import sys
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from zhipuai import ZhipuAI

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Configuration
GLM_API_KEY = os.getenv("GLM_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MODEL_NAME = os.getenv("GLM_MODEL", "glm-4.7")

logger.info(f"GLM_API_KEY set: {bool(GLM_API_KEY)}")
logger.info(f"TELEGRAM_BOT_TOKEN set: {bool(TELEGRAM_BOT_TOKEN)}")
logger.info(f"Using model: {MODEL_NAME}")


async def call_glm_api(prompt: str) -> str:
    """Call GLM API with the given prompt using official SDK."""
    if not GLM_API_KEY:
        return "Error: GLM_API_KEY not configured"

    try:
        client = ZhipuAI(api_key=GLM_API_KEY)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096,
        )

        logger.info(f"API call successful, model: {MODEL_NAME}")

        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content
        else:
            return "Error: No response from GLM API"

    except Exception as e:
        logger.error(f"Error calling GLM API: {e}")
        # Check if it's an auth/balance error
        error_str = str(e)
        if "1113" in error_str or "余额" in error_str:
            return "Error: API balance issue or invalid API key. Check your Zhipu AI console."
        elif "1211" in error_str or "模型" in error_str:
            return f"Error: Model '{MODEL_NAME}' not found. Check available models in your Zhipu AI console."
        elif "401" in error_str or "auth" in error_str.lower():
            return "Error: Authentication failed. Check your API key."
        return f"Error: {str(e)}"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    welcome_message = (
        f"Hello! I'm a bot powered by {MODEL_NAME}.\n\n"
        "Just send me a message and I'll respond.\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show help message"
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_message = (
        f"I can help you with questions using {MODEL_NAME}.\n\n"
        "Just send me any question or request, and I'll do my best to help!\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages."""
    user_message = update.message.text
    await update.message.chat.send_action("typing")
    response = await call_glm_api(user_message)

    if len(response) > 4096:
        for i in range(0, len(response), 4096):
            await update.message.reply_text(response[i:i+4096])
    else:
        await update.message.reply_text(response)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")


def main() -> None:
    """Start the bot."""
    logger.info("Starting bot...")

    if not GLM_API_KEY:
        logger.error("GLM_API_KEY environment variable is not set!")
        sys.exit(1)
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set!")
        sys.exit(1)

    try:
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        application.add_error_handler(error_handler)

        logger.info("Bot is running...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
