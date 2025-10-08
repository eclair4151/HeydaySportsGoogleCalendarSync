from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def main():
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0, access_type='offline',
        prompt='consent')  # opens browser for consent
    with open('token.json', 'w') as f:
        f.write(creds.to_json())
    print("Token saved to token.json")

if __name__ == '__main__':
    main()