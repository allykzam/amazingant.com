title: F# and WPF
date: 2014-12-08 16:53
modified: 2016-05-20 16:05
category: blog
tags: F#, FSharp, WPF, .NET
wp-archive: 383

In certain projects, it may be deemed appropriate to utilize both F# and WPF.
Visual Studio has a large number of issues that make this difficult, not the
least of which is that it simply doesn't support creating a WPF project with F#
out-of-the-box. What follows is a guide based on what I've run into, which
should be enough to get up-and-running. Please be aware that I've tried to work
with something resembling the Model-View-ViewModel design pattern, but I can't
say as I've strictly adhered to it here or anywhere else -- I also provide an
example type named `CarListViewController`, which is used to show how one might
write a code-behind file with event handlers, etc., as has typically been done
in WinForms projects.

Although I will explain some F#-isms, don't expect this tutorial to explain all
F# to you. This will go more smoothly if you've played around with F# a bit
already. Assume the same disclaimer for WPF, but doubled, as I touch on XAML and
WPF less than I do on F#. This is really about mixing the two, not getting
started in one of them.

Also of note, I'm writing this while working with Visual Studio 2013
Professional edition, and so some aspects of this may not match expectations if
my steps are followed with a different version. If the licensing terms are
acceptable, the Community edition of Visual Studio 2013 and later supports
extensions, and should work well if Professional is not available.

<!-- more -->

### Visual Studio 2010 Support

Visual Studio 2010 and earlier aren't supported at all for this method of
building a F#/WPF application, because of the magic of type providers.
Unfortunately, they were introduced into Visual Studio with 2012 and the release
of F# 3.0. There are other ways this can be done, but none of them feel as
well-polished, so I won't go into detail on them.

The best option I can think of when build a F#/WPF application when Visual
Studio 2010 or earlier must be used is to build the WPF application in VB or C#,
but only use it for the XAML and code-behind files, referencing a separate F#
library containing the Model and ViewModel layers of the MVVM pattern.

I only mention all of this because I've had to support building everything in
Visual Studio 2010, so while this tutorial may work well for some, it has the
potential to be entirely useless for others.


### One-Time Setup

These extra tools are not required when working with an existing project, but
may still prove useful at some later point. First up, download and install the
`F# Empty WPF Project` extension; this can be found
[here][FSEmptyProjectExtension]. Next, use Visual Studio's Extensions and
Updates window to find and install the `Visual F# Power Tools` extension, and
then under `Tools -> Options -> General` enable the `Folder organization`
option. The F# Power Tools extension isn't strictly required at all, but makes
the process of adding/using folders in an F# project a bit easier, among other
wonderful goodies. It's certainly worth installing if you plan to use F#, even
if you don't plan to work with WPF. See [this section][FSPowerToolsFolderLimits]
for some of the pitfalls of folders in F# projects; it's getting better, but
isn't exactly a perfect situation.


### Getting Started

Once the empty project extension is installed, create a new project using the
`F# Empty Windows App (WPF)` template; I've named mine `FSharpWpfGuide`. This
project type automatically includes three NuGet packages:

* `Expression.Blend.Sdk` -- I haven't actually used this, so I'm not entirely
  sure of its purpose.
* `FSharp.ViewModule.Core` -- provides base classes which I'll be using to make
  the MVVM pattern and use of `ICommand` much easier
* `FsXaml.Wpf` -- includes a type provider for F# which parses XAML files and
  provides type definitions for them

The magic sauce here is the type provider from `FsXaml.Wpf`; for readers not
familiar with type providers, what this does is parses a XAML file while
developing in Visual Studio _before_ compiling. The result is a type definition
that can be used to generate the associated component, and provides properties
for any XAML elements with an `x:Name` attribute. It might not seem like much,
but I promise it's magic. ;)

<strike>Before moving forward, ask Visual Studio to build the solution, and a
warning will appear. There's a lot of text in the warning window, but the gist
is that since the type provider needs to read and write files on the local
machine, and will execute code, there's potential for a malicious type provider
to be written. This is the part where I warn that Visual Studio should not be
run as an administrator. That said, to continue, the type provider needs to be
enabled.</strike>

