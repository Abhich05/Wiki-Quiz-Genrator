"""
Enhanced Wikipedia service with entity extraction and section parsing
"""
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional, Tuple
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
import time

logger = logging.getLogger(__name__)


class EnhancedWikipediaService:
    """
    Enhanced Wikipedia scraping with entity extraction and section parsing
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WikiQuizBot/2.0 (Educational Purpose; +https://github.com/Abhich05/Wiki-Quiz-Genrator)'
        })
        self.timeout = 15
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def scrape_full_article(self, url: str) -> Dict:
        """
        Scrape complete Wikipedia article with all metadata
        
        Returns:
            Dict containing:
            - title: Article title
            - summary: First paragraph
            - content: Full article text
            - sections: List of section titles
            - raw_html: Original HTML
            - key_entities: Extracted entities
            - infobox: Structured data from infobox
        """
        logger.info(f"Scraping Wikipedia article: {url}")
        start_time = time.time()
        
        try:
            # Validate and normalize URL
            url = self._normalize_url(url)
            
            # Fetch article
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract data
            title = self._extract_title(soup)
            summary = self._extract_summary(soup)
            content, sections = self._extract_content_and_sections(soup)
            key_entities = self._extract_entities(soup, content)
            infobox = self._extract_infobox(soup)
            
            processing_time = time.time() - start_time
            
            logger.info(f"Successfully scraped article: {title} ({processing_time:.2f}s)")
            
            return {
                "url": url,
                "title": title,
                "summary": summary,
                "content": content,
                "sections": sections,
                "raw_html": response.text,
                "key_entities": key_entities,
                "infobox": infobox,
                "processing_time": processing_time
            }
            
        except requests.RequestException as e:
            logger.error(f"Failed to scrape article: {e}")
            raise Exception(f"Failed to fetch Wikipedia article: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing article: {e}")
            raise Exception(f"Error processing article content: {str(e)}")
    
    def _normalize_url(self, url: str) -> str:
        """Normalize Wikipedia URL"""
        if url.startswith('http'):
            return url
        # Assume it's a topic name
        topic = url.strip().replace(' ', '_')
        return f"https://en.wikipedia.org/wiki/{topic}"
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        title_elem = soup.find('h1', {'id': 'firstHeading'})
        if title_elem:
            return title_elem.get_text().strip()
        return "Unknown Title"
    
    def _extract_summary(self, soup: BeautifulSoup) -> str:
        """Extract first paragraph as summary"""
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if not content_div:
            return ""
        
        # Find first paragraph with substantial text
        paragraphs = content_div.find_all('p', recursive=False)
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 100 and not text.startswith('Coordinates:'):
                # Clean up citation markers
                text = re.sub(r'\[\d+\]', '', text)
                return text
        
        return ""
    
    def _extract_content_and_sections(self, soup: BeautifulSoup) -> Tuple[str, List[str]]:
        """
        Extract main content and section titles
        
        Returns:
            Tuple of (full_content, section_titles)
        """
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if not content_div:
            return "", []
        
        # Remove unwanted elements
        for element in content_div.find_all(['script', 'style', 'table', '.navbox', '.ambox', '.mw-editsection']):
            element.decompose()
        
        # Extract sections
        sections = []
        section_content = []
        
        headings = content_div.find_all(['h2', 'h3'])
        for heading in headings:
            # Get section title
            span = heading.find('span', {'class': 'mw-headline'})
            if span:
                title = span.get_text().strip()
                # Skip certain sections
                if title.lower() not in ['see also', 'references', 'external links', 'notes', 'bibliography']:
                    sections.append(title)
        
        # Get all paragraphs
        paragraphs = content_div.find_all('p')
        full_content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        # Clean up content
        full_content = re.sub(r'\[\d+\]', '', full_content)  # Remove citations
        full_content = re.sub(r'\s+', ' ', full_content)  # Normalize whitespace
        
        return full_content, sections
    
    def _extract_entities(self, soup: BeautifulSoup, content: str) -> Dict[str, List[str]]:
        """
        Extract key entities from article
        
        Returns:
            Dict with keys: people, organizations, locations
        """
        entities = {
            "people": [],
            "organizations": [],
            "locations": []
        }
        
        # Extract from infobox and content links
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if not content_div:
            return entities
        
        # Find all wiki links
        links = content_div.find_all('a', href=re.compile(r'^/wiki/'))
        seen = set()
        
        for link in links[:50]:  # Limit to first 50 links
            title = link.get('title', '')
            text = link.get_text().strip()
            
            if not title or title in seen or len(text) < 3:
                continue
            
            seen.add(title)
            
            # Simple heuristic classification
            # People: often have birth/death dates nearby
            parent_text = link.parent.get_text() if link.parent else ''
            
            if any(pattern in parent_text.lower() for pattern in ['born', 'died', '(', '–', 'was a']):
                if text and len(text.split()) <= 4:  # Likely a person name
                    entities["people"].append(text)
            
            # Organizations: University, Company, Institute, etc.
            elif any(keyword in text for keyword in ['University', 'Institute', 'Company', 'Corporation', 'Organization', 'Society', 'Association']):
                entities["organizations"].append(text)
            
            # Locations: Countries, cities, etc.
            elif any(keyword in title for keyword in ['Country', 'City', 'State', 'Province']) or title in self._get_common_locations():
                entities["locations"].append(text)
        
        # Deduplicate and limit
        entities["people"] = list(dict.fromkeys(entities["people"]))[:10]
        entities["organizations"] = list(dict.fromkeys(entities["organizations"]))[:10]
        entities["locations"] = list(dict.fromkeys(entities["locations"]))[:10]
        
        return entities
    
    def _get_common_locations(self) -> set:
        """Common location names for entity extraction"""
        return {
            'United_States', 'United_Kingdom', 'Germany', 'France', 'Japan', 
            'China', 'India', 'Russia', 'Canada', 'Australia',
            'London', 'New_York', 'Paris', 'Tokyo', 'Berlin',
            'Cambridge', 'Oxford', 'Princeton', 'Harvard'
        }
    
    def _extract_infobox(self, soup: BeautifulSoup) -> Dict:
        """Extract structured data from infobox"""
        infobox = soup.find('table', {'class': 'infobox'})
        if not infobox:
            return {}
        
        data = {}
        rows = infobox.find_all('tr')
        
        for row in rows:
            th = row.find('th')
            td = row.find('td')
            
            if th and td:
                key = th.get_text().strip()
                value = td.get_text().strip()
                # Clean up
                value = re.sub(r'\[\d+\]', '', value)
                value = re.sub(r'\s+', ' ', value)
                data[key] = value
        
        return data


# Create service instance
enhanced_wikipedia_service = EnhancedWikipediaService()
