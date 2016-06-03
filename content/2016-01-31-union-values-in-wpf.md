title: Union Values in WPF
date: 2016-01-04 09:35:47
category: blog
tags: F#, FSharp, WPF, .NET
wp-archive: 418

This morning I convered an enumeration from some VB code into a union in F#.
This enum had been created so that I could create a generic "tab" view and
view-model in WPF, and could easily tell each instance what tab it was to be.
Unfortunately, I began receiving an error to the effect of `The TypeConverter
for "Tabs" does not support converting from a string.` To solve this, I added an
attribute to the union and a separate class definition; I can now set `<DataTab
TabType="Search" />` with no problems! Code below for my own future reference:

<noscript>
<a href="https://gist.github.com/amazingant/a35528775f7966adcb1e">Source code on
GitHub's Gist site</a>
</noscript>
<script
src="https://gist.github.com/amazingant/a35528775f7966adcb1e.js?file=Tabs.fsi"
type="text/javascript"></script>
