import simplejson
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('sqlite:///db.sqlite3', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class AlchemyEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    simplejson.dumps(data)
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            return fields

        return simplejson.JSONEncoder.default(self, obj)
