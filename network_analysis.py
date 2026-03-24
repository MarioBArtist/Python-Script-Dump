#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime
import urllib.parse

class NetworkAnalyzer:
    def __init__(self):
        self.target = "www.temu.com"
        self.base_url = f"https://{self.target}"
        self.traffic_logs = []
    
    def capture_http_requests(self):
        """Capture and analyze HTTP requests to admin endpoints"""
        print("Capturing HTTP requests to admin interfaces...")
        
        admin_endpoints = [
            '/admin',
            '/admin/dashboard', 
            '/admin/users',
            '/admin/settings',
            '/administrator',
            '/manage',
            '/backend',
            '/control-panel'
        ]
        
        for endpoint in admin_endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10, allow_redirects=False)
                end_time = time.time()
                
                request_log = {
                    'timestamp': datetime.now().isoformat(),
                    'url': url,
                    'method': 'GET',
                    'status_code': response.status_code,
                    'response_time': round((end_time - start_time) * 1000, 2),
                    'content_length': len(response.content),
                    'content_type': response.headers.get('content-type'),
                    'server': response.headers.get('server'),
                    'security_headers': {
                        'x-frame-options': response.headers.get('x-frame-options'),
                        'x-content-type-options': response.headers.get('x-content-type-options'),
                        'strict-transport-security': response.headers.get('strict-transport-security'),
                        'content-security-policy': response.headers.get('content-security-policy'),
                        'x-xss-protection': response.headers.get('x-xss-protection')
                    },
                    'vulnerability_status': 'CRITICAL' if response.status_code == 200 else 'SECURED'
                }
                
                self.traffic_logs.append(request_log)
                
                status_color = "🚨 CRITICAL" if response.status_code == 200 else "✅ SECURED"
                print(f"{status_color} {endpoint} - {response.status_code} - {response.headers.get('content-type')}")
                
            except Exception as e:
                print(f"❌ ERROR {endpoint}: {str(e)}")
    
    def analyze_security_headers(self):
        """Analyze security header implementation"""
        print("\nAnalyzing security headers...")
        
        security_analysis = {
            'missing_headers': [],
            'insecure_configurations': [],
            'secure_configurations': []
        }
        
        for log in self.traffic_logs:
            headers = log['security_headers']
            
            # Check for missing security headers
            if not headers.get('x-frame-options'):
                security_analysis['missing_headers'].append('X-Frame-Options')
            if not headers.get('x-content-type-options'):
                security_analysis['missing_headers'].append('X-Content-Type-Options')
            if not headers.get('strict-transport-security'):
                security_analysis['missing_headers'].append('Strict-Transport-Security')
            if not headers.get('content-security-policy'):
                security_analysis['missing_headers'].append('Content-Security-Policy')
            
            # Check for insecure configurations
            if headers.get('x-frame-options') and 'ALLOW' in headers['x-frame-options']:
                security_analysis['insecure_configurations'].append('X-Frame-Options: ALLOW')
            
            # Check for secure configurations
            if headers.get('x-frame-options') == 'DENY':
                security_analysis['secure_configurations'].append('X-Frame-Options: DENY')
            if headers.get('x-content-type-options') == 'nosniff':
                security_analysis['secure_configurations'].append('X-Content-Type-Options: nosniff')
        
        return security_analysis
    
    def generate_network_report(self):
        """Generate comprehensive network analysis report"""
        print("Generating network analysis report...")
        
        self.capture_http_requests()
        security_analysis = self.analyze_security_headers()
        
        network_report = {
            'timestamp': datetime.now().isoformat(),
            'target': self.target,
            'total_requests': len(self.traffic_logs),
            'successful_requests': len([log for log in self.traffic_logs if log['status_code'] == 200]),
            'failed_requests': len([log for log in self.traffic_logs if log['status_code'] != 200]),
            'traffic_logs': self.traffic_logs,
            'security_analysis': security_analysis,
            'vulnerability_summary': {
                'exposed_endpoints': len([log for log in self.traffic_logs if log['vulnerability_status'] == 'CRITICAL']),
                'protected_endpoints': len([log for log in self.traffic_logs if log['vulnerability_status'] == 'SECURED']),
                'vulnerability_percentage': round((len([log for log in self.traffic_logs if log['vulnerability_status'] == 'CRITICAL']) / len(self.traffic_logs)) * 100, 2) if self.traffic_logs else 0
            }
        }
        
        # Save report
        with open('/workspace/temu_phase7_real_evidence/network_analysis_report.json', 'w') as f:
            json.dump(network_report, f, indent=2)
        
        print("Network analysis report saved.")
        return network_report

if __name__ == "__main__":
    analyzer = NetworkAnalyzer()
    report = analyzer.generate_network_report()
    
    print("\n=== NETWORK ANALYSIS SUMMARY ===")
    print(f"Total Requests: {report['total_requests']}")
    print(f"Exposed Endpoints: {report['vulnerability_summary']['exposed_endpoints']}")
    print(f"Vulnerability Percentage: {report['vulnerability_summary']['vulnerability_percentage']}%")
