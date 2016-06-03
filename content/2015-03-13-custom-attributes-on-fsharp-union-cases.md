title: Custom attributes on F#'s Discriminated Union cases
date: 2015-03-13 15:06
category: blog
tags: F#, FSharp, .NET
wp-archive: 390

Working on a project, I found myself wanting to match different discriminated
union cases with text for output. Normally I write this out as a discriminated
union with a separate function that uses pattern matches to determine which
value to return, but I'd really like to attach the text directly to the
different union cases. If I could find a way to do that, I wouldn't have to dig
around my code as much to find out where the different messages came from.

As I've been poking at .NET's Reflection abilities recently, I figured the
easiest way for me to make that happen would be to add my own attribute type,
and apply them to the different union cases. Should be easy enough to get the
attribute back and pull the text from there, right? Not so fast! Union cases are
internally defined and hidden from F# code in such a way that you'd have to go
through the union's type definition, grab values from
`System.Type.GetMembers()`, and match them by name; at that point, I may as well
have just matched the values by union case and not used attributes at all.

The solution is down in `Microsoft.FSharp.Reflection`, which provides a handful
of useful functions for discriminated unions. The process therefore becomes:

* Get the `Microsoft.FSharp.Reflection.UnionCaseInfo` by passing in the union
  value and a `typeof<X>` to the union's type
* Call `GetCustomAttributes()` on the `UnionCaseInfo` value
* Filter the returned attribute values (they're an `obj` array) to find the
  attribute you want
* Return the contents of the attribute

This is the full contents of how I did it:

<noscript>
<a href="https://gist.github.com/amazingant/7135f89daf6e6bd2a105">Source code on
GitHub's Gist site</a>
</noscript>
<script
src="https://gist.github.com/amazingant/7135f89daf6e6bd2a105.js?file=Errors.fs"
type="text/javascript"></script>
