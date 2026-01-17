# Telegram Chat Mashup Bot - Implementation Plan

## Overview
A Telegram bot that monitors a group chat, saves messages to text files, and periodically generates a "mashup" - a surreal remix of things people actually said using GLM 4.7.

## Architecture Decisions

### Storage
- **Location**: Local filesystem (MacBook server for privacy)
- **Format**: One `.txt` file per interval
- **File naming**: `messages_YYYYMMDD_HHMMSS.txt`
- **No GitHub** - chat data stays private

### Group Support
- **Single group only** - simpler, saves API quota

### Mashup Trigger
- **Random timing** - completely unpredictable
- **Configurable probability window**

### Mashup Style
- Uses GLM 4.7 to intelligently remix messages
- Preserves original wording
- Semi-coherent, dream-logic flow
- Not random gibberish

---

## Configuration

### Environment Variables (.env)
```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token
GLM_API_KEY=your_glm_coding_plan_key
ALLOWED_USERS=username1,username2  # Telegram usernames who can configure

# Optional (with defaults)
SAVE_INTERVAL_MINUTES=60           # How often to start a new message file
MASHUP_MIN_INTERVAL_HOURS=2        # Minimum time between mashups
MASHUP_MAX_INTERVAL_HOURS=12       # Maximum time between mashups
MASHUP_MIN_FILES=2                 # Minimum source files to use
MASHUP_MAX_FILES=5                 # Maximum source files to use
CHAT_ID=                           # If restricting to one group
```

### Telegram Commands (authorized users only)
- `/status` - Show bot status, file count, last mashup time
- `/mashup` - Trigger mashup manually
- `/set_interval <minutes>` - Change save interval
- `/set_mashup_range <min> <max>` - Set hours range for random mashup timing

---

## File Structure

```
chat-mashup-bot/
├── bot.py              # Main bot logic
├── messages/           # Directory for chat logs
│   ├── messages_20250118_143000.txt
│   ├── messages_20250118_150000.txt
│   └── ...
├── mashups/            # Directory for generated mashups (optional)
├── config.py           # Configuration handling
├── requirements.txt
└── .env
```

---

## Master Prompt for GLM 4.7

```
You are a chaotic remixer of group chat conversations. Your job is to take raw message logs and produce a "mashup" - a surreal, semi-coherent remix of what was actually said.

HOW IT WORKS:
1. Extract the actual message content from logs (ignore timestamps, usernames, metadata)
2. Select interesting phrases, sentences, or complete messages
3. Rearrange and combine them into something that flows
4. The result should feel like a conversation that almost makes sense, but is delightfully off

THE VIBE:
- Think "dream logic" or "half-remembered conversation"
- It should be readable and have grammatical structure
- Contextual connections between phrases earn bonus points
- Absurd juxtapositions are good, but total randomness is lazy

RULES:
- ONLY use phrases that appear in the provided logs
- Preserve original wording exactly - don't paraphrase
- You MAY add: articles, prepositions, conjunctions to glue things together
- You MAY NOT: add new ideas, change meaning, or invent content
- Output 3-8 sentences
- No preamble, no explanation, no "here's your mashup"

EXAMPLES:

Good mashup from a gaming chat:
"bro I literally died because my cat sat on my keyboard and now I'm banned from the server until someone fixes the router which my roommate allegedly broke while making toast at 3am"

Good mashup from a work chat:
"the deployment failed because Karen brought a cake to the sprint planning and now nobody can find the documentation for that API we definitely wrote last quarter"

WHAT NOT TO DO:
- "The people discussed gaming and food" (too vague, uses none of their words)
- "I am an AI creating a remix" (meta-commentary is banned)
- Random word salad with no grammar (lazy, not funny)

NOW PROCESS THESE LOGS:
{logs}
```

---

## Implementation Steps

1. **Set up basic bot structure**
   - python-telegram-bot framework
   - Message handler for group chats
   - File writer for saving messages

2. **Implement interval-based file rotation**
   - Timer that starts new file every N minutes
   - Creates `messages/` directory if not exists

3. **Random mashup scheduler**
   - Background task that runs at random intervals
   - Selects random files from `messages/`
   - Calls GLM 4.7 with master prompt

4. **Authorization system**
   - Check if user is in ALLOWED_USERS
   - Only allow commands from authorized users

5. **Telegram commands**
   - /status, /mashup, /set_interval, /set_mashup_range

6. **Testing**
   - Local testing first
   - Then deploy to MacBook server

---

## Message File Format

Each file contains raw messages with timestamps and usernames for context:

```
=== Chat Log Started: 2025-01-18 14:30:00 ===

[2025-01-18 14:30:15] @john: bro anyone else having connection issues
[2025-01-18 14:30:42] @jane: nah mine is fine
[2025-01-18 14:31:03] @mike: my cat sat on my keyboard again
[2025-01-18 14:31:45] @john: LMAO
[2025-01-18 14:32:10] @sarah: wait what happened
[2025-01-18 14:33:00] @mike: i queued for ranked and now im banned
...

=== Chat Log Ended: 2025-01-18 15:30:00 ===
```

---

## MacBook Server Setup Notes

When ready to deploy to MacBook as 24/7 server:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create .env file**
   ```bash
   cp .env.example .env
   # Edit .env with your tokens
   ```

3. **Run as service**
   - Use launchd (macOS native) to keep bot running
   - Or use `screen`/`tmux` for simple sessions
   - Consider `supervisor` for more robust process management

4. **Auto-start on boot**
   - Create a launchd plist file
   - Place in `~/Library/LaunchAgents/`

Example launchd plist:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.chatmashupbot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/chat-mashup-bot/bot.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/path/to/chat-mashup-bot</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
```

---

## Future Enhancements (Optional)

- Database storage instead of files (SQLite, PostgreSQL)
- Web dashboard to view mashups and stats
- Different mashup "modes" (coherent vs chaotic)
- Filter messages by user
- Export mashups as images
- Multi-group support with per-group storage

---

## Notes for Next Session

- User has MacBook Pro 16 2019 - will use as local server for privacy
- User has unlimited GLM Coding Plan API
- Focus on getting basic functionality working first
- Master prompt may need iteration based on results
- Consider adding visualization/stats of chat activity
