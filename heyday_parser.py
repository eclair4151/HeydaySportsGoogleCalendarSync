import requests
from bs4 import BeautifulSoup
import datetime
import os
import json

def get_heyday_games():
    # --- Setup ---
    BASE_URL = "https://philadelphia.leaguelab.com"

    login_url = BASE_URL + "/login"
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        ),
        "Referer": login_url,
    })

    # --- Step 1: GET login page ---
    resp = session.get(login_url)
    resp.raise_for_status()

    # --- Step 2: Extract reqToken from HTML ---
    soup = BeautifulSoup(resp.text, "html.parser")
    token_input = soup.find("input", {"name": "reqToken"})
    req_token = token_input["value"] if token_input else None
    if not req_token:
        raise RuntimeError("reqToken not found")

    # --- Step 3: POST login form ---
    heyday_username, heyday_password = load_credentials()

    payload = {
        "reqToken": req_token,
        "cmd": "processLogin",
        "Username": heyday_username,
        "Password": heyday_password,
        "RememberMe": "1",
        "sign in": "Log In",
    }

    post_resp = session.post(login_url, data=payload, allow_redirects=True)
    post_resp.raise_for_status()

    # --- Step 4: Fetch player schedule ---
    schedule_url = BASE_URL + "/player/schedule"
    sched_resp = session.get(schedule_url)
    sched_resp.raise_for_status()

    soup = BeautifulSoup(sched_resp.text, "html.parser")
    games = []

    for date_div in soup.select("#upcomingDatesContainer .myScheduleDate"):
        date_text = date_div.find("h2").get_text(strip=True)

        for game_div in date_div.select(".gameOrAssignment"):
            rsvp_div = game_div.select_one(".RSVPContainer")
            if not rsvp_div or "id" not in rsvp_div.attrs:
                continue  # skip unscheduled games

            # Extract numeric game ID
            parts = rsvp_div["id"].split("_")
            if len(parts) < 2:
                continue
            game_id = parts[1]

            my_team = game_div.select_one(".gameTeams .myteam")
            opponent = game_div.select_one(".gameTeams .opponent")
            time = game_div.select_one(".slotInfo .time")
            location = game_div.select_one(".slotInfo .location a")
            field = game_div.select_one(".slotInfo .myScheduleField")

            time_value = time.get_text(strip=True)
            if not time_value or not date_text:
                continue

            # Check if date_text if "Today" or "Tomorrow", or Tuesday, October 14. Handle that, then combine with the time of format 6:15 PM and parse the datetime into a unix timestamp
            if date_text.lower() == "today":
                date_obj = datetime.datetime.now()
            elif date_text.lower() == "tomorrow":
                date_obj = datetime.datetime.now() + datetime.timedelta(days=1)
            else:
                try:
                    date_obj = datetime.datetime.strptime(date_text, "%A, %B %d")
                    date_obj = date_obj.replace(year=datetime.datetime.now().year)
                except ValueError:
                    continue

            datetime_str = f"{date_obj.strftime('%Y-%m-%d')} {time_value}"
            try:
                datetime_obj = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %I:%M %p")
                game_time = int(datetime_obj.timestamp())
            except ValueError:
                continue

            # ignore all games in the past
            if game_time < int(datetime.datetime.now().timestamp()):
                continue

            my_team_name = my_team.get_text(strip=True) if my_team else ""
            if not my_team_name:
                continue

            opponent_name = opponent.get_text(strip=True).strip("*") if opponent else ""
            opponent_href = opponent["href"] if opponent and "href" in opponent.attrs else ""
            sport_name = convert_field_to_sport(field.get_text(strip=True)) if field else ""
            location = location.get_text(strip=True) if location else ""

            games.append({
                "id": game_id,
                "game_time": game_time,
                "my_team": my_team_name,
                "opponent": opponent_name,
                "opponent_url": opponent_href,
                "location": location,
                "sport_name": sport_name
            })

    print(f'Found {len(games)} scheduled games on Heyday')
    return games




def convert_field_to_sport(field_name):
    sports = ["Football",
              "Kickball",
              "Soccer",
              "Softball",
              "Wiffle Ball",
              "Volleyball",
              "Basketball",
              "Floor Hockey",
              "Field Hockey",
              "Cornhole",
              "Pickleball",
              "Tennis",
              "Dodgeball",
              "Bowling"]

    field_name = field_name.lower()
    for sport in sports:
        if sport.lower() in field_name:
            return sport
    return ""

def load_credentials():
    # Try environment variables first
    heyday_username = os.getenv("HEYDAY_USERNAME")
    heyday_password = os.getenv("HEYDAY_PASSWORD")

    # If not found, try loading from JSON file
    if not heyday_username or not heyday_password:
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(script_dir, "heyday_login.json")
            with open(json_path, "r") as f:
                creds = json.load(f)
                heyday_username = creds.get("username")
                heyday_password = creds.get("password")
        except FileNotFoundError:
            pass

    if not heyday_username or not heyday_password:
        raise RuntimeError("Credentials must be set via environment variables or heyday_login.json file")

    return heyday_username, heyday_password
