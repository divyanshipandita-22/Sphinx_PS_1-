"""
URL Scraper for product pages
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

class ProductScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    def scrape(self, url):
        """
        Scrape product description from URL
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Try to find product description areas
            product_text = self._extract_product_text(soup)
            
            if not product_text or len(product_text) < 50:
                return "Could not extract product description. Please try pasting the text manually."
            
            return product_text
            
        except requests.exceptions.Timeout:
            return "Timeout: The website took too long to respond."
        except requests.exceptions.ConnectionError:
            return "Connection error: Could not reach the website."
        except Exception as e:
            return f"Error scraping URL: {str(e)}"
    
    def _extract_product_text(self, soup):
        """
        Intelligently extract product-related text
        """
        text_parts = []
        
        # Priority areas to look for product info
        priority_selectors = [
            '[class*="description"]', 
            '[class*="product"]', 
            '[class*="details"]',
            '[id*="description"]', 
            '[id*="product"]', 
            '[id*="details"]',
            '.product-description', 
            '.product-details', 
            '.description',
            '.product-info',
            '[itemprop="description"]'
        ]
        
        # Extract from priority areas
        for selector in priority_selectors:
            try:
                elements = soup.select(selector)
                for elem in elements:
                    if elem.name == 'meta':
                        content = elem.get('content', '')
                        if content:
                            text_parts.append(content)
                    else:
                        text = elem.get_text(strip=True)
                        if text and len(text) > 20:
                            text_parts.append(text)
            except:
                pass
        
        # Also check meta tags
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            text_parts.append(meta_desc.get('content'))
        
        og_desc = soup.find('meta', {'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            text_parts.append(og_desc.get('content'))
        
        # If no priority content, get main text
        if not text_parts:
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            if main_content:
                text_parts.append(main_content.get_text())
        
        # Combine and clean
        full_text = ' '.join(text_parts)
        full_text = re.sub(r'\s+', ' ', full_text)
        full_text = full_text.strip()
        
        # Remove common non-product text
        remove_patterns = [
            r'Add to cart.*?', r'Share.*?', r'Follow us.*?',
            r'Sign up.*?', r'Newsletter.*?', r'Copyright.*?'
        ]
        for pattern in remove_patterns:
            full_text = re.sub(pattern, '', full_text, flags=re.IGNORECASE)
        
        # Limit length
        return full_text[:4000]
    
    def extract_brand_name(self, url, soup=None):
        """
        Attempt to extract brand name from URL or page
        """
        # Try from URL
        domain = urlparse(url).netloc
        brand = domain.replace('www.', '').split('.')[0]
        
        # Try from page metadata
        if soup:
            meta_brand = soup.find('meta', {'property': 'og:site_name'})
            if meta_brand:
                brand = meta_brand.get('content', brand)
        
        return brand.title()

# Test
if __name__ == "__main__":
    print("Testing Web Scraper...")
    scraper = ProductScraper()
    print("Scraper ready!")