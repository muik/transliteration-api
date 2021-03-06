from google.appengine.ext import ndb
from collections import Counter
from datetime import datetime

class Result(ndb.Model):
  MAX_ITEM_COUNT = 30
  device_ids = ndb.StringProperty(repeated=True)
  inputs = ndb.StringProperty(repeated=True)
  input = ndb.StringProperty()
  output = ndb.StringProperty()
  learned = ndb.BooleanProperty()
  suggests = ndb.StringProperty(repeated=True)
  hits = ndb.IntegerProperty(default=1)
  created_at = ndb.DateTimeProperty(auto_now_add=True)
  updated_at = ndb.DateTimeProperty(auto_now=True)
  suggested_at = ndb.DateTimeProperty()

  def has_suggests(self):
    return self.suggests != None and len(self.suggests) > 0

  @classmethod
  def query_having_suggests(cls):
    return cls.query(cls.suggests != None)

  def append_input(self, input):
    if self.inputs == None:
      self.inputs = []
    self.inputs.append(input)
    if len(self.inputs) > self.MAX_ITEM_COUNT:
      self.inputs = self.inputs[:self.MAX_ITEM_COUNT]

  def append_device_id(self, device_id):
    if self.device_ids == None:
      self.device_ids = []
    self.device_ids.append(device_id)
    if len(self.device_ids) > self.MAX_ITEM_COUNT:
      self.device_ids = self.device_ids[:self.MAX_ITEM_COUNT]

  def append_suggest(self, suggest):
    if not self.suggests:
      self.suggests = []
    self.suggests.append(suggest.strip())
    self.suggested_at = datetime.now()

  def remove_suggest(self, suggest):
    suggest = suggest.strip()
    self.suggests = [v for v in self.suggests if v != suggest]
    if not self.has_suggests():
      self.suggested_at = None

  def common_device_id(self):
    if not self.device_ids:
      return '' 
    return Counter(self.device_ids).most_common(1)[0][0]

  def common_input(self):
    if not self.inputs:
      return self.input
    return Counter(self.inputs).most_common(1)[0][0]

  def common_suggest(self):
    if not self.suggests:
      return None
    return Counter(self.suggests).most_common(1)[0][0]

  def common_suggests(self, limit=5):
    if not self.suggests:
      return []
    return [item[0] for item in Counter(self.suggests).most_common(limit)]
