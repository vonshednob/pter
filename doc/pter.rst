====
pter
====
-----------------------------
Personal Task Entropy Reducer
-----------------------------

Synopsis
========

::

  pter [-h] [-c configuration] filename [filename ...]
  qpter [-h] [-c configuration] filename [filename ...]


Description
===========

pter is a tool to manage your tasks when they are stored in the todo.txt
file format. pter is targeted at users applying the `Getting Things Done`_
method, but can be used by anyone that uses todo.txt files.

pter offers these features:

 - Fully compatible to the todo.txt standard
 - Support for `due:`, `h:`, `t:`
 - Save search queries for quick access (see `Searching`_ and `Named Searches`_)
 - Convenient entering of dates (see `Relative Dates`_)
 - Configurable behaviour, shortcuts, and colors (see `Files`_)
 - Time tracking

qpter is the Qt version of pter (ie. pter with a graphical user interface)
and supports mostly the same features but sometimes looks for other
sections in the configuration.


Options
=======

  ``-c configuration``
    Path to the configuration file you wish to use. The default is
    ``$XDG_CONFIG_HOME/pter/pter.conf`` (usually
    ``~/.config/pter/pter.conf``).

  ``-h``
    Show the help.

  ``filename``
    Path to your todo.txt file. The first file that you provide is the one
    where new tasks will be created in.


Files
=====

Aside from the data files in the todo.txt format (see `Conforming to`_),
pter's behaviour can be configured through a configuration file.

The configuration file's default location is at ``~/.config/pter/pter.conf``.

There should have been an example configuration file, ``example.conf`` distributed with your copy of pter that can give you an idea on how that works. In this documentation you will find the full explanation.

The configuration file is entirely optional and each option has a default
value. That allows you to run pter just fine without ever configuring
anything.

The configuration file has four sections (the names are case-sensitive):

 - `General`_, for general behaviour,
 - `Symbols`_, for icons used in the (task) display,
 - `Keys`_, to override default keyboard controls in lists,
 - Editor:Keys, to override the default keyboard controls in edit fields (detailed in `Keys`_),
 - `Colors`_, for coloring the TUI,
 - `GUI:Colors`_, for coloring the tasks in the GUI,
 - `Highlight`_, for coloring specific tags of tasks,
 - GUI:Highlight, for coloring specific tags of tasks (GUI version, see `Highlight`_).
 - `GUI`_, for other GUI specific options

