# Access log in Apache combined format for AWStats, with the visitor's real IP.
# Requests arrive through cloudflared, so the socket peer is always Tower; Cloudflare
# puts the visitor's address in CF-Connecting-IP. LAN requests without it log the peer.
from gunicorn.glogging import Logger

bind = "0.0.0.0:8000"
workers = 2
timeout = 120
accesslog = "/app/logs/access.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'


class CloudflareLogger(Logger):
    def atoms(self, resp, req, environ, request_time):
        atoms = super().atoms(resp, req, environ, request_time)
        atoms["h"] = environ.get("HTTP_CF_CONNECTING_IP") or atoms["h"]
        return atoms


logger_class = CloudflareLogger
