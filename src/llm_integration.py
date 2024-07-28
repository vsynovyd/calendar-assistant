# llm_integration.py

import openai
import json
from datetime import datetime, timedelta
from config import OPENAI_API_KEY, CLIENT_ID, CLIENT_SECRET, TENANT_ID
from calendar_integration import OutlookCalendar

# set OpenAI API key
openai.api_key = OPENAI_API_KEY

def send_reply(message: str) -> str:
    """
    Sends a reply to the user.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}],
    )
    return response.choices[0].message['content']

def get_calendar_summary(start_date, end_date):
    """
    Fetches calendar events within a specified date range and returns a summary.
    """
    calendar = OutlookCalendar(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
    events = calendar.get_calendar_events(start_date, end_date)
    events_str = "\n".join([f"{event['subject']} - {event['start']['dateTime']} - {event['end']['dateTime']}" for event in events])
    return events_str