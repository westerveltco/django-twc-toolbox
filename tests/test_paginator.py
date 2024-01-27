from __future__ import annotations

import datetime
import itertools
import random
from dataclasses import asdict
from dataclasses import dataclass

import pytest
from django import VERSION as DJANGO_VERSION
from django.core.paginator import EmptyPage
from django.core.paginator import Page
from django.core.paginator import PageNotAnInteger
from django.db.models.query import QuerySet
from django.utils import timezone
from model_bakery import baker

from django_twc_toolbox.paginator import DatePage
from django_twc_toolbox.paginator import DatePaginator

from .dummy.models import DateOrderableModel
from .dummy.models import DateTimeOrderableModel


@dataclass
class ModelClassParams:
    """
    Stores parameters for a pytest parameterized test case.

    Intended to be used as a parameter to a parameterized test case along
    with the indirect `model_data_queryset` fixture.
    """

    model_class: type[DateOrderableModel | DateTimeOrderableModel]
    number_of_days: int

    def __iter__(self):
        return iter(asdict(self).values())

    @classmethod
    def from_request(cls, request):
        return cls(
            model_class=request.param.model_class,
            number_of_days=request.param.number_of_days,
        )


@pytest.fixture
def model_data_queryset(request, db):
    """
    Sets up a queryset of the specified model class with the specified number of days of data
    for use in pagination tests.

    Depending on the test parameterization, it uses `ModelClassParams` to determine the model class
    and the number of days for data generation. If not parameterized with `ModelClassParams`,
    it defaults to `DateOrderableModel` with 90 days of data.

    The fixture supports creating data for both `DateOrderableModel` and `DateTimeOrderableModel`.
    For `DateTimeOrderableModel`, it generates two data points per day.

    The DatePaginator expects an ordered data structure, so the data is returned ordered to make
    all the tests do not need to worry about the initial ordering. In the tests that need to verify
    the ordering, they can apply their own sorting to the data.
    """
    # Check if the request has the expected parameterization
    if hasattr(request, "param") and isinstance(request.param, ModelClassParams):
        model_class, number_of_days = ModelClassParams.from_request(request)
    else:
        # Default values for tests that don't use ModelClassParams
        model_class = DateOrderableModel  # or any default model
        number_of_days = 90  # default number of days

    if model_class == DateOrderableModel:
        date_values = (
            timezone.now() - datetime.timedelta(days=i) for i in range(number_of_days)
        )
    else:
        current_time = timezone.now()
        date_values = itertools.chain.from_iterable(
            (
                current_time - datetime.timedelta(days=i, hours=12),
                current_time - datetime.timedelta(days=i),
            )
            for i in range(number_of_days)
        )

    baker.make(
        model_class,
        date=itertools.cycle(date_values),
        _quantity=number_of_days,
    )

    return model_class.objects.all().order_by("date")


@pytest.fixture(params=["queryset", "list", "tuple"])
def objects(request, model_data_queryset):
    """
    Provides the model data needed in different formats to make sure our custom
    DatePaginator can handle all the data structures a Django Paginator should handle.

    It uses the `model_data_queryset` fixture to get the initial queryset and then
    provides it in three different structures: QuerySet, list, and tuple.
    """
    if request.param == "queryset":
        ret = model_data_queryset
    elif request.param == "tuple":
        ret = tuple(model_data_queryset)
    else:
        ret = list(model_data_queryset)

    return ret


