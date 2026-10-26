#!/usr/bin/env python3
import os
import yaml
from datetime import datetime, date, timedelta

def load_config(path="config.yaml"):
    """读取 YAML 配置文件"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"找不到配置文件: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def generate_ics(config, output_path="output/anniversary.ics"):
    """根据配置生成 ICS 日历文件"""
    # ICS 文件的基础头部
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//GitHub Anniversary Counter//CN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:纪念日",
        "X-APPLE-CALENDAR-COLOR:#FF2968", # 给苹果日历设置一个粉色主题
    ]
    
    # 获取今天的日期
    today = date.today()
    # 计算明天的日期（用于全天事件的 DTEND）
    tomorrow = today + timedelta(days=1)
    
    now_utc = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    
    for idx, item in enumerate(config.get("anniversaries", [])):
        name = item["name"]
        # 解析配置中的日期时间
        start_dt = datetime.strptime(item["date"], "%Y-%m-%d %H:%M")
        start_date = start_dt.date()
        
        # 计算天数差
        delta_days = (today - start_date).days
        
        if delta_days >= 0:
            # 纪念日已过（含当天），计算正数天数。当天算第 1 天
            days_count = delta_days + 1
            title = f"{name} 第 {days_count} 天"
        else:
            # 纪念日还没到，计算倒数天数
            days_left = abs(delta_days)
            title = f"距离 {name} 还有 {days_left} 天"
        
        # 为了保证每天日历都能刷新，UID 必须包含今天的日期
        # 这样苹果日历会认为每天是一个新事件，替换掉旧的，不会堆积
        uid = f"anniv-{idx}-{today.strftime('%Y%m%d')}@github-actions"
        
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now_utc}",
            # 设置为全天事件 (VALUE=DATE)
            f"DTSTART;VALUE=DATE:{today.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{tomorrow.strftime('%Y%m%d')}",
            f"SUMMARY:{title}",
            "TRANSP:TRANSPARENT", # 设置为“空闲”，不占用你的日程时间
            "END:VEVENT",
        ])
    
    # ICS 文件尾部
    lines.append("END:VCALENDAR")
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 写入文件（使用 \r\n 换行是 ICS 格式的严格标准）
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
