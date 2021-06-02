// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        edit_mode : false,
        edit_id : 0,
        add_mode: false,
        add_name: "",
        add_steps: "",
        add_cook_time: 0,
        add_can_edit : false,
        add_shared: false,
        add_ingredient: "",
        add_amount: "",
        showinfotextbox: false,
        rows: [],
        temps: [],
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
        a.map((e) => {e._state = {name: "clean", steps: "clean", cook_time:"clean", shared: "clean"} ;});
        return a;
    }
    app.add_temp_ingredient = function () {
        
            app.vue.temps.push({
                amount: app.vue.add_amount,
                ingredient: app.vue.add_ingredient,
                
                _state: {amount: "clean", ingredient: "clean"},
            });
            app.enumerate(app.vue.temps);
            app.reset_ingredient_form();
            

    };
    app.delete_temp_ingredient = function(ingredient,amount) {
        
        for (let i = 0; i < app.vue.temps.length; i++) {
            if (app.vue.temps[i].ingredient === ingredient && app.vue.temps[i].amount === amount) {
                app.vue.temps.splice(i, 1);
                app.enumerate(app.vue.temps);
                break;
            }
        }
    };
    app.edit_temp_ingredient = function() {
        
    };

    app.delete_ingredient = function(row_idx,ing,amount) {
        let id = app.vue.rows[row_idx].id;
        axios.get(delete_ingredient_url, {params: {id: id,ingredient:ing,amount:amount}}).then(function (response) {
            for (let i = 0; i < app.vue.rows.length; i++) {
                if (app.vue.rows[i].id === id) {
                    for(let r= 0; r< app.vue.rows[i].myingredients.length;r++)
                    {   if(app.vue.rows[i].myingredients[r].ingredient==ing && app.vue.rows[i].myingredients[r].amount == amount)
                        {
                            console.log("testtest");
                            app.vue.rows[i].myingredients.splice(r, 1);
                            app.enumerate(app.vue.rows[i].myingredients);
                            break;
                        }

                    }
                    
                }
            }
            });
        
    };
    app.edit_ingredient = function() {
        
    };
    app.add_recipe = function () {
        axios.post(add_recipe_url,
            {
                name: app.vue.add_name,
                steps: app.vue.add_steps,
                cook_time: app.vue.add_cook_time,
                shared: app.vue.add_shared,
                ingredients : app.vue.temps,
            }).then(function (response) {
            app.vue.rows.push({
                id: response.data.id,
                name: app.vue.add_name,
                steps: app.vue.add_steps,
                cook_time: app.vue.add_cook_time,
                shared: app.vue.add_shared,
                myingredients: JSON.parse(JSON.stringify(app.vue.temps)),
                _state: {name: "clean", steps: "clean", cook_time:"clean", shared: "clean",myingredients: "clean",},
            });
            app.enumerate(app.vue.rows);
            app.reset_form();
            app.set_add_status(false);
            app.vue.temps =[];
        });
    };
    
    app.reset_ingredient_form = function () {

        app.vue.add_ingredient= "";
        app.vue.add_amount= "";
    };
    app.reset_form = function () {

        app.vue.add_name= "";
        app.vue.add_steps= "";
        app.vue.add_cook_time= 0;
        app.vue.add_shared= false;
    };

    app.delete_recipe = function(row_idx) {
        
        let id = app.vue.rows[row_idx].id;
        axios.get(delete_recipe_url, {params: {id: id}}).then(function (response) {
            for (let i = 0; i < app.vue.rows.length; i++) {
                if (app.vue.rows[i].id === id) {
                    app.vue.rows.splice(i, 1);
                    app.enumerate(app.vue.rows);
                    break;
                }
            }
            });
    };

    app.set_add_status = function (new_status) {
        app.vue.add_mode = new_status;
    };

    app.start_edit = function (row_idx, fn) {
        app.vue.rows[row_idx]._state[fn] = "edit";
    };

    app.stop_edit = function (row_idx, fn) {
        let row = app.vue.rows[row_idx];
        if (row._state[fn] === "edit") {
            row._state[fn] = "pending";
            axios.post(edit_recipe_url,
                {
                    id: row.id,
                    field: fn,
                    value: row[fn], // row.first_name
                }).then(function (result) {
                row._state[fn] = "clean";
            });
        }
        // If I was not editing, there is nothing that needs saving.
    };
    app.start_edit_ingredient = function (row_idx,row_idx2, fn) {
        app.vue.rows[row_idx].myingredients[row_idx2]._state[fn] = "edit";
    };

    app.stop_edit_ingredient = function (row_idx,row_idx2, fn) {
        let row = app.vue.rows[row_idx].myingredients[row_idx2];
        if (row._state[fn] === "edit") {
            row._state[fn] = "pending";
            // axios.post(edit_ingredient_url,
            //     {
            //         id: row.id,
            //         field: fn,
            //         value: row[fn], // row.first_name
            //     }).then(function (result) {
            //     row._state[fn] = "clean";
            // });
            row._state[fn] = "clean";
        }
        // If I was not editing, there is nothing that needs saving.
    };
    app.start_edit_temp = function (row_idx, fn) {
        app.vue.temps[row_idx]._state[fn] = "edit";
    };

    app.stop_edit_temp = function (row_idx, fn) {
        let row = app.vue.temps[row_idx];
        if (row._state[fn] === "edit") {
            row._state[fn] = "pending";
            row._state[fn] = "clean";

        }
        // If I was not editing, there is nothing that needs saving.
    };
    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        add_temp_ingredient: app.add_temp_ingredient,
        add_recipe: app.add_recipe,
        set_add_status: app.set_add_status,
        delete_recipe: app.delete_recipe,
        start_edit_ingredient: app.start_edit_ingredient,
        stop_edit_ingredient: app.stop_edit_ingredient,
        start_edit: app.start_edit,
        stop_edit: app.stop_edit,
        start_edit_temp: app.start_edit_temp,
        stop_edit_temp: app.stop_edit_temp,
        delete_temp_ingredient: app.delete_temp_ingredient,
        edit_temp_ingredient: app.edit_temp_ingredient,
        delete_ingredient: app.delete_ingredient,
        edit_ingredient: app.edit_ingredient,
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
    // For the moment, we 'load' the data from a string.
    app.init = () => {
        axios.get(load_recipes_url).then(function (response) {
           app.vue.rows = app.decorate(app.enumerate(response.data.rows));
            //app.vue.temps = app.decorate(app.enumerate(response.data.temps));
       });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);