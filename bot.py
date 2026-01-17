import os
import sys
import asyncio
import logging
import time
import hmac
import hashlib
import base64
import json
from typing import Optional
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import httpx

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
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# GLM 4.7 Coding model name
MODEL_NAME = os.getenv("GLM_MODEL", "glm-4.7")

logger.info(f"GLM_API_KEY set: {bool(GLM_API_KEY)}")
logger.info(f"TELEGRAM_BOT_TOKEN set: {bool(TELEGRAM_BOT_TOKEN)}")
logger.info(f"Using model: {MODEL_NAME}")


def generate_glm_token(api_key: str, exp_seconds: int = 3600) -> str:
    """
    Generate JWT token for GLM API.
    GLM API key format: id.secret
    """
    try:
        parts = api_key.split(".")
        if len(parts) != 2:
            logger.warning("API key doesn't match expected 'id.secret' format, using as-is")
            return api_key

        api_id, api_secret = parts

        # Header
        header = {
            "alg": "HS256",
            "sign_type": "SIGN"
        }

        # Payload
        now = int(time.time())
        payload = {
            "api_key": api_id,
            "exp": now + exp_seconds,
            "timestamp": now
        }

        # Encode header and payload
        header_encoded = base64.urlsafe_b64encode(
            json.dumps(header, separators=(',', ':')).encode()
        ).rstrip(b'=').decode()

        payload_encoded = base64.urlsafe_b64encode(
            json.dumps(payload, separators=(',', ':')).encode()
        ).rstrip(b'=').decode()

        # Signature
        message = f"{header_encoded}.{payload_encoded}"
        signature = hmac.new(
            api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()

        signature_encoded = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()

        return f"{message}.{signature_encoded}"
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        return api_key


async def call_glm_api(prompt: str) -> str:
    """Call GLM API with the given prompt."""
    if not GLM_API_KEY:
        return "Error: GLM_API_KEY not configured"

    # Generate JWT token
    token = generate_glm_token(GLM_API_KEY)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 4096
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(GLM_API_URL, headers=headers, json=payload)

            logger.info(f"API response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                else:
                    return f"Error: Unexpected response format: {data}"
            else:
                logger.error(f"API response: {response.text}")
                return f"HTTP Error {response.status_code}: {response.text}"
    except httpx.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        return f"HTTP Error: {str(e)}"
    except Exception as e:
        logger.error(f"Error calling GLM API: {e}")
        return f"Error: {str(e)}"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    welcome_message = (
        "Hello! I'm a bot powered by GLM API.\n\n"
        "Just send me a message and I'll respond.\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show help message"
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_message = (
        "I can help you with coding questions using the GLM API.\n\n"
        "Just send me any coding question or request, and I'll do my best to help!\n\n"
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
