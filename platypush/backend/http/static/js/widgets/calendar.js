$(document).ready(function() {
    var $widget = $('.widget.calendar'),
        $nextEventContainer = $widget.find('.calendar-next-event-container'),
        $eventsListContainer = $widget.find('.calendar-events-list-container');

    var formatDateString = function(date) {
        return date.toDateString().substring(0, 10);
    };

    var formatTimeString = function(date) {
        return date.toTimeString().substring(0, 5);
    };

    var refreshStatus = function(status) {
        setState(state=status.state);
        if ('elapsed' in status) {
            setTrackElapsed(status.elapsed);
        }
    };

    var refreshCalendar = function() {
        execute(
            {
                type: 'request',
                action: 'calendar.get_upcoming_events',
                args: {
                    max_results: 9,
                }
            },

            onSuccess = function(response) {
                var events = response.response.output;
                $eventsListContainer.html('');

                for (var i=0; i < events.length; i++) {
                    var event = events[i];
                    var start = new Date('dateTime' in event.start ? event.start.dateTime : event.start.date);
                    var end = new Date('dateTime' in event.end ? event.end.dateTime : event.end.date);
                    var summary = event.summary;

                    if (i == 0) {
                        $nextEventContainer.find('.summary').text(summary);
                        $nextEventContainer.find('.date').text(formatDateString(start));
                        $nextEventContainer.find('.time').text(
                            formatTimeString(start) + ' - ' + formatTimeString(end));
                    } else {
                        var $event = $('<div></div>').addClass('calendar-event').addClass('row');
                        var $eventDate = $('<div></div>').addClass('date')
                            .addClass('three columns').text(formatDateString(start));

                        var $eventTime = $('<div></div>').addClass('time').addClass('one column')
                            .text('dateTime' in event.start ? formatTimeString(start) : '-');

                        var $eventSummary = $('<div></div>').addClass('summary')
                            .addClass('eight columns').text(summary);

                        $eventDate.appendTo($event);
                        $eventTime.appendTo($event);
                        $eventSummary.appendTo($event);
                        $event.appendTo($eventsListContainer);
                    }
                }
            }
        );
    };

    var initWidget = function() {
        refreshCalendar();
        setInterval(refreshCalendar, 900000);
    };

    var init = function() {
        initWidget();
    };

    init();
});

