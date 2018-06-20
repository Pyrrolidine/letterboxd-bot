# Changelog

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [1.4.2](https://gitlab.com/Porkepik/PublicLetterboxdDiscordBot/compare/v1.4.1...v1.4.2) - 2018-06-19
### Fixed
- TV shows and miniseries present on Letterboxd can now be searched with the film command.

## [1.4.1](https://gitlab.com/Porkepik/PublicLetterboxdDiscordBot/compare/v1.4.0...v1.4.1) - 2018-06-16
### Fixed
- Fix film year filter inaccurately returning a film not matching the year when the correct year was specified for another film. (Example: !f planet of the apes (2001) returned the original and not the 2001 remake)

## [1.4.0](https://gitlab.com/Porkepik/PublicLetterboxdDiscordBot/compare/v1.3.2...v1.4.0) - 2018-06-10
### Added
- Add link to the MKDb page of the film.

### Changed
- New !checklb as an embed.

### Fixed
- Fix review links on phone Discord apps.

## [1.3.2](https://gitlab.com/Porkepik/PublicLetterboxdDiscordBot/compare/v1.3.1...v1.3.2) - 2018-06-07
### Fixed
- Fix film search using a backslash.

## [1.3.1](https://gitlab.com/Porkepik/PublicLetterboxdDiscordBot/compare/v1.3.0...v1.3.1) - 2018-06-06
### Fixed
- Fix !film crash when a film had no ratings on MKDb.

## [1.3.0](https://gitlab.com/Porkepik/PublicLetterboxdDiscordBot/compare/v1.2.0...v1.3.0) - 2018-06-06
### Added
- eiga.me (MKDb) implementation to display community average ratings, exclusive to one server.

## [1.2.0](https://gitlab.com/Porkepik/PublicLetterboxdDiscordBot/compare/v1.1.0...v1.2.0) - 2018-06-05
### Added
- If the bot was slow to respond (>5s), a warning is displayed.
- The activity status now displays the version.

## [1.1.0](https://gitlab.com/Porkepik/PublicLetterboxdDiscordBot/compare/v1...v1.1.0) - 2018-06-04
### Added
- Emojis for visual cues on website status with !checklb.

### Changed
- New !helplb as an embed.

### Fixed
- Fix film search using a slash.
- Fix film search ending with a dot.

## 1.0.0 - 2018-05-25
- Stable release after a month of development.
