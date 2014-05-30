# heavily based on https://gist.github.com/eskil/2338529
import time
from M2Crypto import ASN1, EVP, RSA, X509

def update_cert_expiration(cert, days=365):
	t = long(time.time())
	now = ASN1.ASN1_UTCTIME()
	now.set_time(t)
	expire = ASN1.ASN1_UTCTIME()
	expire.set_time(t + days * 24 * 60 * 60)
	cert.set_not_before(now)
	cert.set_not_after(expire)

def create_rsa_key(bits=1024):
	rsa = RSA.gen_key(bits, 65537, lambda:None)
	return rsa

def create_self_signed_cert(rsa, subject={'CN':'Testing'}, san=None):
	""" Creates a self-signed cert
	    Pass in an RSA private key object
	    Pass in a dictionary of subject name data, using C ST L O OU CN keys
	    Pass in an optional san like 'DNS:example.com'
	    Returns a X509.X509 object
	"""
	pk = EVP.PKey()
	pk.assign_rsa(rsa)

	name = X509.X509_Name()
	for key in ['C', 'ST', 'L', 'O', 'OU', 'CN']:
		if subject.get(key, None):
			setattr(name, key, subject[key])

	cert = X509.X509()
	cert.set_serial_number(1)
	cert.set_version(2)
	update_cert_expiration(cert)
	cert.set_issuer(name)
	cert.set_subject(name)
	cert.set_pubkey(pk)
	cert.add_ext(X509.new_extension('basicConstraints', 'CA:FALSE'))
	cert.add_ext(X509.new_extension('subjectKeyIdentifier', cert.get_fingerprint()))
	cert.add_ext(X509.new_extension('subjectAltName', san))
	cert.sign(pk, 'sha1')
	return cert
