# **kwargs e.x:
# cls_ e.x : Class

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