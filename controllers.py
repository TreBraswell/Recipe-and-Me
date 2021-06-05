"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""
import time

import uuid
import random

from yatl.helpers import A
from .models import get_user_email, get_user

from pydal.validators import *
from py4web.utils.url_signer import URLSigner
from py4web.utils.form import Form, FormStyleBulma
from py4web import action, request, abort, redirect, URL
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash, Field
url_signer = URLSigner(session)

@action('search_recipes')
@action.uses(db)
def search_recipes():
    q = request.params.get("q")
    t = request.params.get("t")
    t = [] if t is None or t == '' else t.split(',')
    rows = get_shared_recipes(q, t)
    return dict(rows=rows)

@action('search_ingredients')
@action.uses(db)
def search_ingredients():
    q = request.params.get("q")
    ingredients = db(db.ingredients.name.like(f'%{q}%')).select(orderby=db.ingredients.name).as_list()
    return dict(ingredients=ingredients)

@action('get_recipe_ingredients/<recipe_id>', method="GET")
@action.uses(db)
def get_recipe_ingredients(recipe_id):
    # get recipe ingredients names out from the database
    rows = db((db.recipe_ingredients.recipe == recipe_id) &
        (db.recipe_ingredients.ingredient == db.ingredients.id)
        ).select(db.ingredients.name, db.recipe_ingredients.quantity).as_list()
    return dict(rows=rows)

@action('set_recipe_ingredient', method=["POST"])
@action.uses(url_signer.verify(), db)
def set_recipe_ingredient():
    recipe_id =request.json.get('recipe_id')
    recipe_ingredient_id = request.json.get('recipe_ingredient_id')
    ingredient_name = request.json.get('ingredient_name')
    quantity = request.json.get('quantity')

    if get_user_email() != db.recipes[recipe_id].m_email:
        return "Access denied"
    
    return update_or_insert_recipe_ingredient(recipe_id, recipe_ingredient_id, ingredient_name, quantity)

def update_or_insert_recipe_ingredient(recipe_id, recipe_ingredients_id, ingredient_name, quantity):
    # get ID of existing ingredient row in ingredients table, or insert a new row for the ingredient
    ingredient = db(db.ingredients.name == ingredient_name).select(db.ingredients.id).first()
    ingredient_id = ingredient.id if ingredient is not None else None

    if ingredient_id is None:
        ingredient_id = db.ingredients.insert(name=ingredient_name)

    # update or insert to our row in recipe ingredients
    if recipe_ingredients_id is not None:
        # if we have a recipe_ingredients id, update that entry
        db.recipe_ingredients.update_or_insert(
            (db.recipe_ingredients.id == recipe_ingredients_id),
            recipe=recipe_id,
            ingredient=ingredient_id,
            quantity=quantity)
        response = "ok"
    else:
        # otherwise, update or insert a recipe_ingredients entry with an unknown id
        db.recipe_ingredients.update_or_insert(
            ((db.recipe_ingredients.recipe == recipe_id) & (db.recipe_ingredients.ingredient == ingredient_id)),
            recipe=recipe_id,
            ingredient=ingredient_id, 
            quantity=quantity)
        
        recipe_ingredient_id = db(((db.recipe_ingredients.recipe == recipe_id) & (db.recipe_ingredients.ingredient == ingredient_id))).select().first().id

    return recipe_ingredients_id

@action('delete_recipe_ingredient', method="POST")
@action.uses(url_signer.verify(), db)
def delete_recipe_ingredient():
    recipe_id = request.json.get('recipe_id')
    recipe_ingredient_id = request.json.get('recipe_ingredient_id') 

    if get_user_email() != db.recipes[recipe_id].m_email:
        return "Access denied"

    # delete recipe ingredients row matching this recipe and ingredient
    db(db.recipe_ingredients.id == recipe_ingredient_id).delete()

    return "ok"

@action('index')
def index_redirect():
    redirect(URL(''))

