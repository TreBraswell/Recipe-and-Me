"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  ... the action uses the generic.html template
@action.uses(session)         ... the action uses the session
@action.uses(db)              ... the action uses the db
@action.uses(T)               ... the action uses the i18n & pluralization
@action.uses(auth.user)       ... the action requires a logged in user
@action.uses(auth)            ... the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app 
will result in undefined behavior
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
    """
    Returns a list of all the shared recipes which have a title containing
    the search query and which are tagged with all of the tag filters bring used
    in the search.
    """

    query = request.params.get("q")
    tag = request.params.get("t")

    tag = [] if tag is None or tag == '' else tag.split(',')
    rows = get_shared_recipes(query, tag)

    return dict(rows=rows)

@action('search_ingredients')
@action.uses(db)
def search_ingredients():
    """
    Returns a list of ingredients, found by searching for ingredients that
    contain the string passed in, or simply returns all ingredients if
    there is no search query.
    """

    query = request.params.get("q")

    ingredients = db(db.ingredients.name.like(f'%{query}%')
        ).select(orderby=db.ingredients.name).as_list()

    return dict(ingredients=ingredients)

@action('get_recipe_ingredients/<recipe_id>', method="GET")
@action.uses(db)
def get_recipe_ingredients(recipe_id):
    """
    Returns a list of all the ingredients for a recipe and their quantities.
    """

    rows = db((db.recipe_ingredients.recipe == recipe_id) &
        (db.recipe_ingredients.ingredient == db.ingredients.id)
        ).select(
            db.recipe_ingredients.id, 
            db.ingredients.name, 
            db.recipe_ingredients.quantity
        ).as_list()

    return dict(rows=rows)

@action('set_recipe_ingredient', method=["POST"])
@action.uses(url_signer.verify(), db)
def set_recipe_ingredient():
    """
    Sets a recipe-ingredient's recipe, ingredient and quantity, for one of a
    user's existing recipes. Can only be used by the creator of the recipe.
    Reuses existing ingredient rows if they are in the database to avoid
    ingredient duplication.
    """

    recipe_id = request.json.get('recipe_id')
    recipe_ingredient_id = request.json.get('recipe_ingredient_id')
    ingredient_name = request.json.get('ingredient_name')
    quantity = request.json.get('quantity')

    if get_user_email() != db.recipes[recipe_id].m_email:
        return "Access denied"
    
    # get ID of existing row in ingredients table, or insert a new row
    ingredient = db(db.ingredients.name == ingredient_name
        ).select(db.ingredients.id).first()

    ingredient_id = ingredient.id if ingredient is not None else None

    if ingredient_id is None:
        ingredient_id = db.ingredients.insert(name=ingredient_name)

    # update or insert to our row in recipe ingredients
    if recipe_ingredient_id is not None:
        # if we have a recipe_ingredients id, update that entry
        db.recipe_ingredients.update_or_insert(
            (db.recipe_ingredients.id == recipe_ingredient_id),
            recipe=recipe_id,
            ingredient=ingredient_id,
            quantity=quantity)

        response = dict(recipe_ingredient_id=recipe_ingredient_id, ok="ok")
    else:
        # otherwise, update/insert a recipe_ingredients entry with an unknown id
        db.recipe_ingredients.update_or_insert(
            ((db.recipe_ingredients.recipe == recipe_id) & 
            (db.recipe_ingredients.ingredient == ingredient_id)),
            recipe=recipe_id,
            ingredient=ingredient_id, 
            quantity=quantity)
        
        recipe_ingredient_id = db(
            ((db.recipe_ingredients.recipe == recipe_id) & 
            (db.recipe_ingredients.ingredient == ingredient_id))
            ).select().first().id

    return dict(recipe_ingredient_id=recipe_ingredient_id)

