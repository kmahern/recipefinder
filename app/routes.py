from datetime import datetime, timezone
from urllib.parse import urlsplit
from flask import flash, redirect, render_template, request, url_for
from app import app
from app.forms import EditProfileForm, IngredientForm, RecipeMethodForm, LoginForm, RecipeForm, RegistrationForm
from flask_login import current_user, login_required, login_user, logout_user
import sqlalchemy as sa
from app import db
from app.models import Ingredient, Recipe, User

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    recipes = db.session.scalars(user.recipes.select()).all()
    return render_template('user.html', user=user, recipes=recipes)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = RecipeForm()
    if form.validate_on_submit():
        recipe = Recipe(title=form.title.data, creator=current_user)
        db.session.add(recipe)
        db.session.commit()
        flash('Your recipe has been added!')
        return redirect(url_for('recipe', id=recipe.id))
    recipes = db.session.scalars(current_user.recipes.select()).all()
    return render_template("index.html", title='Home Page', form=form,
                           recipes=recipes)

@app.route('/recipe/<id>', methods=['GET', 'POST'])
@login_required
def recipe(id):
    ingredient_form = IngredientForm()
    recipe_method_form = RecipeMethodForm()
    recipe = db.first_or_404(sa.select(Recipe).where(Recipe.id == id))
    if ingredient_form.validate_on_submit():
        ingredient = Ingredient(description=ingredient_form.description.data, quantity=ingredient_form.quantity.data, unit=ingredient_form.unit.data, recipe=recipe)
        db.session.add(ingredient)
        db.session.commit()
        return redirect(url_for('recipe', id=recipe.id))
    if recipe_method_form.validate_on_submit():
        recipe.method = recipe_method_form.method.data
        db.session.commit()
        return redirect(url_for('index'))
    elif request.method == 'GET':
        recipe_method_form.method.data = recipe.method
    ingredients = db.session.scalars(recipe.ingredients.select()).all()
    return render_template('recipe.html', recipe=recipe, ingredients=ingredients, ingredient_form=ingredient_form, recipe_method_form=recipe_method_form)

@app.route('/delete_ingredient/<id>', methods=['GET'])
@login_required
def delete_ingredient(id):
    ingredient = db.first_or_404(sa.select(Ingredient).where(Ingredient.id == id))
    recipe = ingredient.recipe
    Ingredient.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('recipe', id=recipe.id))
    