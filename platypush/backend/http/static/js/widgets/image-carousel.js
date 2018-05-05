$(document).ready(function() {
    var $imgElement = $('.image-carousel').find('.carousel'),
        config = window.widgets['image-carousel'],
        images = config.imageUrls,
        processedImages = 0;

    var shuffleImages = function() {
		for (var i=images.length-1; i > 0; i--) {
			var j = Math.floor(Math.random() * (i + 1));
			var x = images[i];
			images[i] = images[j];
			images[j] = x;
        }
    };

    var refreshImage = function() {
        $imgElement.css('background-image', "url('" + images[processedImages++] + "')");
        if (processedImages == images.length-1) {
            shuffleImages();
            processedImages = 0;
        }
    };

    var initWidget = function() {
        shuffleImages();
        refreshImage();
        setInterval(refreshImage,
            'refresh_seconds' in config ? config.refresh_seconds * 1000 : 15000);
    };

    var init = function() {
        initWidget();
    };

    init();
});

