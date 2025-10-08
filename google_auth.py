from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def main():
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "token.json")
    with open(json_path, 'w') as f:
        f.write(creds.to_json())
    print("Token saved to token.json")

if __name__ == '__main__':
    main()