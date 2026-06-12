#!/usr/bin/env python3
"""
Markdown → WeChat 公众号富文本 转换脚本

微信公众号的编辑器不支持 CSS class，只能接受内联样式。
本工具将 Markdown 转换为带内联样式的 HTML，在浏览器打开后
全选(Ctrl+A) → 复制(Ctrl+C) → 粘贴到公众号后台即可。

用法:
    python3 wechat_convert.py <markdown文件路径>

输出:
    同目录下的 .html 文件
"""

import sys
import os
import re
import markdown
from pathlib import Path
from html import unescape


def convert_md_to_html(md_text: str) -> str:
    """将 Markdown 转换为公众号兼容的 HTML"""

    # 预处理：去掉 Markdown 中的目录部分（# 目录 ... 到下一个 # 之前）
    # 公众号不支持内部锚点跳转，保留 TOC 反而有死链接
    md_text = re.sub(
        r'^##\s+目录\s*\n(?:-.*\n?)*',
        '',
        md_text,
        flags=re.MULTILINE
    )

    raw_html = markdown.markdown(
        md_text,
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.toc',
            'markdown.extensions.nl2br',
        ]
    )

    # === 全局替换：对整个 HTML 做正则 ===

    # 1. 标题（可能带 id 属性如 <h1 id="llm">）
    raw_html = re.sub(
        r'<h1[^>]*>(.*?)</h1>',
        r'<section style="text-align: center; margin: 28px 0 16px 0; font-size: 22px; font-weight: bold; color: #1a1a1a;">\1</section>',
        raw_html
    )
    raw_html = re.sub(
        r'<h2[^>]*>(.*?)</h2>',
        r'<section style="margin: 24px 0 12px 0; font-size: 18px; font-weight: bold; color: #1a1a1a; border-left: 4px solid #07c160; padding-left: 12px;">\1</section>',
        raw_html
    )
    raw_html = re.sub(
        r'<h3[^>]*>(.*?)</h3>',
        r'<section style="margin: 20px 0 10px 0; font-size: 16px; font-weight: bold; color: #333;">\1</section>',
        raw_html
    )
    raw_html = re.sub(
        r'<h[4-6][^>]*>(.*?)</h[4-6]>',
        r'<section style="margin: 16px 0 8px 0; font-size: 15px; font-weight: bold; color: #555;">\1</section>',
        raw_html
    )
    raw_html = re.sub(
        r'<h2>(.*?)</h2>',
        r'<section style="margin: 24px 0 12px 0; font-size: 18px; font-weight: bold; color: #1a1a1a; border-left: 4px solid #07c160; padding-left: 12px;">\1</section>',
        raw_html
    )
    raw_html = re.sub(
        r'<h3>(.*?)</h3>',
        r'<section style="margin: 20px 0 10px 0; font-size: 16px; font-weight: bold; color: #333;">\1</section>',
        raw_html
    )
    raw_html = re.sub(
        r'<h[4-6]>(.*?)</h[4-6]>',
        r'<section style="margin: 16px 0 8px 0; font-size: 15px; font-weight: bold; color: #555;">\1</section>',
        raw_html
    )

    # 2. 段落
    raw_html = re.sub(
        r'<p>(.*?)</p>',
        r'<p style="margin: 10px 0; line-height: 1.8; font-size: 15px; color: #333; letter-spacing: 0.5px;">\1</p>',
        raw_html
    )

    # 3. 代码块: <pre><code>...</code></pre>
    # 用替换函数来处理，因为内容中可能有 HTML 实体
    def replace_codeblock(m):
        content = m.group(1)
        # 公众号不支持 code 标签嵌套在 pre 中，直接用 div + 内联样式
        escaped = content.replace('</code>', '').replace('<code>', '')
        return f'<section style="background-color: #f7f7f7; border-radius: 6px; padding: 14px 16px; margin: 14px 0; overflow-x: auto; font-size: 13px; font-family: Consolas, Monaco, \\\'Courier New\\\', monospace; line-height: 1.6; color: #333; border: 1px solid #e8e8e8; white-space: pre-wrap; word-break: break-all;">{escaped}</section>'

    raw_html = re.sub(
        r'<pre><code>(.*?)</code></pre>',
        replace_codeblock,
        raw_html,
        flags=re.DOTALL
    )

    # 4. 行内代码
    raw_html = re.sub(
        r'<code>(.*?)</code>',
        r'<code style="background-color: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 13px; font-family: Consolas, Monaco, \\\'Courier New\\\', monospace; color: #d63384;">\1</code>',
        raw_html
    )

    # 5. 表格：整体包裹 + 行列样式
    def replace_table(m):
        content = m.group(1)
        # 给 th 加样式
        content = re.sub(r'<th>(.*?)</th>', r'<th style="background-color: #07c160; color: #fff; padding: 10px 12px; text-align: left; font-weight: 600; white-space: nowrap;">\1</th>', content)
        # 给 td 加样式
        content = re.sub(r'<td>(.*?)</td>', r'<td style="padding: 8px 12px; border-bottom: 1px solid #f0f0f0; color: #333;">\1</td>', content)
        # 给 tr 加样式
        content = re.sub(r'<tr>', r'<tr style="transition: background 0.2s;">', content)
        return f'<div style="overflow-x: auto; margin: 16px 0; border: 1px solid #e0e0e0; border-radius: 6px;"><table style="width: 100%; border-collapse: collapse; font-size: 14px; min-width: 500px;">{content}</table></div>'

    raw_html = re.sub(
        r'<table>(.*?)</table>',
        replace_table,
        raw_html,
        flags=re.DOTALL
    )

    # 6. blockquote
    def replace_blockquote(m):
        content = m.group(1)
        return f'<blockquote style="margin: 14px 0; padding: 12px 16px; background-color: #f9f9f9; border-left: 4px solid #07c160; color: #666; font-size: 14px; line-height: 1.7; border-radius: 0 4px 4px 0;">{content}</blockquote>'

    raw_html = re.sub(
        r'<blockquote>(.*?)</blockquote>',
        replace_blockquote,
        raw_html,
        flags=re.DOTALL
    )

    # 7. 列表
    raw_html = re.sub(
        r'<ul>',
        r'<ul style="padding-left: 24px; margin: 10px 0; line-height: 1.8; font-size: 15px; color: #333;">',
        raw_html
    )
    raw_html = re.sub(
        r'<ol>',
        r'<ol style="padding-left: 24px; margin: 10px 0; line-height: 1.8; font-size: 15px; color: #333;">',
        raw_html
    )
    raw_html = re.sub(
        r'<li>',
        r'<li style="margin: 4px 0;">',
        raw_html
    )

    # 8. 链接
    raw_html = re.sub(
        r'<a\s+href="(.*?)">(.*?)</a>',
        r'<a href="\1" style="color: #07c160; text-decoration: none; border-bottom: 1px solid #07c160;" target="_blank">\2</a>',
        raw_html
    )

    # 9. 图片
    raw_html = re.sub(
        r'<img\s+src="(.*?)"\s*(?:alt="(.*?)")?\s*/?>',
        r'<img src="\1" alt="\2" style="max-width: 100%; height: auto; margin: 14px 0; border-radius: 6px; display: block;">',
        raw_html
    )

    # 10. 水平线
    raw_html = re.sub(
        r'<hr\s*/?>',
        r'<hr style="border: none; border-top: 1px solid #e0e0e0; margin: 24px 0;">',
        raw_html
    )

    # 11. 删除 目录的锚点链接（公众号里内部跳转无效）
    # 但保留链接样式即可

    # 12. 修复代码块中转义的单引号
    raw_html = raw_html.replace("\\'", "'")

    return raw_html