This warning doesn't come up anymore, as of Visual Studio 2015 with Update 1.
Yay!


#### Files

According to the Solution Explorer, the new project should contain the following
files:

* `MainWindow.xaml` and `MainWindow.xaml.fs`
  * These are the XAML file and its code-behind for a default empty window

* `App.xaml`
  * This file matches the file named `Application.xaml` which is typically
    created in Visual Studio's existing WPF project template. I won't get into
    the details of what it can do, but anything that a normal `Application.xaml`
    file could do can be done here

* `App.fs`
  * This is akin to the `Program.cs` file in a C# project, or the default
    `Module1.vb` in a VB console application (VB doesn't give the developer
    access to this in a WinForms or WPF project), and it contains the main
    entry-point for the application. At this point, it should already contain
    use of the `FsXaml.Xaml` type provider to load up `App.xaml` and launch it.

* `App.config`
  * As with any C# or VB project, this optionally contains settings and runtime
    configurations for the application.

* `packages.config`
  * NuGet utilizes this XML file to track the packages installed, as well as the
    required version numbers.


### Adding a Window

For the sake of going through more work, remove the files `MainWindow.xaml` and
`MainWindow.xaml.fs`. "MainWindow" is a more apt name, but I'll be using
"MainForm" simply to force myself to show how to change the startup window.

In the Solution Explorer, right-click `App.xaml` and select `Add Above -> New
Item...`, then type `MainForm.xaml` into the file-name box. The particular file
type selected doesn't matter much, so long as it's a single file being added. I
strongly recommend simply not touching it, and leaving `Source File` selected.

To ensure that the XAML file is included correctly, right-click it in Solution
Explorer, pick `Properties`, and change the `Build Action` to `Resource`. It is
**VERY IMPORTANT** that this be done for **EVERY** `*.xaml` file, or the
application will throw an exception at runtime while trying to utilize the
associated control(s). It will not provide the wonderful compile-time errors and
warnings that F# developers are used to.

Moving on, replace all of the text in the file with the following:

```XML
<Window
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    Title="Testing"
    Height="200"
    Width="400"
    >
    <Canvas>
    </Canvas>
</Window>
```

The contents so far should be pretty easy to understand, so I'll gloss over them
and stick to the F#-specifics. In the Solution Explorer, right-click `Add Below
-> New Item...`, and name the new file `MainForm.xaml.fs`.

Based on the way F# handles values, if you're not already aware, F# code cannot
reference values which have not been declared yet. By extension, this means that
files have to be compiled in a certain order, else the compiler will reject code
which references values from other un-compiled files. This is why Visual Studio
gives us the option to arrange files in a different order with F#, offering the
`Add Above` and `Add Below` options for new files.

Replace the contents of the new `MainForm.xaml.fs` with the following:

```FSharp
namespace FSharpWpfGuide.Views

type MainForm = FsXaml.XAML<"MainForm.xaml", true>

namespace FSharpWpfGuide.ViewModels

type MainFormViewModel() =
    member __.Title = "F# |> WPF Guide"
```

This new code uses the `FsXaml.XAML` type provider to generate a type definition
named `MainForm`, which is based on the contents of `MainForm.xaml`. The second
parameter, `true` in this case, indicates whether or not the type provider
should generate properties for XAML nodes with an `x:Name` attribute; it's
easiest to just assume this should always be `true`. In a different namespace,
we then declare a simple type which contains a single value. There isn't much
need for this, but it allows for our first data binding. Before proceeding,
build the solution.

Back in `MainForm.xaml`, add the following:

```diff
  <Window
      xmlns="https://schemas.microsoft.com/winfx/2006/xaml/presentation"
      xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
+     xmlns:viewmodels="clr-namespace:FSharpWpfGuide.ViewModels;assembly=FSharpWpfGuide"
-     Title="Testing"
+     Title="{Binding Title}"
      Height="200"
      Width="400"
      >
      <Window.DataContext>
          <viewmodels:MainFormViewModel />
      </Window.DataContext>
      <Canvas>
      </Canvas>
  </Window>
