SQLAlchemy HiLo PK Generator
============================

There are two flavors of the HiLo generator, ``HiLoGenerator`` and
``RowPerTableHiLoGenerator``. ``HiLoGenerator`` will create a single
column table to keep track of the ``hi`` value:

.. code:: sql

    CREATE TABLE single_hilo (
        next_hi BIGINT NOT NULL
    )

``RowPerTableHiLoGenerator`` will create a two column table to keep
track of the ``hi`` value per table per row:

.. code:: sql

    CREATE TABLE row_per_table_hilo (
            table_name VARCHAR(255) NOT NULL,
            next_hi BIGINT NOT NULL,
            PRIMARY KEY (table_name)
    )

You can use them in your models like any other ``Sequence``:

.. code:: python

    class Entity(Base):

        id = Column(BigInteger(), HiLoGenerator(), primary_key=True)
        ...

or

.. code:: python

    class Entity(Base):

        id = Column(BigInteger(), RowPerTableHiLoGenerator(), primary_key=True)
        ...

