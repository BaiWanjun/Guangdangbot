from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import random
from datetime import datetime, timedelta
import json
import os

events_list = [
    ["睡觉", "养足精力，明日再战", "翻来覆去睡不着"],
    ["体育锻炼", "身体棒棒哒", "消耗的能量全吃回来了"],
    ["玩网游", "犹如神助", "匹配到一群猪队友"],
    ["写作业", "都会写，写的全对", "上课讲了这些了吗"],
    ["装逼", "获得众人敬仰", "被识破"],
    ["装弱", "谦虚最好了", "被看穿"],
    ["熬夜", "事情终究是可以完成的", "爆肝"],
    ["出行", "一路顺风", "路途必然坎坷"],
    ["扶老奶奶过马路", "功德++", "会被讹"],
    ["搞基", "友谊地久天长", "会被掰弯"],
    ["泡妹子", "说不定可以牵手", "一定会被拒绝"],
    ["上B站", "愉悦身心", "会被老师发现"],
    ["洗澡", "你多久没洗澡了？", "当心着凉"],
    ["写作文", "非常有文采", "不知所云，离题千里"],
    ["学数论", "数论大法好", "咋看都不会"],
    ["唱歌", "成为歌神", "别人唱歌要钱，你要命"],
    ["抽卡", "一发入魂", "只有保底"],

    ["点外卖", "及时送到", "一直没有送到还不给退款"],
    ["放假", "自由自在的一个假期", "就放一天，全是作业"],
    ["交友", "友谊地久天长", "交友不慎"],
    ["看视频网站", "愉悦身心", "会被老师看见"],
    ["吃罐罐", "今天能吃到超级香的罐罐", "罐罐里面有苦瓜"],
    ["吃罐罐", "今天能吃到超级香的罐罐", "罐罐里面有苦瓜"],
    ["吃罐罐", "今天能吃到超级香的罐罐", "罐罐里面有苦瓜"],
    ["吃罐罐", "今天能吃到超级香的罐罐", "罐罐里面有苦瓜"],
    ["吃罐罐", "今天能吃到超级香的罐罐", "罐罐里面有苦瓜"],
    ["晒太阳", "暖呼呼的很舒服", "晒太久变成小黑猫"],
    ["钻纸箱", "发现了完美猫窝", "纸箱突然塌了"],
    ["玩逗猫棒", "反应快如闪电", "扑空摔了一跤"],
    ["踩奶", "心情超级放松", "把主人衣服抓坏了"],
    ["舔毛", "毛发变得非常顺滑", "舔了一嘴猫毛"],
    ["半夜跑酷", "成功吵醒所有人", "撞翻水杯被制裁"],
    ["追尾巴", "玩得开心极了", "撞到墙角哭唧唧"],
    ["抓小球", "抓到小球超有成就感", "球滚到沙发底下找不到"],
    ["偷吃零食", "偷偷吃到美味小零食", "零食只有苦瓜"],
    ["蹭主人腿", "主人摸摸你，好幸福", "主人踩到你小爪子生气了"],
    ["躺床上", "睡得香甜，做个美梦", "主人需要你起床但赖床了"],
    ["跳高", "跳得很高，身体棒棒哒", "跳空落地，差点摔疼"],
    ["抓沙发", "磨爪子磨得很舒爽", "抓坏沙发被训斥"],
    ["追光点", "抓到了光点，超开心", "光点消失了，你扑空了"],
    ["喝水", "喝到新鲜水水，身体棒棒的", "苦瓜味水"],
    ["翻垃圾桶", "找到了好吃的惊喜", "是发霉苦瓜"],
    ["打呼噜", "打呼噜声音好听，大家安心", "打太响吵到别人"],
    ["偷懒", "懒洋洋一天，完全放松", "被麻麻捏屁股"],
    ["猫咪社交", "认识新朋友，开心喵～", "被猫揍"],
]

meow_list = [
    "唔咩",
    "咩啊",
    "咕咕",
    "呱",
    "嗯麻",
    "嗯咩啊",
    "嗯咕咕",
    "唔咩啊",
    "唔麻"
]

special_events = {
    (8, 19): ["咣当生日", "今天是咣当的生日！一起庆祝吧喵~"],
}

fortune_levels = [
    ("大凶", 1),
    ("凶", 3),
    ("中平", 3),
    ("吉", 2),
    ("小吉", 2),
    ("中吉", 2),
    ("大吉", 1)
]
special_fortune_levels = [
    ("凶", 3),
    ("中平", 3),
    ("吉", 2),
    ("小吉", 2),
    ("中吉", 2),
    ("大吉", 1)
]

DATA_FILE = "fortune_data.json"

