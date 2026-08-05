# Python 日期时间处理详解

## 1. 日期时间处理概述

### 1.1 Python 中的时间相关模块

Python 处理日期时间主要涉及两个内置模块：

| 模块 | 说明 | 典型用途 |
|------|------|----------|
| `time` | 底层时间操作，基于 C 语言的 time.h | 时间戳、计时、休眠 |
| `datetime` | 面向对象的日期时间处理 | 日期计算、格式化、时区 |

此外还有：
- `calendar`：日历相关（判断闰年、生成月历等）
- `zoneinfo`（Python 3.9+）：内置时区数据库（IANA）
- `pytz`：第三方时区库（zoneinfo 之前的方案）

### 1.2 三种时间表示

Python 中时间有三种常见表示形式：

```python
import time
from datetime import datetime

# 1. 时间戳（timestamp）：从 1970-01-01 00:00:00 UTC 起的秒数（浮点数）
ts = time.time()
print(ts)        # 1722856800.123456

# 2. 结构化时间（struct_time）：含年月日等字段的命名元组
st = time.localtime()
print(st)        # time.struct_time(tm_year=2026, tm_mon=8, ...)

# 3. 格式化字符串：人类可读的日期字符串
s = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(s)         # 2026-08-05 14:30:00
```

---

## 2. time 模块

### 2.1 时间戳与 struct_time

```python
import time

# 当前时间戳（UTC，浮点秒数）
ts = time.time()
print(ts)                         # 1722856800.123456

# 时间戳 -> 本地 struct_time
local = time.localtime(ts)
print(local.tm_year)              # 2026
print(local.tm_mon)               # 8

# 时间戳 -> UTC struct_time
utc = time.gmtime(ts)

# struct_time -> 时间戳
print(time.mktime(local))
```

`struct_time` 的字段：

| 字段 | 含义 | 取值范围 |
|------|------|----------|
| `tm_year` | 年 | 如 2026 |
| `tm_mon` | 月 | 1~12 |
| `tm_mday` | 日 | 1~31 |
| `tm_hour` | 时 | 0~23 |
| `tm_min` | 分 | 0~59 |
| `tm_sec` | 秒 | 0~61（含闰秒） |
| `tm_wday` | 星期 | 0~6（0=周一） |
| `tm_yday` | 一年中第几天 | 1~366 |
| `tm_isdst` | 是否夏令时 | 0/1/-1 |

### 2.2 格式化与解析

```python
import time

# struct_time -> 格式化字符串
print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
# 2026-08-05 14:30:00

# 格式化字符串 -> struct_time
s = '2026-08-05 14:30:00'
st = time.strptime(s, '%Y-%m-%d %H:%M:%S')
print(st.tm_year, st.tm_mon, st.tm_mday)   # 2026 8 5
```

### 2.3 计时与休眠

```python
import time

# 休眠（秒）
time.sleep(2)          # 暂停 2 秒

# 计时：perf_counter 精度更高，适合性能测试
start = time.perf_counter()
# ... 执行待测代码 ...
end = time.perf_counter()
print(f'耗时 {end - start:.6f} 秒')

# 计时：time.time() 适合粗略测量
t0 = time.time()
# ... 代码 ...
print(f'耗时 {time.time() - t0:.3f} 秒')
```

> **提示**：测量代码执行时间优先用 `time.perf_counter()`（高精度单调时钟），而非 `time.time()`（受系统时钟调整影响）。

---

## 3. datetime 模块

`datetime` 模块提供四个核心类：

| 类 | 说明 |
|------|------|
| `date` | 日期（年、月、日） |
| `time` | 时间（时、分、秒、微秒，**注意与 `time` 模块同名但不同**） |
| `datetime` | 日期 + 时间 |
| `timedelta` | 时间差（两个日期/时间之间的差） |

### 3.1 date 对象

```python
from datetime import date

# 创建日期
d = date(2026, 8, 5)
print(d)                  # 2026-08-05

# 当前日期
today = date.today()
print(today)

# 从 ISO 格式字符串创建
d2 = date.fromisoformat('2026-12-31')

# 从时间戳创建
d3 = date.fromtimestamp(1722856800)

# 属性
print(d.year, d.month, d.day)        # 2026 8 5
print(d.weekday())                   # 1（0=周一，此处 2026-08-05 是周三？见下）

# ISO 星期：1=周一 ... 7=周日
print(d.isoweekday())

# 格式化
print(d.strftime('%Y/%m/%d'))        # 2026/08/05
```

