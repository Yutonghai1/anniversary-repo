#!/usr/bin/env python3
import os
import yaml
from datetime import datetime, date, timedelta, timezone

def load_config(path="config.yaml"):
    """读取 YAML 配置文件"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"找不到配置文件: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        # 增加空文件保护
        if not data:
            raise ValueError("❌ config.yaml 内容为空或格式错误，请检查缩进和冒号（必须是英文冒号且后跟空格）")
        return data

def generate_ics(config, output_path="output/anniversary.ics"):
    """根据配置生成 ICS 日历文件"""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//GitHub Anniversary Counter//CN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:纪念日",
        "X-APPLE-CALENDAR-COLOR:#FF2968",
    ]
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    # 修复 utcnow 的警告，使用带时区的当前时间
    now_utc = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    
    anniversaries = config.get("anniversaries", [])
    if not anniversaries:
        raise ValueError("❌ 在 config.yaml 中未找到 'anniversaries' 列表，请检查拼写")

    for idx, item in enumerate(anniversaries):
        name = item.get("name", "未命名")
        date_str = item.get("date")
        
        if not date_str:
            print(f"⚠️ 警告: 第 {idx+1} 个纪念日缺少 'date' 字段，已跳过")
            continue
            
        try:
            start_dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            start_date = start_dt.date()
        except ValueError:
            print(f"⚠️ 警告: '{date_str}' 日期格式错误，应为 'YYYY-MM-DD HH:MM'，已跳过")
            continue
        
        delta_days = (today - start_date).days
        
        if delta_days >= 0:
            days_count = delta_days + 1
            title = f"{name} 第 {days_count} 天"
        else:
            days_left = abs(delta_days)
            title = f"距离 {name} 还有 {days_left} 天"
        
        uid = f"anniv-{idx}-{today.strftime('%Y%m%d')}@github-actions"
        
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now_utc}",
            f"DTSTART;VALUE=DATE:{today.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{tomorrow.strftime('%Y%m%d')}",
            f"SUMMARY:{title}",
            "TRANSP:TRANSPARENT",
            "END:VEVENT",
        ])
    
    lines.append("END:VCALENDAR")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(lines))
        
    print(f"✅ 成功生成 ICS 文件: {output_path}")

if __name__ == "__main__":
    try:
        config_data = load_config()
        generate_ics(config_data)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        exit(1)
