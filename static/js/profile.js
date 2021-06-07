// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        add_mode: false,
        add_can_edit : false,

        add_name: "",
        add_steps: "",
        add_cook_time: 0,
        add_shared: false,
        add_image_url: "",

        add_ingredient: "",
        add_amount: "",

        showinfotextbox: false,
        recipes: [],
        temp_ingredients: [],

        all_ingredients: [],
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    // This decorates the recipe rows (e.g. that come from the server)
    // adding information on their state:
    // - clean: read-only, the value is saved on the server
    // - edit : the value is being edited
    // - pending : a save is pending.
    app.decorate = (a) => {
        a.map((e) => {
            e._state = {
                name: "clean", 
                steps: "clean", 
                cook_time:"clean", 
                shared: "clean", 
                image_url: "clean"
            };
            e.add_ingredient_edit = "";
            e.add_amount_edit = "";
            e.add_mode = false;
            e.image_url = 
                    (e.image_url != null)
                    ? e.image_url 
                    : "";
        });

        return a;
    };

    // Decorates the ingredient rows by adding clean state to them to start off
    app.decorate_ingredients = (a) => {
        a.map((e) => {
            e._state = {
                "amount": "clean", 
                "ingredient": "clean"
            };
        });

        return a;
    };

    // Adds a temporary ingredient to the new recipe being created, ...
    // local-only because the recipe is not on the server yet
    app.add_temp_ingredient = function () {
        let temp_ingredient = {
            amount: app.vue.add_amount,
            ingredient: app.vue.add_ingredient,
        }
        temp_ingredient = app.decorate_ingredients(temp_ingredient);

        app.vue.temp_ingredients.push(temp_ingredient);
        app.enumerate(app.vue.temp_ingredients);
        app.reset_temp_ingredient_form();
    };

    // Deletes a temporary ingredient to the new recipe being created
    app.delete_temp_ingredient = function(ingredient,amount) {
        for (let i = 0; i < app.vue.temp_ingredients.length; i++) {
            if (app.vue.temp_ingredients[i].ingredient === ingredient 
                    && app.vue.temp_ingredients[i].amount === amount) {
                app.vue.temp_ingredients.splice(i, 1);
                app.enumerate(app.vue.temp_ingredients);

                break;
            }
        }
    };

    // Adds an ingredient to a recipe that already exists on the server.
    // Both updates local view and posts the new ingredient to the server.
    app.add_ingredient_func = function (recipe_idx) {
        let recipe = app.vue.recipes[recipe_idx];
        let ingredient = {
            "ingredient": recipe.add_ingredient_edit, 
            "amount": recipe.add_amount_edit
        };
        
        axios.post(set_recipe_ingredient_url,
            {
                recipe_id: recipe.id,
                recipe_ingredient_id: ingredient.id,
                ingredient_name: ingredient.ingredient,
                quantity: ingredient.amount,
            }).then(function (response) {
                ingredient.id = response.data.recipe_ingredient_id,
                ingredient._state = {amount: "clean", ingredient: "clean"},

                rcp_ingr_idx = recipe.myingredients.findIndex(
                        x => x.ingredient == ingredient.ingredient);

                if (rcp_ingr_idx == -1) {
                    // append new ingredient entry to our local list
                    recipe.myingredients.push(ingredient);
                }
                else {
                    // replace existing ingredient entry if user is trying ...
                    // to add the same ingredient again
                    Vue.set(
                        app.vue.recipes[recipe_idx].myingredients[rcp_ingr_idx], 
                        "amount", 
                        ingredient.amount
                    );
                }

                app.enumerate(app.vue.recipes[recipe_idx].myingredients);

                // reset add ingredients form for the recipe
                app.reset_ingredient_form(recipe_idx)
        });
    };

    // Deletes an ingredient to a recipe that already exists on the server.
    // Both updates local view and posts the ingredient deletion to the server.
    app.delete_ingredient = function (row_idx, ing, amount, rcp_ingr_id) {
        let id = app.vue.recipes[row_idx].id;
        let recipes = app.vue.recipes;

        axios.post(
            delete_recipe_ingredient_url, 
            {
                recipe_id: id, 
                recipe_ingredient_id: rcp_ingr_id,
        }).then(function () {
            for (let i = 0; i < recipes.length; i++) {
                if (recipes[i].id !== id) continue;
                
                for (let r= 0; r < recipes[i].myingredients.length; r++) {   
                    if (recipes[i].myingredients[r].ingredient == ing 
                            && recipes[i].myingredients[r].amount == amount) {
                        recipes[i].myingredients.splice(r, 1);
                        app.enumerate(recipes[i].myingredients);
                        break;
                    }
                }
            }
            });
    };

    // Moves a newly created recipe from the temporary creation area to the ...
    // main recipe list, and posts the new recipe to the server.
    app.add_recipe = function () {
        axios.post(add_recipe_url, {
                name: app.vue.add_name,
                steps: app.vue.add_steps,
                cook_time: app.vue.add_cook_time,
                shared: app.vue.add_shared,
                image_url: app.vue.add_image_url,
                ingredients : app.vue.temp_ingredients,
            }).then(function (response) {
            app.vue.recipes.unshift({
                id: response.data.id,
                name: app.vue.add_name,
                steps: app.vue.add_steps,
                cook_time: app.vue.add_cook_time,
                shared: app.vue.add_shared,
                image_url: app.vue.add_image_url,
                myingredients: 
                        JSON.parse(JSON.stringify(app.vue.temp_ingredients)),
                _state: {
                    name: "clean", 
                    steps: "clean", 
                    cook_time:"clean", 
                    shared: "clean", 
                    image_url: "clean", 
                    myingredients: "clean",
                },
                add_ingredient_edit: "",
                add_amount_edit: "",
                add_mode: false,
            });
            
            app.vue.recipes[0].myingredients = app.decorate_ingredients(
                    app.enumerate(app.vue.recipes[0].myingredients));

            app.vue.recipes = app.decorate(app.enumerate(app.vue.recipes));

            app.reset_form();
            app.set_add_status(false);
            app.vue.temp_ingredients = [];
        });
    };
    
    // Resets the temporary recipe creation area's add-ingredient form
    app.reset_temp_ingredient_form = function () {
        app.vue.add_ingredient= "";
        app.vue.add_amount= "";
    };

    // Resets an existing recipe's add-ingredient form
    app.reset_ingredient_form = function (recipe_idx) {
        let recipe = app.vue.recipes[recipe_idx];
        recipe.add_ingredient_edit = "";
        recipe.add_amount_edit = "";
        recipe.add_mode = false;
        recipe.image_url = 
                (recipe.image_url != "") 
                ? recipe.image_url 
                : "https://bulma.io/images/placeholders/1280x960.png"
    };

    // Resets the temporary recipe creation area's entire form
    app.reset_form = function () {
        app.vue.add_name = "";
        app.vue.add_steps = "";
        app.vue.add_cook_time = 0;
        app.vue.add_shared = false;
        app.vue.add_image_url = "";

        app.reset_temp_ingredient_form();
    };

    app.delete_recipe = function(row_idx) {
        let id = app.vue.recipes[row_idx].id;
        axios.post(delete_recipe_url, {id: id}).then(function () {
            for (let i = 0; i < app.vue.recipes.length; i++) {
                if (app.vue.recipes[i].id === id) {
                    app.vue.recipes.splice(i, 1);
                    app.enumerate(app.vue.recipes);
                    break;
                }
            }
            });
    };

    app.set_add_status = function (new_status) {
        app.vue.add_mode = new_status;
    };

    app.start_edit = function (row_idx, fn) {
        app.vue.recipes[row_idx]._state[fn] = "edit";
    };

    app.stop_edit = function (row_idx, fn) {
        let row = app.vue.recipes[row_idx];
        if (row._state[fn] === "edit" || fn == "shared") {
            row._state[fn] = "pending";
            axios.post(edit_recipe_url,
                {
                    id: row.id,
                    field: fn,
                    value: row[fn],
                }).then(function () {
                row._state[fn] = "clean";
            });
        }
        // If I was not editing, there is nothing that needs saving.
    };
    app.start_edit_ingredient = function (recipe_idx, ingr_idx, fn) {
        app.vue.recipes[recipe_idx].myingredients[ingr_idx]._state[fn] = "edit";
    };

    app.stop_edit_ingredient = function (recipe_idx, ingr_idx, fn) {
        let recipe = app.vue.recipes[recipe_idx];
        let ingredient = app.vue.recipes[recipe_idx].myingredients[ingr_idx];
        if (ingredient._state[fn] === "edit") {
            ingredient._state[fn] = "pending";
            axios.post(set_recipe_ingredient_url, {
                    recipe_id: recipe.id,
                    recipe_ingredient_id: ingredient.id,
                    ingredient_name: ingredient.ingredient,
                    quantity: ingredient.amount,
                }).then(function (response) {
                    ingredient._state[fn] = "clean";
                    Vue.set(
                        app.vue.recipes[recipe_idx].myingredients[ingr_idx],
                        "id",
                        response.data.recipe_ingredient_id
                    );
            });
            ingredient._state[fn] = "clean";
        }
        // If I was not editing, there is nothing that needs saving.
    };
    app.start_edit_temp = function (ingredient_idx, fn) {
        app.vue.temp_ingredients[ingredient_idx]._state[fn] = "edit";
    };

    app.stop_edit_temp = function (ingredient_idx, fn) {
        let row = app.vue.temp_ingredients[ingredient_idx];
        if (row._state[fn] === "edit") {
            row._state[fn] = "pending";
            row._state[fn] = "clean";
        }
        // If I was not editing, there is nothing that needs saving.
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        set_add_status: app.set_add_status,
        add_recipe: app.add_recipe,
        delete_recipe: app.delete_recipe,

        start_edit_ingredient: app.start_edit_ingredient,
        stop_edit_ingredient: app.stop_edit_ingredient,
        start_edit: app.start_edit,
        stop_edit: app.stop_edit,
        add_ingredient_func: app.add_ingredient_func,
        delete_ingredient: app.delete_ingredient,

        add_temp_ingredient: app.add_temp_ingredient,
        start_edit_temp: app.start_edit_temp,
        stop_edit_temp: app.stop_edit_temp,
        delete_temp_ingredient: app.delete_temp_ingredient,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    // Generally, this will be a network call to the server to
    // load the data.
    app.init = () => {
        axios.get(load_recipes_url).then(function (response) {
          for (recipe of response.data.rows) {
            recipe.myingredients = app.decorate_ingredients(
                    app.enumerate(recipe.myingredients));
          }

          app.vue.recipes = app.decorate(app.enumerate(response.data.rows));
       });

       axios.get(search_ingredients_url, {params:{q: ""}})
            .then(function (response) {
                let search_results = response.data.ingredients;
                app.vue.all_ingredients = search_results;
            });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it
init(app);