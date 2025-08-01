#!/usr/bin/env python3
"""
XE.GR DEEP INVESTIGATION - WEBSITE ARCHITECTURE ANALYSIS
Understanding the target before building the extraction strategy
"""

import asyncio
import aiohttp
import json
import logging
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XEGRInvestigator:
    """Deep investigation of xe.gr website architecture"""
    
    def __init__(self):
        self.investigation_data = {
            'timestamp': datetime.now().isoformat(),
            'website': 'xe.gr',
            'findings': {}
        }
        
        logger.info("🔍 STARTING DEEP XE.GR INVESTIGATION")
        logger.info("📋 Analyzing website structure, APIs, security measures")
    
    async def investigate_website_structure(self):
        """Investigate xe.gr website structure and technology"""
        
        logger.info("🏗️ INVESTIGATING WEBSITE STRUCTURE")
        
        findings = {}
        
        # 1. Basic website analysis
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                # Test homepage
                logger.info("🏠 Analyzing homepage...")
                async with session.get('https://xe.gr') as response:
                    if response.status == 200:
                        html = await response.text()
                        findings['homepage'] = self.analyze_homepage(html, dict(response.headers))
                    else:
                        findings['homepage'] = {'error': f'Status {response.status}'}
                
                # Test robots.txt
                logger.info("🤖 Checking robots.txt...")
                try:
                    async with session.get('https://xe.gr/robots.txt') as response:
                        if response.status == 200:
                            robots = await response.text()
                            findings['robots_txt'] = self.analyze_robots_txt(robots)
                        else:
                            findings['robots_txt'] = {'status': response.status}
                except:
                    findings['robots_txt'] = {'error': 'Not accessible'}
                
                # Test sitemap
                logger.info("🗺️ Checking sitemap...")
                try:
                    async with session.get('https://xe.gr/sitemap.xml') as response:
                        if response.status == 200:
                            sitemap = await response.text()
                            findings['sitemap'] = self.analyze_sitemap(sitemap)
                        else:
                            findings['sitemap'] = {'status': response.status}
                except:
                    findings['sitemap'] = {'error': 'Not accessible'}
                
                # Test API discovery
                logger.info("🔌 Discovering API endpoints...")
                findings['api_discovery'] = await self.discover_api_endpoints(session)
                
        except Exception as e:
            logger.error(f"❌ Website structure analysis failed: {e}")
            findings['error'] = str(e)
        
        self.investigation_data['findings']['website_structure'] = findings
        return findings
    
    def analyze_homepage(self, html: str, headers: Dict) -> Dict:
        """Analyze homepage for technology stack and structure"""
        
        soup = BeautifulSoup(html, 'html.parser')
        analysis = {
            'size': len(html),
            'technologies': [],
            'security_headers': {},
            'javascript_frameworks': [],
            'api_endpoints_found': [],
            'form_endpoints': [],
            'interesting_urls': []
        }
        
        # Analyze headers for security and technology clues
        security_headers = ['x-frame-options', 'x-content-type-options', 'x-xss-protection', 'content-security-policy', 'strict-transport-security']
        for header in security_headers:
            if header in [h.lower() for h in headers.keys()]:
                analysis['security_headers'][header] = headers.get(header, headers.get(header.upper()))
        
        # Look for technology indicators
        if 'react' in html.lower():
            analysis['technologies'].append('React')
        if 'angular' in html.lower():
            analysis['technologies'].append('Angular')
        if 'vue' in html.lower():
            analysis['technologies'].append('Vue.js')
        if 'jquery' in html.lower():
            analysis['technologies'].append('jQuery')
        
        # Find JavaScript files that might contain API endpoints
        script_tags = soup.find_all('script', src=True)
        for script in script_tags:
            src = script.get('src')
            if src:
                analysis['javascript_frameworks'].append(src)
        
        # Look for API endpoints in JavaScript
        api_patterns = [
            r'/api/[^"\s]+',
            r'/graphql[^"\s]*',
            r'ajax[^"\s]*',
            r'endpoint[^"\s]*'
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            analysis['api_endpoints_found'].extend(matches)
        
        # Find forms (potential data submission endpoints)
        forms = soup.find_all('form')
        for form in forms:
            action = form.get('action')
            method = form.get('method', 'GET')
            if action:
                analysis['form_endpoints'].append({'action': action, 'method': method})
        
        # Look for interesting URLs
        url_patterns = [
            r'https://xe\.gr/[^"\s]+/search[^"\s]*',
            r'https://xe\.gr/[^"\s]+/property[^"\s]*',
            r'https://xe\.gr/[^"\s]+/api[^"\s]*'
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            analysis['interesting_urls'].extend(matches)
        
        return analysis
    
    def analyze_robots_txt(self, robots: str) -> Dict:
        """Analyze robots.txt for crawling restrictions"""
        
        analysis = {
            'disallowed_paths': [],
            'allowed_paths': [],
            'crawl_delay': None,
            'sitemaps': [],
            'user_agents': []
        }
        
        lines = robots.split('\n')
        current_user_agent = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('User-agent:'):
                current_user_agent = line.split(':', 1)[1].strip()
                analysis['user_agents'].append(current_user_agent)
            elif line.startswith('Disallow:'):
                path = line.split(':', 1)[1].strip()
                analysis['disallowed_paths'].append(path)
            elif line.startswith('Allow:'):
                path = line.split(':', 1)[1].strip()
                analysis['allowed_paths'].append(path)
            elif line.startswith('Crawl-delay:'):
                delay = line.split(':', 1)[1].strip()
                analysis['crawl_delay'] = delay
            elif line.startswith('Sitemap:'):
                sitemap = line.split(':', 1)[1].strip()
                analysis['sitemaps'].append(sitemap)
        
        return analysis
    
    def analyze_sitemap(self, sitemap: str) -> Dict:
        """Analyze sitemap for URL patterns"""
        
        analysis = {
            'total_urls': 0,
            'property_urls': [],
            'search_urls': [],
            'api_urls': [],
            'url_patterns': {}
        }
        
        # Count URLs
        url_matches = re.findall(r'<loc>(.*?)</loc>', sitemap)
        analysis['total_urls'] = len(url_matches)
        
        # Categorize URLs
        for url in url_matches:
            if '/property/' in url.lower():
                analysis['property_urls'].append(url)
            elif '/search' in url.lower():
                analysis['search_urls'].append(url)
            elif '/api/' in url.lower():
                analysis['api_urls'].append(url)
        
        # Find URL patterns
        pattern_counts = {}
        for url in url_matches:
            # Extract URL pattern
            pattern = re.sub(r'/\d+', '/{id}', url)
            pattern = re.sub(r'[?&][^=]+=[^&]*', '', pattern)  # Remove query params
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        analysis['url_patterns'] = pattern_counts
        
        return analysis
    
    async def discover_api_endpoints(self, session: aiohttp.ClientSession) -> Dict:
        """Discover API endpoints through common paths"""
        
        logger.info("🔍 Testing common API endpoints...")
        
        common_api_paths = [
            '/api',
            '/api/v1',
            '/api/v2',
            '/graphql',
            '/rest',
            '/ajax',
            '/search/api',
            '/property/api',
            '/api/search',
            '/api/properties',
            '/api/listings'
        ]
        
        findings = {
            'accessible_endpoints': [],
            'blocked_endpoints': [],
            'redirect_endpoints': [],
            'error_endpoints': []
        }
        
        for path in common_api_paths:
            url = f'https://xe.gr{path}'
            try:
                async with session.get(url) as response:
                    status = response.status
                    
                    if status == 200:
                        findings['accessible_endpoints'].append({
                            'path': path,
                            'status': status,
                            'content_type': response.headers.get('content-type', ''),
                            'size': len(await response.text())
                        })
                    elif status in [301, 302, 307, 308]:
                        findings['redirect_endpoints'].append({
                            'path': path,
                            'status': status,
                            'location': response.headers.get('location', '')
                        })
                    elif status in [403, 429]:
                        findings['blocked_endpoints'].append({
                            'path': path,
                            'status': status
                        })
                    else:
                        findings['error_endpoints'].append({
                            'path': path,
                            'status': status
                        })
                        
            except Exception as e:
                findings['error_endpoints'].append({
                    'path': path,
                    'error': str(e)
                })
            
            # Small delay between requests
            await asyncio.sleep(0.5)
        
        return findings
    
    async def analyze_search_functionality(self):
        """Analyze how xe.gr search functionality works"""
        
        logger.info("🔍 ANALYZING SEARCH FUNCTIONALITY")
        
        findings = {}
        
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                
                # Test basic search page
                search_urls = [
                    'https://xe.gr/search',
                    'https://xe.gr/property/search',
                    'https://xe.gr/en/search',
                    'https://xe.gr/el/search'
                ]
                
                findings['search_pages'] = {}
                
                for search_url in search_urls:
                    try:
                        logger.info(f"🔍 Testing: {search_url}")
                        async with session.get(search_url) as response:
                            findings['search_pages'][search_url] = {
                                'status': response.status,
                                'content_type': response.headers.get('content-type', ''),
                                'size': len(await response.text()) if response.status == 200 else 0
                            }
                            
                            if response.status == 200:
                                html = await response.text()
                                findings['search_pages'][search_url]['analysis'] = self.analyze_search_page(html)
                                
                    except Exception as e:
                        findings['search_pages'][search_url] = {'error': str(e)}
                    
                    await asyncio.sleep(1)
                
        except Exception as e:
            findings['error'] = str(e)
        
        self.investigation_data['findings']['search_functionality'] = findings
        return findings
    
    def analyze_search_page(self, html: str) -> Dict:
        """Analyze search page structure"""
        
        soup = BeautifulSoup(html, 'html.parser')
        
        analysis = {
            'forms': [],
            'javascript_files': [],
            'ajax_endpoints': [],
            'search_parameters': [],
            'filters': []
        }
        
        # Find search forms
        forms = soup.find_all('form')
        for form in forms:
            form_data = {
                'action': form.get('action'),
                'method': form.get('method', 'GET'),
                'inputs': []
            }
            
            inputs = form.find_all(['input', 'select', 'textarea'])
            for inp in inputs:
                form_data['inputs'].append({
                    'name': inp.get('name'),
                    'type': inp.get('type'),
                    'value': inp.get('value'),
                    'placeholder': inp.get('placeholder')
                })
            
            analysis['forms'].append(form_data)
        
        # Find JavaScript files (might contain search logic)
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script.get('src')
            if src and ('search' in src.lower() or 'filter' in src.lower()):
                analysis['javascript_files'].append(src)
        
        # Look for AJAX endpoints in JavaScript
        ajax_patterns = [
            r'ajax[^"]*',
            r'fetch\([^)]*["\']([^"\']+)["\']',
            r'\.get\([^)]*["\']([^"\']+)["\']',
            r'\.post\([^)]*["\']([^"\']+)["\']'
        ]
        
        for pattern in ajax_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            analysis['ajax_endpoints'].extend(matches)
        
        return analysis
    
    async def investigate_anti_bot_measures(self):
        """Investigate anti-bot protection measures"""
        
        logger.info("🛡️ INVESTIGATING ANTI-BOT MEASURES")
        
        findings = {
            'detection_methods': [],
            'blocking_patterns': [],
            'javascript_challenges': [],
            'rate_limiting': {},
            'security_services': []
        }
        
        try:
            # Test with different user agents
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'curl/7.68.0',
                'python-requests/2.25.1',
                'Scrapy/2.5.0',
                'bot'
            ]
            
            timeout = aiohttp.ClientTimeout(total=15)
            
            findings['user_agent_tests'] = {}
            
            for ua in user_agents:
                try:
                    headers = {'User-Agent': ua}
                    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                        async with session.get('https://xe.gr') as response:
                            findings['user_agent_tests'][ua] = {
                                'status': response.status,
                                'headers': dict(response.headers),
                                'blocked': response.status in [403, 429, 503]
                            }
                            
                            if response.status == 200:
                                html = await response.text()
                                # Check for anti-bot indicators
                                if 'captcha' in html.lower():
                                    findings['user_agent_tests'][ua]['has_captcha'] = True
                                if 'cloudflare' in html.lower():
                                    findings['user_agent_tests'][ua]['has_cloudflare'] = True
                                if 'blocked' in html.lower():
                                    findings['user_agent_tests'][ua]['blocked_message'] = True
                            
                except Exception as e:
                    findings['user_agent_tests'][ua] = {'error': str(e)}
                
                await asyncio.sleep(2)
            
            # Test rate limiting
            logger.info("⏱️ Testing rate limiting...")
            findings['rate_limit_test'] = await self.test_rate_limiting()
            
        except Exception as e:
            findings['error'] = str(e)
        
        self.investigation_data['findings']['anti_bot_measures'] = findings
        return findings
    
    async def test_rate_limiting(self) -> Dict:
        """Test rate limiting behavior"""
        
        rate_test = {
            'requests_sent': 0,
            'successful_requests': 0,
            'blocked_requests': 0,
            'first_block_at': None,
            'block_duration': None
        }
        
        timeout = aiohttp.ClientTimeout(total=10)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        
        try:
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                for i in range(10):  # Send 10 rapid requests
                    try:
                        start_time = time.time()
                        async with session.get('https://xe.gr') as response:
                            rate_test['requests_sent'] += 1
                            
                            if response.status == 200:
                                rate_test['successful_requests'] += 1
                            elif response.status in [403, 429, 503]:
                                rate_test['blocked_requests'] += 1
                                if rate_test['first_block_at'] is None:
                                    rate_test['first_block_at'] = i + 1
                                    
                    except Exception as e:
                        rate_test['requests_sent'] += 1
                        rate_test['blocked_requests'] += 1
                    
                    await asyncio.sleep(0.5)  # Very short delay
                        
        except Exception as e:
            rate_test['error'] = str(e)
        
        return rate_test
    
    async def run_full_investigation(self):
        """Run complete investigation"""
        
        logger.info("🎯 STARTING COMPREHENSIVE XE.GR INVESTIGATION")
        
        # 1. Website structure analysis
        await self.investigate_website_structure()
        
        # 2. Search functionality analysis  
        await self.analyze_search_functionality()
        
        # 3. Anti-bot measures investigation
        await self.investigate_anti_bot_measures()
        
        # 4. Save results
        await self.save_investigation_results()
        
        # 5. Generate recommendations
        recommendations = self.generate_recommendations()
        
        return self.investigation_data, recommendations
    
    async def save_investigation_results(self):
        """Save investigation results to file"""
        
        filename = f'outputs/xe_gr_investigation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.investigation_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Investigation results saved: {filename}")
    
    def generate_recommendations(self) -> Dict:
        """Generate recommendations based on investigation"""
        
        logger.info("💡 GENERATING EXTRACTION RECOMMENDATIONS")
        
        recommendations = {
            'optimal_strategy': 'unknown',
            'technical_approach': [],
            'risk_level': 'high',
            'success_probability': 0,
            'implementation_complexity': 'high'
        }
        
        findings = self.investigation_data['findings']
        
        # Analyze findings and generate recommendations
        if 'website_structure' in findings:
            homepage = findings['website_structure'].get('homepage', {})
            
            # Check for JavaScript frameworks
            if 'React' in homepage.get('technologies', []):
                recommendations['technical_approach'].append('Browser automation required (React SPA)')
                recommendations['implementation_complexity'] = 'very_high'
            
            # Check for API endpoints
            api_endpoints = homepage.get('api_endpoints_found', [])
            if api_endpoints:
                recommendations['technical_approach'].append('Direct API calls possible')
                recommendations['success_probability'] += 30
        
        if 'anti_bot_measures' in findings:
            anti_bot = findings['anti_bot_measures']
            
            # Check user agent blocking
            ua_tests = anti_bot.get('user_agent_tests', {})
            bot_detected = any(test.get('blocked', False) for test in ua_tests.values())
            
            if bot_detected:
                recommendations['technical_approach'].append('User agent rotation required')
                recommendations['risk_level'] = 'very_high'
            
            # Check rate limiting
            rate_test = anti_bot.get('rate_limit_test', {})
            if rate_test.get('blocked_requests', 0) > 0:
                recommendations['technical_approach'].append('Rate limiting bypass needed')
        
        # Determine optimal strategy
        if recommendations['success_probability'] > 70:
            recommendations['optimal_strategy'] = 'api_direct'
        elif recommendations['success_probability'] > 40:
            recommendations['optimal_strategy'] = 'browser_automation'
        else:
            recommendations['optimal_strategy'] = 'advanced_evasion'
        
        logger.info(f"🎯 Recommended strategy: {recommendations['optimal_strategy']}")
        logger.info(f"📊 Success probability: {recommendations['success_probability']}%")
        
        return recommendations

async def main():
    """Run xe.gr investigation"""
    
    investigator = XEGRInvestigator()
    
    investigation_data, recommendations = await investigator.run_full_investigation()
    
    # Print summary
    logger.info("\n" + "="*80)
    logger.info("🎯 INVESTIGATION SUMMARY")
    logger.info("="*80)
    
    logger.info(f"💡 Optimal Strategy: {recommendations['optimal_strategy']}")
    logger.info(f"📊 Success Probability: {recommendations['success_probability']}%")
    logger.info(f"🔧 Implementation Complexity: {recommendations['implementation_complexity']}")
    logger.info(f"⚠️ Risk Level: {recommendations['risk_level']}")
    
    logger.info("\n🛠️ Technical Approach Required:")
    for approach in recommendations['technical_approach']:
        logger.info(f"  • {approach}")
    
    logger.info("\n📄 Full investigation data saved to outputs/")
    logger.info("🎯 Ready for targeted extraction strategy implementation")

if __name__ == "__main__":
    asyncio.run(main())