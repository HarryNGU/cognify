import os
import requests
from bs4 import BeautifulSoup
from .base_processor import BaseProcessor
import logging

logger = logging.getLogger(__name__)

class HTMLProcessor(BaseProcessor):
    """Processor for HTML files and web content"""
    
    def process(self, file_path):
        """
        Process an HTML file and extract its content
        
        Args:
            file_path: Path to the HTML file
            
        Returns:
            dict: Processed content
        """
        self.validate_file(file_path)
        
        result = {
            'content': '',
            'metadata': self.extract_metadata(file_path),
            'structure': {
                'headings': [],
                'links': []
            },
            'images': [],
            'references': []
        }
        
        try:
            # Read the HTML file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                html_content = f.read()
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else ''
            result['metadata']['title'] = title
            
            # Extract main content (remove scripts, styles, etc.)
            for script in soup(["script", "style", "noscript", "iframe", "svg"]):
                script.extract()
            
            # Get text content
            text = soup.get_text(separator='\n', strip=True)
            result['content'] = text
            
            # Extract structure - headings
            headings = []
            for i in range(1, 7):
                for heading in soup.find_all(f'h{i}'):
                    headings.append({
                        'level': i,
                        'text': heading.get_text(strip=True)
                    })
            result['structure']['headings'] = headings
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                if href and not href.startswith('#') and not href.startswith('javascript:'):
                    links.append({
                        'url': href,
                        'text': text if text else href
                    })
            result['structure']['links'] = links
            
            # Extract images
            images = []
            for img in soup.find_all('img', src=True):
                src = img['src']
                alt = img.get('alt', '')
                if src:
                    images.append({
                        'src': src,
                        'alt': alt,
                        'filename': os.path.basename(src) if '/' in src else src
                    })
            result['images'] = images
            
            # Extract meta tags
            meta_tags = {}
            for meta in soup.find_all('meta'):
                name = meta.get('name', meta.get('property', ''))
                content = meta.get('content', '')
                if name and content:
                    meta_tags[name] = content
            result['metadata']['meta_tags'] = meta_tags
            
        except Exception as e:
            logger.error(f"Error processing HTML file {file_path}: {str(e)}")
            result['content'] = f"Error processing HTML: {str(e)}"
        
        return result
