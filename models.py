"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None


def get_time():
    return datetime.datetime.utcnow()


db.define_table(
    'recipes',
    Field('name', 'string', requires=IS_NOT_EMPTY()),
    Field('steps', 'string'),
    Field('cook_time', 'integer'),
    Field('rating', 'float', default=0.00),
    Field('num_ratings', 'integer', default=0),
    Field('m_datetime', 'datetime', requires=[IS_DATETIME(), IS_NOT_EMPTY()],
          readable=False, writable=False),
    Field('m_email', 'string', default=get_user_email,
          readable=False, writable=False),
    Field('shared', 'boolean', default=False)
)

db.define_table(
    'saved_recipes',
    Field('recipe', 'reference recipes'),
    Field('m_email', default=get_user_email, readable=False, writable=False),
    Field('starred', 'boolean')
)

db.define_table(
    'ingredients',
    Field('name', 'string', requires=IS_NOT_EMPTY()),
    Field('avg_price', 'integer')
)

db.define_table(
    'recipe_ingredients',
    Field('recipe', 'reference recipes'),
    Field('ingredient', 'reference ingredients'),
    Field('quantity', 'string')
)

db.define_table(
    'allergies',
    Field('m_email', 'string', default=get_user_email,
          readable=False, writable=False),
    Field('allergen', 'reference ingredients')
)

db.define_table(  # List of all tags for ALL recipes
    'tags',
    Field('name', 'string', requires=IS_NOT_EMPTY())
)

db.define_table(
    'recipe_tags',
    Field('recipe', 'reference recipes'),
    Field('tag', 'reference tags')  # one tag for one corresponding recipe
)

db.define_table(  # List of Substitutions for ingredients
    'substitutions',
    Field('original_ingredient', 'reference ingredients'),
    Field('sub_ingredient', 'reference ingredients'),
    Field('sub_rate', 'integer', requires=IS_INT_IN_RANGE(1, 6))
)

db.commit()
