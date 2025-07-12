# Changelog

This file contains the changes made between released versions.

The format is based on [Keep a changelog](https://keepachangelog.com/) and the versioning tries to follow
[Semantic Versioning](https://semver.org).


## 3.21.0
### Added
- You can define a separate color for displaying tasks that have been completed using the `completed` and `sel-completed` color names ([#71](https://github.com/vonshednob/pter/issues/71))

### Fixed
- when a `selection` symbol is provided in `Symbols`, it should be used in every list ([#71](https://github.com/vonshednob/pter/issues/71), thanks)

## 3.20.1
### Fixed
- pter no longer crashes when colors are defined with only one value ([#44](https://codeberg.org/vonshednob/pter/issues/44), thanks simonz!)


## 3.20.0
### Added
- Support for `-`/`+2b` as a relative date description to ensure the resulting date ends on a business day (thanks to [joeac](https://codeberg.org/joeac))
- Introduced `business-days` configuration option ([#39](https://codeberg.org/vonshednob/pter/issues/39))


## 3.19.2
### Fixed
- `qpter` would not start at all ([#37](https://codeberg.org/vonshednob/pter/issues/37))


## 3.19.1
### Changed
- Drop the `enum.StrEnum` dependency to stay with Python 3.10 dependency ([#33](https://codeberg.org/vonshednob/pter/issues/33))


## 3.19.0
### Added
- `note`, `projects`, `contexts`, `linenr`, and `spent` added as possible fields for `task-format` ([#69](https://github.com/vonshednob/pter/issues/69))
- `completed_date` is a possible field for `sort:` and the `sort-order` configuration option ([#33](https://codeberg.org/vonshednob/pter/issues/33))
- `due_in` and `duedays` mean the same thing and are both possible fields in `sort:` and the `sort-order` configuration option
- `prio` and `priority` mean the same thing and are both possible fields in `sort:` and the `sort-order` configuration option
- `archive-origin-marker` and `archive-origin-is` options to include the
  origin todo.txt file of a task when archiving it ([#64](https://github.com/vonshednob/pter/issues/64))

### Fixed
- Install the man-pages ([#32](https://codeberg.org/vonshednob/pter/issues/32))


## 3.18.0
### Changed
- Full switch over to `pyproject.toml`
- Requires `pytodotxt` version 2.0.0

### Added
- Support for tasks with `t:` and `due:` with full ISO dates (e.g. `2024-06-21T15:10`; issue [#31](https://codeberg.org/vonshednob/pter/issues/31))
- `duplicate-task` function, by default on `v` and not supported in qpter ([#30](https://codeberg.org/vonshednob/pter/issues/30))


## 3.17.1
### Fixed
- When guessing the location of notes, the path of the first todo files should be taken, not the file itself ([#68](https://github.com/vonshednob/pter/issues/68))

## 3.17.0
### Added
- `done-is` and `done-file` configuration options to allow moving completed
  tasks into a separate file ([#26](https://codeberg.org/vonshednob/pter/issues/26))

## 3.16.3
### Fixed
- `qpter`'s smart search was broken ([#67](https://github.com/vonshednob/pter/issues/67))

## 3.16.2
### Fixed
- Installation via `pipx` was broken when trying to use `qpter`

## 3.16.1
### Fixed
- hooks were broken if a task contained a note ([#25](https://codeberg.org/vonshednob/pter/issues/25))

### Changed
- if no `notes` setting was set up in the configuration, the paths of the used todo.txt files are used as note folders

## 3.16.0
### Changed
- Welcome message shows the version, so you know what you're up against ([#40](https://github.com/vonshednob/pter/issues/40)), thanks andrei-a-papou!)
- The dialog boxes to select things (context, project, link) attempt to not cut off their title
- Searching for `due:` behaves the same way as `due:y`, `due:yes`, and `due:any`: any task with a due date is found
- Searching for `hidden:1` will *only* show hidden tasks, use `hidden:any` to show all tasks including hidden ones
- Searching for `hidden:` will find all tasks that have a `h:` attribute
- Default time-out for the Esc-key is now 200 ms
- Help bar at the bottom will show preferably the user-defined key bindings

### Fixed
- `#`, `[`, and `]` can also be used in key bindings, using `<hash>`, `<lbrack>`, and `<rbrack>` respectively ([#33](https://github.com/vonshednob/pter/issues/33))
- Archiving and task deletion was broken and could crash pter ([#43](https://github.com/vonshednob/pter/issues/43))
- Highlighting in dialog boxes to select things (context, project, link) is covering the whole line now (thanks, andrei-a-papou)
- Sections in the help screen that would be empty because no keybindings have been defined, are no longer shown (thanks, andrei-a-papou)
- Standalone `+` or `@` are no longer listed in their respective completions ([#46](https://github.com/vonshednob/pter/issues/46))
- Mouse wheel scrolling would in some cases cause scrolling, making it look like there was any mouse support. Mouse wheel scrolling should now do nothing. ([#51](https://github.com/vonshednob/pter/issues/51))
- Key sequences work in the help screen, too ([#59](https://github.com/vonshednob/pter/issues/59))
- Scrolling with cursor keys in the help screen are no longer "lagging"
- `quit` removed from the help screen; that means to close the help screen, use `cancel`

### Added
- `inc-due`, `dec-due` functions to increase/decrease due dates by `due-delta` (`1d` by default) or quickly add a due date if there is none, [#48](https://github.com/vonshednob/pter/issues/48)
- `due-skip-weekend` option to skip over weekends when increasing/decreasing a due date
- `clear-due` function to remove due date
- `reduce-distraction` option to hide the task list when editing/creating tasks
- `{{note}}` makes the `note:` attribute of a task available to hooks
- Added `go-word-left`, `go-word-right`, `del-to-eol`, `del-word-left`, and `del-word-right` ([#36](https://github.com/vonshednob/pter/issues/36), thanks andrei-a-papou)
- pter has the commandline parameter `--list-keys` (or short, `-k`) to list all key bindings
- Added search term `due:any` to be more explicit about finding tasks that have any due date
- Added search term `done:any` for consistency
- Added search term `hidden:any`, to find all tasks, even hidden ones
- Added search terms `t:any`, `t:yes`, and `t:no`
- Configuration option `esc-timeout` in the `[General]` section
- `view-note` command, by default on `V` to view a note instead of editing it
- Configure the note viewer with the ``viewer`` option
- `word-boundaries` option in `[General]` section for use with `go-word-` and `del-word-` functions
- `help-action` option to configure the items in the help bar at the bottom of the screen
- `{file}` field in `task-format`
- `reset-terminal` configuration option ([#51](https://github.com/vonshednob/pter/issues/51), thanks, andrei-a-papou!)


## 3.15.2
### Fixed
- Could not change list control key bindings ([#35](https://github.com/vonshednob/pter/issues/35))

### Added
- Support for `F13` through `F20` ([#39](https://github.com/vonshednob/pter/issues/39), thanks to andrei-a-papou!)


## 3.15.1
### Fixed
- Scrolling was broken ([#37](https://github.com/vonshednob/pter/issues/37)), thanks to onovy for fixing it!
- It wasn't possible to change the keybindings of text field editor keys ([#35](https://github.com/vonshednob/pter/issues/35))


## 3.15.0
### Fixed
- The `[Editor:Keys]` section in the configuration file was completely ignored ([#35](https://github.com/vonshednob/pter/issues/35))
- It was not possible to (re-)bind the keys `:` or `=` to any function ([#33](https://github.com/vonshednob/pter/issues/33))

### Added
- You can tell pter to call external programs when certain things happen in the program. The term in the documentation is 'hooks'. ([#23](https://codeberg.org/vonshednob/pter/issues/23))


## 3.14.0
### Added
- `sort-order` option (thanks a lot to onovy)
- shortcut to set a task to priority `D` (thanks a lot to onovy)

### Fixed
- auto suggestions for `note:` did not list files from all folders


## 3.13.0
### Added
- `time-tracking` configuration option to integrate with external time tracking programs

## 3.12.0
### Added
- Sorting by task creation date with `created`
- `search-case-sensitive` can now be `yes`, `no`, or `smart` (assume case-insensitive, but switch to case-sensitive if you search with an uppercase character, [#15](https://codeberg.org/vonshednob/pter/issues/15))
- New feature: auto templates. Apply a template when a new task contains trigger words ([#16](https://codeberg.org/vonshednob/pter/issues/16))

### Fixed
- `pter.config` man page is installed in the correct place

## 3.11.4
### Fixed
- Installer script didn't actually install the man-pages

## 3.11.3
### Changed
- Documentation split up in three different manpages, `pter(1)`, `qpter(1)`, `pter.config(5)`.

## 3.11.2
### Fixed
- Copy to clipboard actually copies to clipboard (not primary or secondary) in X11 now

## 3.11.1
### Added
- Feedback to the user when copying tasks to clipboard

## 3.11.0
### Fixed
- pter would crash when you cancel saving a template
- qpter would not start at all ([#31](https://github.com/vonshednob/pter/issues/31))

### Added
- `Y` calls the `to-clipboard` function that copies the selected task to your clipboard (in pter) ([#32](https://github.com/vonshednob/pter/issues/32))
- ``Ctrl+C`` calls the ``to-clipboard`` function that copies the selected task to your clipboard (in qpter) ([#32](https://github.com/vonshednob/pter/issues/32))

## 3.10.1
### Fixed
- `-u` would report that a new version is available if the version file contained a newline
- Control characters in a task's description (e.g. `\x10`) could crash pter. They are now replaced with a space character during display and edit
- Documentation wasn't very clear about how colors are prioritised/used when displaying items

## 3.10.0
### Changed
- `[Include]` section in configuration file is now deprecated

### Added
- `includes` option in `General` section of the configuration file. This is the preferred way to include additional configuration files.

### Fixed
- `files` option was buggy when only one file was given
- Fix the python 3.12 warnings ([#30](https://github.com/vonshednob/pter/issues/30))


## 3.9.0
### Added
- `files` option in `General` section. These files will be opened if you don't provide files on the commandline.
- Support for detailed notes per task via the `note:` tag

### Fixed
- Desktop file `pter.desktop` can now actually work (due to `files` option in `General`, see above)


## 3.8.0
### Added
- Archiving is now a thing. Default key binding for `archive` function is `%`
- Archive location can be configured, see `archive-is` configuration option
- New function `edit-file-external`, by default not mapped to a key

### Fixed
- Trash file access is more forgiving and won't crash pter


## 3.7.0
### Changed
- When using templates, the initial cursor position will be after the creation date or at the start of the field

### Added
- When editing a task you can `Tab` through not-filled in keys, like `due:`


## 3.6.1
### Fixed
- When scrolling past the end of list of tasks pter could crash (related to key sequences)


## 3.6.0
### Added
- Support for key sequences for some functions ([#3](https://codeberg.org/vonshednob/pter/issues/3))
- `show-related` functionality (comes with `related-show-self` configuration option; [#2](https://codeberg.org/vonshednob/pter/issues/2))

### Fixed
- Fixed some typos and ambiguities in the documentation


## 3.5.0
### Added
- New function `clear-search`, which is bound to `^` by default ([#27](https://github.com/vonshednob/pter/issues/27))
- New functions `select-project` (`F6`) and `select-context` (`F7`) (thanks to [lrustand](https://github.com/lrustand); fixes [#27](https://github.com/vonshednob/pter/issues/27))

### Changed
- Completion now will only show contexts or projects that actually start with what you've typed already


## 3.4.1
### Fixed
- Deleting tasks was broken (thank you for fixing it, [Fabian-G](https://codeberg.org/Fabian-G)!)
- Prevent creation of empty tasks (again, thanks to [Fabian-G](https://codeberg.org/Fabian-G))
- Fixed startup bug when there were empty task lines (once more, thank you [Fabian-G](https://codeberg.org/Fabian-G))


## 3.4.0
### Changed
- Priorities are now supported in the full specified range of todo.txt, i.e. from `A` through `Z` (thanks to Gerrit)


## 3.3.2
### Fixed
- `editor` configuration option now works with editors that require additional parameters, like `editor = code -r -w`

## 3.3.1
### Fixed
- Cancelling to save a search crashed pter


## 3.3.0
### Fixed
- Wrap of day would not update tasks with `t:` that should become visible ([#14](https://github.com/vonshednob/pter/issues/14))
- Type confusion could crash qpter

### Added
- Functions (and shortcuts in terminal version) to change the priority of a task directly ([#16](https://github.com/vonshednob/pter/issues/16))


## 3.2.0
### Added
- `-s` parameter to start pter with a named search from the start

## 3.1.4
### Fixed
- pter crashed when newly installed because of the non-existing log directory

## 3.1.3
### Fixed
- Bad implementation of `Application.refresh` could cause black screens with newer versions of cursedspace


## 3.1.2
### Changed
- Refer mostly to vonshednob.cc instead of github.com

### Fixed
- Close the completion when the cursor leaves the word that the completion was started for
- Check latest version by querying vonshednob.cc/pter/latest


## 3.1.1
### Added
- Support for `not:pri:`, which was kind-of implied in the documentation, but not really implemented yet
- Support for relative dates in searches for `due:` (and before/after), `created:` (and before/after), and `completed:` (and before/after), which was already promised in the documentation but didn't fully work (and when it did, it was horribly inefficient)

### Fixed
- Implementation for `lessimportant:` and `moreimportant:` was broken ([#13](https://github.com/vonshednob/pter/issues/13))


## 3.1.0
### Added
- Support for recurring tasks ([#12](https://github.com/vonshednob/pter/issues/12))

### Fixed
- Potential crash when the todo.txt changed in the background at a bad time
- Various previously overlooked remnants from the refactoring


## 3.0.0
### Added
- `delete-task` function controlled by `delete-is` configuration option, disabled by default to prevent accidental deletions ([#9](https://github.com/vonshednob/pter/issues/9))

### Fixed
- The configuration file’s keys are now case-sensitive (as documented before, but not implemented accordingly). This might break your existing configuration file, especially with respect to keybindings.


## 2.2.1
### Fixed
- The search bar would not show '(no search active)' when starting pter

### Changed
- Depend on version 1.3.0 of cursedspace


## 2.2.0
### Fixed
- Completion could leave some lines on the screen after being closed ([#8](https://github.com/vonshednob/pter/issues/8))
- Selection boxes are using as much room as necessary to show all options
- Help screen scrolls immediately when cursor keys are used

### Added
- Completion key configuration options `comp-next`, `comp-prev`, `comp-use`, and `comp-close`
- Documentation for the completion options


## 2.1.0
### Added
- Basic autocompletion support for contexts and projects when searching, adding or editing tasks ([#6](https://github.com/vonshednob/pter/issues/7))

### Changed
- Depends on version 1.2.0 of cursedspace

### Fixed
- Lagging cursor when editing or creating a task ([#7](https://github.com/vonshednob/pter/issues/7))
- Make selector windows great(er) again
- Don't show the source selector if only one source file is available


## 2.0.0
### Changed
- Massive refactoring of pter to make the code more readable and maintainable
- pter will try to set the terminal title to `pter`

### Added
- Dependency to `cursedspace`
- Key bindings `page-up` and `page-down`
- Support to edit tasks through an external text editor ([#5](https://github.com/vonshednob/pter/issues/5)), see `editor` configuration option or just try `E` in pter; not supported in qpter!

### Removed
- Key bindings `half-page-up` and `half-page-down`


## 1.0.19
### Fixed
- A task that had no description used to crash pter when searching #54

## 1.0.18
### Added
- Task templates (thanks to [@danielk333](https://github.com/danielk333))

## 1.0.17
### Fixed
- Clearing a search that resulted in 0 visible tasks would crash pter
- Be consistent and accept relative paths as well as the `~/` (user home) notion

## 1.0.16
### Added
- Detect the passing of midnight
- Commandline parameter "-n" to add a task directly

### Changed
- Every 5 seconds check for changes to the source files

### Fixed
- When stopping tracking before a minute has passed, pter used to not stop tracking
- Even when the filter would result in 0 tasks showing, at least one would still remain visible

## 1.0.15
### Fixed
- Repainting used to cause some flickering and was rather slow

### Changed
- The marker for the currently selected task is stretching over the full width
  of the window

## 1.0.14
### Added
- Support including extra configuration files (issue [#53](https://git.spacepanda.se/bold-kitty/pter/issues/53))
- Man page, .desktop files, and an example configuration are installed with `pip install`

## 1.0.13
### Fixed
- Fixed exception when the terminal resizes around pter (issue [#52](https://git.spacepande.se/bold-kitty/pter/issues/52))
- `clear-contexts` is now working again (regression error)

## 1.0.12
### Fixed
- Regression regarding sorting (related to [#51](https://git.spacepanda.se/bold-kitty/pter/issues/51))

## 1.0.11
### Fixed
- Sorting did not work correctly in pter (issue [#51](https://git.spacepanda.se/bold-kitty/pter/issues/51))

## 1.0.10
### Added
- `daily-reload` option added to qpter (issue [#49](https://git.spacepanda.se/bold-kitty/pter/issues/49))
- `sort:` expression for (saved) searches (issue [#50](https://git.spacepanda.se/bold-kitty/pter/issues/50))

### Fixed
- Vertically center tasks in qpter

## 1.0.9
### Added
- Search for `file:`

## 1.0.8
### Fixed
- qpter now detects stale lock files
- Use the application default font if none is given
- Create configuration folder if it's missing (fixes a crash)
- Tasks with due date were not sorted correctly
- qpter would not show proper spacing between words when no font was configured

### Added
- Support for dark mode

## 1.0.7
### Added
- qpter can be run with -a/--add-task to activate the running qpter and create
  a new task
- -v/--version command line option to show pter's version
- -u/--check-for-updates command line option to check at pypi whether a new
  software version is available
- Support for `id:` attributes (automatic ID creation with `id:#auto`)
- `auto-id` configuration option
- Support for `after:` attribute (`hide-sequential` configuration option)
- Optionally clickable URLs, contexts, and projects (`clickable`)
- Optionally allow multiple instances of qpter (option `single-instance`)
- Support for `ref:` searches
- "New related task" and "New subsequent task" in qpter

### Fixed
- Coloring for due today/tomorrow and overdue corrected
- Don't color as overdue when task is completed
- Color also the checkmark in the 'done' color
- Refreshing task list in qpter was shaky


## 1.0.6
### Fixed
- Sometimes the task list would not update when adding a task
- Added documentation and icons to the distribution files
- Search is correct upon startup

### Added
- qpter detects file changes and reloads automatically


## 1.0.5
### Added
- font and font-size configuration option for the GUI
- About dialog in qpter
- .desktop files added to the extras directory
- Select file to create tasks in (in pter)

### Fixed
- Use .cache location for settings of pter
- pter and qpter used to highlight single `+` and `@` characters

### Changed
- curses is now optional (necessary on Windows)
- qpter does not show the list of files if there is only one file available


## 1.0.4
### Added
- Default colors for project and context in qpter

### Changed
- qpter is always installed, but will not start without PyQt5

### Fixed
- Bugfix: Starting qpter for the first time fails with ValueError exception
- Bugfix: Mixed up GUI:Highlight and GUI:Colors


## 1.0.3
### Changed
- Depend on pytodotxt 1.0.3

### Added
- Configurable protocols for URLs to open with 'u'
- Configuration option "add-creation-date", whether date should be added automatically to a task upon creation
- GUI version using Qt5
- GUI:Colors configuration group
- GUI:Highlight configuration group
- add-creation-date configuration option in General


## 1.0.2
### Added
- Delegate functionality

### Bugfix
- Fixed a crash when a task consists only of a date (issue [#25](https://git.spacepanda.se/bold-kitty/pter/issues/25))


## 1.0.1
### Added
- `clear-contexts` configuration option
- New `search-project` and `search-context` functions on keys `p` and `c` respectively

### Fixed
- Editing a task after marking it as done, keeps it marked as done ([#24](https://git.spacepanda.se/bold-kitty/pter/issues/24))


## 1.0.0
### Added
- Read the manual in a browser (`open-manual` function and `m` shortcut)
- Have a HTML manual (and generate a man-page while at it)
- `duedays` field in `task-format`
- Configurable `task-format`
- Color `pri:` tags just like priorities
- Human-friendly dates

### Removed
- `show-numbers` configuration option is gone (replaced by `task-format`)

### Breaking
- Named searches are stored in `searches.txt`, not `searches.cfg`


## 0.2.0
Split off into its own project called `pter`.


## 0.1.10
### Added
- Open URL of tasks
- Editor keys are configurable
- Allow multiple todo.txt files
- Task time tracking
- Configure symbols for text field overflow
- Search with relative dates
- Case-sensitive search behaviour is optional
- Accept unicode characters in input fields
- Custom coloring of key:value attributes


## 0.1.9
### Added
- Safe save behaviour is now configurable in pytodoterm
- Load Search and Save Search is shown in the help in pytodoterm
- Searching for relative dates in pytodoterm


## 0.1.8
### Fixed
- Handle backspace in xterm-like terminals (pytodoterm)
- Show an empty task list if the no tasks match the search query (pytodoterm)


## 0.1.7
### Fixed
- Flicker prevention (pytodoterm)


## 0.1.6
### Added
- New GUI for terminals: pytodoterm

