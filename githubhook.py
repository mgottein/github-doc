import web
from runnable import mapwiki

urls = ('/.*', 'hooks')

app = web.application(urls, globals())

class hooks:
	def POST(self):
		data = web.data()
		print
		print 'DATA RECEIVED:'
		print data
		print
		print 'RUNNING GITHUB-DOC'
		mapwiki()
		print
		return 'OK'

if __name__ == '__main__':
	app.run()