```

The additional `xmlns` attribute allows utilizing values from the second
namespace used in `MainForm.xaml.fs`, the `DataContext` definition is added to
allow nodes to bind their values to values from the type specified (in this
case, the `MainFormViewModel` type), and the adjusted title attribute specifies
that its value is to be bound to the `Title` property in the window's
`DataContext`. Because the codebase was re-compiled after writing
`MainForm.xaml.fs`, IntelliSense and the WPF designer should both know about the
values specified there, and the title in the preview should show up after
updating the XAML.

To ensure that the application will run correctly, there's one last change to
make. In `App.xaml`, change the `StartupUri` attribute to `"MainForm.xaml"`. The
application should build and run with no problem now, although it's still a bit
uninteresting. Hello, world!


### Building a Data Model

#### Folders!

As mentioned previously, adding folders to an F# project can cause issues. The
primary concern here is that for code in one file to reference code from another
file, the "other" file must be compiled prior to compiling the "one file" that
references it. Enjoy that headache.

Fortunately, with the MVVM pattern, there is more of a clear order to the files,
where the View depends on the ViewModel, which depends on the Model; there
should be no instances where a ViewModel depends on a View, nor a Model
depending on a ViewModel. However, it does make perfect sense for a ViewModel or
Model to reference other types at their level.

In the Solution Explorer, right-click the project and select `F# Power Tools ->
New Folder`, and give it the name "Models". Later, it will be necessary to do
this again for "ViewModels" and "Views". Next, use the `F# Power Tools -> Move
Folder Up` option to put the folder at the top of the project file list.


#### Design Models?

To quickly explain the purposes of the three folders as they'll be used here:

* Models hold data. In the MVVM pattern, they hold all business and data logic
  as well, although this doesn't always mesh well with F#, so I won't follow
  that aspect of MVVM at all.

* ViewModels primarily exist to connect the View and Model together in MVVM. In
  this guide, most of the logic will reside here, resulting in something closer
  to the Model-View-Adapter pattern.

* Views display content for the user and send commands to the ViewModel. Views
  really shouldn't be concerned with logic, with the most advanced logic here
  being to change some part of a layout based on content.

As mentioned, the way I'm organizing this doesn't perfectly match the MVVM
pattern, nor the other well-known pattern, the MVC (Model-View-Controller)
pattern; the important part about following any of these patterns is to attempt
to separate data and how it behaves from the way that it's presented, such that
UI problems are UI problems and code problems are just code problems. Whatever
the exact results are, don't assume my way is the absolute best (although it
definitely is, because I said so).

Now, MVVM can be strictly adhered to in F#, so why haven't I done so? Partly
because I don't want to repeat as much code, and perfectly following the MVVM
pattern means a bit more repeated code than I feel like writing.


#### Adding a Data Model

In the Models folder, add a file named `Car.fs` and paste the following code
into it:

```FSharp
namespace FSharpWpfGuide.Models

type Make =
    | Ford
    | Chevy

type Car =
    {
        Make : Make
        Model : string
        Year : int
        Miles : int
    }
```

This super-short type definition for the `Car` type is half of the reason I'm
avoiding strict MVVM adherence in F#; I'll explain why when I get to the
ViewModels.

No longer assuming full familiarity with F#, the basic premise here is that a
type named `Make` has been defined as being one of two cases: `Ford` or `Chevy`
(sorta like an enum). In production code, it may be undesirable to do that for
something like vehicle manufacturers, as the list may change. However, some
things aren't likely to change much, and so defining a type like this makes life
easier.

If it's not too much hassle to recompile later, using these "discriminated
unions" as they're called would still be a good idea for manufactures, as unlike
enums in C# or VB, F# tends to give compiler warnings anywhere that code hasn't
been written to fulfill all possible cases it can think of. If special code is
written for each manufacturer, adding a new one would automatically generate a
bunch of warnings indicating which code needs to be updated!

The second type, `Car`, is defined as a "record", which basically means it has
fields with names. A discriminated union can have properties as well, but they
(usually) aren't named.


#### Fixing Compile Order

It won't be apparent right now, but Visual Studio has put the `Car.fs` file at
the end of the compile listing. Unless that has been fixed since I wrote this,
compiling the solution will now result in a build error complaining about the
`App.fs` file, because it's not the "last" file anymore.

To fix this, right-click the project and select `Unload Project`, then
right-click it again and select `Edit FSharpWpfGuide.fspoj`. Somewhere in the
XML will be the following block:

```XML
<ItemGroup>
    <Resource Include="MainForm.xaml" />
    <Compile Include="MainForm.xaml.fs" />
    <Resource Includ="App.xaml" />
    <Compile Include="App.fs" />
    <Content Include="App.config" />
    <Content Include="packages.config" />
    <Compile Include="Models\Car.fs" />
