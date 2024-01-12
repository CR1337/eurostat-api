import ssl
import sys

import requests
import urllib3

# Soweit ich es verstanden habe, verwenden die Eurostat-Server einen veralteten
# Sicherheitsstandard. Windows stört sich daran nicht, Linux allerdings schon.
# Dieser Code hier ist für die Kommunikation mit dem Server verantwortlich.
# Er prüft zunächst, auf welchem Betriebssystem er läuft und kümmert sich dann
# um den veralteten Standard oder auch nicht. Wichting für die Benutzung ist
# nur, dass dese Datei die Funktion `get` bereitstellt, die sich genauso
# verhält, wie die Funktion `requests.get` aus der `requests`-Bibliothek.

if 'linux' in sys.platform.lower():
    def get(**kwargs) -> requests.Response:
        class CustomHttpAdapter(requests.adapters.HTTPAdapter):

            def __init__(self, ssl_context: ssl.SSLContext = None, **kwargs):
                self._ssl_context = ssl_context
                super().__init__()

            def init_poolmanager(
                self, connections: int, maxsize: int,
                block: bool = False, **kwargs
            ):
                self.poolmanager = urllib3.poolmanager.PoolManager(
                    num_pools=connections, maxsize=maxsize,
                    block=block, ssl_context=self._ssl_context
                )

        def get_legacy_session() -> requests.Session:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
            session = requests.session()
            session.mount('https://', CustomHttpAdapter(context))
            return session

        return get_legacy_session().get(**kwargs)

else:  # windows
    def get(**kwargs) -> requests.Response:
        return requests.get(**kwargs)
