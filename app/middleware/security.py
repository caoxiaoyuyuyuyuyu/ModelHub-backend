"""
Security middleware to filter out automated scanning attempts and reduce log noise.
"""
from flask import request, g
import logging
import re

# Patterns that indicate automated scanning/probing attempts
SCAN_PATTERNS = [
    r'SSH-2\.0',
    r'RTSP/',
    r'SMB',
    r'MSSQLServer',
    r'MongoDB',
    r'Redis',
    r'MySQL',
    r'PostgreSQL',
    r'^EHLO',
    r'^HELP',
    r'^stats',
    r'^serverstatus',
    r'^VERSION',
    r'^Subscribe',
    r'^Query',
    r'^show info',
    r'^GET /nice',
    r'^GET /server-info',
    r'^GET /version',
    r'^\x16\x03',  # SSL/TLS handshake
    r'^\x00',  # Binary protocols
    r'^CNXN',  # ADB protocol
    r'^GIOP',  # CORBA
    r'^JRMI',  # Java RMI
    r'^DIST',  # Erlang distribution
    r'^TNMP',  # TNS protocol
    r'^DmdT',  # DCE RPC
    r'^#ST',  # Telnet
    r'^vp3',  # VNC
    r'^\*1',  # Redis protocol
    r'^stats',  # Memcached
    r'^serverstatus',  # Memcached
]

class SecurityFilter(logging.Filter):
    """Filter to suppress log messages from automated scanning attempts."""
    
    def filter(self, record):
        # Check if this is a bad request error
        if hasattr(record, 'msg') and 'Bad request' in str(record.msg):
            # Check if the request path matches scan patterns
            if hasattr(record, 'args') and record.args:
                request_line = str(record.args[-1]) if record.args else ''
                for pattern in SCAN_PATTERNS:
                    if re.search(pattern, request_line, re.IGNORECASE):
                        return False  # Don't log this
        return True  # Log everything else


def is_scan_attempt(request_line):
    """Check if a request line appears to be a scanning attempt."""
    if not request_line:
        return False
    
    request_str = str(request_line)
    for pattern in SCAN_PATTERNS:
        if re.search(pattern, request_str, re.IGNORECASE):
            return True
    return False


def setup_security_middleware(app):
    """Set up security middleware to filter scan attempts."""
    
    # Add filter to werkzeug logger to suppress scan attempt logs
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.addFilter(SecurityFilter())
    
    @app.before_request
    def check_scan_attempt():
        """Check if request is a scan attempt and handle it silently."""
        # This is handled by Werkzeug's error handling, but we can add
        # additional checks here if needed
        pass
    
    @app.after_request
    def log_security_events(response):
        """Log security events but filter out scan attempts."""
        # Only log actual security issues, not scan attempts
        if response.status_code == 400:
            request_line = f"{request.method} {request.path}"
            if is_scan_attempt(request_line):
                # Silently handle scan attempts - don't log them
                pass
        return response

