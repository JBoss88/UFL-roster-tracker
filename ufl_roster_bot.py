import os
import sys
import hashlib
import requests
import psycopg2 # New database library
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
DATABASE_URL = os.getenv("DATABASE_URL") # New Secret
TRANSACTIONS_URL = "https://uflnewshub.com/transactions"

def get_latest_transactions():
    """Scrapes the latest UFL transactions from the web."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(TRANSACTIONS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content_div = soup.find('div', class_='entry-content')
        if not content_div: return None, None

        latest_date = content_div.find('h2').get_text(strip=True) if content_div.find('h2') else "Recent Moves"
        transaction_list = content_div.find('ul')
        
        if not transaction_list: return None, None
            
        moves = [li.get_text(strip=True) for li in transaction_list.find_all('li')]
        parsed_moves = "\n".join(f"• {move}" for move in moves)
        
        return latest_date, parsed_moves
    except Exception as e:
        print(f"Error fetching UFL data: {e}")
        return None, None

def generate_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def check_and_save_db(date, moves, intel_hash):
    """Checks Postgres for the hash. If new, saves it and returns True."""
    if not DATABASE_URL:
        print("Error: DATABASE_URL environment variable is missing.")
        sys.exit(1)

    try:
        # Connect to Postgres
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 1. Check if we already have this exact intel
        cur.execute("SELECT id FROM ufl_roster_moves WHERE event_hash = %s", (intel_hash,))
        result = cur.fetchone()

        if result:
            conn.close()
            return False # We already sent this one.

        # 2. If it's new, insert it into our historical audit log
        cur.execute(
            "INSERT INTO ufl_roster_moves (event_date, event_hash, raw_data) VALUES (%s, %s, %s)",
            (date, intel_hash, moves)
        )
        conn.commit()
        conn.close()
        return True # Brand new data!

    except Exception as e:
        print(f"Database error: {e}")
        sys.exit(1)

def send_discord_alert(date, moves):
    """Sends the Webhook."""
    payload = {
        "content": "🚨 **New UFL Roster Update**",
        "embeds": [{
            "title": f"Transactions for {date}",
            "description": moves,
            "color": 3447003,
            "footer": {"text": "UFL Automated Intel Bot • Postgres Verified"}
        }]
    }
    requests.post(WEBHOOK_URL, json=payload)
    print("Successfully broadcasted to Discord!")

def main():
    print("Checking for UFL roster moves...")
    date, moves = get_latest_transactions()
    
    if not moves:
        print("No readable transactions found today.")
        sys.exit(0)

    current_intel = f"{date}-{moves}"
    current_hash = generate_hash(current_intel)
    
    # Send data to our Postgres function
    is_new_data = check_and_save_db(date, moves, current_hash)
    
    if is_new_data:
        print("New transactions verified in Database! Firing webhook...")
        send_discord_alert(date, moves)
    else:
        print("Database confirms no new transactions. Shutting down.")

if __name__ == "__main__":
    main()
    