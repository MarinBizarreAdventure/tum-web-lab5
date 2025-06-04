"""
Search Engine Implementation
Supports multiple search engines with fallback options
"""

from urllib.parse import quote
from html_parser import HTMLParser

class SearchEngine:
    def __init__(self, http_client):
        self.http_client = http_client
        self.html_parser = HTMLParser()
        
        # Search engines with their URL patterns
        self.engines = {
            'google': {
                'url': 'https://www.google.com/search?q={}',
                'name': 'Google'
            },
            'bing': {
                'url': 'https://www.bing.com/search?q={}',
                'name': 'Bing'
            },
            'duckduckgo': {
                'url': 'https://duckduckgo.com/html/?q={}',
                'name': 'DuckDuckGo'
            },
            'startpage': {
                'url': 'https://www.startpage.com/sp/search?query={}',
                'name': 'Startpage'
            }
        }
        
        self.default_engine = 'google'
    
    def search(self, query, engine=None):
        """Search for a query using the specified search engine"""
        if not query.strip():
            raise ValueError("Search query cannot be empty")
        
        engine = engine or self.default_engine
        
        # Try the specified engine first
        if engine in self.engines:
            try:
                return self._search_with_engine(query, engine)
            except Exception as e:
                print(f"Error with {self.engines[engine]['name']}: {e}")
        
        # Try fallback engines
        for fallback_engine in self.engines:
            if fallback_engine != engine:
                try:
                    print(f"Trying {self.engines[fallback_engine]['name']}...")
                    return self._search_with_engine(query, fallback_engine)
                except Exception as e:
                    print(f"Error with {self.engines[fallback_engine]['name']}: {e}")
                    continue
        
        raise Exception("All search engines failed")
    
    def _search_with_engine(self, query, engine):
        """Perform search with a specific engine"""
        if engine not in self.engines:
            raise ValueError(f"Unknown search engine: {engine}")
        
        # Encode query for URL
        encoded_query = quote(query)
        search_url = self.engines[engine]['url'].format(encoded_query)
        
        print(f"Searching with {self.engines[engine]['name']}...")
        
        # Make the search request
        html_response = self._make_search_request(search_url)
        
        # Extract results
        results = self._extract_results(html_response, engine)
        
        if not results:
            # Try alternative extraction methods
            results = self._extract_results_fallback(html_response)
        
        return results
    
    def _make_search_request(self, url):
        """Make HTTP request to search engine with proper headers"""
        # Temporarily override user agent for search engines
        original_ua = self.http_client.user_agent
        
        # Use a more realistic user agent for Google
        if 'google.com' in url:
            self.http_client.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        else:
            self.http_client.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        try:
            # Get raw HTML response instead of processed text
            response_data = self._get_raw_html(url)
            return response_data
        finally:
            self.http_client.user_agent = original_ua
    
    def _get_raw_html(self, url):
        """Get raw HTML response for parsing"""
        from urllib.parse import urlparse
        import socket
        import ssl
        
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        path = parsed.path or '/'
        if parsed.query:
            path += '?' + parsed.query
        
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        
        try:
            # Connect
            if parsed.scheme == 'https':
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=host)
            
            sock.connect((host, port))
            
            # Build request with search engine headers
            request = f"GET {path} HTTP/1.1\r\n"
            request += f"Host: {host}\r\n"
            
            # Use appropriate User-Agent based on search engine
            if 'google.com' in url:
                request += "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36\r\n"
            else:
                request += "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36\r\n"
            
            request += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
            request += "Accept-Language: en-US,en;q=0.9\r\n"
            request += "Accept-Encoding: identity\r\n"
            request += "Cache-Control: no-cache\r\n"
            request += "Pragma: no-cache\r\n"
            request += "Connection: close\r\n"
            
            # Add cookies for Google (helps with blocking)
            if 'google.com' in url:
                request += "Cookie: CONSENT=YES+cb.20220419-17-p0.en+FX+{};\r\n".format(int(time.time()))
            
            request += "\r\n"
            
            # Send request
            sock.sendall(request.encode('utf-8'))
            
            # Receive response
            response_data = b''
            while True:
                try:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
                except socket.timeout:
                    break
            
            # Extract body from HTTP response
            response_str = response_data.decode('utf-8', errors='ignore')
            if '\r\n\r\n' in response_str:
                headers, body = response_str.split('\r\n\r\n', 1)
                
                # Check for redirects or errors
                if '301' in headers or '302' in headers:
                    # Handle redirects for search engines
                    import re
                    location_match = re.search(r'Location: ([^\r\n]+)', headers, re.IGNORECASE)
                    if location_match:
                        redirect_url = location_match.group(1).strip()
                        if redirect_url.startswith('/'):
                            redirect_url = f"https://{host}{redirect_url}"
                        print(f"Following redirect to: {redirect_url}")
                        return self._get_raw_html(redirect_url)
                
                return body
            
            return response_str
            
        except Exception as e:
            raise Exception(f"Failed to fetch search results: {e}")
        finally:
            sock.close()
    
    def _extract_results(self, html, engine):
        """Extract search results using engine-specific patterns"""
        return self.html_parser.extract_search_results(html, engine)
    
    def _extract_results_fallback(self, html):
        """Fallback method to extract any links that look like search results"""
        results = []
        
        import re
        
        # Look for common link patterns
        patterns = [
            r'<a[^>]*href="(https?://[^"]*)"[^>]*>([^<]*)</a>',
            r'<a[^>]*href="([^"]*)"[^>]*title="([^"]*)"',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for url, title in matches:
                # Filter out navigation links and ads
                if (title.strip() and 
                    not any(skip in url.lower() for skip in ['duckduckgo.com', 'google.com', 'bing.com', 'ads', 'sponsored']) and
                    url.startswith('http')):
                    
                    results.append({
                        'title': self.html_parser.extract_text(title),
                        'url': url,
                        'description': ""
                    })
        
        # Remove duplicates
        seen_urls = set()
        unique_results = []
        for result in results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        return unique_results[:10]
    
    def get_available_engines(self):
        """Get list of available search engines"""
        return list(self.engines.keys())
    
    def set_default_engine(self, engine):
        """Set the default search engine"""
        if engine in self.engines:
            self.default_engine = engine
        else:
            raise ValueError(f"Unknown search engine: {engine}")