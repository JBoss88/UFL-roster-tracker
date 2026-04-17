import os
import sys
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
# We'll use the Battlehawks official roster page as the target
TEAM_URL = "https://www.theufl.com/teams/st-louis/roster"
TEAM_NAME = "St. Louis Battlehawks"
TEAM_COLOR = 20614  # Battlehawks Blue Hex code converted to integer

def scrape_active_roster():
    """Scrapes the active roster from the official UFL website."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        res = requests.get(TEAM_URL, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Find the main roster table
        roster_table = soup.find('table')
        if not roster_table:
            return None
            
        rows = roster_table.find_all('tr')[1:] # Skip the header row
        
        offense = []
        defense = []
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                name = cols[0].get_text(strip=True).split('#')[0].strip() # Clean up jersey numbers
                position = cols[1].get_text(strip=True)
                
                # Basic sorting by position
                if position in ['QB', 'RB', 'WR', 'TE', 'OL', 'C', 'G', 'T']:
                    offense.append(f"**{position}** - {name}")
                else:
                    defense.append(f"**{position}** - {name}")
                    
        return offense, defense

    except Exception as e:
        print(f"Error fetching roster data: {e}")
        return None, None

def send_weekend_blast(offense, defense):
    """Packages the data into a clean Discord UI card."""
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK is missing.")
        sys.exit(1)

    # Discord embeds have a character limit, so we join the lists with line breaks
    offense_text = "\n".join(offense)[:1024]
    defense_text = "\n".join(defense)[:1024]

    payload = {
        "content": f"🏈 **WEEKEND ROSTER BLAST: {TEAM_NAME}** 🏈\nHere is who is taking the field this weekend.",
        "embeds": [
            {
                "title": "Offensive Unit",
                "description": offense_text,
                "color": TEAM_COLOR
            },
            {
                "title": "Defensive & Special Teams Unit",
                "description": defense_text,
                "color": TEAM_COLOR,
                "footer": {"text": "UFL Automated Roster Bot"}
            }
        ]
    }

    response = requests.post(WEBHOOK_URL, json=payload)
    response.raise_for_status()
    print("Weekend Roster Blast successfully sent!")

def main():
    print(f"Scraping active roster for {TEAM_NAME}...")
    offense, defense = scrape_active_roster()
    
    if not offense and not defense:
        print("Could not find roster data. The UFL website layout may have changed.")
        sys.exit(1)
        
    send_weekend_blast(offense, defense)

if __name__ == "__main__":
    main()