<ItemGroup>
```

Just move that `Models\Car` line up above the `MainForm.xaml` line. After saving
the file, right-click the project again and select `Reload Project`. If the file
is still open, Visual Studio _will_ complain; just say yes.

Note that project files use two spaces for indentation, so if you use a
different number of spaces (or you're a heathen who uses tabs), it would be wise
to fix the spacing after adjusting the file. Otherwise, Visual Studio will do it
for you later. There isn't much else to say here except to be aware that the
project file may need this kind of help again down the road. Welcome to folders
in F# projects.


### Adding a ViewModel

Go ahead and add a folder named "ViewModels" to the project, and move it up
until it's directly below the "Models" folder, then add in a file named
`CarViewModel.fs`. Given that this is the first file in the folder, it would be
prudent to re-open the project file and make sure it was added in the correct
order.

The contents of `CarViewModel.fs` will be a bit longer, so I'll go through it in
sections.

```FSharp
namespace FSharpWpfGuide.ViewModels

open FSharpWpfGuide

type CarViewModel (vehicle : Models.Car) as self =
    inherit FSharp.ViewModule.ViewModelBase()
```

This first section is relatively harmless, defining a new class named
`CarViewModel` which inherits from `FSharp.ViewModule.ViewModelBase.` The value
in parentheses, `vehicle`, is where arguments to the default constructor go. If
the class being inherited has any required parameters, they would go inside the
parentheses following its name.

Last, the `as self` allows easy self-referencing from inside the type's body.
This is akin to C#'s `this` keyboard, or VB's `Me`; in fact, replacing `self`
with `this` or `Me` is entirely possible. I've chosen to use `self` simply
because Everyone Else Is Doing It&trade;.

```FSharp
    let mutable car = vehicle
```

This creates a mutable variable named `car`, and assigns it the value of
`vehicle`. Mutable variables as A Bad Idea&trade; in general, and so functional
programming tries to do away with them. However, we have a UI to build, and
mutable state makes UIs much easier to work with. Sorry, F#.

```FSharp
    let milesToDrive = self.Factory.Backing(<@ self.MilesInput @>, 0)
```

The `self` identifier didn't take long to get used, did it? The
`ViewModelBase.Factory.Backing` function used here takes what is known as a
"quotation," a default value, and optionally some other values, and results in a
`NotifyingValue` containing the default value. Whenever the contents of the
value are updated, it automatically informs anyone listening that the specified
property has changed. This provides the `INotifyPropertyChanged` usefulness with
minimal work, and do to the quotation being actual code, renaming the property
later will (assuming Visual Studio's refactoring tools are used)update this use
of it.

```FSharp
    let drive () =
        let miles = milesToDrive.Value
        if (miles < 0) then invalidArg "miles" "Cannot drive a negative number of miles"
        let newMiles = miles + car.Miles
        cat <- { car with Miles = newMiles }
        self.RaisePropertyChanged <@ self.Miles @>
