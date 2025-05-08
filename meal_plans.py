from transformers import pipeline
from datetime import datetime

def sort_ingredients_by_expiration(ingredients):
    # Sort ingredients by expiration date (index 4 assumed to be 'expiration_date')
    return sorted(ingredients, key=lambda i: datetime.strptime(i[4], "%Y-%m-%d"))

def generate_meal_plan(ingredients, meal_type, num_recipes, must_have, personal_preferences):
    # Get top 5 ingredients that expire soonest
    sorted_ingredients = sort_ingredients_by_expiration(ingredients)
    important = [i[1] for i in sorted_ingredients[:5]]

    # Format all ingredients as strings with quantity and unit
    all_ing = [f"{i[1]} ({i[2]} {i[3]})" for i in sorted_ingredients]

    # Compose the prompt
    prompt = (
        f"You are a helpful meal planner assistant.\n\n"
        f"Generate {num_recipes} {meal_type} recipes using only the following available ingredients "
        f"(each with quantity and unit):\n"
        f"{', '.join(all_ing)}.\n\n"
        f"Prioritize using ingredients that expire soon: {', '.join(important)}.\n"
        f"You must include these ingredients: {', '.join(must_have)}.\n"
        f"Use the specified amounts and units without exceeding them.\n"
        f"Adapt recipes based on the following user preferences (e.g. allergies, preferred preparation methods, temperature): {personal_preferences}.\n\n"
        f"For each recipe, provide:\n"
        f"1. A clear title\n"
        f"2. A list of ingredients with exact amounts and units\n"
        f"3. Easy-to-follow step-by-step cooking instructions\n\n"
        f"Only include information relevant to the recipe."
    )

    # Generate response using Hugging Face pipeline
    generator = pipeline("text-generation", model="gpt2")
    response = generator(prompt, max_length=700, num_return_sequences=1)
    
    return response[0]['generated_text']
