import datetime
import json
import random
import time
from copy import deepcopy
from os.path import dirname, join, exists

import requests

import hoshino
import re
from hoshino import Service
from hoshino.typing import CQEvent

sv_help = """
[假期推送 + 日期] 查看当前日期还有多久放假
 - 年月日之间必须有符号分隔，可以是空格
[剩余假期] 查看还有多久假期
""".strip()

sv = Service(
    name='假期推送',
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    bundle='娱乐',  # 分组归类
    help_=sv_help  # 帮助说明
)


@sv.on_fullmatch("帮助假期推送")
async def bangzhu(bot, ev: CQEvent):
    await bot.send(ev, sv_help)

_today = time.time()

curpath = dirname(__file__)
_data = join(curpath, 'data.json')
_config = join(curpath, 'config.json')
if exists(_data):
    with open(_data, 'r', encoding='UTF-8') as fp:
        root = json.load(fp)
if exists(_config):
    with open(_config, 'r', encoding='UTF-8') as fp:
        text = json.load(fp)

texts = []
for each in text:
    texts.append(each)

_holiday = root['holiday']
holiday_cache = deepcopy(_holiday)

holiday_name1 = ['元旦', '除夕', '清明节', '劳动节', '端午节', '中秋节', '国庆节']
holiday_name2 = ['元旦', '除夕', '清明', '五一', '端午', '中秋', '国庆']


def get_message(group=None):
    holiday_check = [0, 0, 0, 0, 0, 0, 0]
    msg, msg_am, msg_pm = '', '', ''
    today = time.time()
    for data in holiday_cache:
        info = holiday_cache[data]
        timeArray = time.strptime(info['date'], "%Y-%m-%d")
        timeStamp = int(time.mktime(timeArray))
        for i in range(len(holiday_check)):
            if info['name'] == str(holiday_name1[i]) and holiday_check[i] == 0 \
                    and info['holiday'] and today < timeStamp:
                time_int = int((timeStamp - today) / 86400) + 1
                msg_am = msg_am + f'距离【{holiday_name2[i]}】还有：{time_int}天\n'
                msg_pm = msg_pm + f'距离【{holiday_name2[i]}】还有：{time_int - 1}天\n'
                holiday_check[i] = 1
    d1 = datetime.datetime.now()
    to_weekend = 6 - datetime.datetime.now().isoweekday()

    rand_text = None
    if group is not None:
        for each_text in text:
            if text[each_text]["group"] == group:
                rand_text = each_text

    if rand_text is None:
        rand_text = random.choice(texts)

    text1 = text[rand_text]['text1']
    text2 = text[rand_text]['text2']
    text3 = text[rand_text]['text3']
    msg_normal_am = f'【摸鱼办】提醒您：{d1.month}月{d1.day}日上午好，{text1}\n距离【周末】还有：{to_weekend}天\n{msg_am}{text2}\n\n{text3}'
    msg_normal_pm = f'【摸鱼办】提醒您：{d1.month}月{d1.day}日下午好，{text1}\n距离【周末】还有：{to_weekend - 1}天\n{msg_pm}{text2}\n\n{text3}'
    msg_change_am = f'【摸鱼办】提醒您：{d1.month}月{d1.day}日上午好，{text1}\n今天是节假日调休\n{msg_am}{text2}\n\n{text3}'
    msg_change_pm = f'【摸鱼办】提醒您：{d1.month}月{d1.day}日下午好，{text1}\n今天是节假日调休\n\n{msg_pm}{text2}\n\n{text3}'
    url = f'https://timor.tech/api/holiday/info'
    print(url)
    r = requests.get(url)
    holiday = r.json()
    today_type = holiday['type']['type']
    # print(today_type)
    if today_type == 0:  # 工作日
        if datetime.datetime.now().hour < 12:
            msg = msg_normal_am
        elif datetime.datetime.now().hour > 12:
            msg = msg_normal_pm
    elif today_type == 3:  # 调休
        if datetime.datetime.now().hour < 12:
            msg = msg_change_am
        elif datetime.datetime.now().hour > 12:
            msg = msg_change_pm
    return msg


@sv.scheduled_job('cron', hour='11')
async def auto_send_holiday_message():
    # 这边为定时发送消息
    # await bot.send(ev, "测试")
    groups = await sv.get_enable_groups()
    for each_group in groups:
        msg = get_message(each_group)
        await sv.bot.send_group_msg(group_id=each_group, message=msg)


@sv.scheduled_job('cron', hour='16')
async def auto_send_holiday_message():
    # 这边为定时发送消息
    # await bot.send(ev, "测试")
    groups = await sv.get_enable_groups()
    for each_group in groups:
        msg = get_message(each_group)
        await sv.bot.send_group_msg(group_id=each_group, message=msg)


# @sv.on_fullmatch("123")
# async def auto_send_holiday_message(bot, ev: CQEvent):
#    #这边类似广播操作，设置口令就能全群广播
#    await sv.broadcast("msg", 'auto_send_holiday_message', 0.2)