General
-------

  ``use-colors``
    Whether or not to use colors. Defaults to 'yes'.

  ``scroll-margin``
    How many lines to show at the lower and upper margin of lists. Defaults
    to '5'.

  ``safe-save``
    Safe save means that changes are written to a temporary file and that
    file is moved over the actual file after writing was completed.
    Defaults to 'yes'.

    This can be problematic if your files are in folders synchronised with
    cloud services.

  ``search-case-sensitive``
    Whether or not to search case-sensitive. Defaults to 'yes'.

  ``human-friendly-dates``
    Here you can define what fields of a task, that are known to contain a
    date, should be displayed in a more human-friendly way. By default no
    dates are translated.

    Human-friendly means that instead of a 'YYYY-MM-DD' format it might
    show 'next wednesday', 'tomorrow', or 'in 2 weeks'. It means that
    dates, that are further away (in the future or the past) will be less
    precise.

    Possible values are ``due`` (for due dates), ``t`` (for the
    threshold/tickler dates), ``completed`` (for completion dates),
    ``created`` (for creation dates), or ``all`` (for all of the above).
    You can also combine these values by comma separating them like this::

      [General]
      human-friendly-dates = due, t

  ``task-format``
    The format string to use for displaying tasks. Defaults to "``{selection: >} {nr: >} {done} {tracking }{due }{(pri) }{description}``".

    See `Task Format`_ below for more details.

  ``clear-contexts``
    A list of comma separated contexts (without the leading ``@``) to remove from a task
    when it is being marked as done.

    For example, you might want to remove the ``@in`` context or any
    ``@today`` tags when marking a task as done. In that case
    ``clear-contexts`` should be set to ``in, today``.

  ``default-threshold``
    The default ``t:`` search value to use, even when no other search has
    been defined. Defaults to 'today'.

    This option supports `Relative Dates`_.

  ``delegation-marker``
    Marker to add to a task when delegating it. Defaults to ``@delegated``.

  ``delegation-action``
    Action to take when delegating a task.
    One of 'none', or 'mail-to' (defaulting to 'mail-to').

    'none' does nothing, but 'mail-to' will attempt to start your email
    program to write an email. If your task has a 'to:' attribute (or
    whatever you set up for ``delegation-to``, it will be used as the
    recipient for the email.

  ``delegation-to``
    Attribute name to use when delegating a task via email. Defaults to
    ``to``. Eg. "clean the dishes to:bob" will compose the email to "bob"
    when delegating a task and the delegation action is "mail-to".

  ``protocols``
    What protocols should be considered when using the 'Open URL' function
    on a task. Defaults to ``http, https, mailto, ftp, ftps``.

  ``add-creation-date``
    Whether or not to automatically always add the creation date of a task
    to it when creating the task. Defaults to ``yes``.


Symbols
-------

The following symbols (single unicode characters or even longer strings of
unicode characters) can be defined:

 - ``selection``, what symbol or string to use to indicate the selected item of a list
 - ``not-done``, what symbol or string to use for tasks that are not done
 - ``done``, what symbol or string to use for tasks that are done
 - ``overflow-left``, what symbol or string to use to indicate that there is more text to the left
 - ``overflow-right``, what symbol or string to use to indicate that there is more text to the right
 - ``overdue``, the symbol or string for tasks with a due date in the past
 - ``due-today``, the symbol or string for tasks with a due date today
 - ``due-tomorrow``, the symbol or string for tasks with a due date tomorrow
 - ``tracking``, the symbol or string to show that this task is currently being tracked

If you want to use spaces around your symbols, you have to quote them either
with ``'`` or ``"``.

An example could be::

    [Symbols]
    not-done = " "
    done = ✔


Keys
----

In the configuration file you can assign keyboard shortcuts to the various
functions in pter and qpter.

For details on how to setup shortcuts for qpter, please see below in
section `GUI Keys`_.

There are two main distinct groups of functions. The first, for general
lists and the task list:

 - ``create-task``: create a new task
 - ``edit-task``: edit the selected task
 - ``first-item``: jump to the first item in a list
 - ``half-page-down``: scroll down by half a page
 - ``half-page-up``: scroll up by half a page
 - ``jump-to``: enter a number to jump to that item in the list
 - ``last-item``: jump to the last item in a list
 - ``load-search``: show the saved searches to load one
 - ``next-item``: select the next item in a list
 - ``nop``: nothing (in case you want to unbind keys)
 - ``open-url``: open a URL of the selected task
 - ``prev-item``: select the previous item in a list
 - ``quit``: quit the program
 - ``refresh-screen``: rebuild the GUI
 - ``reload-tasks``: enforce reloading of all tasks from all sources
 - ``save-search``: save the current search
 - ``search``: enter a new search query
 - ``search-context``: select a context from the selected task and search for it
 - ``search-project``: select a project from the selected task and search for it
 - ``show-help``: show the full screen help (only key bindings so far)
 - ``open-manual``: open this manual in a browser
 - ``toggle-done``: toggle the "done" state of a task
 - ``toggle-hidden``: toggle the "hidden" state of a task
 - ``toggle-tracking``: start or stop time tracking for the selected task
 - ``delegate``: delegate a task

And the second list of functions for edit fields:

 - ``cancel``, cancel editing, leave the editor (reverts any changes)
 - ``del-left``, delete the character left of the cursor
 - ``del-right``, delete the character right of the cursor
 - ``del-to-bol``, delete all characters from the cursor to the beginning of the line
 - ``go-bol``, move the cursor to the beginning of the line
 - ``go-eol``, move the cursor to the end of the line
 - ``go-left``, move the cursor one character to the left
 - ``go-right``, move the cursor one charackter to the right
 - ``submit-input``, accept the changes, leave the editor (applies the changes)
 - ``select-file``, when creating a new task, this allows you to select
   what todo.txt file to save the task in

Keyboard shortcuts are given by their character, for example ``d``.
To indicate the shift key, use the upper-case of that letter (``D`` in this
example).

To express that the control key should be held down for this shortcut,
prefix the letter with ``^``, like ``^d`` (for control key and the letter
"d").

Additionally there are some special keys understood by pter:

 - ``<backspace>``
 - ``<del>``
 - ``<left>`` left cursor key
 - ``<right>`` right cursor key
 - ``<up>`` cursor key up
 - ``<down>`` cursor key down
 - ``<pgup>`` page up
 - ``<pgdn>`` page down
 - ``<home>``
 - ``<end>``
 - ``<escape>``
 - ``<return>``
 - ``<tab>``
 - ``<f1>`` through ``<f12>``

An example could look like this::

  [Keys]
  ^k = quit
  <F3> = search
  C = create-task


GUI Keys
~~~~~~~~

To assign shortcuts to functions in the Qt GUI, you will have to use the Qt
style key names, see `https://doc.qt.io/qt-5/qkeysequence.html#details`_ .

The assignment is done in the group ``GUI:Keys``, like this::

  [GUI:Keys]
  new = Ctrl+N
  toggle-done = Ctrl+D

Available function names are:

 - ``quit``, quit qpter
 - ``open-manual``, open this manual
 - ``open-file``, open an additional todo.txt,
 - ``new``, open the editor to create a new task,
 - ``edit``, opens the editor for the selected task,
 - ``toggle-done``, toggles the completion of a task,
 - ``toggle-tracking``, toggle the 'tracking' attribute of the selected task,
 - ``toggle-hidden``, toggle the 'hidden' attribute of the selected task,
 - ``search``, opens and focuses the search field,
 - ``named-searches``, opens and focuses the list of named searches,
 - ``focus-tasks``, focuses the task list,
 - ``delegate``, delegate the selected task


Colors
------

Colors are defined in pairs, separated by comma: foreground and background
color. Some color's names come with a ``sel-`` prefix so you can define the
color when it is a selected list item.

You may decide to only define one value, which will then be used as the text
color. The background color will then be taken from ``normal`` or ``sel-normal``
respectively.

If you do not define the ``sel-`` version of a color, pter will use the
normal version and put the ``sel-normal`` background to it.

If you specify a special background for the normal version, but none for the
selected version, the special background of the normal version will be used
for the selected version, too!

 - ``normal``, any normal text and borders
 - ``sel-normal``, selected items in a list
 - ``error``, error messages
 - ``sel-overflow``, ``overflow``, color for the scrolling indicators when editing tasks (and when selected)
 - ``sel-overdue``, ``overdue``, color for a task when it’s due date is in the past (and when selected)
 - ``sel-due-today``, ``due-today``, color for a task that’s due today (and when selected)
 - ``sel-due-tomorrow``, ``due-tomorrow``, color for a task that’s due tomorrow (and when selected)
 - ``inactive``, color for indication of inactive texts
 - ``help``, help text at the bottom of the screen
 - ``help-key``, color highlighting for the keys in the help
 - ``pri-a``, ``sel-pri-a``, color for priority A (and when selected)
 - ``pri-b``, ``sel-pri-b``, color for priority B (and when selected)
 - ``pri-c``, ``sel-pri-c``, color for priority C (and when selected)
 - ``context``, ``sel-context``, color for contexts (and when selected)
 - ``project``, ``sel-project``, color for projects (and when selected)
 - ``tracking``, ``sel-tracking``, color for tasks that are being tracked right now (and when selected)

If you prefer a red background with green text and a blue context, you could define your
colors like this::

  [Colors]
  normal = 2, 1
  sel-normal = 1, 2
  context = 4


GUI:Colors
----------

The GUI has a somewhat different coloring scheme. The available colors are:

 - ``normal``, any regular text in the description of a task,
 - ``done``, color for tasks that are done,
 - ``overdue``, text color for overdue tasks,
 - ``due-today``, color for tasks that are due today,
 - ``due-tomorrow``, color for tasks that are due tomorrow,
 - ``project``, color for projects,
 - ``context``, color for contexts,
 - ``tracking``, color for tasks that are currently being tracked,
 - ``pri-a``, color for the priority A,
 - ``pri-b``, color for the priority b,
 - ``pri-c``, color for the priority c


Highlight
---------

Highlights work exactly like colors, but the color name is whatever tag you
want to have colored.

If you wanted to highlight the ``due:`` tag of a task, you could define
this::

  [Highlight]
  due = 8, 0

For the GUI, use ``GUI:Highlight``. The colors can be specific as hex
values (3, or 6-digits) or named::

  [GUI:Highlight]
  due = red
  t = #4ee
  to = #03fe4b


Task Format
-----------

The task formatting is a mechanism that allows you to configure how tasks are
being displayed in pter. It uses placeholders for elements of a task that you can
order and align using a mini language similar to `Python’s format
specification
mini-language <https://docs.python.org/library/string.html#formatspec>`_, but
much less complete.

qpter uses only part of the definition, see below in the list of field
names, if you only care for qpter.

If you want to show the task’s age and description, this is your
task format::

    task-format = {age} {description}

The space between the two fields is printed! If you don’t want a space
between, this is your format::

    task-format = {age}{description}

You might want to left align the age, to make sure all task descriptions start
below each other::

    task-format = {age: <}{description}

Now the age field will be left aligned and the right side is filled with
spaces. You prefer to fill it with dots?::

    task-format = {age:.<}{description}

Right align works the same way, just with ``>``. There is currently no
centering.

Suppose you want to surround the age with brackets, then you would want to use
this::

    task-format = {[age]:.<}{description}

Even if no age is available, you will always see the ``[...]`` (the amount of
periods depends on the age of the oldest visible task; in this example some
task is at least 100 days old).

If you don’t want to show a field, if it does not exist, for example the
completion date when a task is not completed, then you must not align it::

    task-format = {[age]:.<}{completed}{description}

You can still add extra characters left or right to the field. They will not
be shown if the field is missing::

    task-format = {[age}:.<}{ completed 😃 }{description}

Now there will be an emoji next to the completion date, or none if the task has
no completion date.

All that being said, qpter uses the same ``task-format`` configuration
option to show tasks, but will disregard some fields (see below) and only
use the field names, but not alignment or decorations.


Field Names
~~~~~~~~~~~

The following fields exist:

 - ``description``, the full description text of the task
 - ``created``, the creation date (might be missing)
 - ``age``, the age of the task in days (might be missing)
 - ``completed``, the completion date (might be missing, even if the task is completed)
 - ``done``, the symbol for a completed or not completed task (see below)
 - ``pri``, the character for the priority (might not be defined)
 - ``due``, the symbol for the due status (overdue, due today, due tomorrow; might not be defined)
 - ``duedays``, in how many days a task is due (negative number when overdue tasks)
 - ``selection``, the symbol that’s shown when this task is selected in the list (disregarded in qpter)
 - ``nr``, the number of the task in the list (disregarded in qpter)
 - ``tracking``, the symbol to indicate that you started time tracking of this task (might not be there)

``description`` is potentially consuming the whole line, so you might want to
put it last in your ``task-format``.


GUI
----

The GUI specific options are defined in the ``[GUI]`` section:

  ``font``
    The name of the font to use for the task list.

  ``font-size``
    The font size to use for the task list. You can specify the size either
    in pixel (eg. ``12px``) or point size (eg. ``14pt``). Unlike pixel
    sizes, point sizes may be a non-integer number, eg. ``16.8pt``. 


Keyboard controls
=================

pter and qpter have different keyboard shortcuts.


pter
-----

These default keyboard controls are available in any list:

 - "↓", "↑" (cursor keys): select the next or previous item in the list
 - "j", "k": select the next or previous item in the list
 - "Home": go to the first item
 - "End": go the last item
 - ":": jump to a list item by number (works even if list numbers are not shown)
 - "1".."9": jump to the list item with this number
 - "Esc", "^C": cancel the selection (this does nothing in the list of tasks)

In the list of tasks, the following controls are also available:

 - "?": Show help
 - "m": open this manual in a browser
 - "e": edit the currently selected task
 - "n": create a new task
 - "/": edit the search query
 - "c": search for a context of the currently selected task
 - "p": search for a project of the currently selected task
 - "q": quit the program
 - "l": load a named search
 - "s": save the current search
 - "u": open a URL listed in the selected task
 - "t": Start/stop time tracking of the selected task
 - ">": Delegate the selected task

In edit fields the following keyboard controls are available:

 - "←", "→" (cursor keys): move the cursor one character to the left or right
 - "Home": move the cursor to the first charater
 - "End": move the cursor to the last character
 - "Backspace", "^H": delete the character to the left of the cursor
 - "Del": delete the character under the cursor
 - "^U": delete from before the cursor to the start of the line
 - "Escape", "^C": cancel editing
 - "Enter", "Return": accept input and submit changes


qpter
------

 - Quit: ``Ctrl+Q``
 - Open the manual: ``F1``
 - Focus the task list: ``F6``
 - Open and focus the named searches: ``F8``
 - Create a new task: ``Ctrl+N``
 - Edit the selected task: ``Ctrl+E``
 - Toggle 'done' state of selected task: ``Ctrl+D``
 - Toggle 'hidden' state of selected task: ``Ctrl+H``
 - Toggle 'tracking' state of selected task: ``Ctrl+T``
 - Delegate the selected task: ``Ctrl+G``


Relative dates
==============

Instead of providing full dates for searches or for ``due:`` or ``t:`` when
editing tasks, you may write things like ``due:+4d``, for example, to specify
a date in 4 days.

A relative date will be expanded into the actual date when editing a task
or when being used in a search.

The suffix ``d`` stands for days, ``w`` for weeks, ``m`` for months, ``y`` for years.
The leading ``+`` is implied when left out and if you don’t specify it, ``d`` is
assumed.

``due`` and ``t`` tags can be as simple as ``due:1`` (short for ``due:+1d``, ie.
tomorrow) or as complicated as ``due:+15y-2m+1w+3d`` (two months before the date
that is in 15 years, 1 week and 3 days).

``due`` and ``t`` also support relative weekdays. If you specify ``due:sun`` it is
understood that you mean the next Sunday. If today is Sunday, this is
equivalent to ``due:1w`` or ``due:+7d``.

Finally there are ``today`` and ``tomorrow`` as shortcuts for the current day and
the day after that, respectively. These terms exist for readability only, as
they are equivalent to ``0d`` (or even just ``0``) and ``+1d`` (or ``1d``, or even
just ``1``), respectively.


Searching
=========

One of the most important parts of pter is the search. You can search for
tasks by means of search queries. These queries can become very long at
which point you can save and restore them (see below in `Named Searches`_).

Unless configured otherwise by you, the search is case-sensitive.

Here's a detailed explanation of search queries.

Some fxample search queries are listed in `Named Searches`_.


Search for phrases
------------------

The easiest way to search is by phrase in tasks.

For example, you could search for ``read`` to find any task containing the word
``read`` or ``bread`` or ``reading``.

To filter out tasks that do *not* contain a certain phrase, you can search with
``not:word`` or, abbreviated, ``-word``.


Search for tasks that are completed
-----------------------------------

By default all tasks are shown, but you can show only tasks that are not
completed by searching for ``done:no``.

To only show tasks that you already marked as completed, you can search for
``done:yes`` instead.


Hidden tasks
------------

Even though not specified by the todotxt standard, some tools provide the
“hide” flag for tasks: ``h:1``. pytodoweb understands this, too, and by default
hides these tasks.

To show hidden tasks, search for ``hidden:yes``. Instead of searching for
``hidden:`` you can also search for ``h:`` (it’s a synonym).


Projects and Contexts
---------------------

To search for a specific project or context, just search using the
corresponding prefix, ie. ``+`` or ``@``.

For example, to search for all tasks for project "FindWaldo", you could search
for ``+FindWaldo``.

If you want to find all tasks that you filed to the context "email", search
for ``@email``.

Similar to the search for phrases, you can filter out contexts or projects by
search for ``not:@context``, ``not:+project``, or use the abbreviation ``-@context``
or ``-+project`` respectively.


Priority
--------

Searching for priority is supported in two different ways: you can either
search for all tasks of a certain priority, eg. ``pri:a`` to find all tasks of
priority ``(A)``.
Or you can search for tasks that are more important or less important than a
certain priority level.

Say you want to see all tasks that are more important than priority ``(C)``, you
could search for ``moreimportant:c``. The keyword for “less important” is
``lessimportant``.

``moreimportant`` and ``lessimportant`` can be abbreviated with ``mi`` and ``li``
respectively.


Due date
--------

Searching for due dates can be done in two ways: either by exact due date or
by defining “before” or “after”.

If you just want to know what tasks are due on 2018-08-03, you can search for
``due:2018-08-03``.

But if you want to see all tasks that have a due date set *after* 2018-08-03,
you search for ``dueafter:2018-08-03``.

Similarly you can search with ``duebefore`` for tasks with a due date before a
certain date.

``dueafter`` and ``duebefore`` can be abbreviated with ``da`` and ``db`` respectively.

If you only want to see tasks that have a due date, you can search for
``due:yes``. ``due:no`` also works if you don’t want to see any due dates.

Searching for due dates supports `Relative Dates`_.


Creation date
-------------

The search for task with a certain creation date is similar to the search
query for due date: ``created:2017-11-01``.

You can also search for tasks created before a date with ``createdbefore`` (can
be abbreviated with ``crb``) and for tasks created after a date with
``createdafter`` (or short ``cra``).

To search for tasks created in the year 2008 you could search for
``createdafter:2007-12-31 createdbefore:2009-01-01`` or short ``cra:2007-12-31
crb:2009-01-01``.

Searching for creation dates supports `Relative Dates`_.


Completion date
---------------

The search for tasks with a certain completion date is pretty much identical
to the search for tasks with a certain creation date (see above), but using
the search phrases ``completed``, ``completedbefore`` (the short version is ``cob``), or
``completedafter`` (short form is ``coa``).

Searching for completion dates supports `Relative Dates`_.


Threshold or Tickler search
---------------------------

pter understand the the non-standard suggestion to use ``t:`` tags to
indicate that a task should not be active prior to the defined date.

If you still want to see all tasks, even those with a threshold in the future,
you can search for ``threshold:`` (or, short, ``t:``). See also the
`General`_ configuration option 'default-threshold'.

You can also pretend it’s a certain date in the future (eg. 2042-02-14) and
see what tasks become available then by searching for ``threshold:2042-02-14``.

``threshold`` can be abbreviated with ``t``. ``tickler` is also a synonym for
``threshold``.

Searching for ``threshold`` supports `Relative Dates`_.


Named Searches
==============

Search queries can become very long and it would be tedious to type them
again each time.

To get around it, you can save search queries and give each one a name. The
default keyboard shortcut to save a search is "s" and to load a search is
"l".

The named queries are stored in your configuration folder in the file
``~/.config/pter/searches.txt``.

Each line in that file is one saved search query in the form ``name = search
query``.

Here are some useful example search queries::

  Due this week = done:no duebefore:mon
  Done today = done:yes completed:0
  Open tasks = done:no


Time Tracking
=============

pter can track the time you spend on a task. By default, type "t" to
start tracking. This will add a ``tracking:`` attribute with the current local
date and time to the task.

When you select that task again and type "t", the ``tracking:`` tag will be
removed and the time spent will be saved in the tag ``spent:`` as hours and
minutes.

If you start and stop tracking multiple times, the time in ``spent:`` will
accumulate accordingly. The smallest amount of time tracked is one minute.

This feature is non-standard for todo.txt but compatible with every other
implementation.


Delegating Tasks
================

The ``delegate`` function (on shortcut ``>`` (pter) or ``Ctrl+G`` (qpter)
by default) can be used to mark a task as delegated and trigger the
delegation action.

When delegating a task the configured marker is being added to the task
(configured by ``delegation-marker`` in the configuration file).

The delegation action is configured by setting the ``delegation-action`` in
the configuration file to ``mail-to``. In that case an attempt is made to
open your email program and start a new email. In case you defined a
``to:`` (configurable by defining ``delegation-to``) in your task
description, that will be used as the recipient for the email.


Getting Things Done
===================

With pter you can apply the Getting Things Done method to a single todo.txt
file by using context and project tags, avoiding multiple lists.

For example, you could have a ``@in`` context for the list of all tasks
that are new. Now you can just search for ``@in`` (and save it as a named search) to find all new tasks.

To see all tasks that are on your "Next task" list, a good start is to
search for "``done:no not:@in``" (and save this search query, too).


Conforming to
=============

pter works with and uses the todo.txt file format and strictly adheres to the format
as described at http://todotxt.org/.


Bugs
====

Probably plenty. Please report your findings at https://github.com/vonshednob/pter or via email to the authors.


