"""美化 album-tracker CSS - 只改样式，不动逻辑"""
import os

path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\css\style.css'
with open(path, 'r', encoding='utf-8') as f:
    css = f.read()

replacements = [
    # 1. h1 标题：加下划线装饰
    (
        """h1 {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 42px;
  font-weight: 600;
  line-height: 1.1;
  letter-spacing: -0.03em;
  color: var(--text);
  margin-bottom: 40px;
}""",
        """h1 {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 38px;
  font-weight: 600;
  line-height: 1.15;
  letter-spacing: -0.03em;
  color: var(--text);
  margin-bottom: 6px;
}

h1::after {
  content: '';
  display: block;
  width: 48px;
  height: 3px;
  background: linear-gradient(90deg, var(--warm-gold), var(--accent));
  border-radius: 2px;
  margin-top: 14px;
}"""
    ),
    
    # 2. 统计卡片：渐变背景
    (
        """.stat-card {
  position: relative;
  padding: 28px 32px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  transition: all var(--transition);
  overflow: hidden;
}""",
        """.stat-card {
  position: relative;
  padding: 28px 32px;
  background: linear-gradient(135deg, var(--bg) 0%, rgba(26,58,82,0.02) 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  transition: all var(--transition);
  overflow: hidden;
}"""
    ),
    
    # 3. 统计卡片 hover
    (
        """.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}""",
        """.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-3px);
  border-color: var(--accent);
}"""
    ),
    
    # 4. chart-card 美化
    (
        """.chart-card {
  padding: 32px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}""",
        """.chart-card {
  padding: 28px 30px;
  background: linear-gradient(135deg, var(--bg) 0%, rgba(201,162,39,0.025) 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  transition: all var(--transition);
}

.chart-card:hover {
  box-shadow: var(--shadow);
}"""
    ),
    
    # 5. 榜单 item 增强
    (
        """.lb-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  transition: background var(--transition);
}

.lb-item:hover {
  background: var(--bg-tertiary);
}""",
        """.lb-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  transition: all var(--transition);
  border: 1px solid transparent;
}

.lb-item:hover {
  background: var(--bg-secondary);
  border-color: var(--border-light);
  transform: translateX(2px);
}"""
    ),
    
    # 6. 榜单封面
    (
        """.lb-cover {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
  flex-shrink: 0;
}

.lb-cover-placeholder {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 4px;
  font-size: 16px;
  flex-shrink: 0;
}""",
        """.lb-cover {
  width: 44px;
  height: 44px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.10);
  flex-shrink: 0;
  transition: transform var(--transition);
}

.lb-item:hover .lb-cover {
  transform: scale(1.06);
}

.lb-cover-placeholder {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--bg-tertiary), var(--border-light));
  border-radius: 8px;
  font-size: 18px;
  flex-shrink: 0;
}"""
    ),
    
    # 7. 排名样式
    (
        """.lb-rank {
  font-family: 'Cormorant Garamond', serif;
  font-size: 20px;
  font-weight: 600;
  color: var(--accent);
  min-width: 28px;
  text-align: center;
}

.lb-item:nth-child(1) .lb-rank { color: #f5a623; font-size: 24px; }
.lb-item:nth-child(2) .lb-rank { color: #8e8e93; font-size: 22px; }
.lb-item:nth-child(3) .lb-rank { color: #cd7f32; font-size: 22px; }""",
        """.lb-rank {
  font-family: 'Cormorant Garamond', serif;
  font-size: 20px;
  font-weight: 700;
  color: var(--text-muted);
  min-width: 30px;
  text-align: center;
  opacity: 0.55;
}

.lb-item:nth-child(1) .lb-rank { 
  color: var(--warm-gold); 
  font-size: 24px; 
  opacity: 1; 
}
.lb-item:nth-child(2) .lb-rank { 
  color: #9ca3af; 
  font-size: 22px; 
  opacity: 1; 
}
.lb-item:nth-child(3) .lb-rank { 
  color: #b8865c; 
  font-size: 22px; 
  opacity: 1; 
}"""
    ),
    
    # 8. 收听次数数字
    (
        """.lb-count {
  font-size: 13px;
  color: var(--text-muted);
  white-space: nowrap;
  margin-left: auto;
}""",
        """.lb-count {
  font-family: 'Cormorant Garamond', serif;
  font-size: 17px;
  font-weight: 600;
  color: var(--accent);
  white-space: nowrap;
  margin-left: auto;
}"""
    ),
]

for old, new in replacements:
    if old in css:
        css = css.replace(old, new)
        print(f'  OK: replaced block ({len(old)} chars)')
    else:
        print(f'  SKIP: not found ({len(old)} chars)')

with open(path, 'w', encoding='utf-8') as f:
    f.write(css)

print(f'\nDone! CSS size: {len(css)} bytes')
