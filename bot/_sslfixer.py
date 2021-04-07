import os
import ssl
from . import vars

try:
    context = ssl.create_default_context()
    der_certs = context.get_ca_certs(binary_form=True)
    pem_certs = [ssl.DER_cert_to_PEM_cert(der) for der in der_certs]
    path = os.path.join(vars.directory, 'nativecacerts.pem')

    with open(path, 'w') as outfile:
        for pem in pem_certs:
            outfile.write(pem + '\n')
    os.environ['REQUESTS_CA_BUNDLE'] = path
except:
    pass