@action('delete_recipe_ingredient', method="POST")
@action.uses(url_signer.verify(), db)
def delete_recipe_ingredient():
    """
    Deletes a recipe-ingredient for one of a user's existing recipes. Can only
    be used by the creator of the recipe.
    """

    recipe_id = request.json.get('recipe_id')
    recipe_ingredient_id = request.json.get('recipe_ingredient_id') 

    if get_user_email() != db.recipes[recipe_id].m_email:
        return "Access denied"

    # delete recipe ingredients row matching this recipe and ingredient
    db(db.recipe_ingredients.id == recipe_ingredient_id).delete()

    return "ok"

@action('set_recipe_tag', method=["POST"])
@action.uses(url_signer.verify(), db)
def set_recipe_tag():
    """
    Sets a recipe-tag to a new value, inserting or reusing existing tags as
    necessary. Can be used by any logged-in user, not only the creator of the
    recipe, in order to promote collaborative recipe categorization.
    """

    recipe_id = request.json.get('recipe_id')
    tag_name = request.json.get('tag_name')

    # get ID of existing tag row in tags table, or insert a new row for the tag
    tag = db(db.tags.name == tag_name).select(db.tags.id).first()
    tag_id = tag.id if tag is not None else None

    if tag_id is None:
        tag_id = db.tags.insert(name=tag_name)
    recipe_tag = db(
        (db.recipe_tags.recipe == recipe_id) & (db.recipe_tags.tag == tag_id)
        ).select(db.recipe_tags.id).first()
    if recipe_tag is not None:
        return None
    
    db.recipe_tags.insert(recipe=recipe_id, tag=tag_id)

    return dict(ok="ok")

@action('delete_recipe_tag', method="POST")
@action.uses(url_signer.verify(), db)
def delete_tag():
    recipe_id = request.json.get('recipe_id')
    tag_name = request.json.get('tag_name')

    # get ID of existing tag row in tags table
    tag = db(db.tags.name == tag_name).select(db.tags.id).first()
    tag_id = tag.id if tag is not None else None

    # delete recipe tags row matching this recipe and tag
    db((db.recipe_tags.recipe == recipe_id) & 
        (db.recipe_tags.tag == tag_id)).delete()

    return "ok"

@action('index')
def index_redirect():
    redirect(URL(''))

@action('')  # aka Discover
@action.uses(db, auth, 'index.html')
def index():
    """
    Returns the index page, also known as the discover page.
    """

    rows = get_shared_recipes()
    current_user = get_user()

    return dict(
        rows=rows,
        url_signer=url_signer,
        current_user = current_user,
        search_url = URL('search_recipes', signer=url_signer),
        load_shared_recipes_url = URL('load_shared_recipes'),
        update_rating_url = URL('update_rating', signer=url_signer),
        set_recipe_tag_url = URL('set_recipe_tag', signer=url_signer),
        delete_recipe_tag_url = URL('delete_recipe_tag', signer=url_signer),
    )


@action('profile', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'profile.html')
def profile():
    """
    Returns the user profile page on GET, and updates user profile information
    on POST.
    """

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

        set_recipe_ingredient_url = URL(
            'set_recipe_ingredient', signer=url_signer),
        delete_recipe_ingredient_url = URL(
            'delete_recipe_ingredient', signer=url_signer),
    )

@action('load_recipes')
@action.uses(url_signer.verify(), db)
def load_recipes():
    """
    Loads a user's recipes and their recipes' ingredients lists. Sent to
    and displayed by the profile page when it initializes.
    """

    rows = db(db.recipes.m_email == get_user_email()
        ).select(orderby=~db.recipes.id).as_list()
    
    for row in rows:
        myingredients = []
        recipe_ingredients = db(db.recipe_ingredients.recipe == row["id"]
            ).select().as_list()

        for ingredient in recipe_ingredients:
            ingredient_name = db(db.ingredients.id == ingredient["ingredient"]
                ).select().first().name, 

            myingredients.append({
                "amount": ingredient["quantity"], 
                "ingredient": ingredient_name,
                "id": ingredient["id"]
            })
        row["myingredients"] = myingredients

    return dict(rows=rows)