@action('')  # aka Discover
@action.uses(db, auth, 'index.html', 'layout.html')
def index():
    rows = get_shared_recipes()
    current_user = get_user()
    return dict(
        rows=rows,
        url_signer=url_signer,
        search_url = URL('search_recipes', signer=url_signer),
        load_shared_recipes_url = URL('load_shared_recipes'),
        update_rating_url = URL ('update_rating', signer=url_signer ),
        current_user = current_user,
    )


@action('profile', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'profile.html', 'layout.html', 'auth.html')
def profile():

    user = db(db.auth_user.email == get_user_email()).select().as_list()[0]
    myrecipes = db(db.recipes.m_email == get_user_email()).select()
    form = Form(
        [Field('first_name', 'string', requires=IS_NOT_EMPTY(
            error_message="First name required")),
         Field('last_name', 'string', requires=IS_NOT_EMPTY(
             error_message="Last name required"))],
        record=user,
        csrf_session=session,
        deletable=False,
        formstyle=FormStyleBulma
    )

    if form.accepted:
        row = db(db.auth_user.email == get_user_email()).select().first()
        row.update_record(
            first_name=form.vars['first_name'],
            last_name=form.vars['last_name']
        )
        redirect(URL('profile', signer=url_signer))
    temps =[]
    return dict(
        temps=temps,
        name=f"{user['first_name']} {user['last_name']}",
        url_signer=url_signer,
        form=form,
        myrecipes = myrecipes,
        load_recipes_url = URL('load_recipes', signer=url_signer),
    
        add_recipe_url = URL('add_recipe', signer=url_signer),
        delete_recipe_url = URL('delete_recipe', signer=url_signer),
        edit_recipe_url = URL('edit_recipe', signer=url_signer),
        search_ingredients_url = URL('search_ingredients', signer=url_signer),

        set_recipe_ingredient_url = URL('set_recipe_ingredient', signer=url_signer),
        delete_recipe_ingredient_url = URL('delete_recipe_ingredient', signer=url_signer),
    )

@action('load_recipes')
@action.uses(url_signer.verify(), db)
def load_recipes():
    rows = db(db.recipes.m_email == get_user_email()).select(orderby=~db.recipes.id).as_list()
    
    for row in rows:
        toret =[]
        recipe_ingredients = db(db.recipe_ingredients.recipe == row["id"]).select().as_list()
        for temp in recipe_ingredients:
            toret.append({"amount": temp["quantity"], "ingredient": db(db.ingredients.id == temp["ingredient"]).select().first().name, 'id': temp["id"]})
        row["myingredients"] = toret
    return dict(rows=rows)

@action('load_shared_recipes')
@action.uses(db)
def load_shared_recipes():
    rows = get_shared_recipes()
    tags = db(db.tags).select().as_list()
    for tag in tags:
        tag = dict(name=tag, is_active=False)
    current_user = get_user() 
    return dict(rows=rows, tags=tags, current_user = current_user)

@action('add_recipe', method="POST")
@action.uses(url_signer.verify(), db)
def add_recipe():
    id = db.recipes.insert(
        name=request.json.get('name'),
        steps=request.json.get('steps'),
        cook_time=request.json.get('cook_time'),
        shared=request.json.get('shared'),
    )
    finaltemp = []
    myingredients1 = request.json.get('ingredients')
    
    for temp in myingredients1: 
        
        temp2 = db(db.ingredients.name == temp["ingredient"]).select().first()
        if temp2:
            temp3 = temp2
        else:
           temp3 =  db.ingredients.insert(name = temp["ingredient"])
        temp["id"] = db.recipe_ingredients.insert(recipe = id,ingredient = temp3,quantity = temp["amount"],)
        
    return dict(id=id, myingredients=myingredients1)

