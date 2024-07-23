from __future__ import annotations

from django_twc_toolbox.crud.views import CRUDView

from .models import Bookmark


class BookmarkView(CRUDView):
    model = Bookmark
    fields = ["url", "title", "note"]

    detail_fields = ["url", "title"]
    list_fields = ["url"]


urlpatterns = [
    *BookmarkView.get_urls(),
]
