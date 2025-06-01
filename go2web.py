"""
go2web - HTTP Client from Scratch
Lab 5 - Web Development Course
"""

import sys
import argparse
from http_client import HTTPClient
from search_engine import SearchEngine
from cache import Cache

def show_help():
    """Display help information"""
    help_text = """
go2web - HTTP Client from Scratch

USAGE:
    go2web -u <URL>         # Make an HTTP request to the specified URL and print the response
    go2web -s <search-term> # Make an HTTP request to search the term and print top 10 results
    go2web -h               # Show this help

EXAMPLES:
    go2web -u https://example.com
    go2web -u http://httpbin.org/json
    go2web -s "python programming"
    go2web -s machine learning

FEATURES:
    - Raw HTTP implementation using TCP sockets
    - Human-readable output (HTML tags stripped)
    - Search functionality with top 10 results
    - HTTP redirect following
    - Response caching
    - Content negotiation (JSON/HTML)

Created by: Negai Marin
Course: Web Development Lab 5
"""
    print(help_text)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='HTTP Client from Scratch', add_help=False)
    parser.add_argument('-u', '--url', help='URL to fetch')
    parser.add_argument('-s', '--search', nargs='+', help='Search term(s)')
    parser.add_argument('-h', '--help', action='store_true', help='Show help')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching')
    parser.add_argument('--cache-ttl', type=int, default=300, help='Cache TTL in seconds (default: 300)')
    
    # Parse known args to handle multiple search terms
    args, unknown = parser.parse_known_args()
    
    # Handle help
    if args.help or len(sys.argv) == 1:
        show_help()
        return
    
    # Initialize cache
    cache = None if args.no_cache else Cache(ttl=args.cache_ttl)
    
    # Initialize HTTP client
    client = HTTPClient(cache=cache)
    
    try:
        if args.url:
            # URL mode
            print(f"Fetching: {args.url}")
            print("-" * 50)
            response = client.get(args.url)
            print(response)
            
        elif args.search:
            # Search mode
            search_term = ' '.join(args.search + unknown)
            print(f"Searching for: '{search_term}'")
            print("-" * 50)
            
            search_engine = SearchEngine(client)
            results = search_engine.search(search_term)
            
            if results:
                print(f"Top {len(results)} results:")
                print()
                
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result['title']}")
                    print(f"   URL: {result['url']}")
                    if result.get('description'):
                        print(f"   {result['description']}")
                    print()
                
                # Interactive mode for accessing results
                while True:
                    try:
                        choice = input("\nEnter result number to visit (1-{}) or 'q' to quit: ".format(len(results)))
                        if choice.lower() == 'q':
                            break
                        
                        num = int(choice)
                        if 1 <= num <= len(results):
                            url = results[num - 1]['url']
                            print(f"\nFetching: {url}")
                            print("-" * 50)
                            response = client.get(url)
                            print(response)
                            print("-" * 50)
                        else:
                            print("Invalid number. Please try again.")
                    except (ValueError, KeyboardInterrupt):
                        break
            else:
                print("No results found.")
        else:
            print("Error: Please specify either -u <URL> or -s <search-term>")
            print("Use -h for help")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()