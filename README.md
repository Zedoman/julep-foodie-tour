# Foodie Tour Planner

A delightful AI-powered application that creates personalized food tours for multiple cities, taking into account local weather conditions and iconic dishes.

## Features

- 🌍 Multi-city food tour planning
- 🌤️ Weather-aware dining recommendations (indoor/outdoor)
- 🍽️ Curated lists of iconic local dishes
- 🏪 Restaurant recommendations based on local specialties
- 📝 Detailed daily itineraries with breakfast, lunch, and dinner suggestions
- 💾 JSON output for easy integration and storage

## Prerequisites

- Python 3.7+
- Julep API key
- OpenWeather API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd julep-foodie-tour
```

2. Install the required dependencies:
```bash
uv sync
```

3. Create a `.env` file in the project root with your API keys:
```env
JULEP_API_KEY=your_julep_api_key
JULEP_ENVIRONMENT=production
OPENWEATHER_API_KEY=your_openweather_api_key
```

## Usage

1. Run the main script:
```bash
python main.py
```

2. The script will:
   - Create a foodie tour for Paris, New York, and Tokyo
   - Check weather conditions for each city
   - Generate recommendations for iconic local dishes
   - Search for restaurants serving these dishes
   - Create a detailed itinerary for each city
   - Save the results to `foodie_tours.json`

## Output Format

The generated `foodie_tours.json` file contains:
- City-specific tours
- Lists of recommended dishes
- Restaurant recommendations
- Detailed itineraries organized by meal times
- Weather information
- Usage statistics

Example structure:
```json
{
  "cities": ["Paris", "New York", "Tokyo"],
  "tours": {
    "Paris": {
      "dishes": [...],
      "restaurants": [...],
      "itinerary": {
        "morning": [...],
        "lunch": [...],
        "dinner": [...]
      }
    },
    // Similar structure for other cities
  }
}
```

## Project Structure

- `main.py`: Main application script
- `foodie_tour_task.yaml`: Task configuration for the Julep agent
- `requirements.txt`: Python dependencies
- `.env`: Environment variables (not tracked in git)
- `foodie_tours.json`: Generated tour data
