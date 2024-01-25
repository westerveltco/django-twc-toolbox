# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project attempts to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## [version]
### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security
-->
## [Unreleased]

## [0.2.1]

### Fixed

- `DatePage.min_date` and `DatePage.max_date` now return the correct dates for the page. `DatePage.min_date` returns the oldest date and `DatePage.max_date` returns the newest date.
- `DatePage.date_range` now returns the correct range of dates for the page.

## [0.2.0]

### Added

- `DatePaginator` and `DatePage` classes, extending Django's built-in `Paginator` and `Page` classes, respectively. These new classes enable pagination based on a specified date field, making it easier to work with date-based data. Useful for applications that require handling of time-series data or chronological records, such as a blog or an event archive.

## [0.1.1]

Initial release!

### Added

- Initial documentation.
- Initial tests.
- Initial CI/CD (GitHub Actions).
- A `TimeStamped` abstract model for adding `created_at` and `updated_at` fields to models.

### New Contributors

- Josh Thomas <josh@joshthomas.dev> (maintainer)

[unreleased]: https://github.com/westerveltco/django-twc-toolbox/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/westerveltco/django-email-toolbox/releases/tag/v0.2.1
[0.2.0]: https://github.com/westerveltco/django-email-toolbox/releases/tag/v0.2.0
[0.1.1]: https://github.com/westerveltco/django-email-toolbox/releases/tag/v0.1.1
