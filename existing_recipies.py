import pandas as pd
import json
import sqlite3
import ast
import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'recipes.csv')
JSON_OUTPUT_PATH = os.path.join(BASE_DIR, 'clean_recipes.json')
DB_PATH = os.path.join(BASE_DIR, 'clean_recipes.db')  # Updated DB filename for consistency

def process_recipes():
# Load dataset
    print("Loading recipes.csv...")
    recipes_df = pd.read_csv(CSV_PATH)

    # Rename columns for consistency (including categories)
    recipes_df = recipes_df.rename(columns={
        'Unnamed: 0': 'id',
        'Title': 'name',
        'Ingredients': 'ingredients',
        'Instructions': 'steps',
        'Image_Name': 'image_name',
    })

    # Parse ingredients column: string representation to list
    recipes_df['ingredients'] = recipes_df['ingredients'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) and x.strip().startswith('[') else
                [i.strip() for i in x.split(',')] if isinstance(x, str) else x
    )

    # Parse steps/instructions: ensure list of steps
    recipes_df['steps'] = recipes_df['steps'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) and x.strip().startswith('[') else
                [s.strip() for s in x.split('\n')] if isinstance(x, str) else [x]
    )

    # Parse categories: string representation to list or split comma-separated



    # Select and reorder columns
    keep_cols = [
        'id', 'name', 'image_name', 'ingredients',
        'steps'
    ]
    clean_df = recipes_df[keep_cols]

    # Write to JSON
    print("Writing JSON output to", JSON_OUTPUT_PATH)
    recipes_json = clean_df.to_dict(orient='records')
    with open(JSON_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(recipes_json, f, ensure_ascii=False, indent=2)

    # Write to SQLite database
    print("Updating SQLite database at", DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tag = 'clean_recipes'  # Table name updated for clarity
    # Create table with categories column
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {tag} (
            id INTEGER PRIMARY KEY,
            name TEXT,
            image_name TEXT,
            ingredients TEXT,
            steps TEXT
        )
    ''')

    # Insert or replace records
    for rec in recipes_json:
        cursor.execute(f'''
            INSERT OR REPLACE INTO {tag} (
                id, name, image_name, ingredients,
                steps
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            rec['id'],
            rec['name'],
            rec['image_name'],
            json.dumps(rec['ingredients']),
            json.dumps(rec['steps'])
        ))

    conn.commit()
    conn.close()

    print("Done!")

if __name__ == "__main__":
    process_recipes()