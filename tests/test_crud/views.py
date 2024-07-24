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


urlpatterns = [
    *BookmarkView.get_urls(),
    *BookmarkTableView.get_urls(),
]
