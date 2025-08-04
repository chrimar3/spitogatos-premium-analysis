#!/usr/bin/env python3
"""
XE.GR DEEP RECONNAISSANCE MISSION
Comprehensive site structure analysis to find ALL working property access methods
"""

import asyncio
import json
import logging
import re
import time
from datetime import datetime
from typing import List, Dict, Set
from playwright.async_api import async_playwright
from urllib.parse import urljoin, urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XEReconnaissance:
    """Deep reconnaissance of XE.gr structure"""
    
    def __init__(self):
        self.discovered_urls = set()
        self.working_urls = []
        self.failed_urls = []
        self.site_map = {}
        self.property_patterns = []
        self.search_methods = []
        
    async def full_reconnaissance(self):
        """Complete site reconnaissance mission"""
        logger.info("🕵️ XE.GR DEEP RECONNAISSANCE MISSION")
        logger.info("🎯 Objective: Find ALL working property access methods")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,  # Keep visible for manual observation
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                locale='el-GR'
            )
            
            try:
                page = await context.new_page()
                
                # Mission 1: Homepage Analysis
                logger.info("🏠 MISSION 1: Homepage Deep Analysis")
                await self.analyze_homepage(page)
                
                # Mission 2: Property Section Exploration
                logger.info("🏘️ MISSION 2: Property Section Deep Dive")
                await self.explore_property_section(page)
                
                # Mission 3: Search System Investigation
                logger.info("🔍 MISSION 3: Search System Investigation")
                await self.investigate_search_system(page)
                
                # Mission 4: Network Traffic Analysis
                logger.info("🌐 MISSION 4: Network Traffic Analysis")
                await self.analyze_network_traffic(page)
                
                # Mission 5: URL Pattern Discovery
                logger.info("🔗 MISSION 5: URL Pattern Discovery")
                await self.discover_url_patterns(page)
                
                # Mission 6: Sitemap and Robots Analysis
                logger.info("🗺️ MISSION 6: Sitemap & Robots Analysis")
                await self.analyze_sitemaps_and_robots(page)
                
                # Mission 7: Real Property URL Testing
                logger.info("🧪 MISSION 7: Real Property URL Verification")
                await self.test_real_property_urls(page)
                
            except Exception as e:
                logger.error(f"❌ Reconnaissance mission failed: {e}")
            finally:
                logger.info("📊 Generating comprehensive intelligence report...")
                await self.generate_intelligence_report()
                
                # Keep browser open for final manual inspection
                logger.info("🔍 Browser kept open for manual inspection - press Ctrl+C when done")
                try:
                    await asyncio.sleep(300)  # 5 minutes
                except KeyboardInterrupt:
                    logger.info("🔚 Manual inspection completed")
                
                await browser.close()
    
    async def analyze_homepage(self, page):
        """Deep analysis of homepage structure"""
        try:
            await page.goto("https://xe.gr", wait_until="networkidle", timeout=30000)
            await asyncio.sleep(3)
            
            # Handle cookies
            try:
                cookie_btn = await page.wait_for_selector('button:has-text("ΣΥΜΦΩΝΩ")', timeout=5000)
                if cookie_btn:
                    await cookie_btn.click()
                    await asyncio.sleep(2)
                    logger.info("✅ Cookie consent handled")
            except:
                logger.info("ℹ️ No cookie dialog found")
            
            # Extract all navigation links
            logger.info("🔍 Analyzing homepage navigation...")
            nav_links = await page.query_selector_all('a')
            
            homepage_links = []
            for link in nav_links:
                try:
                    href = await link.get_attribute('href')
                    text = await link.inner_text()
                    if href and text:
                        homepage_links.append({
                            'text': text.strip(),
                            'href': href,
                            'is_property_related': any(keyword in href.lower() or keyword in text.lower() 
                                                     for keyword in ['property', 'ακίνητα', 'enoikias', 'polis'])
                        })
                except:
                    continue
            
            self.site_map['homepage_links'] = homepage_links
            property_links = [link for link in homepage_links if link['is_property_related']]
            
            logger.info(f"📊 Homepage analysis: {len(homepage_links)} total links, {len(property_links)} property-related")
            
            # Save homepage HTML for analysis
            html_content = await page.content()
            with open('outputs/xe_homepage_analysis.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Take screenshot
            await page.screenshot(path='outputs/xe_homepage_analysis.png')
            logger.info("💾 Homepage data saved for analysis")
            
        except Exception as e:
            logger.error(f"❌ Homepage analysis failed: {e}")
    
    async def explore_property_section(self, page):
        """Deep exploration of property section"""
        try:
            # Try different property section URLs
            property_urls = [
                "https://xe.gr/ακίνητα",
                "https://xe.gr/property",
                "https://xe.gr/real-estate",
                "https://xe.gr/enoikiaseis",
                "https://xe.gr/poliseis"
            ]
            
            for prop_url in property_urls:
                logger.info(f"🏘️ Testing property URL: {prop_url}")
                try:
                    response = await page.goto(prop_url, wait_until="networkidle", timeout=20000)
                    status = response.status if response else 0
                    
                    if status == 200:
                        logger.info(f"✅ Working property URL: {prop_url}")
                        self.working_urls.append(prop_url)
                        
                        # Analyze property section structure
                        await self.analyze_property_page_structure(page, prop_url)
                    else:
                        logger.info(f"❌ Failed property URL: {prop_url} (Status {status})")
                        self.failed_urls.append(prop_url)
                        
                except Exception as e:
                    logger.info(f"❌ Error accessing {prop_url}: {e}")
                    self.failed_urls.append(prop_url)
                
                await asyncio.sleep(2)
            
            # Try clicking property navigation from homepage
            logger.info("🏠 Attempting property navigation from homepage...")
            try:
                await page.goto("https://xe.gr", wait_until="networkidle", timeout=20000)
                await asyncio.sleep(2)
                
                property_nav_selectors = [
                    'a:has-text("Ακίνητα")',
                    'a:has-text("Property")',
                    'a[href*="property"]',
                    'a[href*="ακίνητα"]',
                    '.nav a:has-text("Ακίνητα")',
                    'nav a:has-text("Ακίνητα")'
                ]
                
                for selector in property_nav_selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=3000)
                        if element and await element.is_visible():
                            href = await element.get_attribute('href')
                            text = await element.inner_text()
                            logger.info(f"🎯 Found property nav: '{text}' -> {href}")
                            
                            await element.click()
                            await page.wait_for_load_state('networkidle', timeout=20000)
                            
                            current_url = page.url
                            logger.info(f"✅ Property navigation successful: {current_url}")
                            
                            if current_url not in self.working_urls:
                                self.working_urls.append(current_url)
                            
                            await self.analyze_property_page_structure(page, current_url)
                            break
                    except:
                        continue
                        
            except Exception as e:
                logger.error(f"❌ Property navigation failed: {e}")
        
        except Exception as e:
            logger.error(f"❌ Property section exploration failed: {e}")
    
    async def analyze_property_page_structure(self, page, url):
        """Analyze structure of property pages"""
        try:
            logger.info(f"🔍 Analyzing property page structure: {url}")
            
            # Wait for content to load
            await asyncio.sleep(3)
            
            # Look for search forms
            search_forms = await page.query_selector_all('form')
            logger.info(f"📝 Found {len(search_forms)} forms on property page")
            
            # Analyze search inputs
            search_inputs = await page.query_selector_all('input')
            input_details = []
            
            for input_elem in search_inputs:
                try:
                    input_type = await input_elem.get_attribute('type')
                    input_name = await input_elem.get_attribute('name')
                    input_placeholder = await input_elem.get_attribute('placeholder')
                    input_class = await input_elem.get_attribute('class')
                    
                    input_details.append({
                        'type': input_type,
                        'name': input_name,
                        'placeholder': input_placeholder,
                        'class': input_class
                    })
                except:
                    continue
            
            self.site_map[f'property_page_{len(self.site_map)}'] = {
                'url': url,
                'forms_count': len(search_forms),
                'inputs': input_details,
                'timestamp': datetime.now().isoformat()
            }
            
            # Look for property listings on the page
            listing_selectors = [
                'a[href*="/d/"]',
                'a[href*="property"]',
                'a[href*="enoikiaseis"]',
                'a[href*="poliseis"]',
                '.property-item a',
                '.listing a',
                '.result a',
                '[class*="property"] a',
                '[class*="listing"] a'
            ]
            
            found_listings = []
            for selector in listing_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        href = await element.get_attribute('href')
                        text = await element.inner_text()
                        if href and self.looks_like_property_url(href):
                            found_listings.append({
                                'url': href,
                                'text': text.strip()[:100],
                                'selector': selector
                            })
                except:
                    continue
            
            logger.info(f"🏠 Found {len(found_listings)} potential property listings")
            
            if found_listings:
                self.site_map[f'listings_found_{len(self.site_map)}'] = found_listings[:10]  # Store first 10
            
            # Save page content for analysis
            page_html = await page.content()
            filename = f'outputs/xe_property_page_{len(self.site_map)}.html'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(page_html)
            
            # Screenshot
            screenshot_name = f'outputs/xe_property_page_{len(self.site_map)}.png'
            await page.screenshot(path=screenshot_name)
            
            logger.info(f"💾 Property page analysis saved: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Property page analysis failed: {e}")
    
    def looks_like_property_url(self, url: str) -> bool:
        """Check if URL looks like a property listing"""
        if not url:
            return False
        
        property_indicators = [
            '/d/', '/property/', '/enoikiaseis', '/poliseis',
            'diamerisma', 'apartment', 'house', 'katoikia'
        ]
        
        return any(indicator in url.lower() for indicator in property_indicators)
    
    async def investigate_search_system(self, page):
        """Deep investigation of search functionality"""
        try:
            logger.info("🔍 Investigating search system...")
            
            # Go to main search page
            search_urls = [
                "https://xe.gr/search",
                "https://xe.gr/αναζήτηση",
                "https://xe.gr/property/search"
            ]
            
            for search_url in search_urls:
                try:
                    logger.info(f"🔍 Testing search URL: {search_url}")
                    response = await page.goto(search_url, wait_until="networkidle", timeout=20000)
                    
                    if response and response.status == 200:
                        logger.info(f"✅ Working search URL: {search_url}")
                        
                        # Analyze search form
                        await self.analyze_search_form(page)
                        
                        # Try performing a test search
                        await self.perform_test_search(page, "Κολωνάκι διαμέρισμα")
                        
                        break
                    else:
                        logger.info(f"❌ Search URL failed: {search_url}")
                        
                except Exception as e:
                    logger.info(f"❌ Search URL error {search_url}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"❌ Search system investigation failed: {e}")
    
    async def analyze_search_form(self, page):
        """Analyze search form structure"""
        try:
            # Get all form elements
            forms = await page.query_selector_all('form')
            
            for i, form in enumerate(forms):
                logger.info(f"📝 Analyzing form {i+1}")
                
                # Get form inputs
                inputs = await form.query_selector_all('input, select, textarea')
                
                form_details = []
                for input_elem in inputs:
                    try:
                        tag_name = await input_elem.evaluate('el => el.tagName')
                        input_type = await input_elem.get_attribute('type')
                        input_name = await input_elem.get_attribute('name')
                        input_placeholder = await input_elem.get_attribute('placeholder')
                        input_value = await input_elem.get_attribute('value')
                        
                        form_details.append({
                            'tag': tag_name,
                            'type': input_type,
                            'name': input_name,
                            'placeholder': input_placeholder,
                            'value': input_value
                        })
                    except:
                        continue
                
                self.search_methods.append({
                    'form_index': i,
                    'elements': form_details,
                    'url': page.url
                })
                
                logger.info(f"📊 Form {i+1}: {len(form_details)} elements")
        
        except Exception as e:
            logger.error(f"❌ Search form analysis failed: {e}")
    
    async def perform_test_search(self, page, search_term):
        """Perform test search to see results"""
        try:
            logger.info(f"🧪 Testing search with term: {search_term}")
            
            # Try different input selectors
            input_selectors = [
                'input[type="text"]',
                'input[type="search"]',
                'input[name*="search"]',
                'input[name*="q"]',
                'input[placeholder*="αναζήτηση"]',
                'input[placeholder*="search"]',
                '.search-input',
                '#search'
            ]
            
            search_performed = False
            for selector in input_selectors:
                try:
                    input_elem = await page.wait_for_selector(selector, timeout=3000)
                    if input_elem and await input_elem.is_visible():
                        await input_elem.fill(search_term)
                        logger.info(f"✅ Filled search input: {selector}")
                        
                        # Try to submit
                        await page.keyboard.press('Enter')
                        await asyncio.sleep(5)
                        
                        # Check if URL changed (indicating search worked)
                        current_url = page.url
                        if 'search' in current_url or search_term.lower() in current_url.lower():
                            logger.info(f"✅ Search successful! Result URL: {current_url}")
                            
                            # Look for results
                            await self.analyze_search_results(page)
                            search_performed = True
                            break
                        
                except:
                    continue
            
            if not search_performed:
                logger.warning("⚠️ Could not perform test search")
        
        except Exception as e:
            logger.error(f"❌ Test search failed: {e}")
    
    async def analyze_search_results(self, page):
        """Analyze search results page"""
        try:
            logger.info("📊 Analyzing search results...")
            
            # Wait for results to load
            await asyncio.sleep(3)
            
            # Look for result links
            result_selectors = [
                'a[href*="/d/"]',
                'a[href*="property"]',
                '.result a',
                '.listing a',
                '.property a',
                '[class*="result"] a',
                '[class*="listing"] a'
            ]
            
            all_results = []
            for selector in result_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        href = await element.get_attribute('href')
                        text = await element.inner_text()
                        if href and self.looks_like_property_url(href):
                            all_results.append({
                                'url': href,
                                'text': text.strip()[:100],
                                'selector': selector
                            })
                except:
                    continue
            
            logger.info(f"🎯 Found {len(all_results)} property results from search")
            
            if all_results:
                # Test first few results
                for i, result in enumerate(all_results[:3]):
                    logger.info(f"🧪 Testing result {i+1}: {result['url']}")
                    await self.test_property_url(page, result['url'])
                    await asyncio.sleep(2)
            
            # Save search results
            self.site_map['search_results'] = all_results[:20]  # Store first 20
            
            # Screenshot
            await page.screenshot(path='outputs/xe_search_results.png')
            
            # Save HTML
            html_content = await page.content()
            with open('outputs/xe_search_results.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info("💾 Search results analysis saved")
        
        except Exception as e:
            logger.error(f"❌ Search results analysis failed: {e}")
    
    async def test_property_url(self, page, url):
        """Test if a property URL actually works"""
        try:
            if not url.startswith('http'):
                url = urljoin(page.url, url)
            
            logger.info(f"🧪 Testing property URL: {url}")
            
            response = await page.goto(url, wait_until="load", timeout=15000)
            
            if response and response.status == 200:
                await asyncio.sleep(2)
                
                # Check if it's a real property page
                content = await page.content()
                
                property_indicators = [
                    'τιμή', 'price', 'τ.μ', 'm²', 'ενοικίαση', 'πώληση',
                    'διαμέρισμα', 'apartment', 'energy', 'ενεργειακή'
                ]
                
                indicator_count = sum(1 for indicator in property_indicators if indicator in content.lower())
                
                if indicator_count >= 3:
                    logger.info(f"✅ REAL PROPERTY PAGE: {url} ({indicator_count} indicators)")
                    self.working_urls.append(url)
                    
                    # Extract sample data to verify
                    await self.extract_sample_property_data(page, url)
                else:
                    logger.info(f"❌ Not a property page: {url} (only {indicator_count} indicators)")
                    self.failed_urls.append(url)
            else:
                status = response.status if response else 'no response'
                logger.info(f"❌ Property URL failed: {url} (Status: {status})")
                self.failed_urls.append(url)
        
        except Exception as e:
            logger.info(f"❌ Property URL test failed {url}: {e}")
            self.failed_urls.append(url)
    
    async def extract_sample_property_data(self, page, url):
        """Extract sample data from verified property page"""
        try:
            logger.info(f"📊 Extracting sample data from: {url}")
            
            page_text = await page.inner_text('body')
            title = await page.title()
            
            # Look for key data
            import re
            
            # Price
            price_match = re.search(r'(\d{1,3}(?:\.\d{3})*)\s*€', page_text)
            price = price_match.group(1) if price_match else None
            
            # SQM
            sqm_match = re.search(r'(\d+(?:[.,]\d+)?)\s*τ\.?μ\.?', page_text)
            sqm = sqm_match.group(1) if sqm_match else None
            
            # Energy class
            energy_match = re.search(r'ενεργειακή\s+κλάση\s*[:\-]?\s*([A-G][+]?)', page_text, re.IGNORECASE)
            energy = energy_match.group(1) if energy_match else None
            
            sample_data = {
                'url': url,
                'title': title,
                'price': price,
                'sqm': sqm,
                'energy_class': energy,
                'content_length': len(page_text),
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            if not hasattr(self, 'sample_extractions'):
                self.sample_extractions = []
            
            self.sample_extractions.append(sample_data)
            
            logger.info(f"📊 Sample: {title[:50]}... | €{price} | {sqm}m² | Energy {energy}")
        
        except Exception as e:
            logger.error(f"❌ Sample extraction failed: {e}")
    
    async def analyze_network_traffic(self, page):
        """Analyze network requests to find API endpoints"""
        try:
            logger.info("🌐 Analyzing network traffic for API endpoints...")
            
            # Set up request interception
            requests_log = []
            
            def log_request(request):
                if 'api' in request.url or 'search' in request.url or 'property' in request.url:
                    requests_log.append({
                        'url': request.url,
                        'method': request.method,
                        'headers': dict(request.headers),
                        'post_data': request.post_data if request.post_data else None
                    })
            
            page.on('request', log_request)
            
            # Navigate and perform actions to trigger requests
            await page.goto("https://xe.gr", wait_until="networkidle")
            await asyncio.sleep(3)
            
            # Try to trigger search to see API calls
            try:
                property_link = await page.wait_for_selector('a:has-text("Ακίνητα")', timeout=5000)
                if property_link:
                    await property_link.click()
                    await asyncio.sleep(5)
            except:
                pass
            
            self.site_map['network_requests'] = requests_log
            logger.info(f"📊 Captured {len(requests_log)} relevant network requests")
            
        except Exception as e:
            logger.error(f"❌ Network traffic analysis failed: {e}")
    
    async def discover_url_patterns(self, page):
        """Discover URL patterns from page analysis"""
        try:
            logger.info("🔗 Discovering URL patterns...")
            
            # Analyze all discovered URLs
            all_urls = set()
            
            # From working URLs
            all_urls.update(self.working_urls)
            
            # From site map
            for key, value in self.site_map.items():
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict) and 'url' in item:
                            all_urls.add(item['url'])
                        elif isinstance(item, dict) and 'href' in item:
                            all_urls.add(item['href'])
            
            # Analyze patterns
            patterns = {}
            for url in all_urls:
                if self.looks_like_property_url(url):
                    # Extract pattern
                    pattern = re.sub(r'\d+', '{ID}', url)
                    pattern = re.sub(r'[a-z0-9-]+(?=\.[a-z]+)', '{SLUG}', pattern)
                    
                    if pattern not in patterns:
                        patterns[pattern] = []
                    patterns[pattern].append(url)
            
            self.property_patterns = patterns
            logger.info(f"🔗 Discovered {len(patterns)} URL patterns")
            
            for pattern, examples in patterns.items():
                logger.info(f"   Pattern: {pattern} ({len(examples)} examples)")
        
        except Exception as e:
            logger.error(f"❌ URL pattern discovery failed: {e}")
    
    async def analyze_sitemaps_and_robots(self, page):
        """Analyze sitemaps and robots.txt"""
        try:
            logger.info("🗺️ Analyzing sitemaps and robots.txt...")
            
            # Check robots.txt
            try:
                await page.goto("https://xe.gr/robots.txt", timeout=15000)
                robots_content = await page.inner_text('body')
                
                # Look for sitemap references
                sitemap_matches = re.findall(r'Sitemap:\s*(https?://[^\s]+)', robots_content)
                
                self.site_map['robots_txt'] = {
                    'content': robots_content,
                    'sitemaps': sitemap_matches
                }
                
                logger.info(f"🤖 Robots.txt: {len(sitemap_matches)} sitemaps found")
                
                # Test discovered sitemaps
                for sitemap_url in sitemap_matches:
                    try:
                        await page.goto(sitemap_url, timeout=15000)
                        sitemap_content = await page.inner_text('body')
                        
                        # Extract URLs from sitemap
                        url_matches = re.findall(r'<loc>(.*?)</loc>', sitemap_content)
                        property_urls = [url for url in url_matches if self.looks_like_property_url(url)]
                        
                        logger.info(f"🗺️ Sitemap {sitemap_url}: {len(property_urls)} property URLs")
                        
                        if property_urls:
                            self.site_map[f'sitemap_{len(self.site_map)}'] = {
                                'url': sitemap_url,
                                'property_urls': property_urls[:50]  # Store first 50
                            }
                    except:
                        continue
                        
            except Exception as e:
                logger.info(f"⚠️ Could not access robots.txt: {e}")
        
        except Exception as e:
            logger.error(f"❌ Sitemap/robots analysis failed: {e}")
    
    async def test_real_property_urls(self, page):
        """Test discovered property URLs to find working ones"""
        try:
            logger.info("🧪 Testing discovered property URLs...")
            
            # Collect all discovered property URLs
            test_urls = set()
            
            # From sitemaps
            for key, value in self.site_map.items():
                if 'sitemap_' in key and isinstance(value, dict) and 'property_urls' in value:
                    test_urls.update(value['property_urls'][:10])  # Test first 10 from each sitemap
            
            # From search results
            if 'search_results' in self.site_map:
                for result in self.site_map['search_results'][:10]:
                    test_urls.add(result['url'])
            
            logger.info(f"🧪 Testing {len(test_urls)} discovered URLs...")
            
            # Test each URL
            working_count = 0
            for i, url in enumerate(list(test_urls)[:20]):  # Test max 20 URLs
                logger.info(f"🧪 Testing {i+1}/20: {url[:60]}...")
                
                if await self.test_single_url(page, url):
                    working_count += 1
                
                await asyncio.sleep(1)  # Respectful delay
            
            logger.info(f"✅ Found {working_count} working property URLs out of {min(20, len(test_urls))} tested")
        
        except Exception as e:
            logger.error(f"❌ Property URL testing failed: {e}")
    
    async def test_single_url(self, page, url):
        """Test a single URL and return True if it works"""
        try:
            if not url.startswith('http'):
                url = f"https://xe.gr{url}" if url.startswith('/') else f"https://xe.gr/{url}"
            
            response = await page.goto(url, wait_until="load", timeout=10000)
            
            if response and response.status == 200:
                content = await page.content()
                
                # Quick check for property content
                if any(indicator in content.lower() for indicator in ['τιμή', 'price', 'τ.μ', 'διαμέρισμα']):
                    logger.info(f"✅ WORKING: {url}")
                    
                    if url not in self.working_urls:
                        self.working_urls.append(url)
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"❌ URL test failed {url}: {e}")
            return False
    
    async def generate_intelligence_report(self):
        """Generate comprehensive intelligence report"""
        try:
            logger.info("📊 GENERATING COMPREHENSIVE INTELLIGENCE REPORT")
            
            report = {
                'reconnaissance_timestamp': datetime.now().isoformat(),
                'summary': {
                    'working_urls_found': len(self.working_urls),
                    'failed_urls': len(self.failed_urls),
                    'url_patterns_discovered': len(self.property_patterns),
                    'search_methods_found': len(self.search_methods)
                },
                'working_urls': self.working_urls,
                'failed_urls': self.failed_urls,
                'property_patterns': self.property_patterns,
                'search_methods': self.search_methods,
                'site_structure': self.site_map
            }
            
            # Add sample extractions if any
            if hasattr(self, 'sample_extractions'):
                report['sample_property_data'] = self.sample_extractions
            
            # Save comprehensive report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f'outputs/xe_intelligence_report_{timestamp}.json'
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Intelligence report saved: {report_file}")
            
            # Print executive summary
            logger.info("\n" + "="*80)
            logger.info("🕵️ XE.GR RECONNAISSANCE - EXECUTIVE SUMMARY")
            logger.info("="*80)
            logger.info(f"✅ Working URLs Found: {len(self.working_urls)}")
            logger.info(f"❌ Failed URLs: {len(self.failed_urls)}")
            logger.info(f"🔗 URL Patterns Discovered: {len(self.property_patterns)}")
            logger.info(f"🔍 Search Methods Found: {len(self.search_methods)}")
            
            if self.working_urls:
                logger.info("\n🎯 WORKING PROPERTY URLs:")
                for i, url in enumerate(self.working_urls[:5], 1):
                    logger.info(f"   {i}. {url}")
            
            if hasattr(self, 'sample_extractions'):
                logger.info(f"\n📊 SAMPLE DATA EXTRACTIONS: {len(self.sample_extractions)}")
                for sample in self.sample_extractions[:3]:
                    logger.info(f"   • {sample['title'][:50]}... | €{sample['price']} | {sample['sqm']}m²")
            
            logger.info("\n🎯 NEXT STEPS:")
            if self.working_urls:
                logger.info("   1. Use working URLs to extract real property data")
                logger.info("   2. Implement discovered URL patterns for scaling")
                logger.info("   3. Deploy professional scraper with verified endpoints")
            else:
                logger.info("   1. Manual inspection of browser may reveal additional methods")
                logger.info("   2. Consider alternative Greek property sites")
                logger.info("   3. Analyze network traffic for API endpoints")
            
            logger.info("="*80)
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")

async def main():
    """Run complete reconnaissance mission"""
    reconnaissance = XEReconnaissance()
    await reconnaissance.full_reconnaissance()

if __name__ == "__main__":
    asyncio.run(main())