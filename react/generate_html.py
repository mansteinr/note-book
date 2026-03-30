#!/usr/bin/env python3
"""
批量将 markdown 文件转换为 HTML 文件
"""

import os
import re
from pathlib import Path

def read_markdown_file(filepath):
    """读取 markdown 文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件 {filepath} 失败: {e}")
        return None

def extract_title(content):
    """从 markdown 内容中提取标题"""
    # 查找第一个一级标题
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    
    # 如果没有找到一级标题，使用文件名
    return "React 技术文档"

def extract_toc(content):
    """从 markdown 内容中提取目录"""
    toc_items = []
    
    # 查找所有二级标题
    for match in re.finditer(r'^##\s+(.+)$', content, re.MULTILINE):
        title = match.group(1).strip()
        # 生成锚点ID
        anchor = re.sub(r'[^\w\u4e00-\u9fff\-]', '', title.lower().replace(' ', '-'))
        toc_items.append((title, anchor))
    
    return toc_items

def generate_html_template(title, toc_items, content):
    """生成 HTML 模板"""
    
    # 生成目录 HTML
    toc_html = ''
    for toc_title, toc_anchor in toc_items:
        toc_html += f'                <li><a href="#{toc_anchor}">{toc_title}</a></li>\n'
    
    # 转换 markdown 内容为 HTML
    html_content = markdown_to_html(content)
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/languages/javascript.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/languages/typescript.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/languages/jsx.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --primary-color: #007acc;
            --secondary-color: #2d2d2d;
            --accent-color: #61dafb;
            --text-color: #333;
            --light-bg: #f8f9fa;
            --border-color: #e1e4e8;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
            --info-color: #17a2b8;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            display: flex;
            gap: 30px;
        }}

        .sidebar {{
            width: 280px;
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 20px;
            height: fit-content;
            max-height: calc(100vh - 40px);
            overflow-y: auto;
        }}

        .sidebar h2 {{
            color: var(--primary-color);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--accent-color);
            font-size: 1.5rem;
        }}

        .toc {{
            list-style: none;
        }}

        .toc li {{
            margin-bottom: 12px;
            position: relative;
        }}

        .toc a {{
            color: var(--text-color);
            text-decoration: none;
            display: block;
            padding: 8px 12px;
            border-radius: 6px;
            transition: all 0.3s ease;
            border-left: 3px solid transparent;
        }}

        .toc a:hover {{
            background: var(--light-bg);
            color: var(--primary-color);
            border-left-color: var(--accent-color);
            transform: translateX(5px);
        }}

        .toc a.active {{
            background: var(--primary-color);
            color: white;
            border-left-color: var(--accent-color);
        }}

        .main-content {{
            flex: 1;
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid var(--accent-color);
        }}

        .header h1 {{
            color: var(--primary-color);
            font-size: 2.5rem;
            margin-bottom: 15px;
            background: linear-gradient(45deg, var(--primary-color), var(--accent-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .header .subtitle {{
            color: var(--secondary-color);
            font-size: 1.2rem;
            opacity: 0.8;
        }}

        .content-section {{
            margin-bottom: 40px;
        }}

        .content-section h2 {{
            color: var(--primary-color);
            font-size: 1.8rem;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--light-bg);
            position: relative;
        }}

        .content-section h2::after {{
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 60px;
            height: 2px;
            background: var(--accent-color);
        }}

        .content-section h3 {{
            color: var(--secondary-color);
            font-size: 1.4rem;
            margin: 25px 0 15px;
        }}

        .content-section h4 {{
            color: var(--secondary-color);
            font-size: 1.2rem;
            margin: 20px 0 10px;
        }}

        .content-section p {{
            margin-bottom: 15px;
            font-size: 1.1rem;
        }}

        .content-section ul, .content-section ol {{
            margin: 15px 0 15px 25px;
        }}

        .content-section li {{
            margin-bottom: 8px;
            font-size: 1.1rem;
        }}

        .code-block {{
            background: var(--secondary-color);
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            overflow-x: auto;
            position: relative;
        }}

        .code-block pre {{
            margin: 0;
        }}

        .code-block code {{
            font-family: 'Fira Code', 'Consolas', 'Monaco', 'Andale Mono', 'Ubuntu Mono', monospace;
            font-size: 0.95rem;
        }}

        .code-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            color: #ccc;
            font-size: 0.9rem;
        }}

        .copy-btn {{
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: background 0.3s;
        }}

        .copy-btn:hover {{
            background: var(--accent-color);
        }}

        .note {{
            background: #e7f3ff;
            border-left: 4px solid var(--primary-color);
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}

        .note strong {{
            color: var(--primary-color);
        }}

        .warning {{
            background: #fff3cd;
            border-left: 4px solid var(--warning-color);
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}

        .warning strong {{
            color: var(--warning-color);
        }}

        .tip {{
            background: #d4edda;
            border-left: 4px solid var(--success-color);
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}

        .tip strong {{
            color: var(--success-color);
        }}

        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .comparison-table th {{
            background: var(--primary-color);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        .comparison-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid var(--border-color);
        }}

        .comparison-table tr:hover {{
            background: var(--light-bg);
        }}

        .comparison-table .good {{
            color: var(--success-color);
            font-weight: 600;
        }}

        .comparison-table .bad {{
            color: var(--danger-color);
            font-weight: 600;
        }}

        .comparison-table .neutral {{
            color: var(--warning-color);
            font-weight: 600;
        }}

        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
            color: var(--secondary-color);
            font-size: 0.9rem;
        }}

        .footer a {{
            color: var(--primary-color);
            text-decoration: none;
        }}

        .footer a:hover {{
            text-decoration: underline;
        }}

        @media (max-width: 768px) {{
            .container {{
                flex-direction: column;
            }}
            
            .sidebar {{
                width: 100%;
                position: static;
                max-height: none;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .main-content {{
                padding: 20px;
            }}
        }}

        .back-to-top {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--primary-color);
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            font-size: 1.5rem;
            box-shadow: 0 4px 15px rgba(0, 122, 204, 0.3);
            transition: all 0.3s ease;
            z-index: 1000;
        }}

        .back-to-top:hover {{
            background: var(--accent-color);
            transform: translateY(-5px);
        }}
    </style>
</head>
<body>
    <div class="container">
        <aside class="sidebar">
            <h2>📚 目录</h2>
            <ul class="toc" id="toc">
{toc_html}            </ul>
        </aside>

        <main class="main-content">
            <header class="header">
                <h1>{title}</h1>
                <p class="subtitle">React 技术文档 - 详细解析与最佳实践</p>
            </header>

            <div id="content">
                {html_content}
            </div>

            <footer class="footer">
                <p>© 2024 React 技术文档 | 生成时间: <span id="current-date"></span></p>
                <p>本文档基于 React 官方文档和社区最佳实践编写</p>
                <p><a href="#top">返回顶部</a></p>
            </footer>
        </main>
    </div>

    <a href="#top" class="back-to-top" id="back-to-top">↑</a>

    <script>
        // 设置当前日期
        document.getElementById('current-date').textContent = new Date().toLocaleDateString('zh-CN');
        
        // 代码高亮
        document.addEventListener('DOMContentLoaded', function() {{
            hljs.highlightAll();
        }});
        
        // 复制代码功能
        function copyCode(button) {{
            const codeBlock = button.parentElement.nextElementSibling;
            const codeText = codeBlock.textContent;
            
            navigator.clipboard.writeText(codeText).then(() => {{
                const originalText = button.textContent;
                button.textContent = '已复制!';
                button.style.background = 'var(--success-color)';
                
                setTimeout(() => {{
                    button.textContent = originalText;
                    button.style.background = 'var(--primary-color)';
                }}, 2000);
            }}).catch(err => {{
                console.error('复制失败:', err);
                button.textContent = '复制失败';
                button.style.background = 'var(--danger-color)';
                
                setTimeout(() => {{
                    button.textContent = '复制代码';
                    button.style.background = 'var(--primary-color)';
                }}, 2000);
            }});
        }}
        
        // 目录导航高亮
        window.addEventListener('scroll', function() {{
            const sections = document.querySelectorAll('.content-section h2');
            const tocLinks = document.querySelectorAll('.toc a');
            
            let currentSection = '';
            
            sections.forEach(section => {{
                const sectionTop = section.offsetTop;
                if (scrollY >= sectionTop - 100) {{
                    currentSection = section.getAttribute('id');
                }}
            }});
            
            tocLinks.forEach(link => {{
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${{currentSection}}`) {{
                    link.classList.add('active');
                }}
            }});
            
            // 显示/隐藏返回顶部按钮
            const backToTop = document.getElementById('back-to-top');
            if (window.scrollY > 300) {{
                backToTop.style.display = 'flex';
            }} else {{
                backToTop.style.display = 'none';
            }}
        }});
        
        // 平滑滚动
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function(e) {{
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {{
                    window.scrollTo({{
                        top: targetElement.offsetTop - 20,
                        behavior: 'smooth'
                    }});
                }}
            }});
        }});
        
        // 初始化显示返回顶部按钮
        document.getElementById('back-to-top').style.display = 'none';
    </script>
</body>
</html>'''

def markdown_to_html(markdown_text):
    """简单的 markdown 转 HTML 转换器"""
    if not markdown_text:
        return "<p>内容为空</p>"
    
    html = markdown_text
    
    # 转换标题
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2 id="\1">\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    
    # 转换代码块
    html = re.sub(r'```(\w+)?\n(.*?)\n```', 
                  r'<div class="code-block"><div class="code-header">\1</div><pre><code class="language-\1">\2</code></pre></div>', 
                  html, flags=re.DOTALL)
    
    # 转换行内代码
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # 转换列表
    html = re.sub(r'^\* (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*?</li>\n?)+', r'<ul>\g<0></ul>', html, flags=re.DOTALL)
    
    # 转换加粗
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    
    # 转换斜体
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # 转换段落
    lines = html.split('\n')
    result = []
    in_paragraph = False
    current_paragraph = []
    
    for line in lines:
        if line.strip() == '':
            if in_paragraph and current_paragraph:
                result.append('<p>' + ' '.join(current_paragraph) + '</p>')
                in_paragraph = False
                current_paragraph = []
            result.append('')
        elif line.startswith(('<h', '<ul', '<li', '<div', '<pre', '<code')):
            if in_paragraph and current_paragraph:
                result.append('<p>' + ' '.join(current_paragraph) + '</p>')
                in_paragraph = False
                current_paragraph = []
            result.append(line)
        else:
            in_paragraph = True
            current_paragraph.append(line)
    
    if in_paragraph and current_paragraph:
        result.append('<p>' + ' '.join(current_paragraph) + '</p>')
    
    return '\n'.join(result)

def process_markdown_files(directory):
    """处理目录中的所有 markdown 文件"""
    directory = Path(directory)
    markdown_files = list(directory.glob('*.md'))
    
    print(f"找到 {len(markdown_files)} 个 markdown 文件")
    
    for md_file in markdown_files:
        html_file = md_file.with_suffix('.html')
        
        # 如果 HTML 文件已存在，跳过
        if html_file.exists():
            print(f"跳过: {md_file.name} (HTML 已存在)")
            continue
        
        print(f"处理: {md_file.name} -> {html_file.name}")
        
        # 读取 markdown 内容
        content = read_markdown_file(md_file)
        if content is None:
            continue
        
        # 提取标题和目录
        title = extract_title(content)
        toc_items = extract_toc(content)
        
        # 生成 HTML
        html_content = generate_html_template(title, toc_items, content)
        
        # 写入 HTML 文件
        try:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"  成功生成: {html_file.name}")
        except Exception as e:
            print(f"  写入失败: {e}")

def main():
    """主函数"""
    current_dir = Path(__file__).parent
    print(f"工作目录: {current_dir}")
    
    # 处理当前目录下的 markdown 文件
    process_markdown_files(current_dir)
    
    print("\n处理完成！")

if __name__ == "__main__":
    main()