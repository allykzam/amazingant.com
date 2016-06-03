<?php

$oldLinks = [
            "418" => "/blog/2016/01/04/union-values-in-wpf/",
            "390" => "/blog/2015/03/13/custom-attributes-on-fsharp-union-cases/",
            "239" => "/blog/2013/01/04/new-initial-commit-in-git/",
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