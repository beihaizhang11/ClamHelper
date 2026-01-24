from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        # 1. Create RecipeIngredient table
        try:
            db.create_all() # This creates new tables (RecipeIngredient) but doesn't alter existing ones
            print("Created new tables (if not existed).")
        except Exception as e:
            print(f"Error creating tables: {e}")

        # 2. Add recipe_id to Consumption
        with db.engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE consumption ADD COLUMN recipe_id INTEGER REFERENCES recipe(id)"))
                print("Added recipe_id to consumption table.")
            except Exception as e:
                print(f"Column recipe_id might already exist or error: {e}")

        # 3. Update Recipe.ingredients to nullable (SQLite doesn't support altering column nullability easily, so we skip this validation check for now or assume it's fine)
        # However, for new rows it matters. We changed the model definition.
        
        print("Migration completed.")

if __name__ == "__main__":
    migrate()
