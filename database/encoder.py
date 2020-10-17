import simplejson
from sqlalchemy.ext.declarative import DeclarativeMeta


class AlchemyEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            fields = {}
            for field in [
                x for x in dir(obj) if not x.startswith("_") and x != "metadata"
            ]:
                data = obj.__getattribute__(field)
                try:
                    simplejson.dumps(data)
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            return fields

        return simplejson.JSONEncoder.default(self, obj)
