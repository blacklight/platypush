$(document).ready(function() {
    var $imgContainer = $('.image-carousel').find('.carousel'),
        $imgBackground = $('.image-carousel').find('.carousel-background'),
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
        var nextImage = images[processedImages++];
        var $oldImg = $imgContainer.find('img');
        var $newImg = $('<img></img>')
            .attr('src', nextImage)
            .attr('alt', 'Could not load image')
            .appendTo('body').hide();

        $newImg.on('load', function() {
            $oldImg.remove();
            if ($newImg.width() > $newImg.height()) {
                $newImg.css('width', '100%');
                $imgBackground.css('background-image', '');
            } else {
                $imgBackground.css('background-image', 'url(' + nextImage + ')');
            }

            $newImg.css('max-height', '100%');
            $newImg.remove().appendTo($imgContainer).show();
        });

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

