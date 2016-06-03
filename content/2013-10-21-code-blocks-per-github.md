title: Code blocks per GitHub
date: 2013-10-21 18:26
modified: 2016-06-03 13:21
category: blog
tags: HTML, CSS
wpf-archive: 349

Poking around GitHub with Chrome's element inspector, I've played around with
their CSS, made some adjustments, and come up with my own style for code blocks.
Basically any time inline code gets `<code>` and `</code>` wrapped around it,
and large blocks go in `<pre><code>` and `</code></pre>`.

```CSS
code {
    margin-right: 2px;
    padding-right: 5px;
    padding-left: 3px;
    border: 1px solid #DDDDDD;
    background-color: #F0F0F0;
    border-radius: 5px;
}

pre {
    margin-right: 2px;
    padding-right: 25px;
    padding-left: 15px;
    padding-top: 10px;
    border: 1px solid #DDDDDD;
    background-color: #F0F0F0;
    border-radius: 5px;
    overflow: auto;
}

pre code {
    margin: 0;
    padding: 0;
    border: none;
    background-color: transparent;
    word-wrap: normal;
    white-space: pre;
}
