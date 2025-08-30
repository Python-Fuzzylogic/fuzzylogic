#!/usr/bin/env python3
"""
app.py - Simple web-based GUI for fuzzy logic experimentation and code generation.

This module provides a web interface for:
- Creating fuzzy logic domains
- Defining fuzzy sets with various membership functions
- Visualizing fuzzy sets
- Testing input values
- Generating Python code
"""

import json
import os
import base64
from io import BytesIO
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import webbrowser
import threading
import time

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

from fuzzylogic.classes import Domain
from fuzzylogic.functions import R, S, triangular, trapezoid, rectangular


class FuzzyLogicGUI:
    """Main class for the fuzzy logic GUI."""
    
    def __init__(self):
        self.domains = {}
        self.current_domain = None
        
    def create_domain(self, name, low, high, resolution=0.1):
        """Create a new fuzzy domain."""
        domain = Domain(name, low, high, res=resolution)
        self.domains[name] = domain
        self.current_domain = domain
        return domain
    
    def add_set_to_domain(self, domain_name, set_name, func_type, params):
        """Add a fuzzy set to a domain."""
        if domain_name not in self.domains:
            raise ValueError(f"Domain {domain_name} not found")
        
        domain = self.domains[domain_name]
        
        # Store function definition for code generation
        if not hasattr(self, 'function_definitions'):
            self.function_definitions = {}
        
        self.function_definitions[f"{domain_name}.{set_name}"] = {
            'type': func_type,
            'params': params.copy()
        }
        
        # Create the membership function based on type
        if func_type == 'R':
            func = R(params['low'], params['high'])
        elif func_type == 'S':
            func = S(params['low'], params['high'])
        elif func_type == 'triangular':
            func = triangular(params['low'], params['high'], c=params.get('c'))
        elif func_type == 'trapezoid':
            func = trapezoid(params['low'], params['c_low'], params['c_high'], params['high'])
        elif func_type == 'rectangular':
            func = rectangular(params['low'], params['high'])
        else:
            raise ValueError(f"Unknown function type: {func_type}")
        
        # Add the set to the domain
        setattr(domain, set_name, func)
        return domain
    
    def plot_domain(self, domain_name):
        """Create a plot of the domain and return it as base64 encoded image."""
        if domain_name not in self.domains:
            return None
        
        domain = self.domains[domain_name]
        
        plt.figure(figsize=(10, 6))
        
        # Get all fuzzy sets in the domain
        fuzzy_sets = []
        for attr_name in dir(domain):
            if not attr_name.startswith('_') and attr_name not in ['plot', 'range', 'array']:
                attr = getattr(domain, attr_name)
                if hasattr(attr, 'func') or hasattr(attr, 'plot'):
                    fuzzy_sets.append((attr_name, attr))
        
        # Plot each set in the domain
        if fuzzy_sets:
            for set_name, fuzzy_set in fuzzy_sets:
                try:
                    # Create x values for plotting
                    x_vals = []
                    y_vals = []
                    for x in domain.range:
                        x_vals.append(x)
                        y_vals.append(fuzzy_set(x))
                    
                    plt.plot(x_vals, y_vals, label=f'{domain_name}.{set_name}', linewidth=2)
                except Exception as e:
                    print(f"Warning: Could not plot {set_name}: {e}")
                    continue
        else:
            # No sets to plot, show empty domain
            plt.plot([domain._low, domain._high], [0, 0], 'k--', alpha=0.3, label='Empty domain')
        
        plt.title(f'Domain: {domain_name}')
        plt.xlabel('Input Value')
        plt.ylabel('Membership Degree')
        plt.grid(True, alpha=0.3)
        plt.ylim(-0.05, 1.05)
        plt.xlim(domain._low, domain._high)
        
        # Only add legend if there are labeled plots
        if plt.gca().get_legend_handles_labels()[0]:
            plt.legend()
        
        # Save plot to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plot_data = buffer.getvalue()
        buffer.close()
        plt.close()
        
        return base64.b64encode(plot_data).decode()
    
    def test_value(self, domain_name, value):
        """Test a value against all sets in a domain."""
        if domain_name not in self.domains:
            return None
        
        domain = self.domains[domain_name]
        result = domain(value)
        return {str(k): v for k, v in result.items()}
    
    def generate_code(self):
        """Generate Python code that recreates the current fuzzy logic setup."""
        code_lines = [
            "from fuzzylogic.classes import Domain",
            "from fuzzylogic.functions import R, S, triangular, trapezoid, rectangular",
            "",
        ]
        
        # Store function definitions for later recreation
        function_definitions = getattr(self, 'function_definitions', {})
        
        for domain_name, domain in self.domains.items():
            # Create domain
            code_lines.append(f"{domain_name} = Domain('{domain_name}', {domain._low}, {domain._high}, res={domain._res})")
            
            # Add sets using stored function definitions
            for func_def_key, func_info in function_definitions.items():
                if func_def_key.startswith(f"{domain_name}."):
                    set_name = func_def_key.split('.', 1)[1]
                    
                    if func_info['type'] == 'R':
                        code_lines.append(f"{domain_name}.{set_name} = R({func_info['params']['low']}, {func_info['params']['high']})")
                    elif func_info['type'] == 'S':
                        code_lines.append(f"{domain_name}.{set_name} = S({func_info['params']['low']}, {func_info['params']['high']})")
                    elif func_info['type'] == 'triangular':
                        params = func_info['params']
                        if 'c' in params and params['c'] is not None:
                            code_lines.append(f"{domain_name}.{set_name} = triangular({params['low']}, {params['high']}, c={params['c']})")
                        else:
                            code_lines.append(f"{domain_name}.{set_name} = triangular({params['low']}, {params['high']})")
                    elif func_info['type'] == 'trapezoid':
                        params = func_info['params']
                        code_lines.append(f"{domain_name}.{set_name} = trapezoid({params['low']}, {params['c_low']}, {params['c_high']}, {params['high']})")
                    elif func_info['type'] == 'rectangular':
                        params = func_info['params']
                        code_lines.append(f"{domain_name}.{set_name} = rectangular({params['low']}, {params['high']})")
            
            code_lines.append("")
        
        # Add example usage
        if self.domains:
            code_lines.extend([
                "# Example usage:",
                "# Test a value against all sets in a domain",
            ])
            for domain_name in self.domains.keys():
                code_lines.append(f"# result = {domain_name}(value)")
                code_lines.append(f"# print(result)")
                break  # Just show example for one domain
            
        return "\n".join(code_lines)


class FuzzyLogicRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the fuzzy logic GUI."""
    
    gui_instance = FuzzyLogicGUI()
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.serve_html()
        elif parsed_path.path == '/api/domains':
            self.serve_domains()
        elif parsed_path.path.startswith('/api/plot/'):
            domain_name = parsed_path.path.split('/')[-1]
            self.serve_plot(domain_name)
        elif parsed_path.path == '/api/code':
            self.serve_code()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/create_domain':
            self.create_domain(data)
        elif parsed_path.path == '/api/add_set':
            self.add_set(data)
        elif parsed_path.path == '/api/test_value':
            self.test_value(data)
        else:
            self.send_error(404)
    
    def serve_html(self):
        """Serve the main HTML interface."""
        html_content = self.get_html_content()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_domains(self):
        """Serve the list of domains."""
        domains_info = {}
        for name, domain in self.gui_instance.domains.items():
            sets = []
            for attr_name in dir(domain):
                if not attr_name.startswith('_') and attr_name not in ['plot', 'range', 'array']:
                    attr = getattr(domain, attr_name)
                    if hasattr(attr, 'func'):
                        sets.append(attr_name)
            
            domains_info[name] = {
                'low': domain._low,
                'high': domain._high,
                'resolution': domain._res,
                'sets': sets
            }
        
        self.send_json_response(domains_info)
    
    def serve_plot(self, domain_name):
        """Serve a plot for a domain."""
        plot_data = self.gui_instance.plot_domain(domain_name)
        if plot_data:
            self.send_json_response({'plot': plot_data})
        else:
            self.send_error(404)
    
    def serve_code(self):
        """Serve the generated code."""
        code = self.gui_instance.generate_code()
        self.send_json_response({'code': code})
    
    def create_domain(self, data):
        """Create a new domain."""
        try:
            domain = self.gui_instance.create_domain(
                data['name'], 
                float(data['low']), 
                float(data['high']), 
                float(data.get('resolution', 0.1))
            )
            self.send_json_response({'success': True, 'message': f'Domain {data["name"]} created'})
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)})
    
    def add_set(self, data):
        """Add a set to a domain."""
        try:
            domain = self.gui_instance.add_set_to_domain(
                data['domain_name'],
                data['set_name'],
                data['func_type'],
                data['params']
            )
            self.send_json_response({'success': True, 'message': f'Set {data["set_name"]} added'})
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)})
    
    def test_value(self, data):
        """Test a value against a domain."""
        try:
            result = self.gui_instance.test_value(data['domain_name'], float(data['value']))
            self.send_json_response({'success': True, 'result': result})
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)})
    
    def send_json_response(self, data):
        """Send a JSON response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def get_html_content(self):
        """Get the HTML content for the interface."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fuzzy Logic GUI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .section {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .section h2 {
            margin-top: 0;
            color: #555;
        }
        .form-group {
            margin: 10px 0;
        }
        label {
            display: inline-block;
            width: 120px;
            font-weight: bold;
        }
        input, select, button {
            padding: 8px;
            margin: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #007bff;
            color: white;
            cursor: pointer;
            border: none;
        }
        button:hover {
            background-color: #0056b3;
        }
        .plot-container {
            text-align: center;
            margin: 20px 0;
        }
        .plot-container img {
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .code-output {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            font-family: monospace;
            white-space: pre-wrap;
            overflow-x: auto;
        }
        .result-output {
            background-color: #e8f5e8;
            border: 1px solid #c3e6c3;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
        }
        .error {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Fuzzy Logic Experimentation GUI</h1>
        
        <div class="section">
            <h2>Create Domain</h2>
            <div class="form-group">
                <label>Name:</label>
                <input type="text" id="domainName" placeholder="e.g., temperature">
            </div>
            <div class="form-group">
                <label>Low:</label>
                <input type="number" id="domainLow" placeholder="0" step="any">
            </div>
            <div class="form-group">
                <label>High:</label>
                <input type="number" id="domainHigh" placeholder="100" step="any">
            </div>
            <div class="form-group">
                <label>Resolution:</label>
                <input type="number" id="domainRes" placeholder="0.1" step="any" value="0.1">
            </div>
            <button onclick="createDomain()">Create Domain</button>
        </div>
        
        <div class="section">
            <h2>Add Fuzzy Set</h2>
            <div class="form-group">
                <label>Domain:</label>
                <select id="setDomain">
                    <option value="">Select Domain</option>
                </select>
            </div>
            <div class="form-group">
                <label>Set Name:</label>
                <input type="text" id="setName" placeholder="e.g., hot">
            </div>
            <div class="form-group">
                <label>Function:</label>
                <select id="funcType" onchange="updateFunctionParams()">
                    <option value="R">R (Rising)</option>
                    <option value="S">S (Falling)</option>
                    <option value="triangular">Triangular</option>
                    <option value="trapezoid">Trapezoid</option>
                    <option value="rectangular">Rectangular</option>
                </select>
            </div>
            <div id="functionParams">
                <div class="form-group">
                    <label>Low:</label>
                    <input type="number" id="paramLow" step="any">
                </div>
                <div class="form-group">
                    <label>High:</label>
                    <input type="number" id="paramHigh" step="any">
                </div>
            </div>
            <button onclick="addSet()">Add Set</button>
        </div>
        
        <div class="section">
            <h2>Visualization</h2>
            <div class="form-group">
                <label>Domain:</label>
                <select id="plotDomain">
                    <option value="">Select Domain</option>
                </select>
                <button onclick="plotDomain()">Plot Domain</button>
            </div>
            <div class="plot-container" id="plotContainer">
                <p>No plot generated yet</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Test Values</h2>
            <div class="form-group">
                <label>Domain:</label>
                <select id="testDomain">
                    <option value="">Select Domain</option>
                </select>
            </div>
            <div class="form-group">
                <label>Value:</label>
                <input type="number" id="testValue" step="any">
                <button onclick="testValue()">Test Value</button>
            </div>
            <div id="testResult"></div>
        </div>
        
        <div class="section">
            <h2>Generated Code</h2>
            <button onclick="generateCode()">Generate Python Code</button>
            <div class="code-output" id="codeOutput">
                # Generated code will appear here
            </div>
        </div>
        
        <div id="messageArea"></div>
    </div>

    <script>
        function showMessage(message, isError = false) {
            const messageArea = document.getElementById('messageArea');
            messageArea.innerHTML = `<div class="result-output ${isError ? 'error' : ''}">${message}</div>`;
            setTimeout(() => messageArea.innerHTML = '', 5000);
        }

        function updateDomainSelects() {
            fetch('/api/domains')
                .then(response => response.json())
                .then(domains => {
                    const selects = ['setDomain', 'plotDomain', 'testDomain'];
                    selects.forEach(selectId => {
                        const select = document.getElementById(selectId);
                        select.innerHTML = '<option value="">Select Domain</option>';
                        Object.keys(domains).forEach(domainName => {
                            const option = document.createElement('option');
                            option.value = domainName;
                            option.textContent = domainName;
                            select.appendChild(option);
                        });
                    });
                });
        }

        function createDomain() {
            const data = {
                name: document.getElementById('domainName').value,
                low: document.getElementById('domainLow').value,
                high: document.getElementById('domainHigh').value,
                resolution: document.getElementById('domainRes').value
            };
            
            if (!data.name || !data.low || !data.high) {
                showMessage('Please fill all required fields', true);
                return;
            }

            fetch('/api/create_domain', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    showMessage(result.message);
                    updateDomainSelects();
                    // Clear form
                    document.getElementById('domainName').value = '';
                    document.getElementById('domainLow').value = '';
                    document.getElementById('domainHigh').value = '';
                } else {
                    showMessage(result.error, true);
                }
            });
        }

        function updateFunctionParams() {
            const funcType = document.getElementById('funcType').value;
            const paramsDiv = document.getElementById('functionParams');
            
            let html = '';
            if (funcType === 'R' || funcType === 'S' || funcType === 'rectangular') {
                html = `
                    <div class="form-group">
                        <label>Low:</label>
                        <input type="number" id="paramLow" step="any">
                    </div>
                    <div class="form-group">
                        <label>High:</label>
                        <input type="number" id="paramHigh" step="any">
                    </div>
                `;
            } else if (funcType === 'triangular') {
                html = `
                    <div class="form-group">
                        <label>Low:</label>
                        <input type="number" id="paramLow" step="any">
                    </div>
                    <div class="form-group">
                        <label>High:</label>
                        <input type="number" id="paramHigh" step="any">
                    </div>
                    <div class="form-group">
                        <label>Center (optional):</label>
                        <input type="number" id="paramC" step="any">
                    </div>
                `;
            } else if (funcType === 'trapezoid') {
                html = `
                    <div class="form-group">
                        <label>Low:</label>
                        <input type="number" id="paramLow" step="any">
                    </div>
                    <div class="form-group">
                        <label>Center Low:</label>
                        <input type="number" id="paramCLow" step="any">
                    </div>
                    <div class="form-group">
                        <label>Center High:</label>
                        <input type="number" id="paramCHigh" step="any">
                    </div>
                    <div class="form-group">
                        <label>High:</label>
                        <input type="number" id="paramHigh" step="any">
                    </div>
                `;
            }
            paramsDiv.innerHTML = html;
        }

        function addSet() {
            const funcType = document.getElementById('funcType').value;
            const params = {};
            
            params.low = parseFloat(document.getElementById('paramLow').value);
            params.high = parseFloat(document.getElementById('paramHigh').value);
            
            if (funcType === 'triangular') {
                const c = document.getElementById('paramC').value;
                if (c) params.c = parseFloat(c);
            } else if (funcType === 'trapezoid') {
                params.c_low = parseFloat(document.getElementById('paramCLow').value);
                params.c_high = parseFloat(document.getElementById('paramCHigh').value);
            }
            
            const data = {
                domain_name: document.getElementById('setDomain').value,
                set_name: document.getElementById('setName').value,
                func_type: funcType,
                params: params
            };
            
            if (!data.domain_name || !data.set_name) {
                showMessage('Please select domain and enter set name', true);
                return;
            }

            fetch('/api/add_set', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    showMessage(result.message);
                    document.getElementById('setName').value = '';
                } else {
                    showMessage(result.error, true);
                }
            });
        }

        function plotDomain() {
            const domainName = document.getElementById('plotDomain').value;
            if (!domainName) {
                showMessage('Please select a domain', true);
                return;
            }

            fetch(`/api/plot/${domainName}`)
                .then(response => response.json())
                .then(result => {
                    if (result.plot) {
                        document.getElementById('plotContainer').innerHTML = 
                            `<img src="data:image/png;base64,${result.plot}" alt="Domain Plot">`;
                    } else {
                        showMessage('Failed to generate plot', true);
                    }
                });
        }

        function testValue() {
            const data = {
                domain_name: document.getElementById('testDomain').value,
                value: document.getElementById('testValue').value
            };
            
            if (!data.domain_name || data.value === '') {
                showMessage('Please select domain and enter value', true);
                return;
            }

            fetch('/api/test_value', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    let html = '<h3>Test Results:</h3>';
                    for (const [setName, membership] of Object.entries(result.result)) {
                        html += `<p><strong>${setName}:</strong> ${membership.toFixed(3)}</p>`;
                    }
                    document.getElementById('testResult').innerHTML = html;
                } else {
                    showMessage(result.error, true);
                }
            });
        }

        function generateCode() {
            fetch('/api/code')
                .then(response => response.json())
                .then(result => {
                    document.getElementById('codeOutput').textContent = result.code;
                });
        }

        // Initialize function parameters on load
        updateFunctionParams();
        updateDomainSelects();
    </script>
</body>
</html>'''


def run_gui(port=8000):
    """Run the fuzzy logic GUI web server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, FuzzyLogicRequestHandler)
    
    print(f"Fuzzy Logic GUI running at http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    
    # Try to open browser automatically
    try:
        def open_browser():
            time.sleep(1)  # Wait a moment for server to start
            webbrowser.open(f'http://localhost:{port}')
        
        threading.Thread(target=open_browser, daemon=True).start()
    except:
        pass
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()


if __name__ == '__main__':
    run_gui()