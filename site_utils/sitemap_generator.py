#!/usr/bin/env python3


import sys
import requests
import html
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


def crawl_site(start_url: str) -> set:
    """
    Crawls a website starting from start_url to find all internal links.

    Args:
        start_url: The URL of the website's homepage.

    Returns:
        A set of unique internal URLs found on the site.
    """
    parsed_start_url = urlparse(start_url)
    base_domain = parsed_start_url.netloc

    urls_to_crawl = {start_url}
    crawled_urls = set()

    print(f"Starting crawl at: {start_url}")

    while urls_to_crawl:
        current_url = urls_to_crawl.pop()
        if current_url in crawled_urls:
            continue

        try:
            response = requests.get(current_url, timeout=5)
            # Only process successful text/html responses
            if response.status_code != 200 or 'text/html' not in response.headers.get('Content-Type', ''):
                crawled_urls.add(current_url)
                continue

            print(f"   -> Crawling: {current_url}")
            crawled_urls.add(current_url)

            soup = BeautifulSoup(response.text, 'html.parser')

            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Create an absolute URL from a possible relative link
                absolute_url = urljoin(current_url, href).split('#')[0] # Remove fragments

                # Check if the link belongs to the same domain and hasn't been crawled
                if urlparse(absolute_url).netloc == base_domain and absolute_url not in crawled_urls:
                    urls_to_crawl.add(absolute_url)

        except requests.RequestException as e:
            print(f"   [!] Error crawling {current_url}: {e}")
            crawled_urls.add(current_url) # Mark as crawled to avoid retries

    print(f"Crawl finished. Found {len(crawled_urls)} unique pages.")
    return crawled_urls

def generate_sitemap(urls: set, filename: str = "sitemap.xml"):
    """
    Generates a sitemap.xml file from a set of URLs.

    Args:
        urls: A set of URLs to include in the sitemap.
        filename: The name of the output file.
    """
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for url in sorted(list(urls)):
        # Escape special XML characters in the URL
        escaped_url = html.escape(url)
        xml_content += f"  <url>\n    <loc>{escaped_url}</loc>\n  </url>\n"

    xml_content += '</urlset>'

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        print(f"Sitemap successfully generated and saved to '{filename}'")
    except IOError as e:
        print(f"Error writing to file {filename}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python sitemap_generator.py <https://your-website.com>")
        sys.exit(1)

    homepage_url = sys.argv[1]
    
    # Simple validation for the URL
    if not urlparse(homepage_url).scheme or not urlparse(homepage_url).netloc:
        print(f"Error: Invalid URL provided: '{homepage_url}'")
        print("Please provide a full URL, e.g., https://www.example.com")
        sys.exit(1)

    found_urls = crawl_site(homepage_url)
    if found_urls:
        generate_sitemap(found_urls)