### 3.2 time 对象

```python
from datetime import time

t = time(14, 30, 45, 123456)
print(t)                    # 14:30:45.123456
print(t.hour, t.minute, t.second, t.microsecond)

# 注意：datetime.time 是"一天中的时刻"，不含日期
```

### 3.3 datetime 对象

```python
from datetime import datetime

# 当前本地日期时间
now = datetime.now()
print(now)                  # 2026-08-05 14:30:45.123456

# 当前 UTC 日期时间（推荐用 now(timezone.utc)，见时区章节）
utcnow = datetime.utcnow()  # ⚠️ Python 3.12 起已弃用，建议用 datetime.now(timezone.utc)

# 指定日期时间创建
dt = datetime(2026, 8, 5, 14, 30, 0)
print(dt)

# 从字符串解析
dt2 = datetime.strptime('2026-08-05 14:30:00', '%Y-%m-%d %H:%M:%S')

# 从 ISO 格式创建
dt3 = datetime.fromisoformat('2026-08-05T14:30:00')

# datetime 与 date/time 互转
print(dt.date())            # 2026-08-05
print(dt.time())            # 14:30:00

# 转时间戳
print(dt.timestamp())
```

> **重要**：`datetime.utcnow()` 自 Python 3.12 起被弃用，因为它返回的是**不带时区信息**（naive）的 UTC 时间，容易与本地时间混淆。推荐改用 `datetime.now(timezone.utc)`（见第 5 章）。

---

## 4. timedelta 时间差

`timedelta` 表示两个日期或时间之间的差值，可用于日期运算。

### 4.1 创建与基本运算

```python
from datetime import datetime, timedelta

now = datetime.now()

# 加减时间
tomorrow = now + timedelta(days=1)
last_week = now - timedelta(weeks=1)
in_two_hours = now + timedelta(hours=2)

print(now)
print(tomorrow)
print(last_week)

# timedelta 可指定 weeks/days/hours/minutes/seconds/milliseconds/microseconds
delta = timedelta(days=1, hours=2, minutes=30)
print(delta)                # 1 day, 2:30:00
```

### 4.2 计算两个日期的差

```python
from datetime import date

d1 = date(2026, 8, 5)
d2 = date(2026, 12, 31)

delta = d2 - d1
print(delta)                # 148 days, 0:00:00
print(delta.days)           # 148
print(delta.total_seconds())# 12787200.0
```

### 4.3 timedelta 的属性与运算

```python
from datetime import timedelta

td = timedelta(days=1, hours=2, minutes=30)

# 总秒数（最常用）
print(td.total_seconds())   # 95400.0

# 取整数天
print(td.days)              # 1
print(td.seconds)           # 9000（去掉整天后剩余的秒数，2*3600+30*60）

# timedelta 之间可加减、比较
print(timedelta(hours=2) + timedelta(minutes=30))   # 2:30:00
print(timedelta(hours=2) > timedelta(hours=1))      # True
print(timedelta(hours=2) * 3)                        # 6:00:00
```

---

## 5. 格式化与解析

### 5.1 格式化代码速查

| 代码 | 含义 | 示例 |
|------|------|------|
| `%Y` | 四位年份 | 2026 |
| `%y` | 两位年份 | 26 |
| `%m` | 月份（01-12） | 08 |
| `%d` | 日（01-31） | 05 |
| `%H` | 24 小时制时（00-23） | 14 |
| `%I` | 12 小时制时（01-12） | 02 |
| `%M` | 分（00-59） | 30 |
| `%S` | 秒（00-59） | 45 |
| `%p` | AM/PM | PM |
| `%A` | 星期全名 | Wednesday |
| `%a` | 星期缩写 | Wed |
| `%B` | 月份全名 | August |
| `%b` | 月份缩写 | Aug |
| `%w` | 星期数字（0=周日） | 3 |
| `%j` | 一年中第几天（001-366） | 217 |
| `%U`/%W | 一年中第几周 | 31 |
| `%f` | 微秒（6 位） | 123456 |
| `%Z` | 时区名 | UTC |
| `%z` | 时区偏移 | +0800 |
| `%%` | 字面量 % | % |

