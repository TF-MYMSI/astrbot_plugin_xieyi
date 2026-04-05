from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("test_keyword", "测试", "关键词测试插件", "1.0.0")
class TestKeywordPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        logger.info("测试关键词插件已加载")

    @filter.regex(r"干什么")
    async def on_what_to_do(self, event: AstrMessageEvent):
        logger.info(f"关键词测试插件被触发！消息: {event.message_str}")
        yield event.plain_result("是啊，干什么")
        event.stop_event()

    async def terminate(self):
        logger.info("测试关键词插件已终止")
