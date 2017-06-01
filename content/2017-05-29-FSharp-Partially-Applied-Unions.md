title: F# Partially-Applied Unions
date: 2017-05-29
category: blog
tags: F#, FSharp, .NET

The other day I was trying to think how I could group together discriminated
union values in a way to let me later determine if values were
mutually-exclusive. For a simple discriminated union, I came up with a pretty
simple solution: store a `Map<SomeUnion, SomeUnion list>`. Each key in the map
would refer to a `SomeUnion` value, and the corresponding value would be a list
of all the other `SomeUnion` values that it was mutually-exclusive with.

As I began to work up the data model for this, I quickly realized that the union
cases in the `SomeUnion` type would need to contain additional metadata that was
not relevant to whether or not two values were mutually-exclusive. Certain cases
of the `SomeUnion` type might be sub-categorized in some way that was relevant,
but they might also contain file paths, or ID numbers corresponding to database
records. So to really solve my problem using unions, I needed to find a way to
leave out some of the values when constructing a `SomeUnion` value, and treat
the omitted values as a sort of wildcard.

For those who do not work with F#, or have not paid close enough attention,
union cases in F# can only contain a single value. To include multiple values,
you do so by providing a tuple. The compiler takes the time to provide these out
as named members which are useful when working with a union from C# or VB, but
regardless, there is no way for one to "omit" values when creating a union case.

On one hand, if I were working with a dynamically-typed language like Python, I
would probably have just passed `None` for all of the values I wanted to treat
like wildcards, and made sure that the types (which I control anyway) do not
take the time to be picky about the values they are given. On the other hand, I
am not working with a dynamically-typed language, and while I do not have a firm
opinion as to whether dynamic or static typing is better, I do like working with
static types. So this is a brief explanation of what I came up.


<!-- more -->


### Quick Summary

In my finished code, the basic concept is that for each union case which
contains two or more "fields" (i.e. its constructor requires passing a tuple),
the union case gets a wrapper function inside of a quotation. This quotation is
then used within another quotation later, where it can be treated like a normal
F# function, allowing parameters to be omitted. Static functions on a helper
type, `UnionMetadata<'T>`, take the finished quotation, and return a
`UnionMetadata<'T>` value, where `'T` is the union type being worked with. An
example:


```FSharp
[<StructuralComparison; StructuralEquality>]
type SomeUnion =
    | CaseA of bool * int * string
    | CaseB of int
    | CaseC
    ...

let CaseAWrapper = <@ (fun x y z -> CaseA(x, y, z)) @>
```

With the above code in place, the `CaseAWrapper` value can be used in another
quotation, which can then be passed to the `FromQuotation` function on the
`UnionMetadata` type. In F# Interactive, it would look something like this:


```FSharp
let meta = UnionMetadata<SomeUnion>.FromQuotation <@ (%CaseAWrapper) true @>;;

val meta : UnionMetadata<SomeUnion> =
    {
        UnionCase = "CaseA";
        SuppliedArguments =
            [
                (Some true, "Item1");
                (null, "Item2");
                (null, "Item3");
            ]
    }
```

From there, the `UnionMetadata<'T>` type provides a few helper functions that
can be used to determine whether or not a given value matches the metadata. In
this case, one could call `meta.ValueMatches (CaseA (true, 5, "test"))` which
would return `true`; passing `CaseA (false, 5, "test")` would result in `false`
instead, matching the given contents of the `meta` value.

To further test this, the `CaseAWrapper` value could be rewritten, and the
`meta` value updated:


```FSharp
let CaseAWrapper = <@ (fun y x z -> CaseA(x, y, z)) @>
let meta = UnionMetadata<SomeUnion>.FromQuotation <@ (%CaseAWrapper) 10 @>;;

val CaseAWrapper : FSharp.Quotations.Expr<(bool -> string -> SomeUnion)>
...
val meta : UnionMetadata<SomeUnion> =
    {
        UnionCase = "CaseA";
        SuppliedArguments =
            [
                (null, "Item1");
                (Some 10, "Item2");
                (null, "Item3");
            ]
    }
```

Using this updated definition for `meta`, any `CaseA` value where the `int`
field was set to `10` would cause `meta.ValueMatches` to return `true`, while
any other `int` value cause `meta.ValueMatches` to return `false`. And that's
about all you need to know to use the `UnionMetadata<'T>` type.