### 5.2 strftime 与 strptime

```python
from datetime import datetime

dt = datetime(2026, 8, 5, 14, 30, 45)

# datetime -> 字符串（strftime = string format time）
print(dt.strftime('%Y年%m月%d日 %H:%M:%S'))   # 2026年08月05日 14:30:45
print(dt.strftime('%Y-%m-%d %I:%M %p'))        # 2026-08-05 02:30 PM
print(dt.strftime('%A, %B %d, %Y'))            # Wednesday, August 05, 2026

# 字符串 -> datetime（strptime = string parse time）
s = '2026-08-05 14:30:45'
dt2 = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
print(dt2)
```

### 5.3 ISO 8601 格式

ISO 8601 是国际标准日期时间格式（`YYYY-MM-DDTHH:MM:SS`），Python 提供专用方法：

```python
from datetime import datetime

dt = datetime(2026, 8, 5, 14, 30, 45)

# 转 ISO 格式
print(dt.isoformat())          # 2026-08-05T14:30:45

# 从 ISO 格式解析（Python 3.7+）
print(datetime.fromisoformat('2026-08-05T14:30:45'))
```

> **建议**：程序间数据交换（如 API、日志）优先用 ISO 8601 格式，避免不同地区格式歧义。

---

## 6. 时区处理

### 6.1 naive 与 aware 日期时间

- **naive（朴素）**：不带时区信息，"裸"的日期时间，含义依赖上下文。
- **aware（感知）**：带时区信息，能明确对应到某个绝对时刻。

```python
from datetime import datetime, timezone, timedelta

# naive：无时区
naive = datetime.now()
print(naive.tzinfo)         # None

# aware：带时区（UTC）
aware = datetime.now(timezone.utc)
print(aware.tzinfo)         # UTC

# 创建自定义时区（东八区）
tz_bj = timezone(timedelta(hours=8))
bj_time = datetime.now(tz_bj)
print(bj_time)              # 2026-08-05 22:30:00+08:00
```

### 6.2 使用 zoneinfo（Python 3.9+）

`zoneinfo` 是 Python 3.9+ 内置的时区库，基于 IANA 时区数据库，能正确处理夏令时：

```python
from datetime import datetime
from zoneinfo import ZoneInfo

# 指定时区创建
tz_sh = ZoneInfo('Asia/Shanghai')
tz_ny = ZoneInfo('America/New_York')

now_sh = datetime.now(tz_sh)
now_ny = datetime.now(tz_ny)

print('上海:', now_sh)      # 2026-08-05 22:30:00+08:00
print('纽约:', now_ny)      # 2026-08-05 10:30:00-04:00

# 时区转换：用 astimezone
sh_to_ny = now_sh.astimezone(tz_ny)
print('上海转纽约:', sh_to_ny)   # 与 now_ny 时刻一致
```

> **注意**：使用 `ZoneInfo` 需要系统装有 IANA 时区数据库。Windows 系统若缺失，可通过 `pip install tzdata` 提供数据。

### 6.3 时区转换实战

```python
from datetime import datetime
from zoneinfo import ZoneInfo

# 解析一个"上海时间"字符串，转为其他时区
s = '2026-08-05 14:30:00'
dt_sh = datetime.strptime(s, '%Y-%m-%d %H:%M:%S').replace(tzinfo=ZoneInfo('Asia/Shanghai'))

print('上海:', dt_sh)
print('UTC :', dt_sh.astimezone(ZoneInfo('UTC')))
print('东京:', dt_sh.astimezone(ZoneInfo('Asia/Tokyo')))
print('纽约:', dt_sh.astimezone(ZoneInfo('America/New_York')))
```

### 6.4 时区处理建议

- **存储**：内部统一存 UTC 时间（时间戳或带 UTC 时区的 datetime）。
- **展示**：在展示层根据用户时区转换。
- **避免 naive 时间混用**：aware 与 naive 之间做运算会抛 `TypeError`，应统一。
- **优先用 `zoneinfo`**（3.9+），`pytz` 接口风格不同（`pytz.localize`），新项目不必再引入。

