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

    // This decorates the rows (e.g. that come from the server)
    // adding information on their state:
    // - clean: read-only, the value is saved on the server
    // - edit : the value is being edited
    // - pending : a save is pending.
    app.decorate = (a) => {
        a.map((e) => {
            e._state = {name: "clean", steps: "clean", cook_time:"clean", shared: "clean", image_url: "clean"};
            e.add_ingredient_edit = "";
            e.add_amount_edit = "";
            e.add_mode = false;
            e.image_url = e.image_url
        });

        return a;
    };

    app.decorate_ingredients = (a) => {
        a.map((e) => {
            e._state = {"amount": "clean", "ingredient": "clean"};
        });

        return a;
    };

    app.add_temp_ingredient = function () {
        app.vue.temp_ingredients.push({
            amount: app.vue.add_amount,
            ingredient: app.vue.add_ingredient,
            
            _state: {amount: "clean", ingredient: "clean"},
        });
        app.enumerate(app.vue.temp_ingredients);
        app.reset_ingredient_form();
    };

    app.delete_temp_ingredient = function(ingredient,amount) {
        for (let i = 0; i < app.vue.temp_ingredients.length; i++) {
            if (app.vue.temp_ingredients[i].ingredient === ingredient && app.vue.temp_ingredients[i].amount === amount) {
                app.vue.temp_ingredients.splice(i, 1);
                app.enumerate(app.vue.temp_ingredients);
                break;
            }
        }
    };

    app.add_ingredient_func = function (recipe_idx) {
        let recipe = app.vue.recipes[recipe_idx];
        console.log(recipe_idx)
        console.log(recipe)
        let ingredient = {"ingredient": recipe.add_ingredient_edit, "amount": recipe.add_amount_edit};
        
        axios.post(set_recipe_ingredient_url,
            {
                recipe_id: recipe.id,
                recipe_ingredient_id: ingredient.id,
                ingredient_name: ingredient.ingredient,
                quantity: ingredient.amount,
            }).then(function (response) {
                ingredient.id = response,
                ingredient._state = {amount: "clean", ingredient: "clean"},
                recipe.myingredients.push(ingredient);
                app.enumerate(recipe.myingredients);

                // reset add ingredients form for the recipe
                recipe.add_ingredient_edit = "";
                recipe.add_amount_edit = "";
                recipe.add_mode = false;
                recipe.image_url = recipe.image_url != "" ? recipe.image_url : "https://bulma.io/images/placeholders/1280x960.png"
        });
    };

    app.delete_ingredient = function(row_idx, ing, amount, recipe_ingredient_id) {
        let id = app.vue.recipes[row_idx].id;

        axios.post(delete_recipe_ingredient_url, {recipe_id: id, recipe_ingredient_id: recipe_ingredient_id})
        .then(function () {
            for (let i = 0; i < app.vue.recipes.length; i++) {
                if (app.vue.recipes[i].id === id) {
                    for(let r= 0; r< app.vue.recipes[i].myingredients.length;r++)
                    {   if(app.vue.recipes[i].myingredients[r].ingredient==ing && app.vue.recipes[i].myingredients[r].amount == amount)
                        {
                            app.vue.recipes[i].myingredients.splice(r, 1);
                            app.enumerate(app.vue.recipes[i].myingredients);
                            break;
                        }
                    }
                }
            }
            });
    };

    app.add_recipe = function () {
        axios.post(add_recipe_url,
            {
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
                myingredients: JSON.parse(JSON.stringify(app.vue.temp_ingredients)),
                _state: {name: "clean", steps: "clean", cook_time:"clean", shared: "clean", image_url: "clean", myingredients: "clean",},
                add_ingredient_edit: "",
                add_amount_edit: "",
                add_mode: false,
            });
            
            app.vue.recipes[0].myingredients = app.decorate_ingredients(app.enumerate(app.vue.recipes[0].myingredients));

            app.vue.recipes = app.decorate(app.enumerate(app.vue.recipes));

            app.reset_form();
            app.set_add_status(false);
            app.vue.temp_ingredients =[];
        });
    };
    
    app.reset_ingredient_form = function () {
        app.vue.add_ingredient= "";
        app.vue.add_amount= "";
    };

    app.reset_ingredient_form = function (row_idx) {
        app.vue.add_ingredient= "";
        app.vue.add_amount= "";
    };

    app.reset_form = function () {
        app.vue.add_name = "";
        app.vue.add_steps = "";
        app.vue.add_cook_time = 0;
        app.vue.add_shared = false;
        app.vue.add_image_url = "";
    };

    app.delete_recipe = function(row_idx) {
        let id = app.vue.recipes[row_idx].id;
        axios.post(delete_recipe_url, {id: id}).then(function (response) {
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
                }).then(function (result) {
                row._state[fn] = "clean";
            });
        }
        // If I was not editing, there is nothing that needs saving.
    };
    app.start_edit_ingredient = function (recipe_idx, ingredient_idx, fn) {
        app.vue.recipes[recipe_idx].myingredients[ingredient_idx]._state[fn] = "edit";
    };

    app.stop_edit_ingredient = function (recipe_idx, ingredient_idx, fn) {
        let recipe = app.vue.recipes[recipe_idx];
        let ingredient = app.vue.recipes[recipe_idx].myingredients[ingredient_idx];
        if (ingredient._state[fn] === "edit") {
            ingredient._state[fn] = "pending";
            axios.post(set_recipe_ingredient_url,
                {
                    recipe_id: recipe.id,
                    recipe_ingredient_id: null,
                    ingredient_name: ingredient.ingredient,
                    quantity: ingredient.amount,
                }).then(function () {
                    ingredient._state[fn] = "clean";
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
            recipe.myingredients = app.decorate_ingredients(app.enumerate(recipe.myingredients));
          }

          app.vue.recipes = app.decorate(app.enumerate(response.data.rows));
       });

       axios.get(search_ingredients_url, {params: {q: ""}})
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