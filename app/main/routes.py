from datetime import datetime, timezone
from urllib.parse import urlsplit
from flask import current_app, flash, redirect, render_template, request, url_for, g
from app.main.forms import EditProfileForm, IngredientForm, RecipeMethodForm, RecipeForm
from flask_login import current_user, login_required
import sqlalchemy as sa
from app import db
from app.models import Ingredient, Recipe, User
from app.main import bp
from flask import g
from app.main.forms import SearchForm

@bp.route('/user/<username>')
@login_required
def user(username):
    page = request.args.get('page', 1, type=int)
    user = db.first_or_404(sa.select(User).where(User.username == username))
    # recipes = db.session.scalars(user.recipes.select()).all()
    query = user.recipes.select().order_by(Recipe.timestamp.desc())
    recipes = db.paginate(query, page=page,
                        per_page=current_app.config['RECIPES_PER_PAGE'], error_out=False)
    next_url = url_for('main.index', page=recipes.next_num) \
        if recipes.has_next else None
    prev_url = url_for('main.index', page=recipes.prev_num) \
        if recipes.has_prev else None
    return render_template('user.html', user=user, recipes=recipes.items, next_url=next_url, prev_url=prev_url)

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        g.search_form = SearchForm()

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = RecipeForm()
    page = request.args.get('page', 1, type=int)
    if form.validate_on_submit():
        recipe = Recipe(title=form.title.data, creator=current_user)
        db.session.add(recipe)
        db.session.commit()
        flash('Your recipe has been added!')
        return redirect(url_for('main.recipe', id=recipe.id))
    query = current_user.recipes.select().order_by(Recipe.timestamp.desc())
    recipes = db.paginate(query, page=page,
                        per_page=current_app.config['RECIPES_PER_PAGE'], error_out=False)
    next_url = url_for('main.index', page=recipes.next_num) \
        if recipes.has_next else None
    prev_url = url_for('main.index', page=recipes.prev_num) \
        if recipes.has_prev else None
    return render_template("index.html", title='Home Page', form=form,
                           recipes=recipes.items, next_url=next_url, prev_url=prev_url)

@bp.route('/recipe/<id>', methods=['GET', 'POST'])
@login_required
def recipe(id):
    ingredient_form = IngredientForm()
    recipe_method_form = RecipeMethodForm()
    recipe = db.first_or_404(sa.select(Recipe).where(Recipe.id == id))
    if ingredient_form.validate_on_submit():
        ingredient = Ingredient(description=ingredient_form.description.data, quantity=ingredient_form.quantity.data, unit=ingredient_form.unit.data, recipe=recipe)
        db.session.add(ingredient)
        db.session.commit()
        return redirect(url_for('main.recipe', id=recipe.id))
    if recipe_method_form.validate_on_submit():
        recipe.method = recipe_method_form.method.data
        db.session.commit()
        return redirect(url_for('main.index'))
    elif request.method == 'GET':
        recipe_method_form.method.data = recipe.method
    ingredients = db.session.scalars(recipe.ingredients.select()).all()
    return render_template('recipe.html', recipe=recipe, ingredients=ingredients, ingredient_form=ingredient_form, recipe_method_form=recipe_method_form)

@bp.route('/delete_ingredient/<id>', methods=['GET'])
@login_required
def delete_ingredient(id):
    ingredient = db.first_or_404(sa.select(Ingredient).where(Ingredient.id == id))
    recipe = ingredient.recipe
    Ingredient.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('main.recipe', id=recipe.id))

@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    recipes, total = Recipe.search(g.search_form.q.data, page,
                               current_app.config['RECIPES_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['RECIPES_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=('Search'), recipes=recipes,
                           next_url=next_url, prev_url=prev_url)
    