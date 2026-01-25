from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        # Add recipe_type column to Recipe table
        with db.engine.connect() as conn:
            try:
                # Add the column with default value '经典'
                conn.execute(text("ALTER TABLE recipe ADD COLUMN recipe_type VARCHAR(20) DEFAULT '经典'"))
                conn.commit()
                print("Added recipe_type column to recipe table.")
            except Exception as e:
                print(f"Column recipe_type might already exist or error: {e}")
        
        print("Migration completed.")

if __name__ == "__main__":
    migrate()
