from google.appengine.ext import ndb
from collections import Counter

class Result(ndb.Model):
  device_id = ndb.StringProperty()
  input = ndb.StringProperty()
  output = ndb.StringProperty()
  learned = ndb.BooleanProperty()
  suggests = ndb.StringProperty(repeated=True)
  hits = ndb.IntegerProperty(default=1)
  created_at = ndb.DateTimeProperty(auto_now_add=True)
  updated_at = ndb.DateTimeProperty(auto_now=True)

  def common_suggests(self):
    if not self.suggests:
      return []
    return [item[0] for item in Counter(self.suggests).most_common(5)]


class Correction(ndb.Model):
  device_id = ndb.StringProperty()
  input = ndb.StringProperty()
  output = ndb.StringProperty()
  learned = ndb.BooleanProperty()
  suggest = ndb.StringProperty()
  created_at = ndb.DateTimeProperty(auto_now_add=True)
