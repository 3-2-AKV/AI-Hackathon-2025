# AI-Hackathon-2025

## Cookbook tab fixes:
1. Add the date when the recipy was added
2. Name of the recipe -> click -> recipe on the right side should appear
3. In the table columns: name, type, indgredients, date
4. Check if possible to limit characters for ingredients 

## Add:
1. Remove button for recipes from the db

!!!!! CHANGE SHOW expired to HIDE expired

💡Idea: Cookbook ai search with descriptions - you just say in the input what you want to have in the recipe and the AI searches through our cookbook and prints everything that might match.

        prompt = (
            "SYSTEM: You are a JSON-only generator. Output _only_ valid JSON.\n\n"
            # "Whenever you mention temperatures, use the Unicode degree sign (°) followed by “C” (e.g. 180°C).\\n\\n"
            f"You are a helpful meal planner assistant.\n\n"
            f"Generate {num_recipes} {meal_type} recipes using the following available ingredients "
            f"You must include these ingredients: {', '.join([i['name'] for i in checked_items])}.\n"
            f"{sort_ingredients_by_expiration(ingredients)}"
            f"Use the needed amounts and units from what's provided without exceeding them. You don't have to use full amount of indgredients that's provided.\n"
            f"If you need to add any other ingredients apart from {', '.join([i['name'] for i in checked_items])}, you can use the ingredients from this list:"
            f"(each with quantity and unit):\n"
            f"{', '.join([i for i in all_ing])}.\n\n"
            f"Adapt recipes based on the following user preferences (e.g. allergies, preferred preparation methods, temperature): {personal_preferences}.\n\n"
            f"For each recipe, provide:\n"
            f"1. A clear name of the meal without any creative/strange titles (do not repeat the title twice)\n"
            f"2. Meal type (breakfast, lunch, dinner, or dessert)\n"
            f"3. A list of ingredients with exact amounts and units\n"
            f"4. Easy-to-follow step-by-step cooking instructions\n\n"
            f"ONLY include information relevant to the recipe."
            f"Prioritize using ingredients that expire soon: {', '.join([i for i in important])}.\n"
            f"\n\nFinally, return exactly valid JSON (no extra commentary) in this form:\n"
            "`[{`\n"
            "  \"name\": \"<recipe title>\",\n"
            "  \"type\": \"<meal type>\",\n"
            "  \"ingredients\": [\n"
            "    \"ingredient1 (amount unit)\",\n"
            "    …\n"
            "  ],\n"
            "  \"instructions\": [\n"
            "    \"Step 1…\",  \n"
            "    …\n"
            "  ]\n"
            "`}]`\n"
            "\n\nIMPORTANT: After you think, _end_ with strictly this schema and nothing else:\n"
            "[\n"
            "  {\"name\":\"Recipe Title\",\"ingredients\":[\"…\"],\"instructions\":[\"…\"]}\n"
            "]\n"
            "END\n"
        )