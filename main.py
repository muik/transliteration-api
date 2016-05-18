from datetime import datetime
import logging
from google.appengine.ext import ndb
from flask import Flask, request, render_template, Response
import pytz
import models
import auth

app = Flask(__name__)

@app.template_filter('localtime')
def localtime(time):
  timezoneLocal = pytz.timezone('Asia/Seoul')
  utc = pytz.utc
  return utc.localize(time).astimezone(timezoneLocal)

@app.route('/results.txt', methods=['GET'])
@auth.requires_admin
def txt_results():
  results = []
  list = models.Result.query_having_suggests().fetch(10000)
  for item in list:
    results.append('%s\t%s' % (item.common_input(), item.common_suggest()))
  return '\n'.join(results)

@app.route('/migrate', methods=['GET'])
@auth.requires_admin
def migrate():
  list = models.Result.query().order(models.Result.updated_at).fetch(10000)
  for item in list:
    if item.has_suggests():
      item.suggested_at = item.updated_at
    else:
      item.suggested_at = None
    item.put()
  return get_response('ok')

@app.route('/results', methods=['GET'])
@auth.requires_admin
def results():
  if request.url_root == 'http://localhost:10080/':
    host = 'http://0.0.0.0:8080'
  else:
    host = 'https://transliterator.herokuapp.com'
  keyword = request.args.get('q')
  options = {}
  suggests_option = request.args.get('suggests')
  if keyword:
    keyword = keyword.strip()
    q = models.Result.query(ndb.OR(models.Result.inputs == keyword, models.Result.output == keyword, models.Result.suggests == keyword))
  elif suggests_option == '1':
    q = models.Result.query(models.Result.suggested_at != None).order(-models.Result.suggested_at)
  elif suggests_option == '0':
    q = models.Result.query(models.Result.suggested_at == None).order(-models.Result.updated_at)
  else:
    q = models.Result.query().order(-models.Result.updated_at)

  list = q.fetch(300)
  return render_template('results.html', list=list, host=host, q=keyword)

def get_response(text, status=200):
  response = Response(text, status)
  if request.url_root == 'http://localhost:10080/':
    response.headers['Access-Control-Allow-Origin'] = '*'
  elif request.url_root.startswith('https:'):
    response.headers['Access-Control-Allow-Origin'] = 'https://transliterator.herokuapp.com'
  else:
    response.headers['Access-Control-Allow-Origin'] = 'http://transliterator.herokuapp.com'
  return response

@app.route('/results/<string:id>/suggests/<string:suggest>', methods=['DELETE'])
@auth.requires_admin
def remove_suggest(id, suggest):
  item = models.Result.get_by_id(long(id))
  if not item:
    return get_response('Not found result', 404)
  item.remove_suggest(suggest)
  if item.put():
    return get_response('Deleted')
  return get_response('Error', 500)

@app.route('/results/<string:id>', methods=['DELETE'])
@auth.requires_admin
def delete_result(id):
  item = models.Result.get_by_id(long(id))
  if not item:
    return get_response('Not Found')
  item.key.delete()
  return get_response('Deleted')

@app.route('/results/<string:id>/suggests', methods=['POST'])
def update_result(id):
  suggest = request.form['suggest']
  if suggest:
    suggest = suggest.strip()
  if not suggest:
    return get_response('bad request', 400)
  item = models.Result.get_by_id(long(id))
  item.append_suggest(suggest)
  if item.put():
    return get_response(str(item.key.id()), 200)
  return get_response('error', 500)

@app.route('/results', methods=['POST'])
def new_result():
  for key in ['deviceId', 'input', 'output', 'learned']:
    if not request.form[key] or not request.form[key].strip():
      return get_response('bad request', 400)
  device_id = request.form['deviceId'].strip()
  input = request.form['input'].strip()
  input_lower = input.lower()
  output = request.form['output'].strip()
  learned = request.form['learned'] == 'true'
  item = models.Result.query(models.Result.input == input_lower,
      models.Result.output == output, models.Result.learned == learned).get()
  if item:
    item.append_device_id(device_id)
    item.append_input(input)
    item.hits += 1
    if item.put():
      return get_response(str(item.key.id()), 200)
    return get_response('update error', 500)
  item = models.Result()
  item.device_ids = [device_id]
  item.inputs = [input]
  item.input = input_lower
  item.output = output
  item.learned = learned
  if item.put():
    return get_response(str(item.key.id()), 201)
  return get_response('create error', 500)

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
