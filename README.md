# 🏈 UFL Roster Intel Bot

A serverless Python automation pipeline that monitors United Football League (UFL) roster transactions, validates the data against a PostgreSQL database to prevent duplicates, and broadcasts real-time alerts to a Discord community via Webhooks.

Built to demonstrate end-to-end data scraping, cloud-based CI/CD scheduling, and relational database state management.

## 🏗️ Architecture & Tech Stack

- **Language:** Python 3.13
- **Data Extraction:** `requests` & `BeautifulSoup4`
- **State Management:** PostgreSQL (via `psycopg2`) hosted on Neon.tech
- **Delivery:** Discord Webhooks (JSON payload formatting)
- **CI/CD & Automation:** GitHub Actions (Ubuntu-latest runners)

## 🧠 Engineering Highlights

When designing this pipeline, several architectural decisions were made to ensure data integrity and cloud compute efficiency:

### 1. Database-Driven State Management

Instead of relying on flat text files for state tracking, this bot uses a **PostgreSQL** database.
Every time new transactions are found, the script generates a cryptographic hash (`MD5`) of the data and queries the database.

- If the hash exists, the script gracefully terminates, ensuring idempotency.
- If the hash is new, the script inserts the transaction into an audit log table and fires the webhook.
- **Why this matters:** It guarantees data integrity, prevents duplicate alerts, and creates a historical dataset of UFL transactions for future analytics.

### 2. Serverless Execution

The bot runs entirely in the cloud using **GitHub Actions**. It executes on an hourly CRON schedule. This approach removes the need for a dedicated, always-on server (like an EC2 instance), drastically reducing compute overhead while maintaining high availability.

## 🚀 Local Setup & Installation

To run this project locally for development or testing:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/ufl-roster-bot.git](https://github.com/yourusername/ufl-roster-bot.git)
   cd ufl-roster-bot
   ```
