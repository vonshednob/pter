# Changelog

This file contains the changes made between released versions.

The format is based on [Keep a changelog](https://keepachangelog.com/) and the versioning tries to follow
[Semantic Versioning](https://semver.org).

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

