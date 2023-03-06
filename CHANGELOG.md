# Changelog

This file contains the changes made between released versions.

The format is based on [Keep a changelog](https://keepachangelog.com/) and the versioning tries to follow
[Semantic Versioning](https://semver.org).


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

