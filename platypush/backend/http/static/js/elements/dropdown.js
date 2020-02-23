Vue.component('dropdown', {
    template: '#tmpl-dropdown',
    props: {
        id: {
            type: String,
        },

        visible: {
            type: Boolean,
            default: false,
        },

        items: {
            type: Array,
            default: [],
        },

        classes: {
            type: Array,
            default: () => [],
        },
    },

    methods: {
        clicked: function(item) {
            if (item.click && !item.disabled) {
                item.click();
            }

            if (!item.preventClose) {
                closeDropdown();
            }
        },
    },
});

let openedDropdown;

let clickHndl = function(event) {
    if (!openedDropdown) {
        return;
    }

    var element = event.target;
    while (element) {
        if (element === openedDropdown) {
            return;
        }

        element = element.parentElement;
    }

    // Click outside the dropdown, close it
    closeDropdown();
};

function closeDropdown() {
    if (!openedDropdown) {
        return;
    }

    document.removeEventListener('click', clickHndl);

    if (openedDropdown.className.indexOf('hidden') < 0) {
        openedDropdown.className = (openedDropdown.className + ' hidden').trim();
    }

    openedDropdown = undefined;
}

function openDropdown(element) {
    element = parseElement(element);
    if (!element) {
        console.error('Invalid dropdown element');
        return;
    }

    event.stopPropagation();
    closeDropdown();

    if (getComputedStyle(element.parentElement).position === 'relative') {
        // Position the dropdown relatively to the parent
        element.style.left = (window.event.clientX - element.parentElement.offsetLeft + element.parentElement.scrollLeft) + 'px';
        element.style.top = (window.event.clientY - element.parentElement.offsetTop + element.parentElement.scrollTop) + 'px';
    } else {
        // Position the dropdown absolutely on the window
        element.style.left = (window.event.clientX + window.scrollX) + 'px';
        element.style.top = (window.event.clientY + window.scrollY) + 'px';
    }

    document.addEventListener('click', clickHndl);
    element.className = element.className.split(' ').filter(c => c !== 'hidden').join(' ');
    openedDropdown = element;

    const maxLeft = Math.min(window.innerWidth, element.parentElement.clientWidth) + element.parentElement.scrollLeft;
    const maxTop = Math.min(window.innerHeight, element.parentElement.clientHeight) + element.parentElement.scrollTop;

    if (element.parentElement.offsetLeft + element.offsetLeft + parseFloat(getComputedStyle(element).width) >= maxLeft) {
        if (parseFloat(element.style.left) - parseFloat(getComputedStyle(element).width) >= 0) {
            element.style.left = (parseFloat(element.style.left) - parseFloat(getComputedStyle(element).width)) + 'px';
        }
    }

    if (element.parentElement.offsetTop + element.offsetTop + parseFloat(getComputedStyle(element).height) >= maxTop) {
        if (parseFloat(element.style.top) - parseFloat(getComputedStyle(element).height) >= 0) {
            element.style.top = (parseFloat(element.style.top) - parseFloat(getComputedStyle(element).height)) + 'px';
        }
    }

    if (parseFloat(element.style.left) < 0) {
        element.style.left = 0;
    }

    if (parseFloat(element.style.top) < 0) {
        element.style.top = 0;
    }
}

