"""
HTTP Client Implementation using raw TCP sockets
No built-in HTTP libraries allowed
"""

import socket
import ssl
import json
from urllib.parse import urlparse, quote
from html_parser import HTMLParser

class HTTPClient:
    def __init__(self, cache=None, timeout=30, max_redirects=5):
        self.cache = cache
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.user_agent = "go2web/1.0"
        
    def get(self, url, follow_redirects=True):
        """Make HTTP GET request to URL"""
        # Check cache first
        if self.cache:
            cached_response = self.cache.get(url)
            if cached_response:
                print("(From cache)")
                return cached_response
        
        response = self._make_request(url, follow_redirects)
        
        # Cache successful responses
        if self.cache and response:
            self.cache.set(url, response)
        
        return response
    
    def _make_request(self, url, follow_redirects=True, redirect_count=0):
        """Internal method to make HTTP request"""
        if redirect_count > self.max_redirects:
            raise Exception("Too many redirects")
        
        # Parse URL
        parsed = urlparse(url)
        if not parsed.scheme:
            url = "http://" + url
            parsed = urlparse(url)
        
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        path = parsed.path or '/'
        if parsed.query:
            path += '?' + parsed.query
        
        if not host:
            raise ValueError("Invalid URL: no host specified")
        
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        
        try:
            # Connect
            if parsed.scheme == 'https':
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=host)
            
            sock.connect((host, port))
            
            # Prepare HTTP request
            request = self._build_request(host, path)
            
            # Send request
            sock.sendall(request.encode('utf-8'))
            
            # Receive response
            response_data = self._receive_response(sock)
            
            # Parse response
            headers, body = self._parse_response(response_data)
            
            # Handle redirects
            if follow_redirects and headers.get('status_code') in [301, 302, 303, 307, 308]:
                location = headers.get('location')
                if location:
                    if location.startswith('/'):
                        # Relative redirect
                        location = f"{parsed.scheme}://{host}:{port}{location}"
                    elif not location.startswith('http'):
                        # Relative to current path
                        base_url = f"{parsed.scheme}://{host}:{port}"
                        location = base_url + '/' + location.lstrip('/')
                    
                    print(f"Redirecting to: {location}")
                    return self._make_request(location, follow_redirects, redirect_count + 1)
            
            # Process response body based on content type
            return self._process_response_body(headers, body)
            
        except socket.timeout:
            raise Exception(f"Request timeout after {self.timeout} seconds")
        except socket.gaierror:
            raise Exception(f"Could not resolve hostname: {host}")
        except ConnectionRefusedError:
            raise Exception(f"Connection refused to {host}:{port}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
        finally:
            sock.close()
    
    def _build_request(self, host, path):
        """Build HTTP request string"""
        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += f"User-Agent: {self.user_agent}\r\n"
        request += "Accept: text/html,application/json,*/*\r\n"
        request += "Accept-Encoding: identity\r\n"
        request += "Connection: close\r\n"
        request += "\r\n"
        return request
    
    def _receive_response(self, sock):
        """Receive complete HTTP response"""
        response_data = b''
        
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk
            except socket.timeout:
                break
        
        return response_data
    
    def _parse_response(self, response_data):
        """Parse HTTP response into headers and body"""
        try:
            response_str = response_data.decode('utf-8', errors='ignore')
        except UnicodeDecodeError:
            response_str = response_data.decode('latin-1', errors='ignore')
        
        if '\r\n\r\n' not in response_str:
            raise Exception("Invalid HTTP response: no header-body separator found")
        
        header_section, body = response_str.split('\r\n\r\n', 1)
        header_lines = header_section.split('\r\n')
        
        # Parse status line
        if not header_lines:
            raise Exception("Invalid HTTP response: no status line")
        
        status_line = header_lines[0]
        status_parts = status_line.split(' ', 2)
        if len(status_parts) < 2:
            raise Exception("Invalid HTTP status line")
        
        status_code = int(status_parts[1])
        status_message = status_parts[2] if len(status_parts) > 2 else ""
        
        # Parse headers
        headers = {
            'status_code': status_code,
            'status_message': status_message
        }
        
        for line in header_lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
        
        return headers, body
    
    def _process_response_body(self, headers, body):
        """Process response body based on content type"""
        content_type = headers.get('content-type', '').lower()
        status_code = headers.get('status_code')
        
        # Check for errors
        if status_code >= 400:
            error_msg = f"HTTP {status_code} {headers.get('status_message', '')}"
            if body:
                # Try to extract error message from body
                if 'json' in content_type:
                    try:
                        error_data = json.loads(body)
                        if isinstance(error_data, dict):
                            error_msg += f"\n{error_data.get('error', error_data.get('message', body[:200]))}"
                    except:
                        error_msg += f"\n{body[:200]}"
                else:
                    # Extract text from HTML error pages
                    parser = HTMLParser()
                    text = parser.extract_text(body)
                    if text.strip():
                        error_msg += f"\n{text[:200]}"
            raise Exception(error_msg)
        
        # Process based on content type
        if 'json' in content_type:
            try:
                json_data = json.loads(body)
                return self._format_json(json_data)
            except json.JSONDecodeError:
                return f"Invalid JSON response:\n{body}"
        
        elif 'html' in content_type or '<html' in body.lower():
            # Parse HTML and extract readable text
            parser = HTMLParser()
            text = parser.extract_text(body)
            return text if text.strip() else "No readable content found."
        
        else:
            # Plain text or other content
            return body
    
    def _format_json(self, json_data):
        """Format JSON data for human-readable output"""
        if isinstance(json_data, dict):
            result = []
            for key, value in json_data.items():
                if isinstance(value, (dict, list)):
                    result.append(f"{key}: {json.dumps(value, indent=2)}")
                else:
                    result.append(f"{key}: {value}")
            return "\n".join(result)
        elif isinstance(json_data, list):
            result = []
            for i, item in enumerate(json_data):
                result.append(f"[{i}] {json.dumps(item, indent=2) if isinstance(item, (dict, list)) else item}")
            return "\n".join(result)
        else:
            return str(json_data)