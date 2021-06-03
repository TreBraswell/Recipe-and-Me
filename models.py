"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None


def get_user():
    return auth.current_user.get('id') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


db.define_table(
    'recipes',
    Field('name', 'string', requires=IS_NOT_EMPTY()),
    Field('steps', 'string'),
    Field('cook_time', 'integer'),
    Field('rating', 'float', default=0.00),
    Field('num_ratings', 'integer', default=0),
    Field('m_datetime', 'datetime', default=get_time(), requires=[IS_DATETIME(), IS_NOT_EMPTY()],
          readable=False, writable=False),
    Field('m_email', 'string', default=get_user_email,
          readable=False, writable=False),
    Field('shared', 'boolean', default=False),
    Field('image_url', 'string', default='https://bulma.io/images/placeholders/1280x960.png')
)

db.define_table(
    'saved_recipes',
    Field('recipe', 'reference recipes'),
    Field('m_email', default=get_user_email, readable=False, writable=False),
    Field('starred', 'boolean')
)
#list of all ingredients
db.define_table(
    'ingredients',
    Field('name', 'string', requires=IS_NOT_EMPTY()),
    Field('avg_price', 'integer'),
)
#list of ingredients that relate to a specifc recipe
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

db.define_table(    # ratings of recipes by user
    'rating',
    Field('recipe', 'reference recipes'),
    Field ('user', 'reference auth_user', defaul =  get_user),
    Field('rating', 'integer')
    
    )


db.commit()


# MySQL table definitions
'''
CREATE TABLE `recipes`(
    `id` INTEGER AUTO_INCREMENT,
    `name` VARCHAR(512),
    `steps` VARCHAR(512),
    `cook_time` INTEGER,
    `rating` DOUBLE,
    `num_ratings` INTEGER,
    `m_datetime` TIMESTAMP,
    `m_email` VARCHAR(512),
    `shared` VARCHAR(1),
    `image_url` VARCHAR(512),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `saved_recipes`(
    `id` INTEGER AUTO_INCREMENT,
    `recipe` INTEGER,
    `m_email` VARCHAR(512),
    `starred` VARCHAR(1),
    PRIMARY KEY (`id`),
    KEY `recipe_fk` (`recipe`),
    CONSTRAINT `recipe_fk` FOREIGN KEY (`recipe`) REFERENCES `recipes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `ingredients`(
    `id` INTEGER AUTO_INCREMENT,
    `name` VARCHAR(512),
    `avg_price` INTEGER,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `recipe_ingredients`(
    `id` INTEGER AUTO_INCREMENT,
    `recipe` INTEGER,
    `ingredient` INTEGER,
    `quantity` VARCHAR(512),
    PRIMARY KEY (`id`),
    KEY `ri_recipe_fk` (`recipe`),
    CONSTRAINT `ri_recipe_fk` FOREIGN KEY (`recipe`) REFERENCES `recipes` (`id`) ON DELETE CASCADE,
    KEY `ri_ingredient_fk` (`ingredient`),
    CONSTRAINT `ri_ingredient_fk` FOREIGN KEY (`ingredient`) REFERENCES `ingredients` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `allergies`(
    `id` INTEGER AUTO_INCREMENT,
    `m_email` VARCHAR(512),
    `allergen` INTEGER,
    PRIMARY KEY (`id`),
    KEY `allergen_fk` (`allergen`),
    CONSTRAINT `allergen_fk` FOREIGN KEY (`allergen`) REFERENCES `ingredients` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `tags`(
    `id` INTEGER AUTO_INCREMENT,
    `name` VARCHAR(512),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `recipe_tags`(
    `id` INTEGER AUTO_INCREMENT,
    `recipe` INTEGER,
    `tag` INTEGER,
    PRIMARY KEY (`id`),
    KEY `rt_recipe_fk` (`recipe`),
    CONSTRAINT `rt_recipe_fk` FOREIGN KEY (`recipe`) REFERENCES `recipes` (`id`) ON DELETE CASCADE,
    KEY `tag_fk` (`tag`),
    CONSTRAINT `tag_fk` FOREIGN KEY (`tag`) REFERENCES `tags` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `substitutions`(
    `id` INTEGER AUTO_INCREMENT,
    `original_ingredient` INTEGER,
    `sub_ingredient` INTEGER,
    `sub_rate` INTEGER,
    PRIMARY KEY (`id`),
    KEY `original_ingredient_fk` (`original_ingredient`),
    CONSTRAINT `original_ingredient_fk` FOREIGN KEY (`original_ingredient`) REFERENCES `ingredients` (`id`) ON DELETE CASCADE,
    KEY `sub_ingredient_fk` (`sub_ingredient`),
    CONSTRAINT `sub_ingredient_fk` FOREIGN KEY (`sub_ingredient`) REFERENCES `ingredients` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `rating`(
    `id` INTEGER AUTO_INCREMENT,
    `recipe` INTEGER,
    `user` INTEGER,
    `rating` INTEGER,
    PRIMARY KEY (`id`),
    KEY `r_recipe_fk` (`recipe`),
    CONSTRAINT `r_recipe_fk` FOREIGN KEY (`recipe`) REFERENCES `recipes` (`id`) ON DELETE CASCADE,
    KEY `r_user_fk` (`recipe`),
    CONSTRAINT `r_user_fk` FOREIGN KEY (`recipe`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
'''