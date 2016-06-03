title: My Projects
date: 2016-05-10 13:10
home-title: My Projects
home-color: #178000
home-image: alakazam.png
home-desc: Info about some of the stuff I work on other than actual work


I don't spend loads of my free time working on code, so most of what I've done
is for my employer. Of the stuff I've done in my free time, most of it doesn't
get published anywhere because either I changed my mind, couldn't figure out
what I wanted to do, or because it's just so hacky that I don't want to admit I
wrote it. ;)

For the odd things that have actually been published publicly, take a look at my
[GitHub profile][github-profile]. I mostly use GitHub's gists site for code
samples to send people, but you're welcome to look at [my gists][gists] too if
you want.

The odd things I've written that might actually be worth looking at are:

### This site

Source code for this site is available [on GitHub][site-source], although it
might be more fun to look at it here? The site is built on a bunch of markdown
files and the Pelican static site generator. I'm not terribly familiar with
Python, but I saw another site using it and providing all of their source, so it
was easy enough to just make changes to do what I wanted.


### [fbdev][fbdev-project]

At one point I decided I wanted to poke around the frame-buffer devices on linux
systems, and turned it into an adventure in learning C. The project originally
just took over your display and rendered either a donut shape or a cube on your
screen, but since then I've started playing around with loading sprites, and
incorporating basic keyboard input so you can move things around. This might
turn into a fun project if I find more time to work on it?


### [FAKE][fake-project] / [Paket][paket-project]

Neither of these projects are my doing, but I've made some small contributions
to both. For anyone working in .NET, I also highly recommend taking a look at
both of them!

[FAKE][fake-project] is a make-like tool, intended for writing build scripts
with. It can automate most of the work you go through when building or releasing
.NET projects. At work, I've rigged up our build server to just run the scripts
written with FAKE; the build server can just run one command, and the build
scripts build, test, and deploy everything for us.

[Paket][paket-project] is sorta like NuGet? But it's built primarily in F#, does
its best to maintain compatibility rather than breaking things whenever someone
wants to implement big new features, and provides dependency management for
things other than packaged binaries. Paket will actually let you point to a
GitHub project (or a gist) or even a specific http URI, and will pull the
appropriate files down for you. Need a single file from another project? Paket
will help you with that!


### [FSharpWpfGuide][fsharp-wpf-guide]

At some point I was trying to get started writing a WPF application with F#.
Rather than promptly forgetting everything I had learned, I wrote up
instructions as a blog post and carefully followed them to create a project.
This project contains all of the code for that blog post, along with a full
commit history.

If you already know WPF and F#, but aren't sure how to get started writing a
single project that uses both, feel free to use my code and blog post as an
example for how to do so.


### [FParsecScript][fpscript-project]

For fun, I built a scripting engine! The full commit history is hidden because
I've made lots of references to things I was doing for my employer at the time,
but the code here works. The engine parses and executes a VB-like scripting
language with some small changes here and there to suit my needs. There are also
some helpful hooks to make it easy to embed into another project.

Be aware that this project isn't really complete, so there are lots of missing
features. You can't define functions or new types, I only ever got around to
using getters for properties (you can't set a property), and so on.


### Other Stuff

There are also a handful of other projects on my GitHub profile, like the
[Validation][validation-project] library and the
[BuildUpdater][buildupdater-project] tool. Many of these other projects solved a
problem I was having at some point, and haven't had to deal with since, so
they've stayed rather stagnant.


[github-profile]: https://github.com/amazingant
[gists]: https://gist.github.com/amazingant
[site-source]: https://github.com/amazingant/amazingant.com
[fbdev-project]: https://github.com/amazingant/fbdev
[fake-project]: https://fsharp.github.io/FAKE/
[paket-project]: http://fsprojects.github.io/Paket/
[fsharp-wpf-guide]: https://github.com/amazingant/FSharpWpfGuide
[fpscript-project]: https://github.com/amazingant/FParsecScript
[validation-project]: https://github.com/amazingant/Validation
[buildupdater-project]: https://github.com/amazingant/BuildUpdater
