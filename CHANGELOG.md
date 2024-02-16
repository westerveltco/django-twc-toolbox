# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project attempts to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## [${version}]
### Added - for new features
### Changed - for changes in existing functionality
### Deprecated - for soon-to-be removed features
### Removed - for now removed features
### Fixed - for any bug fixes
### Security - in case of vulnerabilities
[${version}]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v${version}
-->

## [Unreleased]

## [0.3.0]

### Added

- Added the `page_date_range` argument to the `DatePaginator`, taking the place of the existing `date_range` argument. This change clarifies that it represents constraining the range of dates for each page, not the entire range of dates for the paginator.

### Changed

- Updated the `DatePaginator` class to use the `page_date_range` argument instead of the deprecated `date_range` argument.
- `DatePage.min_date`, `DatePage.max_date`, and `DatePage.date_range` are now `cached_property` attributes instead of being set in the `__init__` method.
- Now using [`django-twc-package`](https://github.com/westerveltco/django-twc-package) template for repository and package structure.

### Deprecated

- The `date_range` argument of the `DatePaginator` class is now deprecated. It will be removed in version 0.4.0.

### Removed

- Removed the `orphans` kwarg from `DatePaginator`, which is inherited from Django's built-in `Paginator`. Given its date range-based pagination, the concept of orphans, applicable to item count per page, is not super useful. If it is passed in, a warning will be issued.

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

[unreleased]: https://github.com/westerveltco/django-twc-toolbox.git/compare/v0.3.0...HEAD
[0.2.1]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.2.1
[0.2.0]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.2.0
[0.1.1]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.1.1

[0.3.0]: https://github.com/westerveltco/django-twc-toolbox.git/releases/tag/v0.3.0
