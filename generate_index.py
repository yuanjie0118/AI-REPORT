#!/usr/bin/env python3
"""扫描 reports/ 模块子目录，自动生成索引页 index.html"""
import os, re
from datetime import datetime

REPORTS_DIR = "reports"
MODULE_MAP = {
    "it": "IT",
    "business": "业务",
    "finance": "财务",
    "warehouse": "仓储",
    "customer_service": "客服"
}

def parse_filename(filename):
    """解析文件名，提取日期和项目名
    格式: YYYY-MM-DD-项目名.html
    """
    m = re.match(r'^(\d{4}-\d{2}-\d{2})-(.+)\.html$', filename)
    if m:
        return m.group(1), m.group(2)
    return None, None

def generate_index():
    reports = []
    # 遍历模块子目录
    for module_key in sorted(os.listdir(REPORTS_DIR)):
        module_dir = os.path.join(REPORTS_DIR, module_key)
        if not os.path.isdir(module_dir):
            continue
        module_name = MODULE_MAP.get(module_key, module_key)
        for f in sorted(os.listdir(module_dir), reverse=True):
            if f.endswith('.html'):
                date_str, project = parse_filename(f)
                if date_str and project:
                    reports.append({
                        'file': f,
                        'date': date_str,
                        'project': project,
                        'module_key': module_key,
                        'module_name': module_name,
                        'path': f'{REPORTS_DIR}/{module_key}/{f}'
                    })

    # 按日期倒序，同日期按模块、项目排序
    reports.sort(key=lambda x: (
        -datetime.strptime(x['date'], '%Y-%m-%d').timestamp(),
        x['module_name'],
        x['project']
    ))

    # 按日期分组
    groups = {}
    for r in reports:
        groups.setdefault(r['date'], []).append(r)

    # 统计各模块数量
    module_counts = {}
    for r in reports:
        module_counts[r['module_name']] = module_counts.get(r['module_name'], 0) + 1

    module_stat_cards = ""
    for name, count in sorted(module_counts.items()):
        module_stat_cards += f'<div class="stat-card"><div class="num">{count}</div><div class="label">{name}</div></div>'

    rows = ""
    for date in sorted(groups.keys(), reverse=True):
        rows += f'<tr class="date-row"><td colspan="3">📅 {date}</td></tr>\n'
        for r in groups[date]:
            rows += f'<tr><td><span class="badge">{r["module_name"]}</span></td><td><a href="{r["path"]}">{r["project"]}</a></td><td>{r["date"]}</td></tr>\n'

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>报表中心</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif; background: #f5f7fa; color: #333; padding: 40px 20px; }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  h1 {{ font-size: 28px; margin-bottom: 8px; color: #1a1a2e; }}
  .subtitle {{ color: #888; font-size: 14px; margin-bottom: 24px; }}
  .stats {{ display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }}
  .stat-card {{ background: #fff; border-radius: 12px; padding: 16px 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); min-width: 100px; flex: 1; }}
  .stat-card .num {{ font-size: 24px; font-weight: 700; color: #0f3460; }}
  .stat-card .label {{ font-size: 12px; color: #888; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
  th {{ background: #1a1a2e; color: #fff; padding: 14px 20px; text-align: left; font-size: 14px; font-weight: 500; }}
  td {{ padding: 12px 20px; border-bottom: 1px solid #f0f0f0; font-size: 14px; }}
  tr:hover td {{ background: #f8f9ff; }}
  tr.date-row td {{ background: #f0f2f5; font-weight: 600; color: #555; padding: 10px 20px; font-size: 13px; }}
  a {{ color: #0f3460; text-decoration: none; font-weight: 500; }}
  a:hover {{ text-decoration: underline; }}
  .badge {{ display: inline-block; padding: 2px 10px; border-radius: 10px; font-size: 12px; font-weight: 600; background: #e8f0fe; color: #0f3460; }}
  .empty {{ text-align: center; padding: 60px 20px; color: #888; }}
  .footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: #aaa; }}
</style>
</head>
<body>
<div class="container">
  <h1>报表中心</h1>
  <p class="subtitle">按模块分类的历史报表归档与快速导航</p>
  <div class="stats">
    <div class="stat-card"><div class="num">{len(reports)}</div><div class="label">报表总数</div></div>
    <div class="stat-card"><div class="num">{len(groups)}</div><div class="label">日期跨度</div></div>
    {module_stat_cards}
  </div>
  {'<table><thead><tr><th style="width:80px">模块</th><th>项目名称</th><th style="width:120px">生成日期</th></tr></thead><tbody>' + rows + '</tbody></table>' if reports else '<div class="empty">暂无报表，请先生成报告文件并放入 reports/ 模块子目录</div>'}
  <div class="footer">自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
</div>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[index] 索引页已生成，共 {len(reports)} 条记录，模块: {', '.join(module_counts.keys())}")

if __name__ == "__main__":
    generate_index()
