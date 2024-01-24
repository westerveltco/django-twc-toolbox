from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from django.core.paginator import Page
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.functional import cached_property

if TYPE_CHECKING:
    from typing import Any

    from django.core.paginator import _SupportsPagination


class DatePaginator(Paginator):
    def __init__(
        self,
        object_list: _SupportsPagination,
        date_field: str,
        date_range: datetime.timedelta,
        **kwargs,
    ) -> None:
        self.date_field = date_field
        self.date_range = date_range
        super().__init__(
            object_list,
            1,  # per_page is 1 as we paginate by date
            **kwargs,
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
        if self._is_chronological():
            # if chronological, we are moving forward in time through the `object_list`
            # so any time we need to get the next segment's end date, we need to
            # add the date_range. to start we add the date_range to the first date.
            current_end_date = first_date + self.date_range
            # less than or equal because we are moving forwards in time and dates
            # in the future are greater than dates in the past
            # yesterday < today < tomorrow
            while current_end_date <= last_date:
                # keep the tuple ordering consistent with the chronological order
                # so start_date < end_date
                segments.append((current_start_date, current_end_date))
                current_start_date = current_end_date
                current_end_date += self.date_range
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
            # first date.
            current_end_date = first_date - self.date_range
            # again, greater than or equal because we are moving backwards in time
            # tomorrow > today > yesterday
            while current_end_date >= last_date:
                # keep the tuple ordering consistent with the reverse chronological
                # order so end_date > start_date
                # segments.append((current_end_date, current_start_date))
                segments.append((current_start_date, current_end_date))
                current_start_date = current_end_date
                current_end_date -= self.date_range
            # subtract because reverse
            # segments.append(
            #     (last_date - datetime.timedelta(days=1), current_start_date)
            # )
            segments.append(
                (current_start_date, last_date - datetime.timedelta(days=1))
            )

        return segments

    def page(self, number: int | str) -> DatePage:
        number = self.validate_number(number)
        start_date, end_date = self.date_segments[number - 1]

        object_list: QuerySet[Any] | list[Any]

        if isinstance(self.object_list, QuerySet):  # type: ignore[misc]
            # For QuerySet, filter based on date range
            if self._is_chronological():
                object_list = self.object_list.filter(
                    **{
                        f"{self.date_field}__gte": start_date,
                        f"{self.date_field}__lt": end_date,
                    }
                )
            else:
                object_list = self.object_list.filter(
                    **{
                        f"{self.date_field}__lte": start_date,
                        f"{self.date_field}__gt": end_date,
                    }
                ).order_by(f"-{self.date_field}")
        else:
            # For non-QuerySet, manually filter and sort
            if self._is_chronological():
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

            # Apply sorting based on the initial order
            object_list.sort(
                key=lambda obj: getattr(obj, self.date_field),
                reverse=not self._is_chronological(),
            )

        return self._get_page(object_list, number, self, start_date, end_date)

    def _is_chronological(self) -> bool:
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
        self.min_date = self.start_date
        self.max_date = self.end_date if number != 1 else timezone.now()
        self.date_range = (self.start_date, self.max_date)