@sv.on_fullmatch("剩余假期")
async def year_holiday(bot, ev: CQEvent):
    false_holiday = 0
    holiday = 0
    msg = '今年剩余的假期有:\n'
    for data in holiday_cache:
        info = holiday_cache[data]
        timeArray = time.strptime(info['date'], "%Y-%m-%d")
        timeStamp = time.mktime(timeArray)
        if info['holiday'] and _today < timeStamp:
            day = datetime.datetime.strptime(info['date'], "%Y-%m-%d").weekday()
            if day == 5 or day == 6:
                false_holiday = false_holiday + 1
            time_int = int((timeStamp - _today) / 86400) + 1
            name = info['name']
            date = info['date']
            msg = msg + f'{date}{name},还有{time_int}天' + '\n'
            holiday = holiday + 1
        elif not info['holiday'] and _today < timeStamp:
            false_holiday = false_holiday + 1
    real_holiday = holiday - false_holiday
    msg = msg + f'共{holiday}天\n减去调休与周末后剩余假期为{real_holiday}天'
    await bot.send(ev, msg)


# 每天四点更新假期数据
@sv.scheduled_job('cron', hour='4')
async def today_holiday():
    url = 'https://timor.tech/api/holiday/year'
    r = requests.get(url)
    holiday = r.json()
    with open(_data, 'w', encoding='UTF-8') as f:
        json.dump(holiday, f)


# 以下为测试用方法

def get_message_test(test_day, group=None):
    holiday_check = [0, 0, 0, 0, 0, 0, 0]
    msg, msg_am, msg_pm = '', '', ''
    today = time.mktime(time.strptime(f"{test_day} 09:00:00", "%Y-%m-%d %H:%M:%S"))
    for data in holiday_cache:
        info = holiday_cache[data]
        timeArray = time.strptime(info['date'], "%Y-%m-%d")
        timeStamp = int(time.mktime(timeArray))
        for i in range(len(holiday_check)):
            if info['name'] == str(holiday_name1[i]) and holiday_check[i] == 0 \
                    and info['holiday'] and today < timeStamp:
                time_int = int((timeStamp - today) / 86400) + 1
                msg_am = msg_am + f'距离【{holiday_name2[i]}】还有：{time_int}天\n'
                msg_pm = msg_pm + f'距离【{holiday_name2[i]}】还有：{time_int - 1}天\n'
                holiday_check[i] = 1
    d1 = datetime.datetime.strptime(f"date:{test_day},time:09:00:00", 'date:%Y-%m-%d,time:%H:%M:%S')
    print(d1)
    to_weekend = 6 - d1.isoweekday()

    rand_text = None
    if group is not None:
        for each_text in text:
            if text[each_text]["group"] == group:
                rand_text = each_text

    if rand_text is None:
        rand_text = random.choice(texts)

    text1 = text[rand_text]['text1']
    text2 = text[rand_text]['text2']
    text3 = text[rand_text]['text3']
    msg_normal_am = f'【摸鱼办】提醒您：{d1.month}月{d1.day}日上午好，{text1}\n距离【周末】还有：{to_weekend}天\n{msg_am}{text2}\n\n{text3}'
    msg_normal_pm = f'【摸鱼办】提醒您：{d1.month}月{d1.day}日下午好，{text1}\n距离【周末】还有：{to_weekend - 1}天\n{msg_pm}{text2}\n\n{text3}'
    msg_change_am = f'【摸鱼办】提醒您：{d1.month}月{d1.day}日上午好，{text1}\n今天是节假日调休\n{msg_am}{text2}\n\n{text3}'
    msg_change_pm = f'【摸鱼办】提醒您：{d1.month}月{d1.day}日下午好，{text1}\n今天是节假日调休\n\n{msg_pm}{text2}\n\n{text3}'
    url = f'https://timor.tech/api/holiday/info/{test_day}'
    print(url)
    r = requests.get(url)
    holiday = r.json()
    today_type = holiday['type']['type']
    # print(today_type)
    if today_type == 0:  # 工作日
        if d1.hour < 12:
            msg = msg_normal_am
        elif d1.hour > 12:
            msg = msg_normal_pm
    elif today_type == 3:  # 调休
        if d1.hour < 12:
            msg = msg_change_am
        elif d1.hour > 12:
            msg = msg_change_pm
    return msg


@sv.on_prefix("假期推送")
async def test_holiday_msg(bot, ev: CQEvent):
    test_day = str(ev.message).strip()
    try:
        match = re.search(r"(\d+)[\s\S]+?(\d+)[\s\S]+?(\d+)", test_day)
        if match:
            test_day = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        else:
            await bot.finish(ev, "日期格式错误~请确保年月日之间有隔开~")
        msg = get_message_test(test_day, ev.group_id)
        if not msg:
            msg = "好耶，今天是休息日"
        await bot.send(ev, str(msg))
    except ValueError as e:
        hoshino.logger.warning(f"{e}")
        await bot.send(ev, '请在指令后跟随标准日期格式哦，如2022-06-01')
