function initMapFromGeopoints(points) {
    var $mapContainer = $('#map-container'),
        $map = $('#map');

    var markerArray = [];
    var directionsService = new google.maps.DirectionsService;

    var map = new google.maps.Map($map.get(0), {
        mapTypeId: google.maps.MapTypeId.ROADMAP,
    });

    var bounds = new google.maps.LatLngBounds();
    var infowindow = new google.maps.InfoWindow();
    var maxPoints = 22;

    var minDist = 100;
    var start = points.length > maxPoints ? points.length-maxPoints-1 : 0;
    var lastPoint;

    for (i = points.length-1; i >= 0 && markerArray.length <= maxPoints; i--) {
        if (lastPoint && latLngDistance(
                [points[i]['latitude'], points[i]['longitude']],
                [lastPoint['latitude'], lastPoint['longitude']]) < minDist) {
            continue;
        }

        lastPoint = points[i];
        var marker = new google.maps.Marker({
            position: new google.maps.LatLng(points[i]['latitude'], points[i]['longitude']),
            map: map
        });

        google.maps.event.addListener(marker, 'click', (function(marker, i) {
            return function() {
                infowindow.setContent(
                    (points[i]['address'] || '[No address]') + ' @ ' +
                    Date.parse(points[i]['created_at']).toLocaleString());
                infowindow.open(map, marker);
            }
        })(marker, i));

        // Extend the bounds to include each marker's position
        bounds.extend(marker.position);
        markerArray.push(marker);
    }

    var listener = google.maps.event.addListener(map, 'idle', function () {
        // Now fit the map to the newly inclusive bounds
        map.fitBounds(bounds);
        setTimeout(function() {
            if (window.zoom) {
                map.setZoom(window.zoom);
            } else {
                map.setZoom(getBoundsZoomLevel(bounds, $map.children().width(), $map.children().height()));
            }
        }, 1000);

        google.maps.event.removeListener(listener);
    });

    // Create a renderer for directions and bind it to the map.
    var directionsDisplay = new google.maps.DirectionsRenderer({map: map});

    // Instantiate an info window to hold step text.
    var stepDisplay = new google.maps.InfoWindow;

    // Display the route between the initial start and end selections.
    calculateAndDisplayRoute(
        directionsDisplay, directionsService, markerArray, stepDisplay, map);
}

function calculateAndDisplayRoute(directionsDisplay, directionsService,
    markerArray, stepDisplay, map) {
    // First, remove any existing markers from the map.
    for (var i = 0; i < markerArray.length; i++) {
        markerArray[i].setMap(null);
    }

    var waypoints = [];
    for (i=1; i < markerArray.length-1; i++) {
        if (!waypoints) waypoints = [];
        waypoints.push({
            location: markerArray[i].getPosition(),
            stopover: true,
        });
    }

    // Retrieve the start and end locations and create a DirectionsRequest using
    // WALKING directions.
    directionsService.route({
        origin: markerArray[0].getPosition(),
        destination: markerArray[markerArray.length-1].getPosition(),
        waypoints: waypoints,
        travelMode: 'WALKING'
    }, function(response, status) {
        // Route the directions and pass the response to a function to create
        // markers for each step.
        if (status === 'OK') {
            directionsDisplay.setDirections(response);
            showSteps(response, markerArray, stepDisplay, map);
        } else {
            // window.alert('Directions request failed due to ' + status);
        }
    });
}

function showSteps(directionResult, markerArray, stepDisplay, map) {
    // For each step, place a marker, and add the text to the marker's infowindow.
    // Also attach the marker to an array so we can keep track of it and remove it
    // when calculating new routes.
    var myRoute = directionResult.routes[0].legs[0];
    for (var i = 0; i < myRoute.steps.length; i++) {
        var marker = markerArray[i] = markerArray[i] || new google.maps.Marker;
        marker.setMap(map);
        marker.setPosition(myRoute.steps[i].start_location);
    }
}

function getBoundsZoomLevel(bounds, width, height) {
    var WORLD_DIM = { height: 256, width: 256 };
    var ZOOM_MAX = 21;

    function latRad(lat) {
        var sin = Math.sin(lat * Math.PI / 180);
        var radX2 = Math.log((1 + sin) / (1 - sin)) / 2;
        return Math.max(Math.min(radX2, Math.PI), -Math.PI) / 2;
    }

    function zoom(mapPx, worldPx, fraction) {
        return Math.floor(Math.log(mapPx / worldPx / fraction) / Math.LN2);
    }

    var ne = bounds.getNorthEast();
    var sw = bounds.getSouthWest();

    var latFraction = (latRad(ne.lat()) - latRad(sw.lat())) / Math.PI;

    var lngDiff = ne.lng() - sw.lng();
    var lngFraction = ((lngDiff < 0) ? (lngDiff + 360) : lngDiff) / 360;

    var latZoom = zoom(height, WORLD_DIM.height, latFraction);
    var lngZoom = zoom(width, WORLD_DIM.width, lngFraction);

    return Math.min(latZoom, lngZoom, ZOOM_MAX);
}

function latLngDistance(a, b) {
    if (typeof(Number.prototype.toRad) === "undefined") {
        Number.prototype.toRad = function() {
            return this * Math.PI / 180;
        }
    }

    var R = 6371e3; // metres
    var phi1 = a[0].toRad();
    var phi2 = b[0].toRad();
    var delta_phi = (b[0]-a[0]).toRad();
    var delta_lambda = (b[1]-a[1]).toRad();

    var a = Math.sin(delta_phi/2) * Math.sin(delta_phi/2) +
        Math.cos(phi1) * Math.cos(phi2) *
        Math.sin(delta_lambda/2) * Math.sin(delta_lambda/2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    return R * c;
}

function updateGeoPoints() {
    var from = new Date(window.map_start).toISOString();
    var to = new Date(window.map_end).toISOString();
    from = from.substring(0, 10) + ' ' + from.substring(11, 19)
    to = to.substring(0, 10) + ' ' + to.substring(11, 19)

    var engine = window.db_conf.engine;
    var table = window.db_conf.table;
    var columns = window.db_conf.columns;

    execute(
        {
            type: 'request',
            action: 'db.select',
            args: {
                engine: engine,
                query: "SELECT " + columns['latitude'] + " AS latitude, " +
                    columns['longitude'] + " AS longitude, " +
                    columns['address'] + " AS address, " +
                    "DATE_FORMAT(" + columns['created_at'] + ", '%Y-%m-%dT%TZ') " +
                    "AS created_at FROM " + table + " WHERE created_at BETWEEN '" +
                    from + "' AND '" + to + "' ORDER BY " + columns['created_at'] + " DESC" }
        },

        onSuccess = function(response) {
            initMapFromGeopoints(response.response.output);
        }
    );
}

function initMap() {
    updateGeoPoints();
}

