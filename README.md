# Heyday Schedule -> Google Calendar Sync

Automatically syncs your Heyday sports schedule from their website to your Google Calendar.

## Features

- Fetches upcoming games from your Heyday schedule
- Creates calendar events with game details (teams, location, time)
- Updates existing events when times change
- Removes events for cancelled games

## Setup

### 1. Create Google Developer Project

1. Go to the Google Cloud Console at https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Navigate to APIs & Services > Library
   - Search for Google Calendar API
   - Click Enable

### 2. Configure OAuth Consent Screen

1. Go to APIs & Services > OAuth consent screen
2. Choose External user type
3. Fill in required application information
4. Add your email to test users
5. In the Scopes section, add the following scope:
   - https://www.googleapis.com/auth/calendar.events

### 3. Create Desktop Application Credentials

1. Go to APIs & Services > Credentials
2. Click Create Credentials > OAuth client ID
3. Select Desktop application as the application type
4. Download the credentials file
5. Rename it to client_secret.json and place it in the project directory

### 4. Setup Heyday Credentials

Set your Heyday login credentials as environment variables or via a heyday_login.json file:

Option 1) environment variables:
```bash
export HEYDAY_USERNAME=your_username
export HEYDAY_PASSWORD=your_password
```

Option 2) heyday_login.json file:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

### 5. Initial Authentication

Run the authentication script to generate your token:

python google_auth.py

This will:
- Open your browser for Google OAuth consent
- Generate a token.json file for future API access
- This only needs to be done once

### 6. Configure Calendar Preferences

You can customize calendar event settings by modifying the constants at the top of `main.py`:

- **GAME_LENGTH_MINS**: Duration to block off on the calendar for each game (default: 60 minutes)
- **GAME_REMINDER_ALERT_MINS**: Minutes before the game to send a reminder alert (default: 30 minutes, set to -1 for no reminder)

Example configuration:
```python
GAME_LENGTH_MINS = 60
GAME_REMINDER_ALERT_MINS = 30
```

## Usage

Run the main sync script:

python main.py

The script will:
1. Log into the Heyday website
2. Fetch your upcoming games
3. Sync them to your Google Calendar

## Files

- main.py - Main script that scrapes schedule and triggers sync
- google_auth.py - One-time authentication setup
- google_cal_sync.py - Google Calendar API integration
- client_secret.json - Google OAuth credentials (you provide)
- token.json - Generated OAuth token (created by google_auth.py)

## Requirements

Install required packages:

```bash
pip install -r requirements.txt
```

## Notes

- Past games are automatically ignored
- Token will auto-refresh when expired
- This is meant to be run periodically (e.g., via cron job) to keep your calendar updated