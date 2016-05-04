from flask import Flask, request, render_template, Response
import models
import logging
app = Flask(__name__)

@app.route('/results', methods=['GET'])
def results():
  list = models.Result.query().order(-models.Result.created_at).fetch(100)
  return render_template('results.html', list=list)

def get_response(text, status):
  response = Response(text, status)
  if request.url_root == 'http://localhost:10080/':
    response.headers['Access-Control-Allow-Origin'] = '*'
  else:
    response.headers['Access-Control-Allow-Origin'] = 'transliterator.herokuapp.com'
  return response

@app.route('/results', methods=['POST'])
def new_result():
  for key in ['deviceId', 'input', 'output', 'learned']:
    if not request.form[key]:
      return get_response('bad request', 400)
  item = models.Result()
  item.device_id = request.form['deviceId']
  item.input = request.form['input']
  item.output = request.form['output']
  item.learned = request.form['learned'] == 'true'
  if item.put():
    return get_response('saved', 201)
  return get_response('error', 500)

@app.route('/corrections', methods=['GET'])
def corrections():
  list = models.Correction.query().order(-models.Correction.created_at).fetch(100)
  return render_template('corrections.html', list=list)

@app.route('/corrections', methods=['POST'])
def new_correction():
  for key in ['deviceId', 'input', 'output', 'learned', 'suggest']:
    if not request.form[key]:
      return get_response('bad request', 400)
  item = models.Correction()
  item.device_id = request.form['deviceId']
  item.input = request.form['input']
  item.output = request.form['output']
  item.learned = request.form['learned'] == 'true'
  item.suggest = request.form['suggest']
  if item.put():
    return get_response('saved', 201)
  return get_response('error', 500)

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