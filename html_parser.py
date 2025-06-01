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
        """Extract search results from Google (basic implementation)"""
        results = []
        
        # Google result pattern (simplified)
        result_pattern = r'<div[^>]*class="[^"]*g[^"]*"[^>]*>(.*?)</div>'
        result_matches = re.findall(result_pattern, html, re.DOTALL | re.IGNORECASE)
        
        for match in result_matches:
            title = ""
            url = ""
            description = ""
            
            # Extract title and URL
            title_match = re.search(r'<h3[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', match, re.DOTALL | re.IGNORECASE)
            if title_match:
                url = title_match.group(1)
                title = self.extract_text(title_match.group(2))
            
            # Extract description
            desc_match = re.search(r'<span[^>]*class="[^"]*st[^"]*"[^>]*>(.*?)</span>', match, re.DOTALL | re.IGNORECASE)
            if desc_match:
                description = self.extract_text(desc_match.group(1))
            
            if title and url:
                results.append({
                    'title': title,
                    'url': url,
                    'description': description
                })
        
        return results