```

This function brings quite a few new things with it. Two parentheses together as
`()` is known as the `unit` type, which is akin to `void` in C#, or similar to a
`Sub` in VB. It isn't typically needed like this, but due to how this function
is used later, this `unit` is specified as a parameter to indicate to code from
outside F# that the function doesn't require any arguments. In most F# functions
which take a unit as an argument, it simply indicates that the result of the
function needs to be regenerated every time it's used, rather than caching the
value somewhere in memory.

Next, `invalidArg` is a build-in F# tool that throws an `ArgumentException`.
There are a handful of these exception-throwing functions built-in, and
information on them and exceptions in F# is available [here][fsharp-exceptions].


The `<-` operator updates a mutable variable (`car` in this case) and sets it to
the value on the right. I mentioned earlier that I'd cover the choice to make
`Car` a record type, and here it is: F# primarily deals with the mathematic
concept of values, insomuch as that new values never replace old ones, and the
contents of a value can never be changed. Of course this is a problem when one
wishes to change one piece of a vehicle's data, and record types allow this
syntax to do so. `{ car with Miles = newMiles }` isn't actually changing the
car's `Miles` value, it's telling F# to copy the `car` value and to use
`newMiles` as the new car's `Miles` value. Still with me? While it's possible to
use mutable values for each of the car's properties, as done for the entire
`car` value, it's typically better and easier to follow F#'s concept of values
as much as possible. Immutable unchanging values that simply get covered up by
new values are much safer than constantly changing state.

Last, `self.RaisePropertyChanged <@ self.Miles @>` does the same thing that the
`milesToDrive` value does automatically, and informs anyone listening that the
`Miles` property has changed. This tells the View (which doesn't exist yet) that
any bindings it has which reference that value need to be updated in the UI.

```FSharp
    let driveCommand =
        self.Factory.CommandSyncChecked(
            drive,
            (fun () -> milesToDrive.Value > 0),
            [<@ self.MilesInput @>]
            )
```

The `CommandSyncChecked` function creates a value which implements the
`ICommand` interface, which means that `driveCommand` is now something that a
XAML-defined button can use as its `Command` property. There are a handful of
functions for synchronous vs asynchronous commands, with or without a parameter,
and with or without a way to turn off the command. However, I've run into many
issues trying to utilize the versions with parameters, so be aware that your
results may vary if choosing to go that route.

`(fun x -> ...)` is the syntax for declaring a lambda, like `(() => ...)` in C#
or `Sub() ...` in VB. This function is what the UI will call when it wants to
know if it can use this command, and as with the `drive` function earlier, it
needs to accept a `unit` value due to interop with C# and VB, and to indicate to
other F# code that it has to be called every time and not cached.

Last, we provide a list of quotations mentioning which properties this command
depends on. A list of two things in F# looks roughly like `[ 1; 2 ]`. In this
case, since the contents of the `milesToDrive` value will be different after the
`MilesInput` property has been changed, I've listed that property. Now, whenever
the contents of `milesToDrive` are changed, the code from using
`self.Factory.Backing` will tell the UI that the `MilesInput` property has
changed, and the UI will automatically know that it needs to check this command
as well.

```FSharp
    do
        self.DependencyTracker.AddPropertyDependency(
            <@ self.MilesInputText @>,
            <@ self.MilesInput @>
            )
```

Sometimes a class needs to _do_ stuff when it's created. A `do` block is used to
make that happen, since we haven't really defined a proper constructor yet for
this class. We'll be creating a property named `MilesInputText` which just
formats the contents of `MilesInput` for display. Since the value of the former
will be different after the latter has changed, I let the `DependencyTracker`
know that a change in the latter means a change in the former.

```FSharp
    new() =
        CarViewModel
            ({
                Make = Models.Ford;
                Model = "Mustang GT";
                Year = 2001;
                Miles = 10;
            })
```

To be used as a `DataContext`, classes must have a constructor with no
parameters. Since the `CarViewModel` class needs some kind of starting value for
its internal `car` value, this `new()` block is used to define another
constructor which has no parameters, and just calls the other constructor.

More interestingly, this is the first example of the syntax for creating a value
of a record type.

```FSharp
    member __.Make wth get () = car.Make
    member __.MakeStr
        with get () =
            match car.Make with
            | Models.Ford -> "Ford"
            | Models.Chevy -> "Chevy"
    member __.Model with get () = car.Model
    member __.Miles with get () = car.Miles
    member __.Drive with get () = driveCommand

    member __.MilesInput
        with get () = milesToDrive.Value
        and set value =
            milesToDrive.Value <- value
    member __.MilesInputText with get = sprintf "Drive %i miles" milesToDrive.Value
