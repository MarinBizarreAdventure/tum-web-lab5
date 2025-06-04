"""
HTML Parser for extracting readable text from HTML content
"""

import re

class HTMLParser:
    def __init__(self):
        # HTML tags to remove completely (including content)
        self.remove_tags = ['script', 'style', 'noscript', 'head', 'meta', 'link']
        
        # Block-level tags that should add line breaks
        self.block_tags = ['div', 'p', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                          'ul', 'ol', 'li', 'blockquote', 'pre', 'hr', 'table', 
                          'tr', 'td', 'th', 'section', 'article', 'aside', 'nav']
    
    def extract_text(self, html):
        """Extract readable text from HTML"""
        if not html:
            return ""
        
        # Remove unwanted tags and their content
        for tag in self.remove_tags:
            pattern = f'<{tag}[^>]*>.*?</{tag}>'
            html = re.sub(pattern, '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Add line breaks for block elements
        for tag in self.block_tags:
            # Opening tags
            html = re.sub(f'<{tag}[^>]*>', '\n', html, flags=re.IGNORECASE)
            # Closing tags
            html = re.sub(f'</{tag}>', '\n', html, flags=re.IGNORECASE)
        
        # Handle special cases
        html = re.sub(r'<br[^>]*>', '\n', html, flags=re.IGNORECASE)
        html = re.sub(r'<hr[^>]*>', '\n---\n', html, flags=re.IGNORECASE)
        
        # Remove all remaining HTML tags
        html = re.sub(r'<[^>]+>', '', html)
        
        # Decode HTML entities
        html = self._decode_html_entities(html)
        
        # Clean up whitespace
        lines = html.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove extra whitespace within lines
            line = re.sub(r'\s+', ' ', line.strip())
            if line:  # Only add non-empty lines
                cleaned_lines.append(line)
        
        # Join lines and limit consecutive newlines
        text = '\n'.join(cleaned_lines)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _decode_html_entities(self, text):
        """Decode common HTML entities"""
        entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
            '&nbsp;': ' ',
            '&ndash;': '–',
            '&mdash;': '—',
            '&ldquo;': '"',
            '&rdquo;': '"',
            '&lsquo;': ''',
            '&rsquo;': ''',
            '&hellip;': '…',
            '&copy;': '©',
            '&reg;': '®',
            '&trade;': '™'
        }
        
        for entity, replacement in entities.items():
            text = text.replace(entity, replacement)
        
        # Handle numeric entities
        text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
        text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), text)
        
        return text
    
    def extract_search_results(self, html, search_engine='duckduckgo'):
        """Extract search results from search engine HTML"""
        results = []
        
        if search_engine == 'duckduckgo':
            results = self._extract_duckduckgo_results(html)
        elif search_engine == 'google':
            results = self._extract_google_results(html)
        
        return results[:10]  # Return top 10 results
    
    def _extract_duckduckgo_results(self, html):
        """Extract search results from DuckDuckGo"""
        results = []
        
        # DuckDuckGo result pattern
        # Look for result containers
        result_pattern = r'<article[^>]*class="[^"]*result[^"]*"[^>]*>(.*?)</article>'
        result_matches = re.findall(result_pattern, html, re.DOTALL | re.IGNORECASE)
        
        for match in result_matches:
            title = ""
            url = ""
            description = ""
            
            # Extract title and URL
            title_match = re.search(r'<h2[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', match, re.DOTALL | re.IGNORECASE)
            if title_match:
                url = title_match.group(1)
                title = self.extract_text(title_match.group(2))
            
            # Extract description
            desc_match = re.search(r'<span[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</span>', match, re.DOTALL | re.IGNORECASE)
            if desc_match:
                description = self.extract_text(desc_match.group(1))
            
            if title and url:
                results.append({
                    'title': title,
                    'url': url,
                    'description': description
                })
        
        # Fallback: simpler pattern matching
        if not results:
            # Look for any links that might be results
            link_pattern = r'<a[^>]*href="(https?://[^"]*)"[^>]*>([^<]*)</a>'
            links = re.findall(link_pattern, html, re.IGNORECASE)
            
            for url, title in links[:10]:
                if title.strip() and not url.startswith('https://duckduckgo.com'):
                    results.append({
                        'title': title.strip(),
                        'url': url,
                        'description': ""
                    })
        
        return results
    
    def _extract_google_results(self, html):
        """Extract search results from Google"""
        results = []
        
        # Google result patterns (multiple patterns for better coverage)
        patterns = [
            # Main result pattern
            r'<div[^>]*data-ved[^>]*>.*?<h3[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?</h3>.*?(?:<div[^>]*class="[^"]*VwiC3b[^"]*"[^>]*>(.*?)</div>)?',
            # Alternative pattern
            r'<div[^>]*class="[^"]*g[^"]*"[^>]*>.*?<h3[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?</h3>.*?(?:<span[^>]*class="[^"]*st[^"]*"[^>]*>(.*?)</span>)?',
            # Simple link pattern
            r'<a[^>]*href="(/url\?q=([^&]*)[^"]*)"[^>]*><h3[^>]*>(.*?)</h3></a>',
            # Direct URL pattern
            r'<h3[^>]*class="[^"]*"[^>]*><a[^>]*href="([^"]*)"[^>]*>(.*?)</a></h3>'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                if len(match) >= 2:
                    url = match[0] if len(match) >= 1 else ""
                    title = match[1] if len(match) >= 2 else ""
                    description = match[2] if len(match) >= 3 else ""
                    
                    # Handle Google's URL encoding
                    if url.startswith('/url?q='):
                        # Extract actual URL from Google's redirect
                        import urllib.parse
                        try:
                            parsed = urllib.parse.parse_qs(url[7:])  # Remove '/url?q='
                            if 'q' in parsed:
                                url = parsed['q'][0]
                        except:
                            continue
                    
                    # Clean up the data
                    if url and title:
                        title_clean = self.extract_text(title).strip()
                        desc_clean = self.extract_text(description).strip() if description else ""
                        
                        # Filter out Google's own links and ads
                        if (title_clean and url.startswith('http') and 
                            'google.com' not in url and 
                            'googleusercontent.com' not in url and
                            not any(skip in url.lower() for skip in ['ads', 'sponsored']) and
                            len(title_clean) > 5):
                            
                            results.append({
                                'title': title_clean,
                                'url': url,
                                'description': desc_clean
                            })
        
        # If main patterns didn't work, try fallback extraction
        if not results:
            results = self._extract_google_fallback(html)
        
        # Remove duplicates
        seen_urls = set()
        unique_results = []
        for result in results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        return unique_results
    
    def _extract_google_fallback(self, html):
        """Fallback method for Google results"""
        results = []
        
        # Look for any links that might be search results
        link_patterns = [
            r'<a[^>]*href="(https?://[^"]*)"[^>]*>([^<]+)</a>',
            r'href="(/url\?q=([^&"]*)[^"]*)"[^>]*>([^<]+)',
        ]
        
        for pattern in link_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            
            for match in matches:
                if len(match) >= 2:
                    if len(match) == 3 and match[0].startswith('/url'):
                        # Google redirect URL
                        url = match[1]
                        title = match[2]
                    else:
                        # Direct URL
                        url = match[0]
                        title = match[1]
                    
                    # Clean and validate
                    title_clean = self.extract_text(title).strip()
                    
                    if (title_clean and url.startswith('http') and 
                        len(title_clean) > 10 and
                        not any(skip in url.lower() for skip in 
                               ['google.com', 'youtube.com', 'facebook.com', 'twitter.com', 'ads'])):
                        
                        results.append({
                            'title': title_clean,
                            'url': url,
                            'description': ""
                        })
        
        return results[:10]