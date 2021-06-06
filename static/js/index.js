// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        query: "",
        query_tags: [],
        tags: [],

        recipes: [],
        recipes_data: [],
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});

        return a;
    };
    
    app.complete = (recipes) => {
        // Initializes useful fields of recipe rows.
        recipes.map((recipe) => {
            recipe.rating = 0;
            recipe.num_stars_display = 0;
            recipe.image_url = recipe.image_url != "" ? recipe.image_url : "https://bulma.io/images/placeholders/1280x960.png";
            recipe.modal = false;
            recipe.temp_tag = "";
        });

        for ( i = 0; i < recipes.length; i++){
            if (recipes[i].total_rating === 0){
                recipes[i].rating = 0;
            }
            else{
                recipes[i].rating = recipes[i].total_rating/(recipes[i].raters.length);
                recipes[i].num_stars_display = recipes[i].rating;
            }
        }
    };
    
    app.set_stars = (recipe_idx, num_stars) => {
        if (!app.vue.recipes[recipe_idx].raters.includes(app.vue.user) && (current_user != null)){
            let recipe = app.vue.recipes[recipe_idx];
            recipe.total_rating = recipe.total_rating + num_stars;
            recipe.raters.push(app.vue.user);
            recipe.rating = (recipe.total_rating)/(recipe.raters.length);

            // Sets the stars on the server.
            axios.post(update_rating_url, {row_id: recipe.id, rating: num_stars});
        }
    };
    
    app.stars_out = (recipe_idx) => {
        let recipe = app.vue.recipes[recipe_idx];
        recipe.num_stars_display = recipe.rating;
    };

    app.stars_over = (recipe_idx, num_stars) => {
        if (!app.vue.recipes[recipe_idx].raters.includes(app.vue.user) && (app.vue.user!= -1)){
            let recipe = app.vue.recipes[recipe_idx];
            recipe.num_stars_display = num_stars;
        }
    };
    
    app.search = function () {
        if (app.vue.query.length > 0 || app.vue.query_tags.length > 0) {
            axios.get(search_url, {params: {q: app.vue.query, t: app.vue.query_tags.map(e => e.name).join(',')}})
                .then(function (result) {
                    let recipes = result.data.rows;
                    app.enumerate(recipes);
                    app.complete(recipes);
                    app.vue.recipes = recipes;
                });
        }
        else {
            // reset the recipe rows displayed to be everything after we clear out the search bar
            app.vue.recipes = app.vue.recipes_data;
        }
    }

    // add a new tag to query_tags
    app.toggle_search_tag = function (index) {
        if (!app.vue.tags[index].is_active) {
            app.vue.query_tags.push(app.vue.tags[index]);

            app.vue.tags[index].is_active = true;
            app.vue.tags = app.enumerate(app.vue.tags);

            app.search();
        }
        else {
            app.remove_search_tag(index)
        }
    }

    app.remove_search_tag = function (index) {
        app.vue.tags[index].is_active = false;
        app.vue.tags = app.enumerate(app.vue.tags);
        result = app.remove_from_array(app.vue.query_tags, app.vue.tags[index].name);

        app.search();
        
        return result;
    }

    app.remove_from_array = (arr, val) => {
        let i = arr.findIndex(x => x.name === val);

        if (i !== -1) {
            arr.splice(i, 1);
            return true;
        }

        return false;
    }
    
    app.set_modal = function (is_displayed, index) {
        app.vue.recipes[index].modal = is_displayed;
    }

    app.add_tag = function (recipe_idx) {
        let recipe = app.vue.recipes[recipe_idx];
        tag_name = recipe.temp_tag.toLowerCase();
        axios.post(set_recipe_tag_url,
            {
                recipe_id: recipe.id,
                tag_name: tag_name,
            }).then(function (result) {
                if (result.data.ok != null) {
                    app.vue.recipes[recipe_idx].tag_rows.push(tag_name);
                    recipe.temp_tag = "";
                }
        });
    }

    app.delete_tag = function (recipe_idx, tag_name) {
        let recipe = app.vue.recipes[recipe_idx];
        axios.post(delete_recipe_tag_url,
            {
                recipe_id: recipe.id,
                tag_name: tag_name,
            }).then(function () {
                let tag_idx = app.vue.recipes[recipe_idx].tag_rows.indexOf(tag_name);
                Vue.delete(app.vue.recipes[recipe_idx].tag_rows, tag_idx);
        });
    }

    // This contains all the methods.
    app.methods = {
        search: app.search,
        toggle_search_tag: app.toggle_search_tag,
        remove_search_tag: app.remove_search_tag,

        set_modal: app.set_modal,

        set_stars: app.set_stars,
        stars_out: app.stars_out,
        stars_over: app.stars_over,
        
        add_tag: app.add_tag,
        delete_tag: app.delete_tag,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Initialization code to load the recipe data
        axios.get(load_shared_recipes_url).then(function (response) {
            let recipes = response.data.rows;
            app.enumerate(recipes);
            app.complete(recipes);
            app.vue.recipes = recipes;
            
            app.vue.recipes_data = app.vue.recipes;
            app.vue.tags = response.data.tags ? app.enumerate(response.data.tags) : []
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it
init(app);
