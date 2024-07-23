import enum
from collections.abc import Callable
from collections.abc import Mapping
from typing import Any
from typing import ClassVar
from typing import TypeVar
from typing import override

from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.core.paginator import Page
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import URLPattern
from django.utils.datastructures import MultiValueDict
from django.utils.decorators import classonlymethod
from django.utils.functional import classproperty
from django.views.generic import View

class Role(enum.Enum):
    LIST = "list"
    DETAIL = "detail"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    def handlers(self) -> dict[str, str]: ...
    def extra_initkwargs(self) -> dict[str, str]: ...
    @property
    def url_name_component(self) -> str: ...
    def url_pattern(self, view_cls: type[View]) -> str: ...
    def get_url(self, view_cls: type[View]) -> URLPattern: ...
    def reverse(self, view: CRUDView, object: models.Model | None = None) -> str: ...
    def maybe_reverse(
        self, view: CRUDView, object: models.Model | None = None
    ) -> str | None: ...

_TModel = TypeVar("_TModel", bound=models.Model)
_TObject = object

class CRUDView(View):
    role: Role
    model: ClassVar[type[models.Model] | None] = None
    fields: ClassVar[list[str] | None] = None

    lookup_field: ClassVar[str]
    lookup_url_kwarg: ClassVar[str | None] = None
    path_converter: ClassVar[str]
    object: models.Model | None = None

    queryset: ClassVar[models.QuerySet[models.Model] | None] = None
    form_class: ClassVar[forms.Form | None] = None
    template_name: ClassVar[str | None] = None
    context_object_name: ClassVar[str | None] = None

    paginate_by: ClassVar[int | None] = None
    page_kwargs: ClassVar[str] = "page"
    allow_empty: ClassVar[bool] = True

    template_name_suffix: ClassVar[str | None] = None

    def list(
        self, request: HttpRequest, *args: _TObject, **kwargs: _TObject
    ) -> TemplateResponse: ...
    def detail(
        self, request: HttpRequest, *args: _TObject, **kwargs: _TObject
    ) -> TemplateResponse: ...
    def show_form(
        self, request: HttpRequest, *args: _TObject, **kwargs: _TObject
    ) -> TemplateResponse: ...
    def process_form(
        self, request: HttpRequest, *args: _TObject, **kwargs: _TObject
    ) -> HttpResponse | HttpResponseRedirect: ...
    def confirm_delete(
        self, request: HttpRequest, *args: _TObject, **kwargs: _TObject
    ) -> TemplateResponse: ...
    def process_deletion(
        self, request: HttpRequest, *args: _TObject, **kwargs: _TObject
    ) -> TemplateResponse: ...
    def get_queryset(self) -> models.QuerySet[models.Model]: ...
    def get_object(self) -> models.Model: ...
    def get_form_class(self) -> type[forms.Form]: ...
    def get_form(
        self,
        data: Mapping[str, _TObject] | None = None,
        files: MultiValueDict[str, UploadedFile] | None = None,
        **kwargs: _TObject,
    ) -> forms.Form: ...
    def form_valid(self, form: forms.Form) -> HttpResponseRedirect: ...
    def form_invalid(self, form: forms.Form) -> HttpResponse: ...
    def get_success_url(self) -> str: ...
    def get_paginate_by(self) -> int | None: ...
    def get_paginator(
        self, queryset: models.QuerySet[_TModel], page_size: int
    ) -> Paginator[_TModel]: ...
    def paginate_queryset(
        self, queryset: models.QuerySet[_TModel]
    ) -> Page[_TModel]: ...
    def get_filterset(
        self, queryset: models.QuerySet[models.Model] | None = None
    ) -> Any: ...  # TODO: change Any to FilterSet
    def get_context_object_name(self, is_list: bool = False) -> str | None: ...
    def get_context_data(self, **kwargs: _TObject) -> dict[str, _TObject]: ...
    def get_template_names(self) -> list[str]: ...
    def render_to_response(self) -> TemplateResponse: ...
    @override
    @classmethod
    def as_view(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls, role: Role, **initkwargs: _TObject
    ) -> Callable[..., HttpResponse]: ...
    url_base: classproperty[str] | ClassVar[str]
    @classonlymethod
    def get_urls(cls, roles: list[Role] | None = None) -> list[URLPattern]: ...
