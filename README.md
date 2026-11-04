# Moscow Telegram autopost

The code and GitHub Actions schedule are now installed in this repository.

## To turn it on (required secrets)

1. Create the Telegram bot with @BotFather and copy its HTTP API token.
2. Make a Telegram channel and add that bot as an administrator with permission to post messages. Set a public channel username (for example, @moscow_news_example).
3. On GitHub open **Settings → Secrets and variables → Actions → New repository secret** and create:
   - `TELEGRAM_BOT_TOKEN` — BotFather token (keep it private; never paste it into chat or commit it).
   - `TELEGRAM_CHANNEL_ID` — channel username such as `@your_channel`.
   - `GEMINI_API_KEY` — optional, Google AI Studio key. If missing, the bot uses RSS title/summary without AI rewrite.
4. Open **Actions → Moscow Telegram autopost → Run workflow** and confirm the branch is `main`; run it.
5. Review the channel output. Scheduled execution is set every 30 minutes (UTC).

## What it does

Collects Moscow headlines from Google News RSS search feeds, filters keyword-matched stories and repeats, optionally asks Gemini to rewrite a short post, then posts with a source link. `bot.py` is the main script and `state.json` keeps duplicate IDs.

## Limits

Not truly unlimited or guaranteed 24/7. RSS feeds may throttle, GitHub Actions has usage policies and scheduled runs can be delayed, and Gemini free-tier use has quotas. The bot does not independently verify claims; source links are attached. Please manually inspect early posts and adjust filters.