### Quotations?

Okay, so if you want more information, lets continue using the `SomeUnion` type
as an example to work with. The basic concept that the `UnionMetadata<'T>` type
uses to make all of this work is F# quotations. Quotations are a sort of
"meta-programming" capability built into F#, which allows you to embed F# code
as a value, in a sort of custom AST (abstract syntax tree) that they created
just for this language feature. The full output from F# Interactive for
`CaseAWrapper` looks something like this:

```FSharp
Lambda (y, Lambda (x, Lambda (z, NewUnionCase (CaseA, x, y, z)))
```

At some point during its work, a compiler might generate something like the
above for code like `(fun y x z -> CaseA(x, y, z))`. Each `Lambda` value
corresponds to one of the function parameters because of how F# handles
currying (a function that takes two arguments is actually a function that takes
one argument and returns a new function that takes the other argument), and the
`NewUnionCase` value obviously corresponds to the creation of the `CaseA` value.
When stuffed into `<@ (%CaseAWrapper) 10 @>`, the value looks more like this:

```FSharp
Application (Lambda (y, Lambda (x, Lambda (z, NewUnionCase (CaseA, x, y, z))), Value (10))
```

The added `Application` on the left side, and the `Value (10)` on the right
side, correspond to the fact that you have performed "function application" by
supplying an argument for the function's first parameter. The
`UnionMetadata<'T>` type has a bunch of overloaded functions all named
`FromQuotation` which each take a slightly different "shape" of quotation. they
take quotation shapes like `Expr<'T>` and `Expr<_ -> 'T>`, which would be used
to process `<@ CaseC @>` and `<@ CaseB @>` respectively; `Expr<'T>` is a
quotation representing a value of type `'T`, while `Expr<_ -> 'T>` is a
quotation representing a function that takes one argument and returns a `'T`
value. The current code for `UnionMetadata<'T>` extends this up to functions
that take ten arguments.

It takes a little bit of juggling and rearranging to do, but the private
functions on the `UnionMetadata<'T>` type takes these three types of quotations,
`Application`, `Lambda`, and `NewUnionCase`, and processes them into the
`SuppliedArguments` collection. The `NewUnionCase` quotation also includes a
`FSharp.Reflection.UnionCaseInfo` value, which includes the union case name;
this is where the `UnionCase` value is populated from.


### So what can I do with it?

Well, I mean, whatever you want to? Here's an example of how I'm using it:


