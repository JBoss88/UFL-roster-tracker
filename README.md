# UFL Roster Intel Bot

A serverless Python automation pipeline that monitors United Football League (UFL) roster transactions and active rosters, then broadcasts real-time alerts to a Discord community via Webhooks.

Transaction alerts use a PostgreSQL database to validate data and prevent duplicate notifications. Weekly roster blasts scrape the official UFL site and post formatted unit breakdowns every Thursday.

Built to demonstrate end-to-end data scraping, cloud-based CI/CD scheduling, and relational database state management.

## Architecture & Tech Stack

- **Language:** Python 3.13
- **Data Extraction:** `requests` & `BeautifulSoup4`
- **State Management:** PostgreSQL (via `psycopg2`) hosted on Neon.tech
- **Delivery:** Discord Webhooks (JSON payload formatting)
- **CI/CD & Automation:** GitHub Actions (Ubuntu-latest runners)

## Scripts

### `ufl_roster_bot.py` — Transaction Monitor
Scrapes the latest UFL roster moves from [uflnewshub.com](https://uflnewshub.com/transactions). Generates an MD5 hash of each transaction batch and queries the database to check if it has already been sent. If new, it logs the transaction to PostgreSQL and fires a Discord webhook alert.

Runs on an **hourly CRON** schedule via GitHub Actions.

### `active_rosters.py` — Weekly Roster Blast
Scrapes the St. Louis Battlehawks active roster from the official UFL website and posts a formatted Discord embed every **Thursday at 10:00 AM Central** (3:00 PM UTC). The embed separates players into offensive and defensive/special teams units.

Does not require a database — idempotency is handled by the weekly schedule itself.

## Engineering Highlights

### Database-Driven State Management

Instead of relying on flat text files for state tracking, the transaction bot uses a **PostgreSQL** database.
Every time new transactions are found, the script generates a cryptographic hash (`MD5`) of the data and queries the database.

- If the hash exists, the script gracefully terminates, ensuring idempotency.
- If the hash is new, the script inserts the transaction into an audit log table and fires the webhook.
- **Why this matters:** It guarantees data integrity, prevents duplicate alerts, and creates a historical dataset of UFL transactions for future analytics.

### Serverless Execution

Both bots run entirely in the cloud using **GitHub Actions** on Ubuntu runners. This approach removes the need for a dedicated, always-on server, drastically reducing compute overhead while maintaining high availability.

## Local Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jacksonboss/UFL-roster-tracker.git
   cd UFL-roster-tracker
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   ```bash
   export DISCORD_WEBHOOK="your_webhook_url"
   export DATABASE_URL="your_neon_postgres_connection_string"  # required for ufl_roster_bot.py only
   ```

5. **Run locally:**
   ```bash
   python ufl_roster_bot.py      # transaction monitor
   python active_rosters.py      # weekly roster blast
   ```

## GitHub Actions Secrets Required

| Secret | Used By | Description |
|---|---|---|
| `DISCORD_WEBHOOK` | Both scripts | Discord Webhook URL for your server channel |
| `DATABASE_URL` | `ufl_roster_bot.py` | Neon.tech PostgreSQL connection string |
