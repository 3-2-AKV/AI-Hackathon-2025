import re
from datetime import datetime, date
from existing_recipies import get_best_matching_recipes
from google import genai
from google.genai import types


# Initialize Gemini API client
client = genai.Client(api_key="AIzaSyDjxajrFdEknEc2eynLQ9507IB_eo_MDiM")

# Current date for expiration checks
today_str = str(date.today())
curr_date = datetime.strptime(today_str, "%Y-%m-%d")

def sort_ingredients_by_expiration(ingredients):
    important = []
    for i in ingredients:
        item_date = datetime.strptime(str(i['expiry']), "%Y-%m-%d")
        if -1 < (item_date - curr_date).days <= 3:
            important.append(i['name'])
    if important:
        return f"Prioritize using ingredients that expire soon: {', '.join(important)}.\n"
    return ""


def generate_meal_plan(ingredients, cart_ings, meal_type, num_recipes, checked_items, personal_preferences):
    if not checked_items:
        return "Please select at least one ingredient."

    important_note = sort_ingredients_by_expiration(ingredients)
    all_ing = [f"{i['name']} ({i['amount']} {i['unit']})" for i in ingredients]
    shopping_cart_ing = [f"{i['name']}" for i in cart_ings]
    input_names = [i['name'] for i in checked_items]

    # Get example recipes
    top_matches = get_best_matching_recipes(input_names)
    reference_recipes = []
    for match in top_matches:
        steps = match.get('steps', [])
        if not isinstance(steps, list):
            steps = ["No steps available."]
        reference_recipes.append({
            'name': match['name'],
            'ingredients': match['ingredients'],
            'steps': steps
        })

    # Build reference string
    reference_str = ''
    for r in reference_recipes:
        reference_str += f"- {r['name']}:\n"
        reference_str += f"  Ingredients: {', '.join(r['ingredients'])}\n"
        reference_str += f"  Steps: {' '.join(r['steps'])}\n\n"

    # Compose the prompt
    prompt = (
        "You are a JSON-only generator. Output _only_ valid JSON.\n\n"
        "You are a helpful meal planner assistant.\n\n"
        f"Here are example recipes:\n\n{reference_str}\n"
        f"Generate {num_recipes} {meal_type} recipes using the following available ingredients. "
        f"You must include these ingredients: {', '.join(input_names)}.\n"
        f"{important_note}Use the needed amounts and units from what's provided without exceeding them. "
        f"If you need to add any other ingredients apart from {', '.join(input_names)}, you can use from this list:"
        f" {', '.join(all_ing)}, {', '.join(shopping_cart_ing)}.\n\n"
        f"Adapt recipes based on the following user preferences: {personal_preferences}.\n\n"
        f"USE MEASURES FOR INGREDIENTS. EXPLAIN EACH STEP CAREFULLY\n\n"
        "For each recipe, provide exactly valid JSON in this form:\n"
        "[{\n  \"name\": \"<title>\",\n  \"type\": \"<meal type (breakfast, lunch, dinner, dessert)>\",\n  \"ingredients\": [\"item1 (amt unit)\", …],\n  \"instructions\": [\"Step 1…\", …]\n}]"
    )

    # Call Gemini API
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=2500
        )
    )

    raw = response.text.strip()
    # Clean any stray tags
    cleaned = re.sub(r'<.*?>', '', raw)
    return cleaned
