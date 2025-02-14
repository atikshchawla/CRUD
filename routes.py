from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User, InventoryItem

routes = Blueprint('routes', __name__)

# Authentication Routes
@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('routes.register'))
            
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('routes.login'))
    return render_template('register.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('routes.dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@routes.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.login'))



@routes.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        quantity = request.form['quantity']
        
        new_item = InventoryItem(
            name=name,
            description=description,
            quantity=quantity,
            user_id=current_user.id
        )
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('routes.dashboard'))
    return render_template('add_item.html')

@routes.route('/delete/<int:id>')
@login_required
def delete_item(id):
    item = InventoryItem.query.get_or_404(id)
    if item.owner != current_user:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('routes.dashboard'))

@routes.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    item = InventoryItem.query.get_or_404(id)
    if item.owner != current_user:
        abort(403)
        
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.quantity = request.form['quantity']
        db.session.commit()
        return redirect(url_for('routes.dashboard'))
    return render_template('edit_item.html', item=item)

@routes.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    items = InventoryItem.query.filter(
        InventoryItem.name.ilike(f'%{query}%'),
        InventoryItem.user_id == current_user.id
    ).all()
    return render_template('dashboard.html', items=items)

# @routes.route('/dashboard')  # <-- Add explicit path
# @login_required
# def dashboard():
#     items = InventoryItem.query.filter_by(user_id=current_user.id).all()
#     return render_template('dashboard.html', items=items)

@routes.route('/dashboard')
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    items = InventoryItem.query.filter_by(user_id=current_user.id).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template('dashboard.html', items=items)

@routes.route('/home')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    return render_template('index.html')

# Update existing routes to use index as landing
@routes.route('/')
def home_redirect():
    return redirect(url_for('routes.index'))