class TestDatePaginator:
    @pytest.mark.parametrize(
        "model_data_queryset,days_per_page,expected_num_pages",
        [
            # date
            # create 90 days of data, paginate by 30 days, expect 3 pages
            (
                ModelClassParams(model_class=DateOrderableModel, number_of_days=90),
                30,
                3,
            ),
            # datetime
            # create 90 days of data (2 per day), paginate by 30 days, expect 2 pages
            (
                ModelClassParams(model_class=DateTimeOrderableModel, number_of_days=90),
                30,
                2,
            ),
            # date
            # create 180 days of data, paginate by 30 days, expect 6 pages
            (
                ModelClassParams(model_class=DateOrderableModel, number_of_days=180),
                30,
                6,
            ),
            # datetime
            # create 180 days of data (2 per day), paginate by 30 days, expect 3 pages
            (
                ModelClassParams(
                    model_class=DateTimeOrderableModel, number_of_days=180
                ),
                30,
                3,
            ),
            # date
            # create 90 days of data, paginate by 60 days, expect 2 pages
            (
                ModelClassParams(model_class=DateOrderableModel, number_of_days=90),
                60,
                2,
            ),
            # date
            # create 90 days of data (2 per day), paginate by 60 days, expect 1 page
            (
                ModelClassParams(model_class=DateTimeOrderableModel, number_of_days=90),
                60,
                1,
            ),
        ],
        indirect=["model_data_queryset"],
    )
    def test_num_pages(self, objects, days_per_page, expected_num_pages):
        paginator = DatePaginator(
            objects, "date", datetime.timedelta(days=days_per_page)
        )

        assert paginator.num_pages == expected_num_pages

    def test_first_page(self, objects):
        paginator = DatePaginator(objects, "date", datetime.timedelta(days=30))
        first_page = paginator.page(1)

        first_segment_start, first_segment_end = paginator.date_segments[0]

        # Count objects in the first segment based on the type of 'objects'
        if isinstance(objects, QuerySet):  # type: ignore[misc]
            objects_in_first_segment = objects.filter(
                date__gte=first_segment_start,
                date__lt=first_segment_end,
            ).count()
        else:
            objects_in_first_segment = sum(
                1
                for entry in objects
                if first_segment_start <= entry.date < first_segment_end
            )

        assert len(first_page.object_list) == objects_in_first_segment

    def test_page_out_of_range(self, objects):
        paginator = DatePaginator(objects, "date", datetime.timedelta(days=30))

        with pytest.raises(EmptyPage):
            paginator.page(4)  # Only 3 pages exist

    def test_with_empty_queryset(self):
        empty = DateOrderableModel.objects.none().order_by("date")
        paginator = DatePaginator(empty, "date", datetime.timedelta(days=30))

        assert paginator.count == 0
        assert paginator.num_pages == 0

    def test_with_empty_list(self):
        paginator = DatePaginator([], "date", datetime.timedelta(days=30))

        assert paginator.count == 0
        assert paginator.num_pages == 0

    def test_with_single_entry(self, db):
        baker.make("dummy.DateOrderableModel", date=timezone.now().date())
        obj = DateOrderableModel.objects.all().order_by("-date")
        paginator = DatePaginator(obj, "date", datetime.timedelta(days=30))

        assert paginator.num_pages == 1
        assert len(paginator.page(1).object_list) == 1

    def test_large_date_range(self, objects):
        large_range = datetime.timedelta(days=365)
        paginator = DatePaginator(objects, "date", large_range)

        assert paginator.num_pages == 1
        assert len(paginator.page(1).object_list) == len(objects)

    def test_small_date_range(self, objects):
        small_range = datetime.timedelta(days=1)
        paginator = DatePaginator(objects, "date", small_range)

        assert paginator.num_pages == len(objects)

    def test_date_range_boundary_cases(self, db, objects):
        if isinstance(objects, QuerySet):  # type: ignore[misc]
            earliest_date = objects.earliest("date").date
        else:
            earliest_date = min(entry.date for entry in objects)

        paginator = DatePaginator(objects, "date", datetime.timedelta(days=30))
        start_of_first_segment, _ = paginator.date_segments[0]

        # Ensure the boundary date falls within the first segment
        boundary_date = max(earliest_date, start_of_first_segment)

        # Create new objects at the boundary date
        new_objects = baker.make(
            "dummy.DateOrderableModel", date=boundary_date, _quantity=5
        )

        # If 'objects' is a tuple/list, manually add these new objects to it
        if not isinstance(objects, QuerySet):  # type: ignore[misc]
            if isinstance(objects, tuple):
                objects = objects + tuple(new_objects)
            else:
                objects.extend(new_objects)

        first_page = paginator.page(1)

        assert all(obj.date >= boundary_date for obj in first_page.object_list)

    def test_non_sequence_page_number(self, objects):
        if isinstance(objects, QuerySet):  # type: ignore[misc]
            random_objects = objects.order_by("?")
        else:
            random_objects = list(objects)
            random.shuffle(random_objects)
            if isinstance(objects, tuple):
                random_objects = tuple(random_objects)

        with pytest.raises(ValueError):
            DatePaginator(random_objects, "date", datetime.timedelta(days=30))

    @pytest.mark.parametrize(
        "model_data_queryset",
        [
            ModelClassParams(model_class=DateOrderableModel, number_of_days=90),
            ModelClassParams(model_class=DateTimeOrderableModel, number_of_days=180),
        ],
        indirect=["model_data_queryset"],
    )
    def test_chronological_ordering(self, objects):
        paginator = DatePaginator(objects, "date", datetime.timedelta(days=30))

        first_page_item_date = paginator.page(1).object_list[0].date
        middle_page_item_date = paginator.page(2).object_list[0].date
        last_page_item_date = paginator.page(3).object_list[0].date

        assert first_page_item_date < middle_page_item_date
        assert middle_page_item_date < last_page_item_date

        for item in paginator.page(1).object_list:
            assert item.date >= first_page_item_date

    @pytest.mark.parametrize(
        "model_data_queryset",
        [
            ModelClassParams(model_class=DateOrderableModel, number_of_days=90),
            ModelClassParams(model_class=DateTimeOrderableModel, number_of_days=180),
        ],
        indirect=["model_data_queryset"],
    )
    def test_reversed_ordering(self, objects):
        if isinstance(objects, QuerySet):  # type: ignore[misc]
            objects = objects.order_by("-date")
        else:
            objects = list(reversed(objects))

        paginator = DatePaginator(objects, "date", datetime.timedelta(days=30))

        first_page_item_date = paginator.page(1).object_list[0].date
        middle_page_item_date = paginator.page(2).object_list[0].date
        last_page_item_date = paginator.page(3).object_list[0].date

        assert first_page_item_date > middle_page_item_date
        assert middle_page_item_date > last_page_item_date

        previous_item = first_page_item_date
        for item in paginator.page(1).object_list:
            assert item.date <= first_page_item_date
            assert item.date <= previous_item
            previous_item = item.date

    def test_paginator_page_function(self, objects):
        paginator = DatePaginator(objects, "date", datetime.timedelta(days=10))

        page = paginator.page(1)

        assert isinstance(page, Page)
        assert page.number == 1

        with pytest.raises(PageNotAnInteger):
            paginator.page("not_a_number")

        with pytest.raises(EmptyPage):
            paginator.page(0)  # Page number less than 1

        with pytest.raises(EmptyPage):
            paginator.page(paginator.num_pages + 1)  # Page number out of range

    @pytest.mark.parametrize(
        "model_data_queryset",
        [
            ModelClassParams(model_class=DateOrderableModel, number_of_days=90),
            ModelClassParams(model_class=DateTimeOrderableModel, number_of_days=180),
        ],
        indirect=["model_data_queryset"],
    )
    def test_paginator_date_range(self, objects):
        date_range = datetime.timedelta(days=10)
        paginator = DatePaginator(objects, "date", date_range)

        with pytest.warns(DeprecationWarning):
            assert paginator.date_range == date_range

    @pytest.mark.parametrize(
        "model_data_queryset",
        [
            ModelClassParams(model_class=DateOrderableModel, number_of_days=90),
            ModelClassParams(model_class=DateTimeOrderableModel, number_of_days=180),
        ],
        indirect=["model_data_queryset"],
    )
    def test_paginator_page_date_range(self, objects):
        date_range = datetime.timedelta(days=10)
        paginator = DatePaginator(objects, "date", date_range)

        assert paginator.page_date_range == date_range

    @pytest.mark.parametrize(
        "model_data_queryset",
        [
            ModelClassParams(model_class=DateOrderableModel, number_of_days=90),
            ModelClassParams(model_class=DateTimeOrderableModel, number_of_days=180),
        ],
        indirect=["model_data_queryset"],
    )
    def test_paginator_page_date_range_missing(self, objects):
        with pytest.raises(ValueError):
            DatePaginator(objects, "date")

    @pytest.mark.parametrize(
        "model_data_queryset",
        [
            ModelClassParams(model_class=DateOrderableModel, number_of_days=90),
            ModelClassParams(model_class=DateTimeOrderableModel, number_of_days=180),
        ],
        indirect=["model_data_queryset"],
    )
    def test_paginator_explicit_date_range(self, objects):
        date_range = datetime.timedelta(days=10)

        with pytest.warns(DeprecationWarning):
            DatePaginator(objects, "date", date_range=date_range)


