#!/usr/bin/env python3

import json
import os
import re
import hashlib
from datetime import datetime
import requests
from urllib.parse import urljoin, urlparse

class EvidenceProcessor:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.evidence = {
            'timestamp': datetime.now().isoformat(),
            'target': 'www.temu.com',
            'evidence_files': {},
            'vulnerabilities': [],
            'risk_assessment': {}
        }
    
    def process_admin_responses(self):
        """Process admin interface HTTP responses"""
        print("Processing admin interface responses...")
        
        admin_endpoints = [
            '/admin', '/admin/', '/admin/dashboard', '/admin/users', '/admin/settings',
            '/administrator', '/administrator/', '/manage', '/manage/',
            '/backend', '/backend/', '/control-panel', '/cp', 'panel', 'console', 
            '/dashboard', '/admin-panel', '/super-admin', '/root'
        ]
        
        for endpoint in admin_endpoints:
            url = f"https://www.temu.com{endpoint}"
            try:
                response = requests.get(url, timeout=10, allow_redirects=False)
                
                evidence_item = {
                    'endpoint': endpoint,
                    'url': url,
                    'status_code': response.status_code,
                    'content_length': len(response.content),
                    'content_type': response.headers.get('content-type', 'unknown'),
                    'server': response.headers.get('server', 'unknown'),
                    'security_headers': {
                        'x-frame-options': response.headers.get('x-frame-options'),
                        'x-content-type-options': response.headers.get('x-content-type-options'),
                        'strict-transport-security': response.headers.get('strict-transport-security'),
                        'content-security-policy': response.headers.get('content-security-policy')
                    },
                    'vulnerability': 'CRITICAL' if response.status_code == 200 else 'SECURED'
                }
                
                # Check for admin functionality in response
                if response.status_code == 200:
                    content = response.text.lower()
                    admin_keywords = ['admin', 'dashboard', 'manage', 'control', 'settings', 'users']
                    admin_found = any(keyword in content for keyword in admin_keywords)
                    evidence_item['admin_functionality_detected'] = admin_found
                
                self.evidence['vulnerabilities'].append(evidence_item)
                
            except Exception as e:
                print(f"Error processing {endpoint}: {str(e)}")
    
    def calculate_risk_score(self):
        """Calculate overall risk score"""
        critical_vulns = len([v for v in self.evidence['vulnerabilities'] if v.get('vulnerability') == 'CRITICAL'])
        total_vulns = len(self.evidence['vulnerabilities'])
        
        if total_vulns > 0:
            risk_percentage = (critical_vulns / total_vulns) * 100
            risk_score = min(100, risk_percentage * 1.5)  # Scale up for critical findings
            
            self.evidence['risk_assessment'] = {
                'critical_vulnerabilities': critical_vulns,
                'total_vulnerabilities': total_vulns,
                'risk_percentage': risk_percentage,
                'risk_score': risk_score,
                'risk_level': 'CRITICAL' if risk_score > 80 else 'HIGH' if risk_score > 60 else 'MEDIUM'
            }
    
    def generate_report(self):
        """Generate comprehensive evidence report"""
        self.process_admin_responses()
        self.calculate_risk_score()
        
        # Save evidence
        with open(os.path.join(self.output_dir, 'evidence_report.json'), 'w') as f:
            json.dump(self.evidence, f, indent=2)
        
        print(f"Evidence report saved to {os.path.join(self.output_dir, 'evidence_report.json')}")
        
        # Print summary
        print("\n=== EVIDENCE SUMMARY ===")
        print(f"Critical Vulnerabilities: {self.evidence['risk_assessment']['critical_vulnerabilities']}")
        print(f"Risk Score: {self.evidence['risk_assessment']['risk_score']:.1f}/100")
        print(f"Risk Level: {self.evidence['risk_assessment']['risk_level']}")
        
        return self.evidence

if __name__ == "__main__":
    processor = EvidenceProcessor('/workspace/temu_phase7_real_evidence')
    evidence = processor.generate_report()
