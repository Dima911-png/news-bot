# Moscow Telegram autopost starter

This repo contains a Telegram channel news autoposter. Configure GitHub Actions secrets before running.

## Setup
1. Create a Telegram bot using @BotFather.
2. Create a channel and add the bot as admin with posting permission.
3. Add repository Actions secrets: TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID; GEMINI_API_KEY is optional.
4. Open Actions and manually run the workflow to test.

RSS provider and GitHub Actions may impose limits; free AI APIs also have quotas. This is not unlimited or guaranteed 24/7. News source URLs are attached; manually review initial output.
