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

### Edit 2016-06-14:

This post was really intended for my own benefit, and I often come back to the
page to remember how to do &lt;thing&gt; rather than go find it elsewhere. If
you just need a new branch with no history, the following command can be used.

```sh
git checkout --orphan <branchname>
```

This can be helpful for repositories where one branch contains the source code
for say, a website, and another branch contains the generated content for it;
this site uses a branch named `generated` with its own history for this purpose,
much like the `gh-pages` branches that sites hosted by GitHub use.

Note that as of git 2.9.0, git will refuse to let you merge this new branch with
an existing branch; the intent here is that if two branches have no mutual
history at all, merging them is likely a mistake. If it isn't a mistake, add
`--allow-unrelated-histories` to your call to `git merge` and it will let you
merge them.


[SOpost]: http://stackoverflow.com/questions/645450/insert-a-commit-before-the-root-commit-in-git