@action('load_shared_recipes')
@action.uses(db)
def load_shared_recipes():
    """
    Loads shared recipes across all users, along with their ingredients and 
    tags. Sent to and displayed bt the main discover page when it initializes.
    """

    rows = get_shared_recipes()
    tags = db(db.tags).select().as_list()

    for tag in tags:
        tag = dict(name=tag, is_active=False)
    
    return dict(rows=rows, tags=tags)

@action('add_recipe', method="POST")
@action.uses(url_signer.verify(), db)
def add_recipe():
    """
    Adds a recipe for a particular user, inserting both the one-to-one (recipe 
    table) data and the many-to-many (recipe ingredients table) data as needed.
    """

    recipe_id = db.recipes.insert(
        name=request.json.get('name'),
        steps=request.json.get('steps'),
        cook_time=request.json.get('cook_time'),
        shared=request.json.get('shared'),
        image_url=request.json.get('image_url'),
    )

    recipe_ingredients = request.json.get('ingredients')
    
    for recipe_ingredient in recipe_ingredients:
        # get ingredient id if the ingredient is already known to the app
        ingredient_id = db(
            db.ingredients.name == recipe_ingredient["ingredient"]
            ).select().first()

        # if not found, insert new ingredient (visible to every user and
        # reusable in every future recipe)
        if ingredient_id is None:
            ingredient_id =  db.ingredients.insert(
               name = recipe_ingredient["ingredient"]
            )

        # link the ingredient and recipe with a new recipe-ingredient entry
        recipe_ingredient["id"] = db.recipe_ingredients.insert(
            recipe = recipe_id, 
            ingredient = ingredient_id, 
            quantity = recipe_ingredient["amount"],
        )
        
    return dict(id=recipe_id, myingredients=recipe_ingredients)

@action('delete_recipe', method="POST")
@action.uses(url_signer.verify(), db)
def delete_recipe():
    """
    Deletes a recipe entirely (which then cascades to delete the corresponding
    recipe-ingredients automatically). Can only be used by the recipe creator.
    """
    recipe_id = request.json.get('id')

    if get_user_email() != db.recipes[recipe_id].m_email:
        return "Access denied"

    assert recipe_id is not None
    db(db.recipes.id == recipe_id).delete()

    return "ok"

@action('edit_recipe', method="POST")
@action.uses(url_signer.verify(), db)
def edit_recipe():
    """
    Edits one of a recipe's one-to-one fields. For example, the recipe name,
    preparation steps, and cook time, as well as others. Can only be used by the
    recipe creator. Does not allow editing recipe ingredients, which is instead
    handled by set_recipe_ingredient().
    """

    recipe_id = request.json.get("id")
    field = request.json.get("field")
    value = request.json.get("value")

    if get_user_email() != db.recipes[recipe_id].m_email:
        return "Access denied"

    if field == "myingredients":
        return "Missing field"
    
    db(db.recipes.id == recipe_id).update(**{field: value})
    return "ok"

def get_shared_recipes(search_term='', search_tags=[]):
    rows = db((db.recipes.shared == True) & 
        (db.recipes.name.like(f'%{search_term}%'))
        ).select(db.recipes.ALL, orderby=~db.recipes.id)

    rows_ingredient_match = db((db.recipes.shared == True) & 
        (db.recipe_ingredients.recipe == db.recipes.id) &
        (db.recipe_ingredients.ingredient == db.ingredients.id) &
        (db.ingredients.name.like(f'%{search_term}%'))
        ).select(db.recipes.ALL, orderby=~db.recipes.id, distinct=True)

    rows = rows | rows_ingredient_match
    rows = sorted(rows.as_list(), key=lambda x: -x['id'])

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
                ingredient_name = db.ingredients[
                    ingredient_row['ingredient']].name
                s += f', {ingredient_name}'
                ingredient = {
                    "name": ingredient_name,
                    "quantity": ingredient_row.quantity
                }

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
    """
    Sets the 1-to-5 star rating for a recipe for a single user.
    """

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