```

Last bit of code is the properties. Properties are defined with the `member`
keyword, and can provide a `get` and/or `set` function as seen to match the
read-only or write-only properties used in C# and VB. The exact layout is very
flexible, so have fun (but not too much fun).

None of these properties need it, but the two underscores on each declaration
can be replaced with an identifier, which then provides a reference back to the
rest of the type. As with the `self` name at the beginning of this file (which
does basically the same thing, but on a wider scope), words like `this` or `Me`
can be used here. Although it's technically still possible to use it as a
reference, two underscores are typically used like this whenever the get/set
code doesn't need a reference to the rest of the type.


### Adding a View

Now add a folder named "Views" and move it up to just below the "ViewModels"
folder, and add files named `CarView.xmal` and `CarView.xaml.fs`. Make sure
`CarView.xaml`'s `Build Action` gets set to `Resource`, and then check the
project file's build order again.

Replace the contents of `CarView.xaml` with the following:

```XML
<UserControl
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
    xmlns:viewmodels="clr-namespace:FSharpWpfGuide.ViewModels;assembly=FSharpWpfGuide"
    mc:Ignorable="d"
    d:DesignWidth="409"
    d:DesignHeight="92"
    >
    <Control.DataContext>
        <viewmodels:CarViewModel />
    </Control.DataContext>
    <StackPanel>
        <TextBox Text="{Binding MilesInput, UpdateSourceTrigger=PropertyChanged}" Name="MilesBox" />
        <Button Name="DriveButton" Command="{Binding Drive}" Content="{Binding MilesInputText}" />
        <Label Content="{Binding Miles}" />
    </StackPanel>
</UserControl>
```

Since the `CarViewModel` type was already defined in the last section, all of
this XAML just works as-is. When it makes sense to do so, it can be very helpful
to write the Model's code first, followed by the ViewModel, and leaving the View
to the end. Of course working in that order isn't always possible.

This simple UI just displays a text box where the user can enter a number of
miles, click a button, and update the number of miles on their Mustang. Note
that the text box for entering miles has an `UpdateSourceTrigger` value in its
binding; setting this to `PropertyChanged` on a `TextBox` element means that the
property in the ViewModel will be updated on every keystroke, rather than just
when focus leaves the box.

One more point of note here, the `Text` property on a `TextBox` control is a
string, and the property it's being bound to here isn't. It wasn't specified
anywhere in `CarViewModel.fs`, but the compiler automatically determined that
the value of `milesToDrive` is an integer because the default value was zero.
Based on that, the compiler also determines that the `MilesInput` property has
to be an integer as well, because it's getter returns `milesToDrive.Value`, and
its setter puts the provided value into `milesToDrive.Value`. What this means
for the UI is that if the user enters `1a`, the box will get a red outline
because the underlying code for the UI encountered an exception trying to
convert `1a` to an integer. I won't go into detail on how to tell the user about
that, but it's worth taking the time to do unless you completely trust your
users.

Next, replace the contents of `CarView.xaml.fs` with the following:

```FSharp
namespace FSharpWpfGuide.Views

type CarView = FsXaml.XAML<"VIews/CarView.xaml", true>
```

As with `MainForm.xaml.fs`, the use of the `FsXaml.XAML` type provider is here
to generate a type definition based on the contents of the `*.xaml` file. Unlike
in `MainForm.xaml.fs`, this use is actually required! I'll wait to explain why,
so as to build suspense.

Open `MainForm.xaml` and make the following changes:

```diff
  <Window
      xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
      xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
      xmlns:viewmodels="clr-namespace:FSharpWpfGuide.ViewModels;assembly=FSharpWpfGuide"
+     xmlns:views="clr-namespace:FSharpWpfGuide.Views;assembly=FSharpWpfGuide"
      Title="{Binding Title}"
      Height="200"
      Width="400"
      >
      <Window.DataContext>
          <viewmodels:MainFormViewModel />
      </Window.DataContext>
      <Canvas>
+         <views:CarView />
      </Canvas>
  </Window>
