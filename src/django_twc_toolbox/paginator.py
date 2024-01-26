from __future__ import annotations

import datetime
import warnings
from typing import TYPE_CHECKING

from django.core.paginator import Page
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.utils.functional import cached_property

if TYPE_CHECKING:
    from typing import Any

    from django.core.paginator import _SupportsPagination


class DatePaginator(Paginator):
    def __init__(
        self,
        object_list: _SupportsPagination,
        date_field: str,
        page_date_range: datetime.timedelta | None = None,
        date_range: datetime.timedelta | None = None,
        **kwargs,
    ) -> None:
        self.date_field = date_field

        if date_range and not page_date_range:
            self._warn_about_date_range_deprecation()
            page_date_range = date_range
        elif not page_date_range:
            raise ValueError("The `page_date_range` argument is required.")

        self.page_date_range = page_date_range

        if kwargs.get("orphans", None):
            warnings.warn(
                "The `orphans` parameter is not applicable for DatePaginator and "
                "will be ignored.",
                UserWarning,
                stacklevel=2,
            )

        super().__init__(
            object_list,
            1,  # per_page is 1 as we paginate by date
            **kwargs,
        )

    @cached_property
    def date_range(self) -> datetime.timedelta:
        self._warn_about_date_range_deprecation()
        return self.page_date_range

    def _warn_about_date_range_deprecation(self):
        warnings.warn(
            "The `date_range` argument is deprecated in favor of `page_date_range` "
            "and will be removed in v0.4.0.",
            DeprecationWarning,
            stacklevel=2,
        )

    @cached_property
    def date_segments(self) -> list[tuple[datetime.datetime, datetime.datetime]]:
        # Check if the object_list is empty.
        # Check for `exists()` first for performance, falling back in case it's
        # not a QuerySet.
        if isinstance(self.object_list, QuerySet):  # type: ignore[misc]
            if not self.object_list.exists():
                return []
        elif not self.object_list:
            return []

        if isinstance(self.object_list, QuerySet):  # type: ignore[misc]
            first_obj = self.object_list.first()
            last_obj = self.object_list.last()
        else:
            first_obj = self.object_list[0]
            last_obj = self.object_list[-1]

        first_date = getattr(first_obj, self.date_field)
        last_date = getattr(last_obj, self.date_field)

        segments = []
        current_start_date = first_date
        if self.chronological:
            # if chronological, we are moving forward in time through the `object_list`
            # so any time we need to get the next segment's end date, we need to
            # add the date_range. to start we add the date_range to the first date.
            # basically any time we need to get the next segment or move the date
            # goalpost, we use addition
            current_end_date = first_date + self.page_date_range
            # less than or equal because we are moving forwards in time and dates
            # in the future are greater than dates in the past
            # yesterday < today < tomorrow
            while current_end_date <= last_date:
                segments.append((current_start_date, current_end_date))
                current_start_date = current_end_date
                # add because we are moving forwards in time
                current_end_date += self.page_date_range
            # Append the last segment to cover any remaining dates not included in the
            # previous segments. This is necessary because the date range defined by
            # `date_range` might not perfectly divide the total span of dates. This final
            # segment captures any dates from the end of the last segment up to and
            # including `last_date`. We add one day to `last_date` to ensure the entire
            # day is covered.
            segments.append(
                (current_start_date, last_date + datetime.timedelta(days=1))
            )
        else:
            # if not chronological, it means we are moving backwards in time through
            # the `object_list` so this time we subtract the date_range to get the
            # next segment's end date. to start we subtract the date_range from the
            # first date. opposite to above, any time we need to get the next segment
            # or move the date goalpost, we use subtraction
            current_end_date = first_date - self.page_date_range
            # greater than or equal because we are moving backwards in time
            # tomorrow > today > yesterday
            while current_end_date >= last_date:
                segments.append((current_start_date, current_end_date))
                current_start_date = current_end_date
                # subtract because we are moving backwards in time
                current_end_date -= self.page_date_range

            # Append the last segment to cover the remaining dates, similar to above.
            # We subtract one day from `last_date` to ensure the entire day is covered.
            segments.append(
                (current_start_date, last_date - datetime.timedelta(days=1))
            )

        return segments

    def page(self, number: int | str) -> DatePage:
        number = self.validate_number(number)
        start_date, end_date = self.date_segments[number - 1]

        object_list = self._get_page_object_list_for_range(start_date, end_date)

        return self._get_page(object_list, number, self, start_date, end_date)

    def _get_page_object_list_for_range(
        self, start_date: datetime.datetime, end_date: datetime.datetime
    ) -> QuerySet[Any] | list[Any]:
        # to make mypy happy
        object_list: QuerySet[Any] | list[Any]

        if isinstance(self.object_list, QuerySet):  # type: ignore[misc]
            if self.chronological:
                filter_kwargs = {
                    f"{self.date_field}__gte": start_date,
                    f"{self.date_field}__lt": end_date,
                }
            else:
                filter_kwargs = {
                    f"{self.date_field}__lte": start_date,
                    f"{self.date_field}__gt": end_date,
                }

            object_list = self.object_list.filter(**filter_kwargs)
        else:
            if self.chronological:
                object_list = [
                    obj
                    for obj in self.object_list
                    # yesterday < today < tomorrow
                    if start_date <= getattr(obj, self.date_field) < end_date
                ]
            else:
                object_list = [
                    obj
                    for obj in self.object_list
                    # tomorrow > today > yesterday
                    if start_date >= getattr(obj, self.date_field) > end_date
                ]

        return object_list

    @cached_property
    def chronological(self) -> bool:
        """Check if the object_list is ordered in chronological order

        Chronological
        - oldest to newest
        - e.g. [yesterday, today, tomorrow]
        - yesterday < tomorrow
        - would return True

        Reverse chronological
        - newest to oldest
        - e.g. [tomorrow, today, yesterday]
        - tomorrow > yesterday
        - would return False
        """
        if self.count == 1:
            return True

        if isinstance(self.object_list, QuerySet):  # type: ignore[misc]
            first_obj = self.object_list.first()
            last_obj = self.object_list.last()
        else:
            first_obj = self.object_list[0]
            last_obj = self.object_list[-1]

        first_date = getattr(first_obj, self.date_field)
        last_date = getattr(last_obj, self.date_field)

        return first_date < last_date

    def _get_page(self, *args, **kwargs) -> DatePage:
        return DatePage(*args, **kwargs)

    @cached_property
    def num_pages(self) -> int:
        return len(self.date_segments)

    def _check_object_list_is_ordered(self):
        """Ensure that the object_list is ordered by date_field"""
        if isinstance(self.object_list, QuerySet):  # type: ignore[misc]
            ordering_fields = self.object_list.query.order_by
            if not ordering_fields or not any(
                field in [self.date_field, f"-{self.date_field}"]
                for field in ordering_fields
            ):
                raise ValueError(
                    f"Paginator received an unordered object_list: {self.object_list}. "
                    "DatePaginator only supports ordered object_list instances. "
                    "DatePaginator only supports object_list instances ordered by "
                    f"the specified date_field. Please use .order_by('{self.date_field}') "
                    f"or .order_by('-{self.date_field}') on the queryset."
                )
        else:
            # For lists, check if elements are in ascending or descending order by date_field
            is_ascending = all(
                getattr(x, self.date_field) <= getattr(y, self.date_field)
                for x, y in zip(self.object_list, self.object_list[1:])
            )
            is_descending = all(
                getattr(x, self.date_field) >= getattr(y, self.date_field)
                for x, y in zip(self.object_list, self.object_list[1:])
            )
            if not (is_ascending or is_descending):
                raise ValueError(
                    "Paginator received an unordered list. DatePaginator only supports "
                    f"lists that are ordered by the specified `date_field` - {self.date_field}."
                )


class DatePage(Page):
    def __init__(
        self,
        object_list: _SupportsPagination,
        number: int,
        paginator: DatePaginator,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> None:
        super().__init__(object_list, number, paginator)
        self.start_date = start_date
        self.end_date = end_date

    @cached_property
    def min_date(self) -> datetime.datetime:
        return min([self.start_date, self.end_date])

    @cached_property
    def max_date(self) -> datetime.datetime:
        return max([self.start_date, self.end_date])

    @cached_property
    def date_range(self) -> tuple[datetime.datetime, datetime.datetime]:
        return (self.min_date, self.max_date)
