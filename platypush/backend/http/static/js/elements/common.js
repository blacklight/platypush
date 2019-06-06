var parseElement = function(element) {
    if (element instanceof Object) {
        if (element.$el) {
            element = element.$el;
        }
    } else if (element instanceof String || typeof(element) === 'string') {
        element = document.getElementById(element);
    } else {
        console.error('Got unexpected type ' + typeof(element) + ' for DOM element');
        return;
    }

    return element;
};

