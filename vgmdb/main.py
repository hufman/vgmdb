from bottle import route

@route('/hello')
def hello():
	return "Hello!"

