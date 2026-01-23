from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Participant, InventoryItem, Recipe, Consumption, Event
from services.llm_service import get_cocktail_suggestion, generate_event_summary, get_omakase_suggestion
import os
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_port=1
)
db.init_app(app)

with app.app_context():
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
    return redirect(url_for('index', _anchor='participants'))

@app.route('/add_inventory', methods=['POST'])
def add_inventory():
    return redirect(url_for('index', _anchor='inventory')) # Deprecated, use save_inventory

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
    return redirect(url_for('index', _anchor='inventory'))

@app.route('/delete_inventory/<int:item_id>', methods=['POST'])
def delete_inventory(item_id):
    item = InventoryItem.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('index', _anchor='inventory'))

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
    return redirect(url_for('index', _anchor='drink'))

@app.route('/event/<int:event_id>/stats')
def event_stats(event_id):
    event = Event.query.get_or_404(event_id)
    consumptions = Consumption.query.filter_by(event_id=event_id).all()
    
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

@app.route('/event/<int:event_id>/get_summary', methods=['POST'])
def get_event_summary(event_id):
    event = Event.query.get_or_404(event_id)
    consumptions = Consumption.query.filter_by(event_id=event_id).all()
    
    # Calculate stats for summary
    stats = {
        'total_drinks': len(consumptions),
        'by_participant': {},
        'drink_counts': {}
    }
    for c in consumptions:
        p_name = c.participant.name
        if p_name not in stats['by_participant']:
            stats['by_participant'][p_name] = {'count': 0, 'drinks': []}
        stats['by_participant'][p_name]['count'] += 1
        stats['by_participant'][p_name]['drinks'].append(c.drink_name)
        
        if c.drink_name not in stats['drink_counts']:
            stats['drink_counts'][c.drink_name] = 0
        stats['drink_counts'][c.drink_name] += 1
        
    # Format stats for LLM
    stats_text = f"总共喝了 {stats['total_drinks']} 杯。\n"
    
    # MVP
    mvp = None
    max_count = 0
    for name, data in stats['by_participant'].items():
        if data['count'] > max_count:
            max_count = data['count']
            mvp = name
    
    if mvp:
        stats_text += f"今日酒神 (MVP)：{mvp}，喝了 {max_count} 杯。\n"
    
    stats_text += "大家喝了：\n"
    for drink, count in stats['drink_counts'].items():
        stats_text += f"- {drink}: {count} 杯\n"
        
    summary = generate_event_summary(event.name, str(event.date), stats_text)
    
    top_drinks = sorted(stats['drink_counts'].items(), key=lambda x: x[1], reverse=True)[:5]

    return jsonify({
        'summary': summary,
        'mvp': mvp,
        'mvp_count': max_count,
        'top_drinks': top_drinks
    })


@app.route('/suggest', methods=['POST'])
def suggest():
    try:
        inventory = InventoryItem.query.all()
        inventory_list = [f"{item.name} ({item.category})" for item in inventory]

        user_request = request.form.get('user_request', '')
        suggestion = get_cocktail_suggestion(inventory_list, user_request)

        # suggestion is now a dict
        return jsonify(suggestion)

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/omakase', methods=['POST'])
def omakase():
    try:
        inventory = InventoryItem.query.all()
        inventory_list = [f"{item.name} ({item.category})" for item in inventory]
        
        mood = request.form.get('mood', '平静')
        weather = request.form.get('weather', '晴朗')
        
        suggestion = get_omakase_suggestion(inventory_list, mood, weather)
        # suggestion is now a dict
        return jsonify(suggestion)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save_recipe', methods=['POST'])
def save_recipe():
    recipe_id = request.form.get('recipe_id')
    name = request.form.get('name')
    ingredients = request.form.get('ingredients')
    instructions = request.form.get('instructions')
    event_id = request.form.get('event_id')
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

    return redirect(url_for('index', _anchor='recipes'))

@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if recipe:
        db.session.delete(recipe)
        db.session.commit()
    return redirect(url_for('index', _anchor='recipes'))

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
    return redirect(url_for('index', _anchor='events'))

@app.route('/event/<int:event_id>/add_recipe', methods=['POST'])
def add_recipe_to_event(event_id):
    recipe_id = request.form.get('recipe_id')
    event = Event.query.get_or_404(event_id)
    recipe = Recipe.query.get(recipe_id)
    
    if recipe and recipe not in event.recipes:
        event.recipes.append(recipe)
        db.session.commit()
        
    return redirect(url_for('index', _anchor='events'))

@app.route('/event/<int:event_id>/remove_recipe', methods=['POST'])
def remove_recipe_from_event(event_id):
    recipe_id = request.form.get('recipe_id')
    event = Event.query.get_or_404(event_id)
    recipe = Recipe.query.get(recipe_id)
    
    if recipe and recipe in event.recipes:
        event.recipes.remove(recipe)
        db.session.commit()
        
    return redirect(url_for('index', _anchor='events'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

