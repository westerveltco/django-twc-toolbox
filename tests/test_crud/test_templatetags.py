from __future__ import annotations

from model_bakery import baker
from neapolitan.views import Role

from django_twc_toolbox.crud.templatetags.neapolitan import action_links
from django_twc_toolbox.crud.templatetags.neapolitan import object_detail
from django_twc_toolbox.crud.templatetags.neapolitan import object_list

from .models import Bookmark
from .test_views import BookmarkView


def test_action_links(db):
    view = BookmarkView()
    object = baker.make(Bookmark)

    actions = action_links(view, object)

    assert actions["detail"]["url"] == f"/bookmark/{object.pk}/"
    assert actions["update"]["url"] == f"/bookmark/{object.pk}/edit/"
    assert actions["delete"]["url"] == f"/bookmark/{object.pk}/delete/"


def test_object_detail(db):
    view = BookmarkView(role=Role.DETAIL)
    object = baker.make(Bookmark)

    detail = object_detail(object, view)
    detail_list = list(detail["object"])

    assert detail_list[0][0] == view.detail_fields[0]
    assert detail_list[0][1] == getattr(object, view.detail_fields[0])
    assert detail_list[1][0] == view.detail_fields[1]
    assert detail_list[1][1] == getattr(object, view.detail_fields[1])


def test_object_list(db):
    view = BookmarkView(role=Role.LIST)
    objects = baker.make(Bookmark, _quantity=5)

    list = object_list(objects, view)

    assert list["headers"] == view.list_fields
    assert len(list["object_list"]) == len(objects)

    detail = list["object_list"][0]["fields"]

    assert detail[0]["value"] == getattr(objects[0], view.list_fields[0])
