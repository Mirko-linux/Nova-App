import requests
from bs4 import BeautifulSoup
import trafilatura
import logging
import time
import random
import urllib.parse
import asyncio
import aiohttp
import re
import json
from typing import List, Dict, Any, Set, Tuple
from urllib.parse import urljoin, urlparse
import pdfplumber
import io
from PIL import Image
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import threading

# --- CONFIGURAZIONE ---
SEARCH_ENGINES = {
    "duckduckgo": {
        "url": "https://html.duckduckgo.com/html/",
        "method": "POST",
        "params": {"q": "", "kl": "it-it"}
    },
    "google": {
        "url": "https://www.google.com/search",
        "method": "GET",
        "params": {"q": "", "hl": "it", "num": 15}
    }
}

MAX_RESULTS = 12
MAX_DEPTH = 2  # Profondità massima di crawling
REQUEST_TIMEOUT = 15
MAX_CONCURRENT_REQUESTS = 5

# Parole chiave per filtrare spam e contenuti irrilevanti
SPAM_KEYWORDS = [
    'casino', 'poker', 'bet', 'gambling', 'viagra', 'cialis', 'porn', 'adult', 'sex',
    'loan', 'mortgage', 'insurance', 'credit', 'debt', 'make money', 'get rich',
    'work from home', 'bitcoin', 'crypto', 'forex', 'trading', 'diet pill', 'weight loss'
]

CONTENT_TYPES = {
    'text': ['.html', '.htm', '.php', '.asp', '.aspx', '.jsp'],
    'pdf': ['.pdf'],
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
    'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'],
    'document': ['.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.odt', '.ods']
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeepResearch")

class ContentAnalyzer:
    """Analizza e classifica il contenuto"""
    
    @staticmethod
    def is_spam(content: str, url: str) -> bool:
        """Determina se il contenuto è spam"""
        content_lower = content.lower()
        url_lower = url.lower()
        
        # Controlla parole chiave di spam
        for keyword in SPAM_KEYWORDS:
            if keyword in content_lower or keyword in url_lower:
                return True
        
        # Controlla ratio link/testo (sito con troppi link potrebbe essere spam)
        link_count = content_lower.count('<a href') if '<a href' in content_lower else 0
        text_length = len(content)
        if text_length > 0 and link_count / text_length > 0.1:  # Più del 10% di link
            return True
            
        return False
    
    @staticmethod
    def calculate_relevance(query: str, content: str, url: str) -> float:
        """Calcola la rilevanza del contenuto rispetto alla query"""
        query_terms = query.lower().split()
        content_lower = content.lower()
        url_lower = url.lower()
        
        relevance = 0.0
        
        for term in query_terms:
            # Peso maggiore per i termini nel titolo/URL
            if term in url_lower:
                relevance += 2.0
            # Peso medio per i termini nel contenuto
            if term in content_lower:
                relevance += 1.0
        
        return relevance / len(query_terms) if query_terms else 0
    
    @staticmethod
    def extract_entities(text: str) -> Dict[str, List[str]]:
        """Estrai entità named dal testo (luoghi, persone, organizzazioni)"""
        # Implementazione semplificata - in produzione usare spaCy o NLTK
        entities = {
            'persons': [],
            'organizations': [],
            'locations': []
        }
        
        # Regex semplificato per estrazione entità
        capital_words = re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', text)
        entities['persons'].extend(capital_words[:3])
        
        org_keywords = ['inc', 'corp', 'ltd', 'company', 'organization', 'foundation']
        for sentence in text.split('.'):
            if any(keyword in sentence.lower() for keyword in org_keywords):
                entities['organizations'].append(sentence[:100])
        
        location_keywords = ['street', 'avenue', 'road', 'city', 'country', 'state']
        for sentence in text.split('.'):
            if any(keyword in sentence.lower() for keyword in location_keywords):
                entities['locations'].append(sentence[:100])
                
        return entities