```

This change adds a `CarView` to `MainForm`.

In a VB or C# project with WPF, a bit of the extra work with XAML files is done
automatically, but since WPF projects for F# aren't supported directly by Visual
Studio, a type isn't generated for every `*.xaml` file in the project. To
relieve the building suspense, what that means is that in a VB or C# project
with WPF, rougly the same stuff that the `FsXaml.XAML` type provider built when
called iin `CarView.xaml.fs` is normally built by Visual Studio. Without that
line in `CarView.xaml.fs`, writing `<views:CarView />` in `MainForm.xaml` would
result in a compiler error, saying that it can't find the definition for
`CarView`. Thank you, type provider!


### Completion?

The project is now complete! The program allows a user to add miles to their
virtual Mustang. Not terribly useful, but adding a save button or a load button
wouldn't take much extra work. But wait, there's more!


### Adding Another ViewModel

Back in the `ViewModels` folder, add a file named `CarListViewModel.fs` below
`CarViewModel.fs`. When I did this, Visual Studio created the file at the bottom
of the project, rather than in the folder specified; if this happens,
right-click the file and use the `F# Power Tools -> Move To Folder` option to
fix this.

Replace the contents of `CarListViewModel.fs` with the following:

```FSharp
namespace FSharpWpfGuide.ViewModels

open FSharpWpfGuide

type CarListViewModel() =
    inherit FSharp.ViewModule.ViewModelBase()

    let cars = System.Collections.ObjectModel.ObservableCollection<CarViewModel>()

    do
        cars.Add(new CarViewModel())
        cars.Add(new CarViewModel({ Make = Models.Chevy; Model = "Camaro ZL1"; Year = 2015; Miles = 10; }))


    member __.Cars with get () = cars
```

Not a lot to talk about here, so I'll focus on the new type being used, the
`ObservableCollection<T>`. This collection type gives us a way to define a
collection that can be watched for changes, which allows WPF elements such as
the `ListView` control to use the collection as a source for list display.
Adding or removing things from the collection automatically feeds information
back to the UI.


### Adding Another View

In the `Views` folder, add a file named `CarListView.xaml` and another named
`CarListView.xaml.fs`. As before, adding directly to the folder will likely
result in them showing up at the bottom of the project, at which point they'll
have to be moved with that `F# Power Tools` option.

For the moment, replace the contents of `CarListView.xaml` with the following:

```XML
<UserControl
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
    xmlns:viewmodels="clr-namespace:FSharpWpfGuide.ViewModels;assembly=FSharpWpfGuide"
    mc:Ignorable="d"
    d:DesignWidth="200"
    d:DesignHeight="100"
    >
    <Control.DataContext>
        <viewmodels:CarListViewModel />
    </Control.DataContext>
    <StackPanel>
        <Button Content="Say Hi" x:Name="TestButton" />
        <ListView ItemsSource="{Binding Cars}" x:Name="CarList">
            <ListView.ItemTemplate>
                <DataTemplate>
                    <StackPanel Orientation="Horizontal">
                        <Label Content="{Binding MakeStr}" />
                        <Label Content="{Binding Model}" />
                    </StackPanel>
                </DataTemplate>
            </ListView.ItemTemplate>
        </ListView>
    </StackPanel>
</UserControl>
```

Notice that the `ListView` used here binds its `ItemsSource` to the `Cars`
property from `CarListViewModel`.

Next, replace the contents of `CarListView.xaml.fs` with the following:

```FSharp
namespace FSharpWpfGuide.Views

type CarListView = FsXaml.XAML<"Views/CarListView.xaml", true>
```

Terribly exciting as usual, but now we have a form with a button that doesn't do
anything. In general, it's preferred to use the `ICommand` stuff from before
(the `Drive` property from `CarViewModel.fs`), but for the sake of showing off
more stuff, I'll use the code-behind for something resembling the common coding
style frequently seen with WinForms.


### Adding a Controller

In the `CarListView.xaml.fs` file, add the following type definition:

```FSharp
type CarListViewController() =
    inherit FsXaml.UserControlViewController<CarListView>()

    let buttonClick (parent : CarListView) _ =
        let msg txt = System.Windows.MessageBox.Show(txt) |> ignore
        match parent.CarList.SelectedItem with
        | :? FSharpWpfGuide.ViewModels.CarViewModel as x ->
            sprintf "Hello. You've selected the %s %s" x.MakeStr x.Model
            |> msg
        | _ -> msg "Hi. You haven't selected a car yet."

    override self.OnInitialized view =
        view.TestButton.Click.Subscribe (buttonClick view) |> self.DisposeOnUnload
```

