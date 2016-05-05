from google.appengine.ext import ndb
from collections import Counter

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

  def common_input(self):
    if not self.inputs:
      return self.input
    return Counter(self.inputs).most_common(1)[0][0]

  def common_suggests(self):
    if not self.suggests:
      return []
    return [item[0] for item in Counter(self.suggests).most_common(5)]
