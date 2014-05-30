import re
import logging
import webid.validator

class WebIDMiddleware(object):
	def __init__(self, application, envkey="HTTP_SSL_CLIENT_CERT", debug=True):
		self.application = application
		self.envkey = envkey
		self.debug = debug

	def __call__(self, environ, start_response):
		if self.envkey in environ:
			try:
				cert = environ[self.envkey]
				environ = dict(environ)
				environ.update(self.parse_webid(cert))
			except Exception as e:
				logging.error("Exception while parsing webid: %s"%(str(e),))
		return self.application(environ, start_response)

	@staticmethod
	def _reformat_cert(cert):
		""" Make sure the cert looks like a real cert
		    Sometimes the cert doesn't have linebreaks
		"""
		certre = re.compile('(-----BEGIN CERTIFICATE-----)([^-]*)(-----END CERTIFICATE-----)', re.DOTALL)
		certparts = certre.search(cert)
		if certparts:
			header = certparts.group(1)
			cert = certparts.group(2)
			footer = certparts.group(3)
			cert = cert.replace(' ', '\n')
			return str(header) + str(cert) + str(footer)
		else:
			logging.debug("Couldn't parse cert %s"%(cert,))

	def parse_webid(self, cert):
		env = {}
		env['webid.valid'] = False
		cert = self._reformat_cert(cert)
		if not cert:        # did not find a cert
			return env
		validator = webid.validator.WebIDValidator(certstr=cert)
		valid, validator = validator.validate()
		uri = validator.validatedURI
		env['webid.uri'] = uri
		profile = validator.profiles.get(uri)
		if profile:
			env['webid.valid'] = True
			env['webid.profile'] = profile
			env['webid.graph'] = profile.graph

		if self.debug:
			env['webid.validator'] = validator
			env['webid.cert'] = cert

		return env
