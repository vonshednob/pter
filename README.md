# pter

Your console and graphical UI to manage your todo.txt file(s).

![A screenshot of pter in action](pter.png)

There’s a presentation of pter in motion on [asciinema](https://asciinema.org/a/629376).

Also in this package, the QT5 based graphical user interface, qpter.

![A screenshot of qpter](qpter.png)

pter has a bunch of features that help you managing your todo.txt file:

 - Fully compatible to the todo.txt standard
 - Support for `due:`, `h:`, `t:`, `rec:`, `id:`
 - Save search queries and sorting for quick access
 - Convenient entering of dates
 - Time tracking, notes, task delegation
 - Connect tasks in sequences
 - Template system and auto-completion for ease of creating tasks
 - Support for archive and trash
 - Can work with multiple todo.txt files at the same time
 - Configurable behaviour, shortcuts, and colors

There is also a graphical user interface called qpter, but some features
are missing.


## Installation

### Install using pipx

To install `pter` using `pipx`, run this:

```sh
    pipx install pter
```

If you wish to use `qpter`, the graphical version of `pter`, make sure you
pass this option to `pipx`:

```sh
    pipx install pter[qt]
```


### Install from PIP

This is the deprecated way to install pter; instead rather use `pipx`; see
above.

To install pter you can either clone the repository (see at the end) or, much
simpler, use pip to install it:

```sh
    pip install pter
```

If you want to use the Qt GUI qpter, you have to install PyQt5::

```sh
    pip install PyQt5
```


## Using pter

To launch pter you have to tell it where your todo.txt file is:

```sh
    pter ~/todo.txt
```

For the graphical user interface (requires QT), you have to start it like
this:

```sh
    qpter ~/todo.txt
```

Both will give you a listing of all your tasks order by how soon they will be
due and what priority you have given them.

You can navigate the tasks with your cursor keys and edit selected tasks by
pressing `e`.

More default shortcuts are:

 - `e`, edit the selected task
 - `n`, create a new task
 - `d`, mark the selected task as done (or toggle back to not done)
 - `?`, show all keyboard shortcuts
 - `q`, quit the program

There is a complex search available (have a look at the manual for details), but the short version is:

 - press `/` to enter your search terms
 - search for `done:n` to only show incomplete tasks
 - search for a context with `@context`
 - search for a project with `+project`
 - search for tasks that do not belong to a context with `-@context` or `not:@context`
 - press `Return` to return the focus to the task list


## Using qpter

To launch the Qt GUI, you may (but don’t have to) provide the location of your
todo.txt file::

```sh
    qpter ~/todo.txt
```


# Contributing

Just like any other open source project, you’re invited to participate in
pter’s development. Any contribution is welcome, from bug reports to pull
requests/sending of patches!

You can find the project at [codeberg](https://codeberg.org/vonshednob/pter)
or just email any of the authors with your input.

There is also a general XMPP discussion channel [pter](xmpp:pter@rooms.spacepanda.se?join)
over at `spacepanda.se`.

