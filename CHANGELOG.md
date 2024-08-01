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

## [0.14.0]

### Added

- Added `format_number_no_round` function to handle formatting of numbers with a specified number of decimal places while trimming excess trailing zeros or adding zeros as needed.
- Support for Python 3.13.

### Changed

- Bumped `django-twc-package` template version to v2024.24.

## [0.13.0]

### Added

- Added a `{% startswith %}` utility templatetag filter.
- Added a generic type argument to `DatePaginator`.

### Changed

- `date_page_range` is now explicitly a required argument to `DatePaginator`. Previously, it was allowed to be `None`, but would still fail if `date_range` was not passed in instead. `date_range` has been removed as an argument, see below.
- Types within `DatePaginator` have been adjusted.

### Removed

- Removed the `date_range` argument from `DatePaginator`, a few versions past when I meant to.

## [0.12.1]

### Fixed

- Fixed a bug in `CRUDView.get_context_data` if the role had no specific context data method defined.

## [0.12.0]

### Added

- Introduced dynamic role-based context data in `CRUDView` with new `get_role_context_data` method through role-specific context methods (e.g., `get_create_context_data`) to add custom context data scoped only to that role.

### Changed

- `get_context_data` now incorporates role-specific context data by calling `get_role_context_data`.

## [0.11.0]

### Added

- Added support for specifying primary filters on `CRUDView` via a `filterset_primary_fields` class attribute. Sometimes you have a model and corresponding crud view that has a bunch of filters attached to it. Rather than show all filters or show none and hide them behind a 'Show Filters' button, this allows you to have a handful of primary filters with the rest of the filters set as secondary. This way, you can always show the primary filters, but hide the secondary ones.
- Added an extra method (`is_active()`) and property (`active_filters`) to the `FilterSet` returned by `CRUDView.get_filterset` related to the active filters set on the view in the current request.

### Changed

- Added override of `get_paginate_by` to `CRUDView` in order to accept arbitrary `args` and `kwargs`. This is due to the differences in the method between `neapolitan.views.CRUDView` and `django_tables2.views.SingleTableMixin`. By making this change, it simplifies the code path in the `CRUDView.list` method a tiny bit.

## [0.10.0]

### Added

- Added `django_twc_toolbox.urls.reverse` and `django_twc_toolbox.urls.reverse_lazy` which take Django's built-in `reverse` and adds the ability to urlencode query parameters and fragments.

## [0.9.3]

### Fixed

- Fixed pagination and ordering of `CRUDView.object_list` when a `table_class` is provided.

## [0.9.2]

### Fixed

- Corrected check for HTMX request (again!).

## [0.9.1]

### Fixed

- Corrected check in `django_twc_toolbox.crud.CRUDView.get_template_names` for if an `HttpRequest` is an HTMX request or not.

## [0.9.0]

### Added

- Two new templatetag filters: `{{ variable|klass }}` and `{{ variable|class_name }}`.
- Support for using django-tables2 with `django_twc_toolbox.crud.CRUDView`. The view now has the option to set `table_class` and `table_data` class attributes that will render the table on the list page using django-tables2.
- Support for template partials in `django_twc_toolbox.crud.CRUDView`, using django-template-partials.

### Fixed

- Functions in `django_twc_toolbox.sentry` now correctly type hinted.

## [0.8.0]

### Added

- Added `django_twc_toolbox.crud` app. Previously, we were maintaining a fork with a handful of customizations on top. The maintenance burden of keeping our fork updated with upstream has proven to be too much of a time commitment, so we are moving what little we have overridden here.
  - Includes a `CRUDView` that inherits from `neapolitan.views.CRUDView` with a few extra urls thrown in the template context, as well as the ability to specify different fields for the list and detail views.
  - `neapolitan.templatetags.neapolitan` is being shadowed allowing both `{% object_detail %}` and `{% object_list %}` to use our `CRUDView`'s ability to use different fields (as mentioned above), as well as return the string version of any related `Model`. (`neapolitan` itself returns a `Model` instance's primary key.) Additionally, the action links for the list view are a dictionary instead of a rendered string.
- Added a handful of core views: 404 and 500 error handling views and `robots.txt` and `.well-known/security.txt` views.

### Removed

- Removed support for Python 3.8 and 3.9.

## [0.7.0]

### Added

- Added `list_templates` management command, inspired by [this post](https://noumenal.es/notes/tailwind/django-integration/) from Carlton Gibson ([@carltongibson](https://github.com/carltongibson)).
- Added `copy_template` management command, taken from [this project](https://github.com/softwarecrafts/django-cptemplate) by Andrew Miller ([@nanorepublica](https://github.com/nanorepublica)).
- Added `ruff` to dev dependency extras.
- Added Sentry trace and profile sampling functionality with configurable discard rules for specific HTTP methods and paths.

## [0.6.0]

### Added

- Added read only versions of `admin.StackedInline` and `admin.TabularInline`.

## [0.5.0]

### Added

- Added a `WithHistory` abstract model for integrating `django-simple-history` `HistoricalRecords`.
- Added custom `createsuperuser` management command to allow for resetting an existing superuser's password in development when `DEBUG=True`.

## [0.4.0]

### Added

- Added a `CuidField` and extra dependencies needed to use it. Install the package with `django-twc-toolbox[cuid]` in order to use it.

### Removed

- Dropped support for Django 3.2 (EOL April 2024).

## [0.3.1]

### Added

- `py.typed` added to the project.

### Changed

- Now using v2024.27 of `django-twc-package`.

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

[unreleased]: https://github.com/westerveltco/django-twc-toolbox/compare/v0.14.0...HEAD
[0.2.1]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.2.1
[0.2.0]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.2.0
[0.1.1]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.1.1
[0.3.0]: https://github.com/westerveltco/django-twc-toolbox.git/releases/tag/v0.3.0
[0.3.1]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.3.1
[0.4.0]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.4.0
[0.5.0]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.5.0
[0.6.0]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.6.0
[0.7.0]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.7.0
[0.8.0]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.8.0
[0.9.0]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.9.0
[0.9.1]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.9.1
[0.9.2]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.9.2
[0.9.3]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.9.3
[0.10.0]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.10.0
[0.11.0]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.11.0
[0.12.0]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.12.0
[0.12.1]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.12.1
[0.13.0]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.13.0
[0.14.0]: https://github.com/westerveltco/django-twc-toolbox/releases/tag/v0.14.0