class TestDatePaginatorInheritance:
    """
    Test that the DatePaginator respects the Django Paginator inheritance.

    Only test the attributes and methods that are not overridden.
    """

    @pytest.fixture
    def paginator(self, objects):
        return DatePaginator(objects, "date", datetime.timedelta(days=10))

    def test___init__(self, objects):
        paginator = DatePaginator(
            objects,
            "date",
            datetime.timedelta(days=10),
            allow_empty_first_page=False,
        )

        assert paginator.object_list == objects
        assert paginator.per_page == 1  # As it paginates by date
        assert paginator.allow_empty_first_page is False
        if DJANGO_VERSION >= (5, 0, 0):
            assert paginator.error_messages == paginator.default_error_messages

    def test_orphans(self, objects):
        with pytest.warns(UserWarning):
            DatePaginator(objects, "date", datetime.timedelta(days=10), orphans=5)

    def test_allow_empty_first_page(self):
        allow_paginator = DatePaginator(
            DateOrderableModel.objects.none().order_by("date"),
            "date",
            datetime.timedelta(days=10),
            allow_empty_first_page=True,
        )

        assert allow_paginator.num_pages == 0

        do_not_allow_paginator = DatePaginator(
            DateOrderableModel.objects.none().order_by("date"),
            "date",
            datetime.timedelta(days=10),
            allow_empty_first_page=False,
        )

        assert do_not_allow_paginator.num_pages == 0
        with pytest.raises(EmptyPage):
            do_not_allow_paginator.page(1)

    @pytest.mark.skipif(
        DJANGO_VERSION < (5, 0, 0),
        reason="`error_messages` kwarg introduced in Django 5.0",
    )
    def test_error_messages(self, objects):
        custom_error_messages = {
            "invalid_page": "Custom invalid page message",
            "min_page": "Custom min page message",
            "no_results": "Custom no results message",
        }

        paginator = DatePaginator(
            objects,
            "date",
            datetime.timedelta(days=10),
            error_messages=custom_error_messages,
        )

        with pytest.raises(PageNotAnInteger) as excinfo:
            paginator.page("invalid")
        assert str(excinfo.value) == custom_error_messages["invalid_page"]

        with pytest.raises(EmptyPage) as excinfo:
            paginator.page(0)
        assert str(excinfo.value) == custom_error_messages["min_page"]

        with pytest.raises(EmptyPage) as excinfo:
            paginator.page(1000)
        assert str(excinfo.value) == custom_error_messages["no_results"]

    def test___iter__(self, paginator):
        for index, page in enumerate(paginator):
            assert page.number == index + 1

    def test_validate_number(self, paginator):
        assert paginator.validate_number(1) == 1

        with pytest.raises(PageNotAnInteger):
            paginator.validate_number("two")

        with pytest.raises(EmptyPage):
            paginator.validate_number(-1)

        with pytest.raises(EmptyPage):
            paginator.validate_number(paginator.num_pages + 1)

    def test_get_page(self, paginator):
        page = paginator.get_page(1)

        assert isinstance(page, Page)
        assert page.number == 1

        # Invalid page number
        invalid_page = paginator.get_page(1000)

        assert invalid_page.number == paginator.num_pages  # Should return the last page

    def test_count(self, objects):
        paginator = DatePaginator(
            objects,
            "date",
            datetime.timedelta(days=10),
        )

        assert paginator.count == len(objects)

    def test_page_range(self, paginator):
        assert len(paginator.page_range) == paginator.num_pages

    def test_get_elided_page_range(self, paginator):
        elided_range = paginator.get_elided_page_range(number=1)
        elided_range_list = list(elided_range)

        assert all(
            isinstance(item, int) or item == paginator.ELLIPSIS
            for item in elided_range_list
        )