@register("astrbot_plugin_dailyacmfortune", "Dayanshifu", "洛谷运势生成和签到打卡", "1.0.2", "https://github.com/Dayanshifu/astrbot_plugin_dailyacmfortune")
class FortunePlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.fortune_data = {}
        self.load_data()

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
    
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.fortune_data = json.load(f)
            except Exception as e:
                logger.error(f"加载运势数据失败: {e}")
                self.fortune_data = {}
        # 初始化每日打卡统计字段
        if "daily_checkin" not in self.fortune_data:
            self.fortune_data["daily_checkin"] = {}

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.fortune_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存运势数据失败: {e}")

    def get_continuous_days(self, user_id: str, today: datetime) -> int:
        if user_id not in self.fortune_data:
            return 0
            
        user_record = self.fortune_data[user_id]
        if "checkin_history" not in user_record:
            return 0
            
        checkin_dates = user_record["checkin_history"]
        if not checkin_dates:
            return 0
            
        # 按日期排序
        sorted_dates = sorted(checkin_dates, reverse=True)
        
        # 检查连续打卡
        continuous_days = 0
        current_date = today.date()
        
        for i, date_str in enumerate(sorted_dates):
            checkin_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            expected_date = current_date - timedelta(days=i)
            
            if checkin_date == expected_date:
                continuous_days += 1
            else:
                break
                
        return continuous_days

    def update_checkin_history(self, user_id: str, today: datetime):
        today_str = today.strftime("%Y-%m-%d")
        
        if user_id not in self.fortune_data:
            self.fortune_data[user_id] = {"checkin_history": []}
        elif "checkin_history" not in self.fortune_data[user_id]:
            self.fortune_data[user_id]["checkin_history"] = []
            
        if today_str not in self.fortune_data[user_id]["checkin_history"]:
            self.fortune_data[user_id]["checkin_history"].append(today_str)

    def get_today_checkin_order(self, user_id: str, today: datetime) -> int:
        """获取用户今日打卡的序号"""
        today_str = today.strftime("%Y-%m-%d")
        daily_checkin = self.fortune_data["daily_checkin"]
        
        # 初始化当日打卡列表
        if today_str not in daily_checkin:
            daily_checkin[today_str] = []
        
        # 如果用户未在当日列表中，添加进去
        if user_id not in daily_checkin[today_str]:
            daily_checkin[today_str].append(user_id)
        
        # 返回用户的打卡序号（索引+1）
        return daily_checkin[today_str].index(user_id) + 1

    def get_user_fortune(self, user_id: str, user_name: str, today: datetime) -> dict:
        today_str = today.strftime("%Y-%m-%d")
        
        self.update_checkin_history(user_id, today)
        # 获取今日打卡序号
        checkin_order = self.get_today_checkin_order(user_id, today)
        
        continuous_days = self.get_continuous_days(user_id, today)
        
        if user_id in self.fortune_data:
            user_record = self.fortune_data[user_id]
            if user_record.get("date") == today_str:
                user_record["continuous_days"] = continuous_days
                user_record["checkin_order"] = checkin_order  # 更新序号（防止重复打卡时序号变化）
                return user_record
                
        fortune_level, special_event = self.generate_fortune(today)
        random_events = random.sample(events_list, 4)
        quote = f"§ {fortune_level} §\n\n"
        
        if fortune_level == "大吉":
            if special_event:
                quote += (f"宜:{special_event[0]}\n")
                quote += (f"{special_event[1]}\n")
                quote += (f"宜:{random_events[0][0]}\n")
                quote += (f"{random_events[0][1]}")
            else:
                quote += (f"宜:{random_events[0][0]}\n")
                quote += (f"{random_events[0][1]}\n")
                quote += (f"宜:{random_events[1][0]}\n")
                quote += (f"{random_events[1][1]}")
            quote += ("\n\n万事皆宜")
        elif fortune_level == "大凶":
            quote += ("诸事不宜\n\n")
            quote += (f"忌:{random_events[2][0]}\n")
            quote += (f"{random_events[2][2]}\n")
            quote += (f"忌:{random_events[3][0]}\n")
            quote += (f"{random_events[3][2]}")
        else:
            if special_event:
                quote += (f"宜:{special_event[0]}\n")
                quote += (f"{special_event[1]}\n")
                quote += (f"宜:{random_events[0][0]}\n")
                quote += (f"{random_events[0][1]}\n")
            else:
                quote += (f"宜:{random_events[0][0]}\n")
                quote += (f"{random_events[0][1]}\n")
                quote += (f"宜:{random_events[1][0]}\n")
                quote += (f"{random_events[1][1]}\n")
            quote += ("\n")
            quote += (f"忌:{random_events[2][0]}\n")
            quote += (f"{random_events[2][2]}\n")
            quote += (f"忌:{random_events[3][0]}\n")
            quote += (f"{random_events[3][2]}")
            
        new_fortune = {
            "date": today_str,
            "fortune_level": fortune_level,
            "quote": quote,
            "special_event": special_event[0] if special_event else None,
            "random_events": random_events,
            "user_name": user_name,
            "continuous_days": continuous_days,
            "checkin_order": checkin_order  # 存储打卡序号
        }
        
        self.fortune_data[user_id].update(new_fortune)
        self.save_data()
        
        return new_fortune

    def generate_fortune(self, today: datetime):
        month = today.month
        day = today.day
        special_event = special_events.get((month, day))
        
        if special_event:
            levels, weights = zip(*special_fortune_levels)
            selected_level = random.choices(levels, weights=weights, k=1)[0]
            return selected_level, special_event
        else:
            levels, weights = zip(*fortune_levels)
            selected_level = random.choices(levels, weights=weights, k=1)[0]
            return selected_level, None

    @filter.command("运势", alias={"今日人品", "运势", "今日运势", "运气", "签到", "打卡"})
    async def helloworld(self, event: AstrMessageEvent):
        today = datetime.now()
        user_id = str(event.get_sender_id())
        user_name = event.get_sender_name()
        user_fortune = self.get_user_fortune(user_id, user_name, today)
        
        continuous_days = user_fortune.get("continuous_days", 0)
        checkin_order = user_fortune.get("checkin_order", 0)  # 获取打卡序号
        
        # 构造头部信息
        header = f"{user_name}的运势"
        checkin_info = f"你今天第{checkin_order}个打卡\n"
        if continuous_days > 0:
            header = f"{checkin_info}你已经连续打卡了{continuous_days}天\n{header}"
        else:
            header = f"{checkin_info}{header}"
            
        yield event.plain_result(f"{header}\n{user_fortune['quote']}")

    @filter.command("咩咩叫")
    async def meow(self, event: AstrMessageEvent):
        result = random.choice(meow_list)  # meow_list 在类外定义
        yield event.plain_result(result)
    async def terminate(self):

        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        self.save_data()
