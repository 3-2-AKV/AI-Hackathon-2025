import re
from datetime import datetime, date
import subprocess
import json
import sqlite3
import pandas as pd
import glob
import os

# 1) Connect (creates file if missing)
conn = sqlite3.connect("food.db")

# 2) Loop through every CSV in data/
for path in glob.glob("data/*.csv"):
    name = os.path.splitext(os.path.basename(path))[0].lower()
    print(f"Loading {name}…")
    df = pd.read_csv(path)
    # Write to SQL table named after the file
    df.to_sql(name, conn, if_exists="replace", index=False)

conn.close()

# Taking the current date - needed to check the spoiled items
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

# --- New: Load recipe database for prompting ---
def parse_r_vector(s: str):
    """Turn a string like c("a","b","c") into ['a','b','c']."""
    return re.findall(r'"([^\"]+)"', s)

# Load your full recipe CSV
RECIPES_DF = pd.read_csv("data/recipes.csv")
RECIPES_DF["parts_list"] = RECIPES_DF["RecipeIngredientParts"].apply(parse_r_vector)
RECIPES_DF["qty_list"] = RECIPES_DF["RecipeIngredientQuantities"].apply(parse_r_vector)
RECIPES_DF["instr_list"] = RECIPES_DF["RecipeInstructions"].apply(parse_r_vector)


def generate_meal_plan(ingredients, meal_type, num_recipes, checked_items, personal_preferences):
    # Ensure at least one ingredient is selected
    if not checked_items:
        return "Please select at least one ingredient."

    # Flag soon-to-expire items
    important = sort_ingredients_by_expiration(ingredients)

    # Build set of chosen ingredient names
    have = {item['name'].lower() for item in checked_items}

    # Filter recipe DB to those using at least one chosen ingredient
    subset = []
    for _, row in RECIPES_DF.iterrows():
        parts_lower = [p.lower() for p in row['parts_list']]
        if have & set(parts_lower):
            ingr_list = [f"{q} {p}" for q, p in zip(row['qty_list'], row['parts_list'])]
            subset.append({
                "name": row.get('Name', 'Unnamed Recipe'),
                "type": meal_type.lower(),
                "ingredients": ingr_list,
                "instructions": row['instr_list']
            })

    # Serialize filtered DB
    db_json = json.dumps(subset, ensure_ascii=False)

    # Compose prompt with embedded recipe DB
    prompt = (
        "SYSTEM: You are a JSON-only generator. Output _only_ valid JSON.\n\n"
        f"Here is your recipe database (only recipes that use at least one chosen ingredient):\n{db_json}\n\n"
        f"Generate exactly {num_recipes} {meal_type} recipe(s) by choosing and/or adapting from the recipes above. "
        f"Follow this schema: [{{\"name\":\"…\",\"type\":\"…\",\"ingredients\":[\"…\"],\"instructions\":[\"…\"]}}]\n"
        "END\n"
    )

    try:
        proc = subprocess.Popen(
            ["ollama", "run", "gemma3"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(prompt, timeout=60)

        if proc.returncode != 0:
            err = stderr.strip() or f"Exit code {proc.returncode}"
            return f"Error fetching recipe: {err}"

        # Clean up any tags
        cleaned = re.sub(r"<.*?>", "", stdout).strip()
        if not cleaned:
            return "No response from the model. Try again or check your Ollama setup."
        return prompt + cleaned

    except subprocess.TimeoutExpired:
        proc.kill()
        return "The model took too long to respond. Please try again."
    except Exception as e:
        return f"Unexpected error: {e}"
