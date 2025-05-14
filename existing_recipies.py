import json
import sqlite3
import math

def get_best_matching_recipes(ingredient_list, db_path='recipes.db', top_n=6):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch all recipes
    cursor.execute("SELECT id, name, ingredients, steps, average_rating, num_ratings FROM existing_rec")
    all_recipes = cursor.fetchall()

    results = []

    for recipe in all_recipes:
        recipe_id, name, ingredients_json, steps_json, avg_rating, num_ratings = recipe

        try:
            recipe_ingredients = json.loads(ingredients_json)
            recipe_steps = json.loads(steps_json)
        except:
            continue


        # Count ingredient matches
        matches = sum(1 for ing in recipe_ingredients if ing.lower() in [i.lower() for i in ingredient_list])

        if matches > 0:
            # Compute score (you can adjust this formula)
            score = matches * (avg_rating + math.log(1 + num_ratings))
            results.append({
                'id': recipe_id,
                'name': name,
                'matches': matches,
                'score': score,
                'ingredients': recipe_ingredients,
                'steps': recipe_steps,
                'average_rating': avg_rating,
                'num_ratings': num_ratings
        })

    conn.close()

    # Sort and return top N
    sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
    return sorted_results[:top_n]