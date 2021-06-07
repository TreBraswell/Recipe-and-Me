# Recipe & Me

> Recipes at your fingertip

Social Media platform for browsing, matching, and rating recipes.

## Model: MySQL database and PyDAL

The following are the primary database tables in Recipe & Me.

### Recipes

The main set of attributes about each recipe.

### Ingredients

The name of each ingredient is a row in this table so it can be re-used. Also if
an ingredient is renamed (which users cannot accomplish, but administrators
can), all occurrences of that ingredient will be changed at once without needing
to touch the recipes table.

### Recipe-ingredients

Has foreign key references to both recipes and ingredients to facilitate the
many-to-many relationship between the two. Also stores the quantity of a
particular ingredient in a particular recipe as a string to allow users
flexibility, e.g. "1 cup" of milk, or "2, diced" of carrots.

### Tags

The name of each tag. This table has similar reasons to exist as the ingredients
table does.

### Recipe-tags

Once again, similar to recipe-ingredients, but without the quantity attribute.

### Ratings

Relates a user, recipe and star rating (in the range 1 to 5), by keeping a
reference to a user (provided by Py4Web's auth.user) and a recipe and tying the
two to a rating attribute.

### Users

Provided by Py4Web, and stores users' names, emails, and Google OAuth tokens.


## Controller: Py4Web

There are two primary pages on Recipe & Me

### Index (Discover) Controller

The discover page needs to show all the recipes which have been publicly shared
by any user, so the controller queries the database for the matching recipes
and puts the results in a de-normalized form that is simpler to display on the
page. The tags list for the filtering drop-down is also retrieved from the
database.

### Profile Controller

The profile information for the user is queried from the database, and a form is
generated for editing this information, which includes items such as first
and last name. Similarly to the discover page, a recipe list list is retrieved,
but this time for just one user and including non-public recipes. Users can use
the non-public recipes as drafts, or just if they don't want to share.


## View: HTML Templates, augmented with Vue.js

### Index (Discover) View

At the top of the page is the heading area with a search bar and a dropdown for
filtering the search by tags.

Below that is an area where tags which are currently being used as a filter can
be viewed and cleared one-by-one.

The main body of the page is the list of recipes. These are cards using the tile
layout in Bulma, and can be clicked on to bring up more details for each recipe
in a modal.

The recipe detail view shows the ingredients and quantity of each ingredient, as
well as other details that do not fit on the smaller cards, like steps for
preparing the recipe.

For logged-in users, the detail view has two input areas: star ratings and tags.
Any user can choose a star rating for a recipe and can see the average rating
for that recipe update immediately. Any user can also delete or add tags for all
recipes on the discover page, not just the recipes they posted. Adding a new tag
allows selecting from existing tags or typing in a new one, which will from then
on be available for reuse by any user.

### Profile View

The left column holds information about the user, like their name, and allows
this information to be edited at will.

The right column holds an area to create a new recipe at the top, followed by
a list of the user's recipes. Each of the user's recipes has edit-in-place
forms which are hidden as read-only until they are clicked on. Editing one of
the ingredients for a recipe brings up auto-completion for ingredients which
have been used by any user on any previous recipes.