```FSharp
type Microsoft.FSharp.Collections.Map<'Key, 'TValue when 'Key : comparison> with
    static member addOrUpdate (key : 'Key) (value : 'TValue) (update : 'TValue -> 'TValue) (oldMap : Map<'Key, 'TValue>) : Map<'Key, 'TValue> =
        if Map.containsKey key oldMap then
            let oldVal = oldMap.[key]
            oldMap
            |> Map.remove key
            |> Map.add key (update oldVal)
        else
            Map.add key value oldMap


type ExclusivityRules =
    {
        MutualExclusions : Map<UnionMetadata<SomeUnion>, UnionMetadata<SomeUnion> list>;
    }
    static member Empty =
        {
            MutualExclusions = Map.empty;
        }

    static member private AddMutualExclusion (x1, x2) (rules : ExclusivityRules) =
        let exclusions =
            rules.MutualExclusions
            |> Map.addOrUpdate x1 [x2] (fun xs -> x2::xs)
            |> Map.addOrUpdate x2 [x1] (fun xs -> x1::xs)
        { rules with MutualExclusions = exclusions }

    static member inline MutuallyExclusive ((e1 : Expr<_>), (e2 : Expr<_>)) : ExclusivityRules -> ExclusivityRules =
        (UnionMetadata<SomeUnion>.FromQuotation<_> e1, UnionMetadata<SomeUnion>.FromQuotation<_> e2)
        |> ExclusivityRules.AddMutualExclusion

    static member inline MutuallyExclusive ((e1 : Expr<SomeUnion>), (e2 : Expr<_>)) : ExclusivityRules -> ExclusivityRules =
        (UnionMetadata<SomeUnion>.FromQuotation e1, UnionMetadata<SomeUnion>.FromQuotation<_> e2)
        |> ExclusivityRules.AddMutualExclusion

    static member inline MutuallyExclusive ((e1 : Expr<_>), (e2 : Expr<SomeUnion>)) : ExclusivityRules -> ExclusivityRules =
        (UnionMetadata<SomeUnion>.FromQuotation<_> e1, UnionMetadata<SomeUnion>.FromQuotation e2)
        |> ExclusivityRules.AddMutualExclusion

    static member inline MutuallyExclusive ((e1 : Expr<SomeUnion>), (e2 : Expr<SomeUnion>)) : ExclusivityRules -> ExclusivityRules =
        (UnionMetadata<SomeUnion>.FromQuotation e1, UnionMetadata<SomeUnion>.FromQuotation e2)
        |> ExclusivityRules.AddMutualExclusion


    member this.GetMutualExclusions (newValue : SomeUnion) (currentValues : SomeUnion list) : SomeUnion list =
        let unionInfo = FSharp.Reflection.FSharpValue.GetUnionFields(newValue, typeof<SomeUnion>)
        let ourExclusionList =
            this.MutualExclusions
            |> Map.toSeq
            |> Seq.filter (fst >> (UnionMetadata<_>.UnionInfoMatchesSpec unionInfo))
            |> Seq.collect snd
            |> Seq.groupBy (fun x -> x.UnionCase)
            |> Seq.map (fun (x, ys) -> x, (ys |> Seq.toList))
            |> Map.ofSeq

        if ourExclusionList.IsEmpty then [] else

        currentValues
        |> Seq.filter
            (fun thisValue ->
                let unionInfo = FSharp.Reflection.FSharpValue.GetUnionFields(thisValue, typeof<SomeUnion>)
                let unionCase = fst unionInfo
                if ourExclusionList.ContainsKey unionCase.Name |> not then false else
                ourExclusionList.[unionCase.Name]
                |> Seq.exists (UnionMetadata<_>.UnionInfoMatchesSpec unionInfo)
            )
        |> Seq.toList
```

The first bit of code adds an extension function `addOrUpdate` to the type
`Map<_,_>`, (roughly matching the method of the same name on the
`ConcurrentDictionary` type) followed by a new type to hold my collection of
rules about what values are mutually-exclusive. The `ExclusivityRules` type
includes an `Empty` member to help me start, because I have other thoughts in
the back of my mind that would require adding additional fields. The
`GetMutualExclusions` function takes a new value and a "current" list of values,
and returns the current values which are considered mutually-exclusive with the
new value. Finally, there are four versions of a `MutuallyExclusive` function
for defining new mutual exclusions.

The four `MutuallyExclusive` functions are almost identical, and are enough to
make the F# compiler happy regardless of what values I use. Each of the
`Expr<_>` parameters is passed to `UnionMetadata<SomeUnion>.FromQuotation<_>`,
and each of the `Expr<SomeUnion>` values is passed to
`UnionMetadata<SomeUnion>.FromQuotation`. This minor difference is enough to
convince the compiler to infer whether it needs to use the `FromQuotation`
overload that takes an `Expr<'T>`, or one of the many `FromQuotation` overloads
that deal with quotations for functions.

The private function `AddMutualExclusion` takes two `UnionMetadata<SomeUnion>`
values, and does most of the legwork, so the `MutuallyExclusive` overloads just
need to call the right `FromQuotation` overload and pass the results off to the
`AddMutualExclusion` function.

From there, I can do this:


```FSharp
let rules =
    ExclusivityRules.Empty
    |> ExclusivityRules.MutuallyExclusive (<@ CaseB @>, <@ (%CaseAWrapper) 10 @>)
    |> ...


let current = [ CaseB 5 ]

let test = rules.GetMutualExclusions (CaseA true 10 "Test") current

...

val test : SomeUnion list = [CaseB 5]
```

In my actual code I'm not using the `SomeUnion` type, but this is the same basic
concept. Depending on what else you want to do, you could extend this to track
certain types of behavior that vary slightly between cases of a union. Or
perhaps certain `SomeUnion` values can be combined together, and
`UnionMetadata<'T>` values could be mapped to functions that handle merging two
values together.


### Where do I get this amazing code?

Source code is available [on
GitHub](https://github.com/amazingant/PartialUnions). As of this writing, the
project is a bit incomplete, but the code needed to start working with the
samples from this post is there, should work, and has a fair bit of XML
documentation written.