Suddenly there's a lot going on in a small space again. This new
`CarListViewController` type inherits the `UserControlViewController<T>` type,
which provides a short list of helper functions we can override,
`OnInitialized`, `OnLoaded`, and `OnUnloaded`, as well as the `DisposeOnUnload`
function. Although they don't provide a full way of linking a button's click
event to an event handler as easily as we can in VB/C#, they do provide a place
to manually do so.

Because the button and textbox defined in `CarListView.xaml` both have `x:Name`
attributes, they can be referenced whenever an instance of the parent
`CarListView` value is available. Thus, in the `OnInitialized` function,
`view.TestButton.Click.Subscribe` allows us to add an event handler to the
`TestButton` object's `Click` event.

Since the `buttonClick` function needs a reference back to the View to find out
what the selected car is, I've used a functional-programming feature known as
"currying." Notice that where the function is used, I've passed it `view` as an
argument, but the function takes two parameters, not one! Through some
background magic in F#, this is a normal thing, and a function that takes two
parameters can be called with just one argument, and then result will actually
be another function which only takes the other parameter. This primarily works
with functions defined in F#, and doesn't work well with functions defined in
VB/C#, but it's a useful feature to be aware of.

Next, calling the `Subscribe` function on an event like this returns a
disposable object. As with external database connections or file handles, this
object needs to be properly disposed of to avoid memory leaks, so we use `|>
self.DisposeOnUnload` to make sure that it is disposed when the View unloads.

Moving on to the `buttonClick` function, I've used an underscore in two places
that would normally have a variable name: in the function definition as a
parameter, and later in the second cast of the `match ... with` block. An
underscore in one of these places, as with the double-underscore on `member`
definitions, is how we indicate that the actual value provided is unimportant to
us; the main difference here is that when an underscore is used like this, F#
will actually prevent us from utilizing the value, versus the double-underscore
which still acted as a strange variable name. Sometimes to make things easier,
F# developers will provide names for different values even though the value
doesn't matter to them; in these cases it's preferred to start the name with an
underscore still, to at least tell other developers that it is unused.

Next, I've used the `match ... with` block to pattern match against the selected
item, but my first match case uses a type name and the `:?` operator, so that
when the `SelectedItem` value is a `CarViewModel`, it will be stored temporarily
in `x` (because I specified `as x`), and then the body of that match will run.
If the user hasn't selected a vehicle yet, the `SelectedItem` value will be
null, so the other match just accepts anything.


### Wrapping Up

Head back into `CarListView.xaml` and apply the following change:

```diff
  <UserControl
      xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
      xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
      xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
      xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
      xmlns:viewmodels="clr-namespace:FSharpWpfGuide.ViewModels;assembly=FSharpWpfGuide"
+     xmlns:views="clr-namespace:FSharpWpfGuide.Views;assembly=FSharpWpfGuide"
+     xmlns:fsxaml="http://github.com/fsprojects/FsXaml"
+     fsxaml:ViewController.Custom="{x:Type views:CarListViewController}"
      mc:Ignorable="d"
      d:DesignWidth="200"
      d:DesignHeight="100"
```

The addition of the `fscaml:ViewController.Custom` value tells the type provider
that the `CarListViewController` type should be the controller used for this
XAML element.

Next, in `MainForm.xaml`, change `<views:CarView />` to `<views:CarListView />`,
and give the program a go. The window should now come up and display a short
list of the two vehicles we put in, and a button that when clicked, either tells
the user that no vehicle has been selected, or informs the user of the make and
model. Still not a terribly useful application, but this should be enough
examples to get started.

That's all I'm going to cover here, since again, this should be enough
information to get started on useful projects. The resulting source for this
tutorial is available on [GitHub][guide-source].

[FSEmptyProjectExtension]: https://visualstudiogallery.msdn.microsoft.com/e0907c99-bb04-4eb8-9692-9333d5ff4399
[FSPowerToolsFolderLimits]: https://fsprojects.github.io/VisualFSharpPowerTools/folderorganization.html#Limitations
[fsharp-exceptions]: http://fsharpforfunandprofit.com/posts/exceptions/
[guide-source]: https://github.com/amazingant/FSharpWpfGuide
