from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 关联表：Event 和 Recipe 的多对多关系
event_recipe = db.Table('event_recipe',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    consumptions = db.relationship('Consumption', backref='participant', lazy=True)

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # category updated: Whisky, Brandy, Tequila, Gin, Rum, Vodka, Liqueur, Mixer, Garnish, Other
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.String(50)) 

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=True) # Legacy text field
    instructions = db.Column(db.Text, nullable=False)
    is_generated = db.Column(db.Boolean, default=False)
    recipe_type = db.Column(db.String(20), default='经典')  # '经典' or '特调'
    # New relationship
    ingredients_structured = db.relationship('RecipeIngredient', backref='recipe', lazy=True, cascade="all, delete-orphan")

class RecipeIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(20), default="ml")

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default="周末聚会")
    date = db.Column(db.Date, default=datetime.utcnow)
    description = db.Column(db.String(200))
    # 建立多对多关系
    recipes = db.relationship('Recipe', secondary=event_recipe, lazy='subquery',
        backref=db.backref('events', lazy=True))

class Consumption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    drink_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True) # 关联到活动
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=True) # 关联到配方

class Bartender(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False) # e.g. "Head Mixologist | Clam Master"
    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)
