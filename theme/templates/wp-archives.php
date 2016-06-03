<?php

$oldLinks = [
    {% for article in articles %}
        {% if article.metadata.get('wp-archive') %}
            "{{ article.metadata.get('wp-archive') }}" => "/{{ article.url }}",
        {% endif %}
    {% endfor %}
];

if (isset($_GET["q"]) && array_key_exists($_GET["q"], $oldLinks))
{
    header("HTTP/1.1 301 Moved Permanently");
    header("Location: ".$oldLinks[$_GET["q"]]);
}
else
{
    header("Location: /404/");
}
