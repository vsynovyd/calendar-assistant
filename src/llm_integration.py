# llm_integration.py

import openai
import json
from datetime import datetime, timedelta
from config import OPENAI_API_KEY, CLIENT_ID, CLIENT_SECRET, TENANT_ID
from calendar_integration import OutlookCalendar

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

def get_calendar_summary(query):
    """
    Fetch calendar events based on the user's query and return a summary.

    Parameters:
    query (str): The user's query to determine the time range for fetching events.

    Returns:
    str: A summary of calendar events within the specified time range.
    """
    calendar = OutlookCalendar(CLIENT_ID, CLIENT_SECRET, TENANT_ID)

    # Determine the time range based on the query
    start_date, end_date = parse_data_from_query(query)
    
    if not start_date or not end_date:
        return "Could not determine the date range from your query. Please specify a valid time range."

    events = calendar.get_calendar_events(start_date.isoformat(), end_date.isoformat())
    events_str = "\n".join([f"{event['subject']} - {event['start']['dateTime']} - {event['end']['dateTime']}" for event in events])
    return events_str


def suggest_meeting_time(query, meeting_length):
    """
    Suggests a meeting time based on user's availability.

    Parameters:
    query (str): The user's query to determine the date for the request.
    meeting_length (int): The length of the meeting in minutes.

    Returns:
    str: A suggested meeting time or a message indicating that no available slots were found.
    """

    calendar = OutlookCalendar(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
    
    # determine the date based on the query
    target_date, _ = parse_data_from_query(query)
    if not target_date:
        return "I couldn't find a date in your query. Please try again."
    
    events = calendar.get_calendar_events(target_date.isoformat(), (target_date + timedelta(days=1)).isoformat())

    # find available slots
    available_slots = find_available_slots(events, meeting_length)
    
    if available_slots:
        return f"I successfully found a slot for you. The meeting will be on {target_date} for {available_slots[0]['start']}."
    else:
        return f"I couldn't find any available slots for {target_date}. Please try a different date."



def parse_data_from_query(query):
    """
    Parse the data from the user's query.

    Parameters:
    query (str): The user's query to determine the date for the request.

    Returns:
    tuple: The parsed start and end dates or None if the dates could not be retrieved from the query.
    """
    days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    today = datetime.now().date()
    
    for i, day in enumerate(days_of_week):
        if day in query.lower():
            target_date = today + timedelta(days=(i - today.weekday()) % 7)
            return target_date, target_date + timedelta(days=1)

    if "next week" in query.lower():
        start_date = today + timedelta(days=(7 - today.weekday()))
        end_date = start_date + timedelta(days=7)
        return start_date, end_date

    if "this week" in query.lower():
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=7)
        return start_date, end_date
    
    return None, None


def find_available_slots(events, meeting_length):
    """
    Find available time slots for a requested meeting.

    Parameters:
    events (list): A list of events from the user's calendar.
    meeting_length (int): The length of the meeting in minutes.

    Returns:
    list: A list of available time slots.
    """

    # assume that the work day is from 9am to 5pm
    workday_start = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    workday_end = datetime.now().replace(hour=17, minute=0, second=0, microsecond=0)

    available_slots = []
    current_time = workday_start

    for event in events:
        event_start = datetime.fromisoformat(event['start']['dateTime'])
        event_end = datetime.fromisoformat(event['end']['dateTime'])

        if current_time + timedelta(minutes=meeting_length) <= event_start:
            available_slots.append({"start": current_time, "end": current_time + timedelta(minutes=meeting_length)})
        current_time = event_end

    return available_slots



# Define tools for the AI to use
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_calendar_summary",
            "description": "Get a summary of the user's calendar events based on a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's query to get the calendar summary."
                    }
                },
                "required": ["query"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_meeting_time",
            "description": "Suggest a meeting time based on the user's availability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's query to get the calendar summary."
                    },
                    "meeting_length": {
                        "type": "integer",
                        "description": "The length of the meeting in minutes."
                    }
                },
                "required": ["query", "meeting_length"]
            },
        },
    }
]

# Example messages to send to the AI
messages = [
    {
        "role": "system", 
        "content": "You are a helpful calendar assistant."
    },
    {
        "role": "user", 
        "content": "query"
     },
]

# Get response from OpenAI
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages,
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "get_calendar_summary"}},
)

# Get response from OpenAI
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages,
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "suggest_meeting_time"}},
)

# Extract function call details from the response
tool_call = response.choices[0].message['tool_calls'][0].function
function_args = json.loads(tool_call.arguments)

# Call the function with the extracted arguments
summary = get_calendar_summary(function_args['start_date'], function_args['end_date'])
print(summary)

# Call the function with the extracted arguments
suggestion = suggest_meeting_time(function_args['query'], function_args['meeting_length'])
print(suggestion)