class TestDatePage:
    @pytest.mark.parametrize(
        "order_by",
        ["date", "-date"],
    )
    def test_page_start_date(self, objects, order_by):
        if isinstance(objects, QuerySet):  # type: ignore[misc]
            objects = objects.order_by(order_by)
        elif order_by == "date":
            objects = list(objects)
        else:
            objects = list(reversed(objects))

        paginator = DatePaginator(objects, "date", datetime.timedelta(days=10))
        page = paginator.page(1)

        start_date, _ = paginator.date_segments[0]

        assert page.start_date == start_date

    @pytest.mark.parametrize(
        "order_by",
        ["date", "-date"],
    )
    def test_page_start_date_single_entry(self, db, order_by):
        baker.make("dummy.DateOrderableModel", date=timezone.now().date())
        obj = DateOrderableModel.objects.all().order_by(order_by)

        paginator = DatePaginator(obj, "date", datetime.timedelta(days=10))
        page = paginator.page(1)

        start_date, _ = paginator.date_segments[0]

        assert page.start_date == start_date

    @pytest.mark.parametrize(
        "order_by",
        ["date", "-date"],
    )
    def test_page_end_date(self, objects, order_by):
        if isinstance(objects, QuerySet):  # type: ignore[misc]
            objects = objects.order_by(order_by)
        elif order_by == "date":
            objects = list(objects)
        else:
            objects = list(reversed(objects))

        paginator = DatePaginator(objects, "date", datetime.timedelta(days=10))
        page = paginator.page(1)

        _, end_date = paginator.date_segments[0]

        assert page.end_date == end_date

    @pytest.mark.parametrize(
        "order_by",
        ["date", "-date"],
    )
    def test_page_end_date_single_entry(self, db, order_by):
        baker.make("dummy.DateOrderableModel", date=timezone.now().date())
        obj = DateOrderableModel.objects.all().order_by(order_by)

        paginator = DatePaginator(obj, "date", datetime.timedelta(days=10))
        page = paginator.page(1)

        _, end_date = paginator.date_segments[0]

        assert page.end_date == end_date

    @pytest.mark.parametrize(
        "order_by",
        ["date", "-date"],
    )
    def test_page_min_date(self, objects, order_by):
        if isinstance(objects, QuerySet):  # type: ignore[misc]
            objects = objects.order_by(order_by)
        elif order_by == "date":
            objects = list(objects)
        else:
            objects = list(reversed(objects))

        paginator = DatePaginator(objects, "date", datetime.timedelta(days=10))
        page = paginator.page(1)

        start_date, end_date = paginator.date_segments[0]

        if order_by == "date":
            assert page.min_date == start_date
        else:
            assert page.min_date == end_date

    @pytest.mark.parametrize(
        "order_by",
        ["date", "-date"],
    )
    def test_page_max_date(self, objects, order_by):
        if isinstance(objects, QuerySet):  # type: ignore[misc]
            objects = objects.order_by(order_by)
        elif order_by == "date":
            objects = list(objects)
        else:
            objects = list(reversed(objects))

        paginator = DatePaginator(objects, "date", datetime.timedelta(days=10))
        page = paginator.page(1)

        start_date, end_date = paginator.date_segments[0]

        if order_by == "date":
            assert page.max_date == end_date
        else:
            assert page.max_date == start_date

        page = paginator.page(2)

        start_date, end_date = paginator.date_segments[1]

        if order_by == "date":
            assert page.max_date == end_date
        else:
            assert page.max_date == start_date

    @pytest.mark.parametrize(
        "order_by",
        ["date", "-date"],
    )
    def test_page_date_range(self, objects, order_by):
        if isinstance(objects, QuerySet):  # type: ignore[misc]
            objects = objects.order_by(order_by)
        elif order_by == "date":
            objects = list(objects)
        else:
            objects = list(reversed(objects))

        paginator = DatePaginator(objects, "date", datetime.timedelta(days=10))
        page = paginator.page(1)

        start_date, end_date = paginator.date_segments[0]

        if order_by == "date":
            assert page.date_range == (start_date, end_date)
        else:
            assert page.date_range == (end_date, start_date)


