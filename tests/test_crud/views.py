from __future__ import annotations

from django_tables2 import tables

from django_twc_toolbox.crud.views import CRUDView

from .models import Bookmark


class BookmarkView(CRUDView):
    model = Bookmark
    fields = ["url", "title", "note"]

    detail_fields = ["url", "title"]
    list_fields = ["url"]


class BookmarkTable(tables.Table):
    class Meta:
        model = Bookmark


class BookmarkTableView(BookmarkView):
    table_class = BookmarkTable
    url_base = "bookmarktable"


class BookmarkTableOrdered(tables.Table):
    class Meta:
        model = Bookmark
        order_by = "title"


class BookmarkTableOrderedView(BookmarkView):
    table_class = BookmarkTableOrdered
    paginate_by = 1
    url_base = "bookmarktableordered"


urlpatterns = [
    *BookmarkView.get_urls(),
    *BookmarkTableView.get_urls(),
    *BookmarkTableOrderedView.get_urls(),
]
