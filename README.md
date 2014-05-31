WSGI\_WebID
===========

A WSGI middleware to authenticate WebID connections.

After wrapping an existing WSGI application with this middleware, the application will receive several new environment variables, depending on the validity of the WebID request.

Constructor
-----------

The constructor for this middleware takes a few arguments:

- `application` - The wrapped WSGI application that will actually handle requests
- `envkey` - The name of the WSGI environment parameter that contains any client SSL certificates, defaults to `HTTP_SSL_CLIENT_CERT`
- `debug` - A boolean of whether to store some extra debug information in the environment, defaults to True

Environment
-----------

The following extra variables may be found in the environment:

- `webid.valid` - Will be present if a client SSL certificate was given, and it will be True if all of the validity checks passed or False otherwise
- `webid.uri` - Will be set to the address contained within the client SSL certificate
- `webid.profile` - If webid.valid, this contains the webid.fetcher.WebIDLoader object for further examination
- `webid.graph` - If webid.valid, this contains an RDFLib graph of the parsed information from the WebID document
- `webid.validator` - If constructed with the debug flag, this contains the webid.validator.WebIDValidator object used to parse the WebID
- `webid.cert` - If constructed with the debug flag, this contains the certstr from the HTTP request that was used

## Web Server Setup

The web server in front of the wrapped WSGI application must listen on HTTPS, in order to allow the WebID client SSL certificate to be sent. The web server must also be configured to accept client SSL certificates, but without verifying them against a CA. The web server must also be configured to pass the entire client SSL certificate to the backend process, either through an HTTP request header through a reverse proxy, or directly as an CGI/WSGI environment variable.

### Apache httpd Setup

First, the server or vhost must be configured as a normal SSL website, by setting `SSLEngine`, `SSLCertificateFile`, and `SSLCertificateKeyFile`.

Next, it must be configured to accept a client cert and pass it on to the backend. Unfortunately, Apache can not request a client SSL certificate without not verifying it against a CA, so it has to be marked as optional and the client must be forced to send it.

    SSLVerifyClient optional_no_ca
    SSLVerifyDepth 2
    RequestHeader set SSL_CLIENT_CERT "%{SSL_CLIENT_CERT}s"

### Flask Setup

After setting up the web server in front, Flask has to wrap its WSGI application with this WebID middleware. There must be a line that wraps the `app.wsgi_app`:

    from wsgi_webid import WebIDMiddleware
    app.wsgi_app = WebIDMiddleware(app.wsgi_app, envkey="HTTP_SSL_CLIENT_CERT")

Then, app can be used with any WSGI server, and WebIDMiddleware will automatically work.


[![Build Status](https://travis-ci.org/hufman/wsgi_webid.svg?branch=master)](https://travis-ci.org/hufman/wsgi_webid)
