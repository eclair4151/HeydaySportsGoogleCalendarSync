import heyday_parser
import google_cal_sync


# How long to block off on the calendar for each game
GAME_LENGTH_MINS = 60

# How many minutes before the game to send a reminder (-1 for no reminder)
GAME_REMINDER_ALERT_MINS = 30


def main():
    games = heyday_parser.get_heyday_games()
    google_cal_sync.sync_games(games, GAME_LENGTH_MINS, GAME_REMINDER_ALERT_MINS)


if __name__ == '__main__':
    main()