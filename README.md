# calendar-assistant
Intelligent Calendar Assistant Project

Here's a comprehensive and well-detailed README file for the Intelligent Calendar Assistant project:

# Intelligent Calendar Assistant

## Overview

The Intelligent Calendar Assistant is a powerful CLI-based tool that integrates with Google Calendar and uses OpenAI's GPT models to provide smart calendar management capabilities. This assistant can help users schedule events, reschedule meetings, cancel appointments, suggest meeting times, and provide calendar summaries using natural language queries.

## Features

1. Schedule events
2. Reschedule meetings
3. Cancel meetings
4. Suggest available meeting times
5. Get calendar summaries
6. Natural language processing for user queries
7. Integration with Google Calendar
8. Recurrence support for events

## Prerequisites

- Python 3.7+
- Google Cloud Platform account with Calendar API enabled
- OpenAI API key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/intelligent-calendar-assistant.git
   cd intelligent-calendar-assistant
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the project root and add the following:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. Set up Google Calendar API:
   - Place your `credentials.json` file in the `src` directory.
   - On first run, you'll be prompted to authorize the application.

## Usage

Run the CLI application:

```
python src/cli.py your_username
```

Replace `your_username` with your desired username for the calendar assistant.

Once the application starts, you can interact with the assistant using natural language queries. For example:

- "Schedule a meeting with John on Monday at 2pm"
- "Reschedule my 3pm meeting to tomorrow at 4pm"
- "Cancel my appointment on Friday"
- "Suggest a meeting time for next Tuesday"
- "Show me my calendar for next week"

## Project Structure

```
intelligent-calendar-assistant/
├── src/
│   ├── calendar_integration.py
│   ├── cli.py
│   ├── config.py
│   ├── credentials.json
│   ├── llm_integration.py
│   └── user_management.py
├── tests/
│   ├── test_cancel.py
│   ├── test_get_summary.py
│   ├── test_reschedule.py
│   ├── test_schedule.py
│   └── test_suggest_time.py
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

## Key Components

1. `calendar_integration.py`: Handles integration with Google Calendar API.
2. `llm_integration.py`: Manages interaction with OpenAI's GPT models and processes natural language queries.
3. `cli.py`: Provides the command-line interface for user interaction.
4. `config.py`: Stores configuration variables.
5. `user_management.py`: Manages user registration and identification.

## Testing

The `tests` directory contains unit tests for various functionalities. To run the tests, use the following command:

```
python -m unittest discover tests
```

## Security

This application uses OAuth 2.0 for Google Calendar authentication and stores tokens securely. However, always keep your `credentials.json` and `.env` files confidential and never commit them to version control.

## Limitations

- The application is designed for personal use and may not be suitable for managing shared calendars or complex organizational schedules.

## Future Improvements

1. Add support for more complex queries and additional calendar operations.
2. Implement a graphical user interface (GUI) for easier interaction.
3. Extend support to other calendar services beyond Google Calendar.

## Contributing

Contributions to the Intelligent Calendar Assistant are welcome! Please feel free to submit pull requests, create issues or spread the word.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the GPT models used in this project.
- Google for the Calendar API.

For more detailed information on specific functions and their implementations, please refer to the source code and comments within each file.
