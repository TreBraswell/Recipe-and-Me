// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        query: "",
        results: [],
        rows: [],
        rows_data: [],
        modals:[]
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.search = function () {
        if (app.vue.query.length > 1) {
            axios.get(search_url, {params: {q: app.vue.query}})
                .then(function (result) {
                    app.vue.results = result.data.results;
                    app.vue.rows = result.data.rows;
                });
        } else {
            app.vue.results = [];

            // reset the rows displayed to be everything after we clear out the search bar
            app.vue.rows = app.vue.rows_data;
        }
    }
    
    app.set_modal = function ( is_displayed, index){
        app.vue.modals[index] = is_displayed;
        console.log( is_displayed, typeof(is_displayed));
        console.log(app.vue.modals);
        this.$forceUpdate()
    }

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        search: app.search,
        set_modal: app.set_modal,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        axios.get(load_shared_recipes_url).then(function (response) {
            app.vue.rows = app.enumerate(response.data.rows);
            app.vue.rows_data = app.vue.rows;
            for (var i = 0; i < app.vue.rows.length; i++){
                app.vue.modals.push(false);
                console.log(typeof(app.vue.modals[i]));
            }
        });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
