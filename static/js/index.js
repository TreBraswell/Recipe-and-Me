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
        query_tags: [],
        tags: [],
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
        if (app.vue.query.length > 1 || app.vue.query_tags.length > 0) {
            axios.get(search_url, {params: {q: app.vue.query, t: app.vue.query_tags.map(e => e.name).join(',')}})
                .then(function (result) {
                    app.vue.rows = app.enumerate(result.data.rows);
                });
        } else {
            // reset the rows displayed to be everything after we clear out the search bar
            app.vue.rows = app.vue.rows_data;
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
        toggle_search_tag: app.toggle_search_tag,
        remove_search_tag: app.remove_search_tag,
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
            app.vue.tags = response.data.tags ? app.enumerate(response.data.tags) : []
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
