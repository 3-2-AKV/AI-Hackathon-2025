import re
from transformers import pipeline
from datetime import datetime
from datetime import date
import subprocess
from database import get_ingredients, create_db, insert_meal_plan, get_grocery_list, remove_ingredient_from_db

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
    if not checked_items:
        return "Please select at least one ingredient."
    else:
        important = sort_ingredients_by_expiration(ingredients)
        all_ing = [f"{i['name']} ({i['amount']} {i['unit']})" for i in ingredients]

        # Compose the prompt
        prompt = (
            f"You are a helpful meal planner assistant.\n\n"
            f"Generate {num_recipes} {meal_type} recipes using the following available ingredients "
            f"You must include these ingredients: {', '.join([i['name'] for i in checked_items])}.\n"
            f"Prioritize using ingredients that expire soon: {', '.join([i for i in important])}.\n"
            f"Use the specified amounts and units without exceeding them.\n"
            f"If you need to add any other ingredients apart from {', '.join([i['name'] for i in checked_items])}, you can use the ingredients from this list:"
            f"(each with quantity and unit):\n"
            f"{', '.join([i for i in all_ing])}.\n\n"
            f"Adapt recipes based on the following user preferences (e.g. allergies, preferred preparation methods, temperature): {personal_preferences}.\n\n"
            f"For each recipe, provide output in exact format:\n"
            f"A clear name of the meal without any creative/strange titles\n"
            f"A list of ingredients with exact amounts and units\n"
            f"Easy-to-follow step-by-step cooking instructions\n\n"
            f"No additional output at the end and beginning.\n"
            f"Remember to ONLY include information relevant to the recipe."
            f"Prioritize using ingredients that expire soon: {', '.join([i for i in important])}.\n"
        )

        try:
            # Launch Ollama process and send prompt via STDIN
            proc = subprocess.Popen(
                ["ollama", "run", "deepseek-r1"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = proc.communicate(prompt, timeout=60)

            # cleaned = re.sub(r"<think>.*?</think>", "", stdout, flags=re.DOTALL).strip()

            if proc.returncode != 0:
                err = stderr.strip() or f"Exit code {proc.returncode}"
                return f"Error fetching recipe: {err}"
            else:
                # Clean any stray tags
                cleaned = re.sub(r"<.*?>", "", stdout).strip()
                cleaned = stdout.split("#", 1)[1].strip()
                if not cleaned:
                    return "No response from the model. Try again or check your Ollama setup."
                else:
                    cleaned1 = cleaned
                    name_match = re.search(r'### Recipe \d+:\s(.+)', cleaned)
                    recipe_name = name_match.group(1).strip() if name_match else "Unknown"
                    ingredients_match = re.search(
                    r'\*\*Ingredients\*\*\n(.+?)\n\n',
                    cleaned,
                    flags=re.DOTALL
                    )
                    ingredients_raw = ingredients_match.group(1).strip() if ingredients_match else ""
                    ingredients_list = [line[2:].strip() for line in ingredients_raw.splitlines() if line.startswith("-")]
                    instructions_match = re.search(
                        r'\*\*Instructions\*\*\n([\s\S]+)$',
                        cleaned,
                        flags=re.DOTALL
                    )
                    instructions_raw = instructions_match.group(1).strip() if instructions_match else ""
                    instructions_list = [
                        line[len(prefix):].strip()
                        for line in instructions_raw.splitlines()
                        if (m := re.match(r'(\d+)\.', line))
                        for prefix in [m.group(0)]
                    ]
                    insert_meal_plan(
                        meal_type=meal_type,
                        meal_name=recipe_name,
                        meal_ingredients=ingredients_list,
                        meal_instructions=instructions_list
                    )
                    return cleaned1

       
        
        except subprocess.TimeoutExpired:
            proc.kill()
            return "The model took too long to respond. Please try again."
        except Exception as e:
            return f"Unexpected error: {e}"
            
       



        # Generate response using Hugging Face pipeline
        # generator = pipeline("text-generation", model="gpt2")
        # response = generator(prompt, max_length=700, num_return_sequences=1)
        
        # return response[0]['generated_text']
