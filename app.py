from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Participant, InventoryItem, Recipe, Consumption, Event
from services.llm_service import get_cocktail_suggestion
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # 为了演示方便，这里简单地重建所有表以应用模型更改
    # 实际生产中应使用 Flask-Migrate
    # db.drop_all() # 慎用，会清空数据
    db.create_all()

@app.route('/')
def index():
    participants = Participant.query.all()
    inventory = InventoryItem.query.all()
    recipes = Recipe.query.all()
    events = Event.query.order_by(Event.date.desc()).all()
    return render_template('index.html', participants=participants, inventory=inventory, recipes=recipes, events=events)

@app.route('/add_participant', methods=['POST'])
def add_participant():
    name = request.form.get('name')
    if name:
        p = Participant(name=name)
        db.session.add(p)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_inventory', methods=['POST'])
def add_inventory():
    return redirect(url_for('index')) # Deprecated, use save_inventory

@app.route('/save_inventory', methods=['POST'])
def save_inventory():
    item_id = request.form.get('item_id')
    name = request.form.get('name')
    category = request.form.get('category')
    quantity = request.form.get('quantity')
    
    if name and category:
        if item_id:
            # Edit
            item = InventoryItem.query.get(item_id)
            if item:
                item.name = name
                item.category = category
                item.quantity = quantity
                db.session.commit()
        else:
            # Add
            item = InventoryItem(name=name, category=category, quantity=quantity)
            db.session.add(item)
            db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_inventory/<int:item_id>', methods=['POST'])
def delete_inventory(item_id):
    item = InventoryItem.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/log_drink', methods=['POST'])
def log_drink():
    participant_id = request.form.get('participant_id')
    drink_name = request.form.get('drink_name')
    event_id = request.form.get('event_id')

    if participant_id and drink_name:
        log = Consumption(participant_id=participant_id, drink_name=drink_name)
        if event_id:
            log.event_id = event_id
        db.session.add(log)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/event/<int:event_id>/stats')
def event_stats(event_id):
    event = Event.query.get_or_404(event_id)
    consumptions = Consumption.query.filter_by(event_id=event_id).all()
    
    # 统计数据结构：
    # stats = {
    #    'total_drinks': 10,
    #    'by_participant': {
    #        'Alice': {'count': 3, 'drinks': ['Mojito', 'Gin Tonic', 'Mojito']},
    #        'Bob': ...
    #    },
    #    'top_drinks': [('Mojito', 5), ('Gin Tonic', 2)]
    # }
    
    stats = {
        'total_drinks': len(consumptions),
        'by_participant': {},
        'drink_counts': {}
    }
    
    for c in consumptions:
        # By Participant
        p_name = c.participant.name
        if p_name not in stats['by_participant']:
            stats['by_participant'][p_name] = {'count': 0, 'drinks': []}
        stats['by_participant'][p_name]['count'] += 1
        stats['by_participant'][p_name]['drinks'].append(c.drink_name)
        
        # Drink Counts
        if c.drink_name not in stats['drink_counts']:
            stats['drink_counts'][c.drink_name] = 0
        stats['drink_counts'][c.drink_name] += 1
        
    # Sort top drinks
    stats['top_drinks'] = sorted(stats['drink_counts'].items(), key=lambda x: x[1], reverse=True)
    
    return render_template('event_stats.html', event=event, stats=stats)

@app.route('/suggest', methods=['POST'])
def suggest():
    # 获取当前库存
    inventory = InventoryItem.query.all()
    inventory_list = [f"{item.name} ({item.category})" for item in inventory]
    
    user_request = request.form.get('user_request', '')
    
    suggestion = get_cocktail_suggestion(inventory_list, user_request)
    
    return jsonify({'suggestion': suggestion})

@app.route('/save_recipe', methods=['POST'])
def save_recipe():
    recipe_id = request.form.get('recipe_id')
    name = request.form.get('name')
    ingredients = request.form.get('ingredients')
    instructions = request.form.get('instructions')
    event_id = request.form.get('event_id') # 可选：直接添加到活动
    is_ai = request.form.get('is_ai') == 'true'

    if name:
        if recipe_id:
            # Update existing recipe
            recipe = Recipe.query.get(recipe_id)
            if recipe:
                recipe.name = name
                recipe.ingredients = ingredients
                recipe.instructions = instructions
                # Don't change is_generated status on edit usually, or maybe set to False if heavily edited? 
                # Keeping it simple for now.
                db.session.commit()
        else:
            # Create new recipe
            recipe = Recipe(name=name, ingredients=ingredients, instructions=instructions, is_generated=is_ai)
            db.session.add(recipe)
            db.session.commit()
            
            if event_id:
                event = Event.query.get(event_id)
                if event:
                    event.recipes.append(recipe)
                    db.session.commit()

    return redirect(url_for('index'))

@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if recipe:
        db.session.delete(recipe)
        db.session.commit()
    return redirect(url_for('index'))

# --- 新增 Event 相关路由 ---

@app.route('/create_event', methods=['POST'])
def create_event():
    name = request.form.get('name')
    date_str = request.form.get('date')
    description = request.form.get('description')
    
    if name:
        event_date = datetime.utcnow().date()
        if date_str:
            try:
                event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        event = Event(name=name, date=event_date, description=description)
        db.session.add(event)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/event/<int:event_id>/add_recipe', methods=['POST'])
def add_recipe_to_event(event_id):
    recipe_id = request.form.get('recipe_id')
    event = Event.query.get_or_404(event_id)
    recipe = Recipe.query.get(recipe_id)
    
    if recipe and recipe not in event.recipes:
        event.recipes.append(recipe)
        db.session.commit()
        
    return redirect(url_for('index'))

@app.route('/event/<int:event_id>/remove_recipe', methods=['POST'])
def remove_recipe_from_event(event_id):
    recipe_id = request.form.get('recipe_id')
    event = Event.query.get_or_404(event_id)
    recipe = Recipe.query.get(recipe_id)
    
    if recipe and recipe in event.recipes:
        event.recipes.remove(recipe)
        db.session.commit()
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
