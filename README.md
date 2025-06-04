# go2web - HTTP Client

Lab 5 - Negai Marin

## Setup

```bash
python setup.py
```

## Usage

```bash
# Help
go2web.bat -h

# Fetch URL  
go2web.bat -u https://httpbin.org/json
go2web.bat -u https://example.com

# Search
go2web.bat -s "python programming"
go2web.bat -s javascript

# Options
go2web.bat -u https://example.com --no-cache
go2web.bat -u https://example.com --cache-ttl 600
```

## Test

```bash
python test.py
```

## Examples

**Basic fetch:**
```bash
$ go2web.bat -u https://httpbin.org/json
Fetching: https://httpbin.org/json
--------------------------------------------------
slideshow: {
  "author": "Yours Truly",
  "title": "Sample Slide Show"
}
```

**Search:**
```bash
$ go2web.bat -s "python tutorial"
Searching for: 'python tutorial'
--------------------------------------------------
Top 5 results:

1. Python Tutorial
   URL: https://docs.python.org/3/tutorial/

Enter result number to visit (1-5) or 'q' to quit: 1
[Shows page content]
```

**Redirects:**
```bash
$ go2web.bat -u http://github.com
Redirecting to: https://github.com
[GitHub content]
```

**Caching:**
```bash
$ go2web.bat -u https://httpbin.org/delay/2
[Takes 2 seconds]

$ go2web.bat -u https://httpbin.org/delay/2
(From cache)
[Instant]
```

**Errors:**
```bash
$ go2web.bat -u https://httpbin.org/status/404
Error: HTTP 404 NOT FOUND
```