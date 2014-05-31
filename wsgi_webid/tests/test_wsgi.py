from unittest import TestCase
import httmock
from . import utils
from webid.cert import Cert
from wsgi_webid import WebIDMiddleware

webid_url = 'http://test.example.com/donttouchme#me'
def create_webid_graph(webid_url, testcert):
	""" Given a webid_url and a webid.cert object, create a webid graph """
	from rdflib import BNode, Graph, Literal, Namespace, URIRef
	from rdflib.namespace import RDF, RDFS, FOAF, XSD
	CERT = Namespace('http://www.w3.org/ns/auth/cert#')
	graph = Graph('IOMemory', BNode())

	person = URIRef(webid_url)
	cert = BNode()
	graph.add((person, RDF.type, FOAF.Person))
	graph.add((person, CERT.key, cert))
	graph.add((cert, RDF.type, CERT.RSAPublicKey))
	graph.add((cert, CERT.modulus, Literal(testcert.get_mod(), datatype=XSD.hexBinary)))
	graph.add((cert, CERT.exponent, Literal(testcert.get_exp(), datatype=XSD.integer)))
	return graph

class TestWSGI(object):
	""" WSGI application that just records the given environment
	    It never calls the WSGI callback function, and returns None
	    Peek into the environ attribute to get the results
	"""
	def __init__(self):
		self.environ = {}
	def __call__(self, environ, callback):
		self.environ = environ
		return None

# create the test webid
rsakey = utils.create_rsa_key()
x509 = utils.create_self_signed_cert(rsakey, san="URI:%s"%webid_url)
cert = Cert(x509.as_pem())
cert.get_pubkey()

class TestWebid(TestCase):
	def setUp(self):
		self.environ = {}
		self.webid_graph = create_webid_graph(webid_url, cert)

	def assertIs(self, left, right):
		self.assertTrue(left is right)

	def assertIsNot(self, left, right):
		self.assertTrue(left is not right)

	@httmock.all_requests
	def webid_server(self, url, request):
		content = None
		headers = {}
		if 'rdf+xml' in request.headers['Accept']:
			headers['Content-Type'] = 'application/rdf+xml'
			content = self.webid_graph.serialize(format='xml')
		return httmock.response(200, content, headers, None, 5, request)

	@httmock.all_requests
	def empty_server(self, url, request):
		return {'status_code': 404}

	def test_null(self):
		with httmock.HTTMock(self.empty_server):
			receiver = TestWSGI()
			wrapping = WebIDMiddleware(receiver)
			wrapping(self.environ, None)
			self.assertFalse('webid.valid' in receiver.environ)
			self.assertFalse('webid.uri' in receiver.environ)
			self.assertFalse('webid.graph' in receiver.environ)

	def test_good(self):
		with httmock.HTTMock(self.webid_server):
			receiver = TestWSGI()
			wrapping = WebIDMiddleware(receiver)
			self.environ['HTTP_SSL_CLIENT_CERT'] = x509.as_pem()
			wrapping(self.environ, None)
			self.assertTrue('webid.valid' in receiver.environ)
			self.assertTrue(receiver.environ['webid.valid'])
			self.assertTrue('webid.uri' in receiver.environ)
			self.assertIsNot(receiver.environ['webid.uri'], None)
			self.assertTrue('webid.graph' in receiver.environ)
			# make sure we don't change the original env
			self.assertFalse('webid.valid' in self.environ)
			self.assertFalse('webid.uri' in self.environ)
			self.assertFalse('webid.graph' in self.environ)

	def test_apache(self):
		with httmock.HTTMock(self.webid_server):
			receiver = TestWSGI()
			wrapping = WebIDMiddleware(receiver)
			self.environ['HTTP_SSL_CLIENT_CERT'] = x509.as_pem().replace('\n', ' ')
			wrapping(self.environ, None)
			self.assertTrue('webid.valid' in receiver.environ)
			self.assertTrue(receiver.environ['webid.valid'])
			self.assertTrue('webid.uri' in receiver.environ)
			self.assertIsNot(receiver.environ['webid.uri'], None)
			self.assertTrue('webid.graph' in receiver.environ)

	def test_truncated(self):
		with httmock.HTTMock(self.webid_server):
			cert = x509.as_pem()
			cert = cert[:-2]
			receiver = TestWSGI()
			wrapping = WebIDMiddleware(receiver)
			self.environ['HTTP_SSL_CLIENT_CERT'] = cert
			wrapping(self.environ, None)
			self.assertTrue('webid.valid' in receiver.environ)
			self.assertFalse(receiver.environ['webid.valid'])
			self.assertFalse('webid.uri' in receiver.environ)
			self.assertFalse('webid.graph' in receiver.environ)

	def test_wrong(self):
		with httmock.HTTMock(self.empty_server):
			receiver = TestWSGI()
			wrapping = WebIDMiddleware(receiver)
			self.environ['HTTP_SSL_CLIENT_CERT'] = x509.as_pem()
			wrapping(self.environ, None)
			self.assertTrue('webid.valid' in receiver.environ)
			self.assertFalse(receiver.environ['webid.valid'])
			self.assertTrue('webid.uri' in receiver.environ)
			self.assertIs(receiver.environ['webid.uri'], None)
			self.assertFalse('webid.graph' in receiver.environ)
