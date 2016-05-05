from flask import Flask, request, render_template, Response, jsonify
import models
import logging
app = Flask(__name__)

@app.route('/results', methods=['GET'])
def results():
  list = models.Result.query().order(-models.Result.updated_at).fetch(100)
  return render_template('results.html', list=list)

def get_response(text, status):
  response = Response(text, status)
  if request.url_root == 'http://localhost:10080/':
    response.headers['Access-Control-Allow-Origin'] = '*'
  elif request.url_root.startswith('https:'):
    response.headers['Access-Control-Allow-Origin'] = 'https://transliterator.herokuapp.com'
  else:
    response.headers['Access-Control-Allow-Origin'] = 'http://transliterator.herokuapp.com'
  return response

@app.route('/results/<string:id>/suggests', methods=['POST'])
def update_result(id):
  suggest = request.form['suggest']
  if suggest:
    suggest = suggest.strip()
  if not suggest:
    return get_response('bad request', 400)
  item = models.Result.get_by_id(long(id))
  if not item.suggests:
    item.suggests = []
  item.suggests.append(suggest)
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