@action('delete_recipe', method="POST")
@action.uses(url_signer.verify(), db)
def delete_recipe():
    id = request.json.get('id')
    assert id is not None
    db(db.recipes.id == id).delete()
    return "ok"

@action('edit_recipe', method="POST")
@action.uses(url_signer.verify(), db)
def edit_recipe():
    # Updates the db record.
    id = request.json.get("id")
    field = request.json.get("field")
    value = request.json.get("value")

    if field == "myingredients":
        return "Missing field"
    
    db(db.recipes.id == id).update(**{field: value})
    return "ok"

@action('edit_ingredient', method="POST")
@action.uses(url_signer.verify(), db)
def edit_ingredient():
    # Updates the db record.
    id = request.json.get("id")
    field = request.json.get("field")
    value = request.json.get("value")
    amou = request.json.get("amount")
    ingre = request.json.get("ingredient")
    if field == 'ingredient' and db(db.ingredients.name == value).select().first() == None:
        
        newref = db.ingredients.insert(
            name = value,
            avg_price = random.randrange(5,15),
        )
        db(db.recipe_ingredients.recipe == id).update(**{'ingredient': newref})
    elif field == "amount":
        db(db.recipe_ingredients.recipe == id).update(**{'quantity': value})
    
    return "ok"

def get_shared_recipes(search_term='', search_tags=[]):
    rows = db((db.recipes.shared == True) & (db.recipes.name.like(f'%{search_term}%'))).select(orderby=~db.recipes.id).as_list()
    for row in reversed(rows):
        # create ingredients string
        ingredient_rows = db(
            (db.recipe_ingredients.recipe == row['id'])).select()
        s = ''
        row["ingredients_rows"] = []
        if ingredient_rows:
            row0 = ingredient_rows[0]
            ingredient_name = db.ingredients[row0['ingredient']].name
            s = ingredient_name
            ingredient = {"name": ingredient_name, "quantity": row0.quantity}
            row["ingredients_rows"].append(ingredient)
            for ingredient_row in ingredient_rows[1:]:
                ingredient_name = db.ingredients[ingredient_row['ingredient']].name
                s += f', {ingredient_name}'
                ingredient = {"name": ingredient_name, "quantity": ingredient_row.quantity}
                row["ingredients_rows"].append(ingredient)
        row["ingredients"] = s
        
        
         # create rating fields
        ratings =  db(( db.rating.recipe == row['id'] )).select()
        row["total_rating"] = 0
        row ["raters"] = []
        if len(ratings)!= 0:
            for rating in ratings:
                row["total_rating"] =row["total_rating"] + rating["rating"]
                row["raters"].append(rating["user"])
        
        
        # create tags string
        tag_rows = db((db.recipe_tags.recipe == row['id'])).select()
        s = ''
        row["tag_rows"] = []
        unmatched_tags = search_tags.copy()
        if tag_rows:
            row0 = tag_rows[0]
            tag_name = db.tags[row0['tag']].name
            s = tag_name
            row["tag_rows"].append(tag_name)

            if tag_name in search_tags:
                unmatched_tags.remove(tag_name)
            
            for tag_row in tag_rows[1:]:
                tag_name = db.tags[tag_row['tag']].name
                s += f', {tag_name}'
                row["tag_rows"].append(tag_name)
                if tag_name in unmatched_tags:
                    unmatched_tags.remove(tag_name)
        row["tags"] = s
        
        # remove row if searching with tags not in this row
        if (len(unmatched_tags) > 0):
                rows.remove(row)
    return rows

@action('update_rating', method="POST")
@action.uses(url_signer.verify(), db, auth.user)
def update_rating():
    """Sets the rating for an image."""
    row_id = request.json.get('row_id')
    rating = request.json.get('rating')
    assert row_id is not None and rating is not None
    db.rating.update_or_insert(
        ((db.rating.recipe == row_id) & (db.rating.user == get_user())),
        recipe=row_id,
        user=get_user(),
        rating=rating
    )
    return "ok"