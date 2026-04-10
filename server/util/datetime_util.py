from datetime import datetime, timezone, timedelta

# 北京时区 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

def now_beijing():
    """返回北京时间（不带时区信息的datetime对象，兼容SQLAlchemy）"""
    return datetime.now(BEIJING_TZ).replace(tzinfo=None)