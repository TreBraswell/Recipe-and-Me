"""
This file defines the database models
"""
import datetime
from .common import db, Field
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None


db.define_table(
    'recipes',
    Field('name', 'string', requires=IS_NOT_EMPTY()),
    Field('steps', 'string'),
    Field('cook_time', 'integer'),
    Field('m_datetime', 'datetime', requires=[IS_DATETIME(), IS_NOT_EMPTY()],
          readable=False, writable=False),
    Field('m_email', 'string', default=get_user_email,
          readable=False, writable=False),
)

db.define_table(
    'recipe_ingredients',
    Field('recipe', 'reference recipes'),
    Field('ingredient_list', 'reference recipe_ingredients'),
    Field('Quantity', 'string')
)

db.define_table(
    'allergies',
    Field('m_email', 'string', default=get_user_email,
          readable=False, writable=False),
    Field('allergen', 'reference recipe_ingredients'),
)

db.define_table(
    'ingredients',
    Field('name', 'string', requires=IS_NOT_EMPTY()),
    Field('avg_price', 'integer'),
)

db.define_table(  # List of all tags for ALL recipes
    'tags',
    Field('name', 'string', requires=IS_NOT_EMPTY()),
)

db.define_table(
    'recipe_tags',
    Field('recipe', 'reference recipes'),
    # all tags that reference the corresponding recipe
    Field('tag_list', 'reference tags'),
)

db.define_table(  # List of Substitutions for ingredients
    'substitutions',
    Field('original_ingredient', 'reference ingredients'),

)

db.commit()
