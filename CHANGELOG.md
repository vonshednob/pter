# Changelog

This file contains the changes made between released versions.

The format is based on [Keep a changelog](https://keepachangelog.com/) and the versioning tries to follow
[Semantic Versioning](https://semver.org).

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

