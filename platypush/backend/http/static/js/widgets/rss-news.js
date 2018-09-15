$(document).ready(function() {
    var $newsElement = $('.rss-news').find('.news-container'),
        config = window.widgets['rss-news'],
        db = config.db,
        news = [],
        default_limit = 10,
        cur_article_index = -1;

    var getNews = function() {
        execute(
            {
                type: 'request',
                action: 'db.select',
                args: {
                    engine: db,
                    query: "select s.title as source, e.title, e.summary, " +
                        "strftime('%Y-%m-%dT%H:%M:%fZ', e.published) as published " +
                        "from FeedEntry e join FeedSource s " +
                        "on e.source_id = s.id order by e.published desc limit " +
                        ('limit' in config ? config.limit : default_limit)
                }
            },

            onSuccess = function(response) {
                if (!response.response.output) {
                    return;
                }

                var firstRun = news.length === 0;
                news = response.response.output;
                cur_article_index = -1;

                if (firstRun) {
                    refreshNews();
                }
            }
        );
    };

    var refreshNews = function() {
        if (news.length === 0) {
            return;
        }

        var updateNewsList = cur_article_index == news.length-1;
        var nextArticle = news[++cur_article_index % news.length];
        var dt = new Date(nextArticle.published);
        var $article = $('<div></div>').addClass('article');
        var $source = $('<div></div>').addClass('source').text(nextArticle.source);
        var $title = $('<div></div>').addClass('title').text(nextArticle.title);
        var $publishTime = $('<div></div>').addClass('publish-time')
            .text(dt.toDateString() + ', ' + dt.toTimeString().substring(0, 5));

        $source.appendTo($article);
        $title.appendTo($article);
        $publishTime.appendTo($article);

        if ($newsElement.find('.article').length) {
            $newsElement.find('.article').remove();
        }

        $article.hide().appendTo($newsElement).show();

        if (updateNewsList) {
            getNews();
        }
    };

    var initWidget = function() {
        getNews();
        setInterval(refreshNews, 15000);
    };

    var init = function() {
        initWidget();
    };

    init();
});