class AdvancedScraper:
    """Scraper avanzato per diversi tipi di contenuto"""
    
    def __init__(self):
        self.visited_urls = set()
        self.session = None
        self.driver = None
        self.lock = threading.Lock()
    
    async def create_session(self):
        """Crea una sessione aiohttp"""
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": random.choice(USER_AGENTS)},
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        )
    
    def setup_selenium(self):
        """Configura Selenium per JavaScript-heavy sites"""
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(REQUEST_TIMEOUT)
    
    async def close_resources(self):
        """Chiudi tutte le risorse"""
        if self.session:
            await self.session.close()
        if self.driver:
            self.driver.quit()
    
    def get_content_type(self, url: str, response_headers: Dict = None) -> str:
        """Determina il tipo di contenuto basato sull'URL e headers"""
        url_lower = url.lower()
        
        # Controlla l'estensione del file
        for content_type, extensions in CONTENT_TYPES.items():
            if any(url_lower.endswith(ext) for ext in extensions):
                return content_type
        
        # Controlla gli headers di response
        if response_headers:
            content_type = response_headers.get('content-type', '').lower()
            if 'pdf' in content_type:
                return 'pdf'
            elif 'image' in content_type:
                return 'image'
            elif 'video' in content_type:
                return 'video'
            elif 'text/html' in content_type:
                return 'text'
        
        return 'unknown'
    
    async def extract_text_content(self, url: str, html: str) -> Dict[str, Any]:
        """Estrai testo da HTML con trafilatura e fallback"""
        try:
            # Prova con trafilatura prima
            text = trafilatura.extract(html, include_comments=False, include_tables=True)
            
            if not text or len(text) < 200:
                # Fallback a BeautifulSoup avanzato
                soup = BeautifulSoup(html, 'html.parser')
                
                # Rimuovi elementi indesiderati
                for element in soup(["script", "style", "nav", "footer", "header", 
                                   "aside", "form", "iframe", "button"]):
                    element.decompose()
                
                # Estrai da articoli e sezioni principali
                article = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile(r'(content|article|main)'))
                
                if article:
                    text = article.get_text(separator=' ', strip=True)
                else:
                    # Estrai da tutti i paragrafi e headings
                    elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
                    text = ' '.join(elem.get_text(strip=True) for elem in elements if len(elem.get_text(strip=True)) > 30)
            
            # Pulizia del testo
            text = re.sub(r'\s+', ' ', text).strip()
            return text if len(text) > 100 else ""
            
        except Exception as e:
            logger.warning(f"Errore estrazione testo da {url}: {e}")
            return ""
    
    async def extract_pdf_content(self, url: str, content: bytes) -> str:
        """Estrai testo da PDF"""
        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip()
        except Exception as e:
            logger.warning(f"Errore estrazione PDF da {url}: {e}")
            return ""
    
    async def extract_image_content(self, url: str, content: bytes) -> str:
        """Estrai testo da immagini usando OCR"""
        try:
            image = Image.open(io.BytesIO(content))
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.warning(f"Errore OCR da {url}: {e}")
            return ""
    
    async def extract_with_selenium(self, url: str) -> str:
        """Estrai contenuto da siti JavaScript-heavy usando Selenium"""
        try:
            self.setup_selenium()
            self.driver.get(url)
            
            # Attendi che il contenuto si carichi
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Prova a trovare il contenuto principale
            selectors = [
                'article', 'main', '[role="main"]', 
                '.content', '.article', '.post-content',
                'div[class*="content"]', 'div[class*="article"]'
            ]
            
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return elements[0].text
            
            # Fallback a tutto il body
            return self.driver.find_element(By.TAG_NAME, "body").text
            
        except Exception as e:
            logger.warning(f"Errore Selenium con {url}: {e}")
            return ""
    
    async def discover_internal_links(self, url: str, html: str, depth: int = 0) -> List[str]:
        """Scopri link interni rilevanti"""
        if depth >= MAX_DEPTH:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        base_domain = urlparse(url).netloc
        internal_links = []
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            full_url = urljoin(url, href)
            
            # Filtra per link interni e non visitati
            if (urlparse(full_url).netloc == base_domain and 
                full_url not in self.visited_urls and
                not any(full_url.lower().endswith(ext) for ext in ['.jpg', '.png', '.gif', '.css', '.js'])):
                
                internal_links.append(full_url)
        
        return internal_links[:3]  # Limita a 3 link interni per profondità
    
    async def extract_content(self, url: str, depth: int = 0) -> Dict[str, Any]:
        """Estrai contenuto completo da una URL"""
        if depth > MAX_DEPTH or url in self.visited_urls:
            return None
        
        with self.lock:
            self.visited_urls.add(url)
        
        try:
            logger.info(f"📄 Estrazione da: {url} (profondità: {depth})")
            
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            
            async with self.session.get(url, headers=headers) as response:
                content_type = self.get_content_type(url, dict(response.headers))
                content = await response.read()
                html = content.decode('utf-8', errors='ignore') if content_type == 'text' else ""
                
                result = {
                    "url": url,
                    "content_type": content_type,
                    "title": "",
                    "text": "",
                    "metadata": {},
                    "internal_links": [],
                    "depth": depth
                }
                
                # Estrazione basata sul tipo di contenuto
                if content_type == 'text':
                    result['text'] = await self.extract_text_content(url, html)
                    
                    # Estrai titolo
                    soup = BeautifulSoup(html, 'html.parser')
                    title_tag = soup.find('title')
                    result['title'] = title_tag.get_text().strip() if title_tag else url
                    
                    # Scopri link interni
                    result['internal_links'] = await self.discover_internal_links(url, html, depth)
                    
                elif content_type == 'pdf':
                    result['text'] = await self.extract_pdf_content(url, content)
                    result['title'] = f"Documento PDF: {url.split('/')[-1]}"
                    
                elif content_type == 'image':
                    result['text'] = await self.extract_image_content(url, content)
                    result['title'] = f"Immagine: {url.split('/')[-1]}"
                
                # Estrai metadati
                if content_type == 'text':
                    soup = BeautifulSoup(html, 'html.parser')
                    meta_tags = soup.find_all('meta')
                    for meta in meta_tags:
                        name = meta.get('name') or meta.get('property') or ''
                        content = meta.get('content', '')
                        if name and content:
                            result['metadata'][name] = content
                
                return result
                
        except Exception as e:
            logger.warning(f"❌ Errore estrazione {url}: {e}")
            return None
    
    async def extract_multiple_contents(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Estrai contenuti da multiple URL in parallelo"""
        tasks = [self.extract_content(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return [result for result in results if result and result.get('text')]

class SearchEngine:
    """Gestisce ricerche su multiple fonti"""
    
    def __init__(self):
        self.scraper = AdvancedScraper()
    
    async def search_with_engine(self, engine: str, query: str) -> List[str]:
        """Esegui ricerca con un motore specifico"""
        engine_config = SEARCH_ENGINES[engine]
        params = engine_config["params"].copy()
        params["q"] = query
        
        try:
            if engine_config["method"] == "POST":
                async with self.scraper.session.post(
                    engine_config["url"], 
                    data=params,
                    headers={"User-Agent": random.choice(USER_AGENTS)}
                ) as response:
                    html = await response.text()
            else:
                async with self.scraper.session.get(
                    engine_config["url"], 
                    params=params,
                    headers={"User-Agent": random.choice(USER_AGENTS)}
                ) as response:
                    html = await response.text()
            
            # Estrai link in base al motore di ricerca
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            if engine == "duckduckgo":
                for result in soup.select('.result'):
                    link_elem = result.select_one('.result__a')
                    if link_elem and link_elem.get('href'):
                        href = link_elem.get('href')
                        if href.startswith('/l/?uddg='):
                            try:
                                parsed_url = urllib.parse.urlparse(href)
                                query_params = urllib.parse.parse_qs(parsed_url.query)
                                if 'uddg' in query_params:
                                    real_url = urllib.parse.unquote(query_params['uddg'][0])
                                    links.append(real_url)
                            except:
                                continue
            
            elif engine == "google":
                for link in soup.select('a[href*="/url?q="]'):
                    href = link.get('href')
                    if href:
                        try:
                            url = href.split('/url?q=')[1].split('&')[0]
                            url = urllib.parse.unquote(url)
                            links.append(url)
                        except:
                            continue
            
            return links[:MAX_RESULTS]
                
        except Exception as e:
            logger.error(f"Errore con {engine}: {e}")
            return []
    
    async def multi_search(self, query: str) -> List[str]:
        """Esegui ricerche su più motori"""
        await self.scraper.create_session()
        
        tasks = []
        for engine in SEARCH_ENGINES.keys():
            tasks.append(self.search_with_engine(engine, query))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combina e deduplica i risultati
        all_links = []
        for result in results:
            if isinstance(result, list):
                all_links.extend(result)
        
        # Rimuovi duplicati
        seen = set()
        unique_links = []
        for link in all_links:
            domain = urlparse(link).netloc
            if domain not in seen:
                seen.add(domain)
                unique_links.append(link)
                
        return unique_links[:MAX_RESULTS]

async def deep_research(query: str) -> Dict[str, Any]:
    """
    Esegue una ricerca approfondita completa
    """
    start_time = time.time()
    logger.info(f"🔍 Avvio ricerca avanzata: {query}")
    
    search_engine = SearchEngine()
    content_analyzer = ContentAnalyzer()
    
    try:
        # Fase 1: Ricerca su multiple fonti
        links = await search_engine.multi_search(query)
        logger.info(f"✅ Trovati {len(links)} link iniziali")
        
        if not links:
            return {
                "query": query,
                "sources": [],
                "results": [],
                "stats": {
                    "total_time": round(time.time() - start_time, 2),
                    "sources_found": 0,
                    "content_extracted": 0
                }
            }
        
        # Fase 2: Estrazione contenuti principali
        main_results = await search_engine.scraper.extract_multiple_contents(links)
        
        # Fase 3: Estrazione contenuti interni (ricorsiva)
        all_results = main_results.copy()
        internal_links = []
        
        for result in main_results:
            internal_links.extend(result.get('internal_links', []))
        
        if internal_links:
            internal_results = await search_engine.scraper.extract_multiple_contents(internal_links)
            all_results.extend(internal_results)
        
        # Fase 4: Filtraggio e ranking
        filtered_results = []
        for result in all_results:
            text = result.get('text', '')
            url = result.get('url', '')
            
            # Filtra spam e contenuti irrilevanti
            if (text and not content_analyzer.is_spam(text, url) and
                content_analyzer.calculate_relevance(query, text, url) > 0.3):
                
                # Aggiungi metadati di rilevanza
                result['relevance'] = content_analyzer.calculate_relevance(query, text, url)
                result['entities'] = content_analyzer.extract_entities(text)
                filtered_results.append(result)
        
        # Ordina per rilevanza
        filtered_results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        # Rimuovi duplicati (stesso dominio)
        seen_domains = set()
        final_results = []
        for result in filtered_results:
            domain = urlparse(result['url']).netloc
            if domain not in seen_domains:
                seen_domains.add(domain)
                final_results.append(result)
        
        # Preparazione risultati finali
        return {
            "query": query,
            "sources": [result["url"] for result in final_results],
            "results": final_results,
            "stats": {
                "total_time": round(time.time() - start_time, 2),
                "sources_found": len(links),
                "content_extracted": len(final_results),
                "internal_links_followed": len(internal_links)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Errore nella ricerca: {e}")
        return {
            "query": query,
            "sources": [],
            "results": [],
            "error": str(e),
            "stats": {
                "total_time": round(time.time() - start_time, 2),
                "sources_found": 0,
                "content_extracted": 0
            }
        }
    finally:
        await search_engine.scraper.close_resources()

# Versione sincrona per compatibilità
def deep_research_sync(query: str) -> Dict[str, Any]:
    """Versione sincrona per integrazione con Flask"""
    return asyncio.run(deep_research(query))
