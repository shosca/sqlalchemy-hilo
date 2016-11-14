import six
from sqlalchemy import Table, Column, String, BigInteger
from sqlalchemy.sql.visitors import VisitableType
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.schema import ColumnDefault, _get_table_key

import logging

__description__ = 'HiLo primary key generators for sqlalchemy'
__version__ = '0.1.1'


log = logging.getLogger()


class HiLoMeta(VisitableType):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        keys = [cls.__name__]
        keys.extend(kwargs[k] for k in sorted(kwargs.keys()))
        key = '.'.join(filter(None, keys))
        if key not in cls._instances:
            cls._instances[key] = super(HiLoMeta, cls).__call__(*args, **kwargs)

        return cls._instances[key]


class HiLoGenerator(six.with_metaclass(HiLoMeta, ColumnDefault)):

    default_name = "single_hilo"
    block = 10000

    __visit_name__ = "column_default"

    def __init__(self,
                 name=None,
                 schema=None,
                 **kwargs):
        super(HiLoGenerator, self).__init__(self.next, **kwargs)
        self.schema = schema
        self.name = name or self.default_name

        self.hi = None
        self.lo = 0

    def next(self, exec_context):
        if self.hi is None or self.lo >= self.block:
            with exec_context.root_connection.engine.connect() as connection:
                with connection.begin():
                    self.hi = self.next_hi(connection)
                    log.info("{}: Grabbed hi:{} for block:{}".format(self, self.hi, self.block))
            self.lo = 0

        self.lo += 1
        return (self.hi * self.block) + self.lo

    def next_hi(self, connection):
        next_hi = connection.execute(
            select([self.hilo_table.c.next_hi])
        ).scalar()
        if next_hi is None:
            next_hi = 0
            connection.execute(self.hilo_table.insert(), next_hi=next_hi)
            return next_hi

        next_hi += 1
        connection.execute(self.hilo_table.update().values(next_hi=next_hi))
        return next_hi

    def _set_parent(self, column):
        super(HiLoGenerator, self)._set_parent(column)
        column._on_table_attach(self._set_table)

    def _set_table(self, column, table):
        self._set_metadata(table.metadata)

    def _set_metadata(self, metadata):
        self.metadata = metadata
        self.hilo_table = Table(
            self.name, self.metadata,
            Column("next_hi", BigInteger(), nullable=False),
            schema=self.schema,
            extend_existing=True
        )

    def __repr__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__,
                                       self.name,
                                       self.schema,
                                       self.block)


class RowPerTableHiLoGenerator(HiLoGenerator):

    default_name = "row_per_table_hilo"

    def __init__(self,
                 table_name=None,
                 **kwargs):
        super(RowPerTableHiLoGenerator, self).__init__(**kwargs)
        self.table_name = table_name

    def next_hi(self, connection):
        next_hi = connection.execute(
            select([self.hilo_table.c.next_hi]).where(
                self.hilo_table.c.table_name == self.table_name
            )
        ).scalar()
        if next_hi is None:
            next_hi = 0
            connection.execute(
                self.hilo_table.insert(), table_name=self.table_name, next_hi=next_hi
            )
            return next_hi

        next_hi += 1
        connection.execute(
            self.hilo_table.update().where(
                self.hilo_table.c.table_name == self.table_name
            ).values(
                next_hi=next_hi
            )
        )
        return next_hi

    def _set_table(self, column, table):
        super(RowPerTableHiLoGenerator, self)._set_table(column, table)
        column.default = RowPerTableHiLoGenerator(
            table_name=_get_table_key(table.name, table.schema),
            name=self.name, schema=self.schema,
        )
        column.default._set_metadata(self.metadata)

    def _set_metadata(self, metadata):
        self.metadata = metadata
        self.hilo_table = Table(
            self.name, self.metadata,
            Column("table_name", String(length=255), primary_key=True),
            Column("next_hi", BigInteger(), nullable=False),
            schema=self.schema,
            extend_existing=True
        )

    def __repr__(self):
        return "{}({}, {}, {}, {})".format(self.__class__.__name__,
                                           self.table_name,
                                           self.name,
                                           self.schema,
                                           self.block)
