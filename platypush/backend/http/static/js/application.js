// Declaration of the main vue app
var app;

function ready(callback){
    if (document.readyState!='loading') callback();
    else if (document.addEventListener) document.addEventListener('DOMContentLoaded', callback);
    else document.attachEvent('onreadystatechange', function(){
        if (document.readyState=='complete') callback();
    });
}

ready(function() {
    app = new Vue({
        el: '#app',
        delimiters: ['[[',']]'],
        data: {
            config: {foo:"bar"}
        },

        created: function() {
        },

        mounted: function() {
        },

        updated: function() {
        },

        destroyed: function() {
        },
    });
});