class TestDatePageInheritence:
    """
    Test that the DatePage respects the Django Page inheritance.

    Only test the attributes and methods that are not overridden.
    """

    @pytest.fixture
    def paginator(self, objects):
        return DatePaginator(objects, "date", datetime.timedelta(days=10))

    def test___init__(self, paginator):
        page = paginator.page(1)
        start_date, end_date = paginator.date_segments[0]

        date_page = DatePage(
            page.object_list, page.number, paginator, start_date, end_date
        )

        assert date_page.object_list == page.object_list
        assert date_page.number == page.number
        assert date_page.paginator == page.paginator

    def test___len__(self, paginator):
        page = paginator.page(1)
        start_date, end_date = paginator.date_segments[0]

        date_page = DatePage(
            page.object_list, page.number, paginator, start_date, end_date
        )

        assert len(date_page) == len(page.object_list)

    def test___getitem__(self, paginator):
        page = paginator.page(1)
        start_date, end_date = paginator.date_segments[0]

        date_page = DatePage(
            page.object_list, page.number, paginator, start_date, end_date
        )

        assert date_page[0] == page.object_list[0]
        assert date_page[:2] == page.object_list[:2]
        with pytest.raises(IndexError):
            date_page[len(page.object_list)]

    def test_has_next(self, paginator):
        last_page_number = paginator.num_pages
        last_start_date, last_end_date = paginator.date_segments[last_page_number - 1]

        last_page = DatePage(
            paginator.page(last_page_number).object_list,
            last_page_number,
            paginator,
            last_start_date,
            last_end_date,
        )

        assert not last_page.has_next()

        second_last_page_number = last_page_number - 1
        second_last_start_date, second_last_end_date = paginator.date_segments[
            second_last_page_number - 1
        ]

        second_last_page = DatePage(
            paginator.page(second_last_page_number).object_list,
            second_last_page_number,
            paginator,
            second_last_start_date,
            second_last_end_date,
        )

        assert second_last_page.has_next()

    def test_has_previous(self, paginator):
        first_start_date, first_end_date = paginator.date_segments[0]

        first_page = DatePage(
            paginator.page(1).object_list,
            1,
            paginator,
            first_start_date,
            first_end_date,
        )

        assert not first_page.has_previous()

        second_start_date, second_end_date = paginator.date_segments[1]

        second_page = DatePage(
            paginator.page(2).object_list,
            2,
            paginator,
            second_start_date,
            second_end_date,
        )

        assert second_page.has_previous()

    def test_has_other_pages(self, objects, paginator):
        first_start_date, first_end_date = paginator.date_segments[0]

        first_page = DatePage(
            paginator.page(1).object_list,
            1,
            paginator,
            first_start_date,
            first_end_date,
        )

        assert first_page.has_other_pages()

        single_paginator = DatePaginator(
            objects, "date", datetime.timedelta(days=len(objects) + 1)
        )
        single_start_date, single_end_date = single_paginator.date_segments[0]

        single_page = DatePage(
            single_paginator.page(1).object_list,
            1,
            single_paginator,
            single_start_date,
            single_end_date,
        )

        assert not single_page.has_other_pages()

    def test_next_page_number(self, paginator):
        first_start_date, first_end_date = paginator.date_segments[0]

        first_page = DatePage(
            paginator.page(1).object_list,
            1,
            paginator,
            first_start_date,
            first_end_date,
        )

        assert first_page.next_page_number() == 2

        last_page_number = paginator.num_pages
        last_start_date, last_end_date = paginator.date_segments[last_page_number - 1]

        last_page = DatePage(
            paginator.page(last_page_number).object_list,
            last_page_number,
            paginator,
            last_start_date,
            last_end_date,
        )

        with pytest.raises(EmptyPage):
            last_page.next_page_number()

    def test_previous_page_number(self, paginator):
        last_page_number = paginator.num_pages
        last_start_date, last_end_date = paginator.date_segments[last_page_number - 1]

        last_page = DatePage(
            paginator.page(last_page_number).object_list,
            last_page_number,
            paginator,
            last_start_date,
            last_end_date,
        )

        assert last_page.previous_page_number() == last_page_number - 1

        first_start_date, first_end_date = paginator.date_segments[0]

        first_page = DatePage(
            paginator.page(1).object_list,
            1,
            paginator,
            first_start_date,
            first_end_date,
        )

        with pytest.raises(EmptyPage):
            first_page.previous_page_number()

    def test_start_index(self, paginator):
        first_start_date, first_end_date = paginator.date_segments[0]

        first_page = DatePage(
            paginator.page(1).object_list,
            1,
            paginator,
            first_start_date,
            first_end_date,
        )

        assert first_page.start_index() == 1

        middle_page_number = paginator.num_pages // 2
        middle_start_date, middle_end_date = paginator.date_segments[
            middle_page_number - 1
        ]

        middle_page = DatePage(
            paginator.page(middle_page_number).object_list,
            middle_page_number,
            paginator,
            middle_start_date,
            middle_end_date,
        )

        assert (
            middle_page.start_index()
            == (middle_page_number - 1) * paginator.per_page + 1
        )

    def test_end_index(self, paginator):
        first_start_date, first_end_date = paginator.date_segments[0]

        first_page = DatePage(
            paginator.page(1).object_list,
            1,
            paginator,
            first_start_date,
            first_end_date,
        )

        assert first_page.end_index() == min(
            first_page.number * paginator.per_page, paginator.count
        )

        last_page_number = paginator.num_pages
        last_start_date, last_end_date = paginator.date_segments[last_page_number - 1]

        last_page = DatePage(
            paginator.page(last_page_number).object_list,
            last_page_number,
            paginator,
            last_start_date,
            last_end_date,
        )

        assert last_page.end_index() == paginator.count
