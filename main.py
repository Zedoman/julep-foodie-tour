import os
import json
from dotenv import load_dotenv
from julep import Julep

load_dotenv()

client = Julep(
    api_key=os.getenv('JULEP_API_KEY'),
    environment=os.getenv('JULEP_ENVIRONMENT', 'production')
)

# Step 1: Create agent
agent = client.agents.create(
    name="FoodieTourAgent",
    about="An AI agent specialized in creating delightful foodie tours",
    model="claude-3.5-sonnet",
    default_settings={
        "temperature": 0.8,
        "max_tokens": 2000
    }
)

# Step 2: Create task
with open("foodie_tour_task.yaml") as f:
    task_yaml = f.read()

task = client.tasks.create(
    agent_id=agent.id,
    name="foodie_tour_planner",
    main=[
        {
            "over": "$ _.cities",
            "map": {
                "tool": "weather",
                "arguments": {
                    "location": "$ _"
                }
            },
            "error": {
                "message": "Failed to retrieve weather data. Please check your OpenWeather API key and internet connection."
            }
        },
        {
            "evaluate": {
                "dining_suggestions": "$ [{'city': c, 'weather': w['weather'][0]['main'], 'recommendation': 'outdoor' if w['main']['temp'] > 18 and w['weather'][0]['main'] in ['Clear', 'Clouds'] else 'indoor'} for c, w in zip(_.cities, steps[0].output)]"
            }
        },
        {
            "over": "$ _.cities",
            "map": {
                "prompt": [
                    {
                        "role": "system",
                        "content": "$ f'List 3 iconic local dishes from {_}'"
                    }
                ],
                "unwrap": True
            }
        },
        {
            "over": "$ zip(_.cities, steps[2].output)",
            "map": {
                "tool": "search",
                "arguments": {
                    "query": "$ f'Best restaurants in {_[0]} serving {', '.join(_[1])}'"
                }
            }
        },
        {
            "over": "$ zip(_.cities, steps[0].output, steps[1].output, steps[2].output, steps[3].output)",
            "map": {
                "prompt": [
                    {
                        "role": "system",
                        "content": "$ f'''You're a travel writer crafting a delightful one-day foodie tour in {_[0]}. The weather today is {_[1]['weather'][0]['description']} with a temperature of {_[1]['main']['temp']}°C. Recommend breakfast, lunch, and dinner options based on these iconic dishes: {', '.join(_[3])}. Use this restaurant list for suggestions: {_[4]} Indicate if dining should be indoors or outdoors: {_[2]['recommendation']}. Write a charming narrative for the foodie journey.'''"
                    }
                ],
                "unwrap": True
            }
        },
        {
            "evaluate": {
                "tour": "$ '\\n\\n---\\n\\n'.join(_)"
            }
        }
    ],
    input_schema={
        "type": "object",
        "properties": {
            "cities": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        }
    }
)

# Step 3: Create session
session = client.sessions.create(agent=agent.id)

# Step 4: Chat with it
response = client.sessions.chat(
    session_id=session.id,
    messages=[
        {
            "role": "user",
            "content": "Plan a foodie tour for cities = ['Paris', 'New York', 'Tokyo']"
        }
    ]
)

tour_content = response.choices[0].message.content

# Improved parsing function
def parse_city_content(content, city):
    city_data = {
        "dishes": [],
        "restaurants": [],
        "itinerary": {
            "morning": [],
            "lunch": [],
            "dinner": []
        }
    }
    
    # Split content into lines and process each line
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    current_section = None
    for line in lines:
        # Detect section headers
        if "Morning" in line or "Breakfast" in line:
            current_section = "morning"
            continue
        elif "Lunch" in line:
            current_section = "lunch"
            continue
        elif "Dinner" in line or "Evening" in line:
            current_section = "dinner"
            continue
            
        # Process content lines
        if line.startswith("- "):
            content = line[2:]
            if current_section:
                city_data["itinerary"][current_section].append(content)
                
                # Extract restaurant names
                if " at " in content.lower():
                    restaurant = content.split(" at ")[-1].split(" (")[0]
                    if restaurant not in city_data["restaurants"]:
                        city_data["restaurants"].append(restaurant)
                elif " from " in content.lower():
                    restaurant = content.split(" from ")[-1].split(" (")[0]
                    if restaurant not in city_data["restaurants"]:
                        city_data["restaurants"].append(restaurant)
                        
                # Extract dishes (simplified logic)
                dish_keywords = {
                    "Paris": ["croissant", "baguette", "crepe", "escargot", "coq au vin"],
                    "New York": ["bagel", "pizza", "pastrami", "cheesecake", "hot dog"],
                    "Tokyo": ["sushi", "ramen", "tempura", "yakitori", "okonomiyaki"]
                }
                
                for keyword in dish_keywords[city]:
                    if keyword in content.lower():
                        dish = content.split(" for ")[0] if " for " in content.lower() else content
                        if dish not in city_data["dishes"]:
                            city_data["dishes"].append(dish)
                            break
    
    return city_data

# Create the tour data structure
tour_data = {
    "cities": ["Paris", "New York", "Tokyo"],
    "tours": {
        "Paris": parse_city_content(tour_content.split("NEW YORK")[0], "Paris"),
        "New York": parse_city_content(tour_content.split("NEW YORK")[1].split("TOKYO")[0], "New York"),
        "Tokyo": parse_city_content(tour_content.split("TOKYO")[1], "Tokyo")
    },
    "created_at": response.created_at.isoformat(),
    "usage": {
        "completion_tokens": response.usage.completion_tokens,
        "prompt_tokens": response.usage.prompt_tokens,
        "total_tokens": response.usage.total_tokens
    }
}

with open("foodie_tours.json", "w", encoding="utf-8") as f:
    json.dump(tour_data, f, indent=2, ensure_ascii=False)

print("Tour details have been saved to foodie_tours.json")