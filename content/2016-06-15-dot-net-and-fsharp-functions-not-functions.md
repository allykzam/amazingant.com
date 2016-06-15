title: .NET and F#: Where functions are functions, except when they're not
date: 2016-06-15 11:28
category: blog
tags: F#, FSharp, .NET

Functions in .NET and F# in particular have some oddities that I've run into and
can be a bit annoying at times. At least partially for my own benefit, I'm
documenting my finds here while I remember them.

<!-- more -->

So in F#, if you want to define a function that adds two values together, you
can write it very simply:

```FSharp
let add x y = x + y
```

This definition for `add` almost doesn't seem worth writing, but it can be
helpful if, say, you want to perform some logging whenever it's used. This
function works great when you go to call it too:

```FSharp
let addNumbers = add 5 10
let addStrings = add "a" "b"
```

When I said it works great, what I actually meant is that it works great
sometimes. If you define `add` as I did and then try to use it like this, you
get two errors from the compiler on the `addStrings` line, telling you that
`"a"` and `"b"` are supposed to be integers, not strings. So how do we fix this?
Well, you could try giving it a type signature:

```FSharp
let add (x : 'a) (y : 'a) : 'a = x + y
```

Except this doesn't work. Rather than fixing things, it adds two warnings now,
telling you that the `addNumbers` line is restricting the type `'a` in the new
signature to be integers. So taking the time to tell the compiler that this
function is generic doesn't work well like this, as the compiler decides that
you're using it for integers anyway, and it ignores your type signature.

When I started working with F#, I had actually played around with Haskell a bit
already, so my initial thought on how to fix this was to give the type signature
like this instead:

```FSharp
let add : 'a -> 'b -> 'c =
    fun x y -> x + y
```

If you look through some of my public F# code and search for `fun`, you'll
actually find that I've used this style frequently. One of the base points
everyone makes about functions in a functional programming language is that
functions are always values, so writing them as a lambda like this shouldn't
make any difference.

Moving on, here's how you actually fix `add`:

```FSharp
let inline add x y = x + y
```

The definitions for `addNumbers` and `addStrings` work correctly now! Yay! Now
if you, like me, had attempted to use full type signatures like `'a -> 'b -> 'c`
because you were used to doing that in Haskell, you'll find that there's no way
to fix your code. Neither of these works:

```FSharp
let inline add : 'a -> 'b -> 'c =
    fun x y -> x + y

let add : 'a -> 'b -> 'c =
    inline fun x y -> x + y
```

The reason here is that in F#, `fun` is used to define a lambda, and while
lambdas are functions, they aren't. Makes sense, doesn't it? Equally confusing,
both of these definitions compile down to the same CIL code:

```FSharp
let normalFunc x y = x + y
let lambdaFunc : 'a -> 'b -> 'c = fun x y -> x + y
```

So the compiled versions are identical, but one is a function and the other
isn't. Clear as mud.

At some point since writing my [F# and WPF][fsharp-and-wpf] article, I found
myself trying to port a View Model to F#, but couldn't get the messaging tools
in MvvmLight to work for me. After reviewing the 5.3.0 release notes recently, I
found out why I had such difficulty. In the messaging tools, you pass an
`Action<T>` to a `Register` function, where `T` is the type of message you want
to process. In F# this is easy to do:

```FSharp
GalaSoft.MvvmLight.Messaging.Messenger.Default.Register
    (
        self,
        fun x -> printfn "Received a message: %s" x
    )
```

This should work, and the F# compiler happily converts our lambda into an
`Action<String>` object, and passes it along to the `Register` method.
Unfortunately, if you wait around for this lambda to be called, you'll likely
never see it happen. The trick here is that the `Messenger` class keeps a
reference to your function with a `WeakReference`. When the F# compiler
helpfully converted your lambda into an `Action<String>`, it did so by stashing
your lambda somewhere, and then replacing it with `new
System.Action<String>(YourLambdaHere)`. Since this new `Action<String>` is only
referenced here and the `Messenger` class only keeps it in a `WeakReference`,
the garbage collector decides that it's free to clean it up.

Writing this inside of a class you're using, you could try fixing this like so:

```FSharp
type YourType() as self =
    let messageHandler = new System.Action<String>(fun x -> printfn "Received a message: %s" x)
    do
        GalaSoft.MvvmLight.Messaging.Messenger.Default.Register(self, messageHandler)
```

Writing the code like this better matches how you're likely to have written the
code in VB or C#, and now `messageHandler` can use `self` to access members in
the current instance of `YourType`; you could even replace the lambda here with
the name of an existing `member` on `YourType` and it would compile and run.
Except this still doesn't work. Defining `messageHandler` here in a type creates
it in the type's constructor; as with the last attempt, as soon as the
constructor ends, the garbage collector decides it can get rid of your handler.

The only way to make sure that your handler stays around for as long as the
instance of `YourType` does is to mark it with the dreaded `mutable` keyword. Do
that, and now this works as expected:

```FSharp
type YourType() as self =
    let mutable messageHandler = new System.Action<String>(fun x -> printfn "Received a message: %s" x)
    do
        GalaSoft.MvvmLight.Messaging.Messenger.Default.Register(self, messageHandler)
```

This code still creates the `Action<String>` during the constructor, but
`messageHandler` is now an `internal` field on the type, and sticks around as it
would if you had written this in VB or C#. Unfortunately, you can't avoid this
by just moving to a member; adding `member x.Handler = new System.Action...`
adds a read-only property to your type that returns a new `Action<String>` every
time it's accessed. This puts you right back in the same boat again, and you
can't (that I know of) add the `mutable` keyword to a member.

At this point, all you can really do is try to streamline the effort of creating
the `messageHandler` value. A helper function like this one works:

```FSharp
let BuildAction<'t> f = new System.Action<'t>(f)

...

    let mutable messageHandler = BuildAction (fun x -> printfn "Received a message: %s" x)
```

This still works because, again, the `mutable` keyword forces the
`messageHandler` to be stored as a field. This also makes it easy enough to
point to an existing `member` definition, so it's about as far as I went.

In case you glossed over most of that, to summarize: a function in F# is always
a function, except when it isn't because it's a value, but you can still treat
that value as a function except when you can't. Make sense?

[fsharp-and-wpf]: {filename}2014-12-18-FSharp-and-WPF.md
