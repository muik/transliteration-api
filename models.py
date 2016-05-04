from google.appengine.ext import ndb

class Result(ndb.Model):
  device_id = ndb.StringProperty()
  input = ndb.StringProperty()
  output = ndb.StringProperty()
  learned = ndb.BooleanProperty()
  created_at = ndb.DateTimeProperty(auto_now_add=True)

class Correction(ndb.Model):
  device_id = ndb.StringProperty()
  input = ndb.StringProperty()
  output = ndb.StringProperty()
  learned = ndb.BooleanProperty()
  suggest = ndb.StringProperty()
  created_at = ndb.DateTimeProperty(auto_now_add=True)
