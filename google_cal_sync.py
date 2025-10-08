from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from datetime import datetime, timedelta, timezone

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_service():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if creds.expired and creds.refresh_token:
        print('Refreshing token')
        creds.refresh(Request())
        with open('token.json', 'w') as f:
            f.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def sync_games(games):
    service = get_service()
    now = datetime.now(timezone.utc).isoformat()

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        singleEvents=False
    ).execute()

    events = [
        e for e in events_result.get('items', [])
        if 'extendedProperties' in e
           and 'private' in e['extendedProperties']
           and 'game_id' in e['extendedProperties']['private']
    ]

    print(f"Found {len(events)} existing game events in calendar")

    game_id_calendar_event_map = {}
    for e in events:
        if 'extendedProperties' in e and 'private' in e['extendedProperties']:
            game_id = e['extendedProperties']['private']['game_id']
            game_id_calendar_event_map[game_id] = e


    for game in games:
        gid = game['id']
        start_dt = datetime.fromtimestamp(game['game_time'], tz=timezone.utc)
        end_dt = start_dt + timedelta(hours=2)
        opponent_url = game['opponent_url']

        event_data = {
            'summary': f"{game['my_team']} vs {game['opponent']}",
            'location': f"{game['location']}",
            'description': f'<a href="{opponent_url}">View Opponent Standings</a>',
            'start': {'dateTime': start_dt.isoformat()},
            'end': {'dateTime': end_dt.isoformat()},
            'extendedProperties': {'private': {'game_id': gid}},
        }

        existing = game_id_calendar_event_map.get(gid)
        if existing:
            existing_start_dt = datetime.fromisoformat(existing['start']['dateTime'])
            new_start_dt = datetime.fromisoformat(event_data['start']['dateTime'])
            if existing_start_dt != new_start_dt:
                service.events().update(
                    calendarId='primary',
                    eventId=existing['id'],
                    body=event_data
                ).execute()
                print(f"Updated game {gid}")
            else:
                print(f"No change for {gid}")
        else:
            service.events().insert(calendarId='primary', body=event_data).execute()
            print(f"Created game {gid}")


    current_game_ids = {game['id'] for game in games}
    for calendar_event_game_id, event in game_id_calendar_event_map.items():
        if calendar_event_game_id not in current_game_ids:
            service.events().delete(
                calendarId='primary',
                eventId=event['id']
            ).execute()
            print(f"Deleted game {calendar_event_game_id}")

