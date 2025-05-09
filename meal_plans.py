from transformers import pipeline
from datetime import datetime
from datetime import date

today_str = str(date.today())
curr_date = datetime.strptime(today_str, "%Y-%m-%d")

def sort_ingredients_by_expiration(ingredients):
    # Sort ingredients by expiration date (index 4 assumed to be 'expiration_date')
    important = []
    for i in ingredients:
        item_date = datetime.strptime(str(i['expiry']), "%Y-%m-%d")
        if -1 < (item_date - curr_date).days <= 3:
            important.append(i['name'])
    return important
    

def generate_meal_plan(ingredients, meal_type, num_recipes, checked_items, personal_preferences):
    # Format all ingredients as strings with quantity and unit
    all_ing = [f"{i[1]} ({i[2]} {i[3]})" for i in sorted_ingredients]

    # Compose the prompt
    prompt = (
        f"You are a helpful meal planner assistant.\n\n"
        f"Generate {num_recipes} {meal_type} recipes using the following available ingredients "
        f"You must include these ingredients: {', '.join([i['name'] for i in checked_items])}.\n"
        f"Prioritize using ingredients that expire soon: {', '.join([i['name'] for i in important])}.\n"
        f"Use the specified amounts and units without exceeding them.\n"
        f"If you need to add any other ingredients apart from {', '.join([i['name'] for i in checked_items])}, you can use the ingredients from this list:"
        f"(each with quantity and unit):\n"
        f"{', '.join([i['name'] for i in all_ing])}.\n\n"
        f"Adapt recipes based on the following user preferences (e.g. allergies, preferred preparation methods, temperature): {personal_preferences}.\n\n"
        f"For each recipe, provide:\n"
        f"1. A clear title\n"
        f"2. A list of ingredients with exact amounts and units\n"
        f"3. Easy-to-follow step-by-step cooking instructions\n\n"
        f"ONLY include information relevant to the recipe."
        f"Prioritize using ingredients that expire soon: {', '.join(important)}.\n"
    )

    # Generate response using Hugging Face pipeline
    generator = pipeline("text-generation", model="gpt2")
    response = generator(prompt, max_length=700, num_return_sequences=1)
    
    return response[0]['generated_text']
