import requests
import json
import os
from datetime import datetime

def lambda_handler(event, context):
    # CREATING LOGGING FUNCTION
    def write_log():
        with open('/tmp/log.txt', 'a') as file:  # Use /tmp directory for Lambda
            # Get the current time
            current_time = datetime.now()
            # Format the timestamp
            timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
            # Write the log entry
            file.write(f"Script ran at: {timestamp}\n")

    # WEATHER LOGIC >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Accuweather API creds
    url = "https://dataservice.accuweather.com/forecasts/v1/hourly/12hour/51946_PC"
    params = {
       "apikey": os.environ.get('ACCUWEATHER_API_KEY'),  # Use os.environ.get to access environment variables
        "metric": "true"
    }

    # make request to API
    response = requests.get(url, params=params)
    weather_data = response.json()

    with open('/tmp/weather_data.json', 'w') as file:  # Use /tmp directory for Lambda
        json.dump(weather_data, file, indent=4)

    # NEW EMPTY LIST
    weather_times_list = []

    # SETTING ITEMS IN THE LIST
    for hour in weather_data:
        if hour['PrecipitationProbability'] > 32:
            weather_times_list.append(hour['DateTime'])

    formatted_times = [datetime.fromisoformat(time).strftime('%H:%M') for time in weather_times_list]

    # SETTING THE CRITERIA FOR THE WEATHER

    # ALL DAY
    all_day_count = sum('07:00' < time <= '22:00' for time in formatted_times)
    is_all_day = all_day_count >= 4

    # EVENING
    evening_count = sum(time > '18:00' for time in formatted_times)
    is_evening = evening_count >= 3

    # AFTERNOON
    afternoon_count = sum('12:00' < time <= '17:00' for time in formatted_times)
    is_afternoon = afternoon_count >= 3

    # MORNING
    morning_count = sum(time < '12:00' for time in formatted_times)
    is_morning = morning_count >= 3

    # SINGLE HOUR
    single_hour = None
    if len(formatted_times) == 1:
        single_hour = formatted_times[0]

    if is_all_day == True:
        message = "It will be raining all day. 🌧️"
    elif is_evening == True:
        message = f"There will be rain tonight from {formatted_times[0]} 🌧️"
    elif is_afternoon == True:
        message = "It will be raining in the afternoon. 🌧️"
    elif is_morning == True:
        message = "It will be raining in the morning. 🌧️"
    elif single_hour:
        message = f"It will be raining at {single_hour}. 🌧️"
    elif len(formatted_times) >= 2:
        message = f"There will be rain today at {', '.join(formatted_times)} 🌧️"

    # WEATHER LOGIC ENDS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ENDS

    # TELEGRAM LOGIC

    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    bot_token = os.environ['BOT_TOKEN']

    # Replace 'YOUR_CHAT_ID' with your actual chat ID
    chat_id = os.environ['CHAT_ID']

    # Telegram URL for sending messages
    send_message_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    if weather_times_list:
        response = requests.post(send_message_url, data={
            'chat_id': chat_id,
            'text': message
        })
    else:
        print("There is no rain today! ☀️")  # Print for debugging purposes when there's no rain

    write_log()
