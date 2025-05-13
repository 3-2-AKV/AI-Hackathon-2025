import pandas as pd
import json
import sqlite3
import ast
import os
import math

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# RECIPES_PATH = os.path.join(BASE_DIR, 'datasets', 'RAW_recipes.csv')
# INTERACTIONS_PATH = os.path.join(BASE_DIR, 'datasets', 'RAW_interactions.csv')
# JSON_OUTPUT_PATH = os.path.join(BASE_DIR, 'clean_recipes.json')
# DB_PATH = os.path.join(BASE_DIR, 'recipes.db')

# # Load datasets
# print("Loading datasets...")
# recipes_df = pd.read_csv(RECIPES_PATH)
# interactions_df = pd.read_csv(INTERACTIONS_PATH)

# # Convert the from string to list
# recipes_df['ingredients'] = recipes_df['ingredients'].apply(ast.literal_eval)
# recipes_df['steps'] = recipes_df['steps'].apply(ast.literal_eval)
# recipes_df['tags'] = recipes_df['tags'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])


# # Calculate average rating and number of ratings
# ratings_summary = interactions_df.groupby('recipe_id')['rating'].agg(['mean', 'count']).reset_index()
# ratings_summary.columns = ['id', 'average_rating', 'num_ratings']

# # Merge
# recipes_df = pd.merge(recipes_df, ratings_summary, on='id', how='left')
# # Fill NaN values and convert to integer
# recipes_df['average_rating'] = recipes_df['average_rating'].fillna(0).round(0).astype(int)
# recipes_df['num_ratings'] = recipes_df['num_ratings'].fillna(0).astype(int)


# # Filter out recipes with fewer than 20 ratings
# recipes_df = recipes_df[recipes_df['num_ratings'] >= 20]

# # Remove unnecessary columns
# keep_cols = ['id', 'name', 'tags', 'ingredients', 'steps', 'average_rating', 'num_ratings']
# clean_df = recipes_df[keep_cols]

# # Write to JSON
# recipes_json = clean_df.to_dict(orient='records')
# with open(JSON_OUTPUT_PATH, 'w', encoding='utf-8') as f:
#     json.dump(recipes_json, f, ensure_ascii=False, indent=2)

# # Write to sqllite database
# conn = sqlite3.connect(DB_PATH)
# cursor = conn.cursor()
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS existing_rec (
#         id INTEGER PRIMARY KEY,
#         name TEXT,
#         tags TEXT,
#         ingredients TEXT,
#         steps TEXT,
#         average_rating INTEGER,
#         num_ratings INTEGER
#     )
# ''')

# for recipe in recipes_json:
#     cursor.execute('''
#         INSERT OR REPLACE INTO existing_rec (
#             id, name, tags, ingredients, steps, average_rating, num_ratings
#         ) VALUES (?, ?, ?, ?, ?, ?, ?)
#     ''', (
#         recipe['id'],
#         recipe['name'],
#         json.dumps(recipe['tags']),
#         json.dumps(recipe['ingredients']),
#         json.dumps(recipe['steps']),
#         recipe['average_rating'],
#         recipe['num_ratings']
#     ))

# conn.commit()
# conn.close()

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