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
from yatl.helpers import A
from .models import get_user_email

from pydal.validators import *
from py4web.utils.url_signer import URLSigner
from py4web.utils.form import Form, FormStyleBulma
from py4web import action, request, abort, redirect, URL
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash, Field
url_signer = URLSigner(session)


@action('index')  # aka Discover
@action.uses(db, auth, 'index.html', 'layout.html')
def index():
    rows = db(db.recipes.shared == True).select().as_list()
    for row in rows:
        # create ingredients string
        ingredient_rows = db(
            (db.recipe_ingredients.recipe == row['id'])).select()
        s = ''
        if ingredient_rows:
            row0 = ingredient_rows[0]
            ingredient_name = db.ingredients[row0['ingredient']].name
            s = ingredient_name
            for ingredient_row in ingredient_rows[1:]:
                ingredient_name = db.ingredients[ingredient_row['ingredient']].name
                s += f', {ingredient_name}'
        row["ingredients"] = s

        # create tags string
        tag_rows = db((db.recipe_tags.recipe == row['id'])).select()
        s = ''
        if tag_rows:
            row0 = tag_rows[0]
            tag_name = db.tags[row0['tag']].name
            s = tag_name
            for tag_row in tag_rows[1:]:
                tag_name = db.tags[tag_row['tag']].name
                s += f', {tag_name}'
        row["tags"] = s

    return dict(rows=rows, url_signer=url_signer)


@action('profile', method=["GET", "POST"])
@action.uses(db, session, auth.user, url_signer.verify(), 'profile.html', 'layout.html', 'auth.html')
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

    return dict(
        name=f"{user['first_name']} {user['last_name']}",
        url_signer=url_signer,
        form=form,
        myrecipes = myrecipes
    )
@action('add_recipe', method=["GET", "POST"])
@action.uses(db, session, auth.user,  url_signer.verify(),'add_recipe.html')
def add_recipe():
    # Insert form: no record= in it.
    form = Form(db.recipes, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We simply redirect; the insertion already happened.
        redirect(URL('profile', signer=url_signer))
    # Either this is a GET request, or this is a POST but not accepted = with errors.
    return dict(form=form,url_signer=url_signer)

@action('edit_recipe/<recipe_id>', method=["GET", "POST"])
@action.uses(db, session, auth.user, url_signer.verify(), 'edit_recipe.html')
def edit_recipe(recipe_id=None):
    assert recipe_id is not None

    # We read the product being edited from the db.
    # p = db(db.product.id == contact_id).select().first()
    p = db.recipes[recipe_id]
    if p is None:
        # Nothing found to be edited!
       redirect(URL('profile', signer=url_signer))
    # Edit form: it has record=
    form = Form(db.recipes, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # The update already happened!
        redirect(URL('profile', signer=url_signer))
    return dict(form=form, url_signer=url_signer)

@action('delete_recipe/<recipe_id>')
@action.uses(db, session, auth.user, url_signer.verify())
def delete_recipe(recipe_id=None):
    assert recipe_id is not None
    db(db.ingredients.recipe_id == recipe_id).delete()
    db(db.recipes.id == recipe_id).delete()
    redirect(URL('profile', signer=url_signer))

@action('edit_ingredient/<recipe_id>')
@action.uses(db, session, auth.user, url_signer.verify(), 'edit_ingredient.html')
def edit_ingredient(recipe_id =None):
    assert recipe_id is not None
    rows  = db(db.ingredients.recipe_id == recipe_id).select()
    return dict(rows =rows,url_signer=url_signer,myid = recipe_id)


@action('add_ingredient/<recipe_id>', method=["GET", "POST"])
@action.uses(db, session, auth.user,url_signer.verify(), 'add_ingredient.html')
def add_ingredient(recipe_id =None):
    assert recipe_id is not None
    # Insert form: no record= in it.
    form = Form([Field('name', requires=IS_NOT_EMPTY()), Field('avg_price', requires=IS_NOT_EMPTY())], csrf_session=session,
            formstyle=FormStyleBulma)
    #mycontact = db(db.contact.id ==contact_id).select().first()
    
    if form.accepted:
        db.ingredients.insert(
        name = form.vars['name'],
        avg_price = form.vars['avg_price'],
        recipe_id = recipe_id
        )
        # We simply redirect; the insertion already happened.
        redirect(URL('edit_ingredient',recipe_id, signer=url_signer))
        #redirect(URL('edit_phones',contact_id , url_signer))
    # Either this is a GET request, or this is a POST but not accepted = with errors.
    return dict(form=form, url_signer=url_signer)
