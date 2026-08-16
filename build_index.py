import base64, re

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_parts(html_content):
    """Extract CSS, HTML body, and JS from a standalone HTML"""
    css_match = re.search(r'<style>(.*?)</style>', html_content, re.DOTALL)
    css = css_match.group(1).strip() if css_match else ''
    
    js_parts = re.findall(r'<script>(.*?)</script>', html_content, re.DOTALL)
    js = '\n'.join(j.strip() for j in js_parts)
    
    # Body = everything between </head> and <script>
    body_match = re.search(r'</head>\s*<body>\s*(.*?)\s*<script>', html_content, re.DOTALL)
    body = body_match.group(1).strip() if body_match else ''
    
    return css, body, js

def b64(s):
    return base64.b64encode(s.encode('utf-8')).decode('ascii')

# Read the backup (original working index.html)
index_html = read_file('index.html.bak')

# Extract menu shell
menu_css_match = re.search(r'<style>(.*?)</style>', index_html, re.DOTALL)
menu_css = menu_css_match.group(1).strip() if menu_css_match else ''

menu_body_match = re.search(r'</head>\s*<body>\s*(.*?)\s*<script>', index_html, re.DOTALL)
menu_body = menu_body_match.group(1).strip() if menu_body_match else ''

menu_js_match = re.search(r'<script>(.*?)</script>', index_html, re.DOTALL)
menu_js = menu_js_match.group(1).strip() if menu_js_match else ''

print(f"Menu CSS: {len(menu_css)} chars")
print(f"Menu body: {len(menu_body)} chars")
print(f"Menu JS: {len(menu_js)} chars")
print(f"Menu body preview: {menu_body[:200]}")

# Process each tool
tools = {
    'sample_report': 'sample-report.html',
    'v50': 'v50.html', 
    'customer_payment': 'customer-payment.html'
}

tool_defs = []
for var_name, filename in tools.items():
    content = read_file(filename)
    css, body, js = extract_parts(content)
    
    css_b64 = b64(css)
    body_b64 = b64(body)
    js_b64 = b64(js)
    
    tool_defs.append(f"var TOOL_{var_name}={{s:atob('{css_b64}'),b:atob('{body_b64}'),c:[atob('{js_b64}')]}};")
    print(f"  TOOL_{var_name}: CSS={len(css)}, Body={len(body)}, JS={len(js)}")

# Build output
tool_section = '\n'.join(tool_defs)

output = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>土土协作</title>
<style>
{menu_css}
</style>
</head>
<body>
{menu_body}
<script>
{menu_js}

{tool_section}

function loadTool(name) {{
  var t = window['TOOL_' + name.replace(/-/g, '_')];
  if (!t) {{ alert('工具未找到'); return; }}
  var s = '';
  if (t.s) s += '<style>' + t.s + '</style>';
  s += t.b;
  if (t.c) {{
    for (var i = 0; i < t.c.length; i++) {{
      s += '<scr' + 'ipt>' + t.c[i] + '</scr' + 'ipt>';
    }}
  }}
  document.open();
  document.write(s);
  document.close();
}}
</script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"\nBuilt index.html: {len(output)} bytes")
