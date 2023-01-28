"""
    Custom-made вариант конструктора ORM-объектов для SQLAlchemy.
    Добавляет возможность передавать объект типа dict в качестве значения, в котором искомое значение достаётся
    по имени атрибута объекта.

        Например:
            category = tables.Category(id={"id": 3, "other": "extra"})
        эквивалентен:
            category = tables.Category(id=3)
"""


def constructor(self, **kwargs):
    cls_ = type(self)
    for k in kwargs:
        if not hasattr(cls_, k):
            raise TypeError(
                "%r is an invalid keyword argument for %s" % (k, cls_.__name__)
            )
        # check if key name is FK name
        fk = cls_.__getattribute__(cls_, k).property.columns[0].foreign_keys

        if isinstance(kwargs[k], dict) and fk:
            foreign_key = list(fk).pop()
            key = foreign_key.column.key
            setattr(self, k, kwargs[k][key])
            continue

        setattr(self, k, kwargs[k])