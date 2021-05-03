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


@action('index') # aka Discover
@action.uses(db, auth, 'index.html')
def index():
    return dict()

#
@action('profile/<user_id:int>')
@action.uses(db, session, auth.user, url_signer.verify(), 'profile.html')
def profile(user_id=None):
    assert user_id is not None
    return dict()


@action('recipe/<recipe_id:int>')
@action.uses(db, session, auth.user, url_signer.verify(), 'recipe.html')
def recipe(recipe_id=None):
    rows =  = db(db.ingredients.recipe_id == recipe_id).select()
    return dict(rows =rows)


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
        redirect(URL('recipe',recipe_id, signer=url_signer))
        #redirect(URL('edit_phones',contact_id , url_signer))
    # Either this is a GET request, or this is a POST but not accepted = with errors.
    return dict(form=form, url_signer=url_signer)

