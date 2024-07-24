from typing import ClassVar

from django_tables2 import tables

TableData = dict[str, object]

class TableMixinBase:
    context_table_name: ClassVar[str]
    table_pagination: bool | dict[str, object] | None
    def get_paginate_by(self, table_data: TableData | None) -> int | None: ...

class SingleTableMixin(TableMixinBase):
    table_class: ClassVar[type[tables.Table] | None] = None
    table_data: ClassVar[TableData | None] = None
    def get_context_data(self, **kwargs: object) -> dict[str, object]: ...
