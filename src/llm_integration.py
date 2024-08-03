# llm_integration.py

import openai
import json
from datetime import datetime, timedelta
from config import OPENAI_API_KEY, CLIENT_ID, CLIENT_SECRET, TENANT_ID
from calendar_integration import OutlookCalendar
import re

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY



def schedule_event(query):
    """
    Schedule an event based on the user's query.

    Parameters:
    query (str): The user's query to determine the name, the time and the length for the event.

    Returns: 
    str: A success result, or inability to schedule an event due to an overlap.
    """
    calendar = OutlookCalendar(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
    
    # Extract event details from the query
    event_name = extract_event_name(query)
    event_time = parse_specific_datetime(query)
    event_length = extract_event_length(query)
    
    # If any required information is missing, ask the user
    if not event_name:
        return "Please provide a name for the event."
    if not event_time:
        return "Please specify the date and time for the event."
    if not event_length:
        return "Please specify the length of the event in minutes."
    
    # Check for conflicts
    end_time = event_time + timedelta(minutes=event_length)
    events = calendar.get_calendar_events(event_time.isoformat(), end_time.isoformat())
    
    if events:
        return f"There's already an event scheduled at {event_time}. Please choose a different time."
    
    # Schedule the event
    success = calendar.create_event(event_name, event_time, end_time)
    
    if success:
        return f"Successfully scheduled '{event_name}' on {event_time.strftime('%Y-%m-%d %H:%M')} for {event_length} minutes."
    else:
        return "Failed to schedule the event. Please try again."

def extract_event_name(query):
    # Implement logic to extract event name from query
    # This is a placeholder implementation
    name_match = re.search(r'"([^"]*)"', query)
    return name_match.group(1) if name_match else None

def extract_event_length(query):
    # Implement logic to extract event length from query
    # This is a placeholder implementation
    length_match = re.search(r'(\d+)\s*(?:minute|min|hour|hr)', query, re.IGNORECASE)
    if length_match:
        length = int(length_match.group(1))
        if 'hour' in length_match.group().lower():
            length *= 60
        return length
    return None

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
    start_date, end_date = parse_data(query)
    
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
    target_date, _ = parse_data(query)
    if not target_date:
        return "I couldn't find a date in your query. Please try again."
    
    events = calendar.get_calendar_events(target_date.isoformat(), (target_date + timedelta(days=1)).isoformat())

    # find available slots
    available_slots = find_available_slots(events, meeting_length)
    
    if available_slots:
        return f"I successfully found a slot for you. The meeting will be on {target_date} for {available_slots[0]['start']}."
    else:
        return f"I couldn't find any available slots for {target_date}. Please try a different date."



def parse_data(query):
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

    # assume that the work day starts at 9am
    workday_start = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

    available_slots = []
    current_time = workday_start

    for event in events:
        event_start = datetime.fromisoformat(event['start']['dateTime'])
        event_end = datetime.fromisoformat(event['end']['dateTime'])

        if current_time + timedelta(minutes=meeting_length) <= event_start:
            available_slots.append({"start": current_time, "end": current_time + timedelta(minutes=meeting_length)})
        current_time = event_end

        # Stop suggesting slots after 5 PM
        if current_time.time() >= datetime.now().replace(hour=17, minute=0, second=0, microsecond=0).time():
            break

    return available_slots


def reschedule_meeting(query, meeting_id):
    """
    Reschedule a meeting based on the user's query.

    Parameters:
    query (str): The user's query to determine the new date/time for the meeting.
    meeting_id (str): The ID of the meeting to be rescheduled.

    Returns:
    str: A message confirming the rescheduling or suggesting the best time.
    """
    calendar = OutlookCalendar(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
    
    # Check if the query contains a specific date and time
    specific_datetime = parse_specific_datetime(query)
    
    if specific_datetime:
        # Reschedule to the specific date and time
        success = calendar.update_event(meeting_id, start_time=specific_datetime)
        if success:
            return f"Meeting rescheduled to {specific_datetime.strftime('%Y-%m-%d %H:%M')}."
        else:
            return "Failed to reschedule the meeting. Please try again."
    else:
        # Analyze the best time for the meeting
        target_date, _ = parse_data(query)
        if not target_date:
            return "I couldn't determine a date from your query. Please try again."
        
        events = calendar.get_calendar_events(target_date.isoformat(), (target_date + timedelta(days=1)).isoformat())
        available_slots = find_available_slots(events, 60)  # Assuming 1-hour meeting
        
        if available_slots:
            best_slot = available_slots[0]
            success = calendar.update_event(meeting_id, start_time=best_slot['start'])
            if success:
                return f"Meeting rescheduled to the best available time: {best_slot['start'].strftime('%Y-%m-%d %H:%M')}."
            else:
                return "Failed to reschedule the meeting. Please try again."
        else:
            return f"I couldn't find any available slots for {target_date}. Please try a different date."



def parse_specific_datetime(query):
    """
    Parse a specific date and time from the query.

    Parameters:
    query (str): The user's query.

    Returns:
    datetime or None: The parsed datetime if found, None otherwise.
    """
    # This is a simplified parser. You might want to use a more robust solution like dateutil.parser
    date_formats = ["%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%m/%d/%Y %H:%M"]
    for format in date_formats:
        try:
            return datetime.strptime(query, format)
        except ValueError:
            pass
    return None


def cancel_meeting(query):
    """
    Cancel one or multiple meetings based on the user's query.

    Parameters:
    query (str): The user's query to cancel meetings.

    Returns:
    str: A message confirming the cancellation of meetings.
    """
    calendar = OutlookCalendar(CLIENT_ID, CLIENT_SECRET, TENANT_ID)

    # Try to parse a specific date and time range from the query
    start_time, end_time = parse_date_time_range(query)

    if start_time and end_time:
        # Cancel multiple meetings within a time range
        events = calendar.get_calendar_events(start_time.isoformat(), end_time.isoformat())
        canceled_count = 0
        for event in events:
            calendar.delete_event(event['id'])
            canceled_count += 1
        return f"Canceled {canceled_count} meeting(s) between {start_time} and {end_time}."
    else:
        # Try to find a single specific time
        specific_time = parse_specific_datetime(query)
        if specific_time:
            events = calendar.get_calendar_events(specific_time.isoformat(), (specific_time + timedelta(minutes=1)).isoformat())
            if events:
                calendar.delete_event(events[0]['id'])
                return f"Canceled the meeting at {specific_time}."
            else:
                return f"No meeting found at {specific_time}."
        else:
            return "Could not determine the time or time range for cancellation. Please provide a specific time or time range."

def parse_date_time_range(query):
    """
    Parse a date and time range from the query.

    Parameters:
    query (str): The user's query.

    Returns:
    tuple: (start_time, end_time) as datetime objects, or (None, None) if parsing fails.
    """
    # This is a simplified parser. You might want to use a more robust solution like dateutil.parser
    today = datetime.now().date()
    
    # Check for day keywords
    if "today" in query.lower():
        start_date = today
    elif "tomorrow" in query.lower():
        start_date = today + timedelta(days=1)
    elif "friday" in query.lower():  # Add more days as needed
        days_ahead = (4 - today.weekday()) % 7
        start_date = today + timedelta(days=days_ahead)
    else:
        return None, None

    # Try to extract time range
    time_pattern = r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))'
    times = re.findall(time_pattern, query.lower())
    
    if len(times) == 2:
        start_time = datetime.strptime(f"{start_date} {times[0]}", "%Y-%m-%d %I:%M%p")
        end_time = datetime.strptime(f"{start_date} {times[1]}", "%Y-%m-%d %I:%M%p")
        return start_time, end_time
    
    return None, None

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
    },
    {
        "type": "function",
        "function": {
            "name": "reschedule_meeting",
            "description": "Reschedule a meeting based on the user's request.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's query to reschedule the meeting."
                    },
                    "meeting_id": {
                        "type": "string",
                        "description": "The ID of the meeting to be rescheduled."
                    }
                },
                "required": ["query", "meeting_id"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_meeting",
            "description": "Cancel one or multiple meetings based on the user's request.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's query to cancel meetings."
                    }
                },
                "required": ["query"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_event",
            "description": "Schedule an event based on the user's query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's query to schedule an event."
                    }
                },
                "required": ["query"]
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


def process_user_query(user_query):
    """
    Process the user's query by determining the function to call and executing it.
    
    Parameters:
    user_query (str): The user's input query.
    
    Returns:
    str: The result of processing the query.
    """
    messages = [
        {"role": "system", "content": "You are a helpful calendar assistant that determines which function to call based on the user's query."},
        {"role": "user", "content": user_query}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    
    if response.choices[0].message.get("tool_calls"):
        function_name = response.choices[0].message["tool_calls"][0].function.name
        function_args = json.loads(response.choices[0].message["tool_calls"][0].function.arguments)
        
        function_mapping = {
            "get_calendar_summary": get_calendar_summary,
            "suggest_meeting_time": lambda q: suggest_meeting_time(q, 60),  # Assuming 60 minutes as default
            "reschedule_meeting": lambda q: reschedule_meeting(q, "placeholder_meeting_id"),  # You'll need to handle meeting_id
            "cancel_meeting": cancel_meeting,
            "schedule_event": schedule_event
        }
        
        if function_name in function_mapping:
            return function_mapping[function_name](function_args.get('query', user_query))
        else:
            return "I'm sorry, I couldn't determine how to handle that request."
    else:
        return "I'm sorry, I couldn't determine how to handle that request. Could you please rephrase?"

