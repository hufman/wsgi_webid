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
