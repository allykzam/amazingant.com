title: New Initial Commit in Git
date: 2013-01-04 13:01:10
category: blog
tags: git, self-help
wp-archive: 239

If you're trying to use git's rebase command on your repo's first commit, you
may not feel there are many options. What I found you could do is to create an
empty commit in a new blank branch, and then rebase everything else off of that
commit, essentially creating a new "original" commit.

<!-- more -->

----

The great thing here is it gets your initial commit to a place where you can use
git rebase to make to make changes to it; the bad thing here is that you're
modifying history, which is never a good idea for anything you've shared with
anyone, especially since in this case you'll be modifying every commit in the
entire repo to have a new origin of this "new" initial commit.

If you're sure you haven't shared the repo with anyone yet, and you don't mind
rewriting history, here's the code:

```sh
# Create a new empty branch called 'newroot'
git symbolic-ref HEAD refs/heads/newroot
git rm --cached -r .
git clean -f -d
# Create a first commit
git commit --allow-empty -m 'initial commit'
# Rebase everything onto this new initial commit
git rebase --onto newroot --root master
# Kill off your empty branch
git branch -d newroot
```

And there you go! If you're doing this to add previous history to your git
repository as I was doing, this can give you what you need to add commits in
before the "beginning of time," remembering to pass `--date=""` when you create
that commit.

For those reading this wondering why I needed to do this, I was attempting to
condense numerous copies of source code amounting to ~8.5GiB into a git
repository that I could use to reference old changes. The resulting repository
was ~300MiB, and came in at just over 100MiB as a bare clone for dumping on a
company server.

The code I used above is taken from the current best answer to a stackoverflow
question [here][SOpost].

Edit 2014-08-01: Mostly for the sake of myself in the future, please note that
`git checkout --orphan <branchname>` works perfectly if you just want a branch
with no history. This doesn't help when you're trying to rebase your
repository's history on top of some additional history you found (or made up?).
I've started keeping a journal as a git repository, and in this case, I want to
keep different branches for different purposes, and I don't want them
intermingled; for this purpose, I have a "work" branch and a "home" branch in
the same repository that share no common history.


[SOpost]: http://stackoverflow.com/questions/645450/insert-a-commit-before-the-root-commit-in-git