def wrap_html(content: str, title: str) -> str:
    """将转换后的内容包装在完整的 HTML 文档中"""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", "Microsoft YaHei", sans-serif;
            background: #f5f5f5;
            padding: 0;
        }}
        .article-container {{
            max-width: 680px;
            margin: 0 auto;
            background: #ffffff;
            padding: 30px 24px;
            min-height: 100vh;
        }}
        @media (max-width: 480px) {{
            .article-container {{
                padding: 20px 16px;
            }}
        }}
    </style>
</head>
<body>
    <div class="article-container">
        <div id="article-content">
            {content}
        </div>
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0 10px 0;">
        <p style="text-align: center; font-size: 13px; color: #999; margin: 10px 0 0 0;">— 全文完 —</p>
    </div>
</body>
</html>'''


def main():
    if len(sys.argv) < 2:
        print("用法: python3 wechat_convert.py <markdown文件路径>")
        sys.exit(1)

    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print(f"文件不存在: {md_path}")
        sys.exit(1)

    md_text = md_path.read_text(encoding='utf-8')

    # 提取标题（第一个 # 开头的行）
    title_match = re.search(r'^#\s+(.*)', md_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else md_path.stem

    # 转换
    content_html = convert_md_to_html(md_text)
    full_html = wrap_html(content_html, title)

    # 保存到同目录
    output_path = md_path.with_suffix('.html')
    output_path.write_text(full_html, encoding='utf-8')

    print(f"✅ 转换完成：{output_path}")
    print(f"📋 用浏览器打开 → Ctrl+A 全选 → Ctrl+C 复制 → 粘贴到公众号后台")


if __name__ == '__main__':
    main()
                                                                                                                                                                                                                                                    