---

## 7. calendar 模块

```python
import calendar

# 判断闰年
print(calendar.isleap(2024))   # True
print(calendar.isleap(2026))   # False

# 某月有多少天
print(calendar.monthrange(2026, 2))   # (6, 28)：2 月 1 日是周日(6)，共 28 天

# 打印月历
print(calendar.month(2026, 8))

# 打印年历
# print(calendar.calendar(2026))
```

---

## 8. 常见实战案例

### 8.1 计算两个日期间隔天数

```python
from datetime import date

d1 = date(2026, 1, 1)
d2 = date(2026, 12, 31)
print(f'相差 {(d2 - d1).days} 天')   # 相差 364 天
```

### 8.2 获取本月第一天与最后一天

```python
import calendar
from datetime import date

today = date.today()
first_day = date(today.year, today.month, 1)
# monthrange 返回 (该月 1 号是星期几, 该月天数)
last_day = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])

print(first_day, last_day)
```

### 8.3 计算距离某日期还有多久

```python
from datetime import datetime

deadline = datetime(2026, 12, 31, 23, 59, 59)
now = datetime.now()
diff = deadline - now

print(f'还剩 {diff.days} 天 {diff.seconds // 3600} 小时')
```

### 8.4 时间戳与日期字符串互转

```python
from datetime import datetime

# 时间戳 -> 日期字符串
ts = 1722856800
print(datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))

# 日期字符串 -> 时间戳
s = '2026-08-05 14:30:00'
dt = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
print(int(dt.timestamp()))
```

### 8.5 计时装饰器

```python
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f'{func.__name__} 耗时 {elapsed:.6f} 秒')
        return result
    return wrapper

@timer
def slow_task():
    time.sleep(1)
    return 'done'

slow_task()   # slow_task 耗时 1.001234 秒
```

### 8.6 生成最近 N 天的日期列表

```python
from datetime import date, timedelta

def last_n_days(n, end=None):
    end = end or date.today()
    return [end - timedelta(days=i) for i in range(n - 1, -1, -1)]

for d in last_n_days(7):
    print(d)
```

---

## 9. 小结

### 9.1 核心要点

- 三种时间表示：**时间戳**（浮点秒）、**struct_time**（结构化）、**格式化字符串**
- `time` 模块偏底层：时间戳、休眠、计时；`datetime` 模块偏业务：日期计算与格式化
- `datetime` 四个核心类：`date`、`time`、`datetime`、`timedelta`
- `timedelta` 用于日期加减运算，`total_seconds()` 取总秒数
- `strftime` 格式化、`strptime` 解析；数据交换优先用 ISO 8601
- 区分 **naive**（无时区）与 **aware**（带时区）时间，内部存 UTC、展示时转换
- Python 3.9+ 用内置 `zoneinfo` 处理时区，无需第三方库
- 计时优先用 `time.perf_counter()`，`datetime.utcnow()` 已弃用

### 9.2 模块选择速查

| 需求 | 推荐方案 |
|------|----------|
| 程序休眠 | `time.sleep()` |
| 计时测性能 | `time.perf_counter()` |
| 当前日期时间 | `datetime.now()` |
| 日期加减 | `datetime` + `timedelta` |
| 格式化/解析 | `strftime` / `strptime` / `isoformat` |
| 时区转换 | `zoneinfo` + `astimezone()` |
| 时间戳转换 | `timestamp()` / `fromtimestamp()` |
| 闰年/月历 | `calendar` 模块 |

### 9.3 常见陷阱

1. **`datetime.utcnow()` 已弃用**：返回 naive 时间，易混淆；改用 `datetime.now(timezone.utc)`。
2. **aware 与 naive 混算报错**：运算前确保双方时区状态一致。
3. **月份/星期从 0 还是从 1 开始**：`date.month` 是 1-12，`weekday()` 是 0-6（周一为 0），注意区分。
4. **`timedelta.seconds` 不含整天**：它只返回去掉整天后的剩余秒数，要总时长用 `total_seconds()`。
5. **Windows 缺时区数据**：`ZoneInfo` 可能找不到数据，安装 `tzdata` 包即可。
