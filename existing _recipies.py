import pandas as pd
import json
import sqlite3
import ast
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECIPES_PATH = os.path.join(BASE_DIR, 'datasets', 'RAW_recipes.csv')
INTERACTIONS_PATH = os.path.join(BASE_DIR, 'datasets', 'RAW_interactions.csv')
JSON_OUTPUT_PATH = os.path.join(BASE_DIR, 'clean_recipes.json')
DB_PATH = os.path.join(BASE_DIR, 'recipes.db')

# Load datasets
print("Loading datasets...")
recipes_df = pd.read_csv(RECIPES_PATH)
interactions_df = pd.read_csv(INTERACTIONS_PATH)

# Convert the from string to list
recipes_df['ingredients'] = recipes_df['ingredients'].apply(ast.literal_eval)
recipes_df['steps'] = recipes_df['steps'].apply(ast.literal_eval)
recipes_df['tags'] = recipes_df['tags'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])


# Calculate average rating and number of ratings
ratings_summary = interactions_df.groupby('recipe_id')['rating'].agg(['mean', 'count']).reset_index()
ratings_summary.columns = ['id', 'average_rating', 'num_ratings']

# Merge
recipes_df = pd.merge(recipes_df, ratings_summary, on='id', how='left')
# Fill NaN values and convert to integer
recipes_df['average_rating'] = recipes_df['average_rating'].fillna(0).round(0).astype(int)
recipes_df['num_ratings'] = recipes_df['num_ratings'].fillna(0).astype(int)

# Remove unnecessary columns
keep_cols = ['id', 'name', 'tags', 'ingredients', 'steps', 'average_rating', 'num_ratings']
clean_df = recipes_df[keep_cols]

# Write to JSON
recipes_json = clean_df.to_dict(orient='records')
with open(JSON_OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(recipes_json, f, ensure_ascii=False, indent=2)

# Write to sqllite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS existing_rec (
        id INTEGER PRIMARY KEY,
        name TEXT,
        tags TEXT,
        ingredients TEXT,
        steps TEXT,
        average_rating INTEGER,
        num_ratings INTEGER
    )
''')

for recipe in recipes_json:
    cursor.execute('''
        INSERT OR REPLACE INTO existing_rec (
            id, name, tags, ingredients, steps, average_rating, num_ratings
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        recipe['id'],
        recipe['name'],
        json.dumps(recipe['tags']),
        json.dumps(recipe['ingredients']),
        json.dumps(recipe['steps']),
        recipe['average_rating'],
        recipe['num_ratings']
    ))

conn.commit()
conn.close()