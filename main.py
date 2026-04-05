from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import time

AGREEMENT_TEXT = """
星恒梦落用户使用协议

版本：v1.0
最后更新：2026年4月4日
联系方式：QQ群 752775661

一、协议范围
本协议适用于：QQ群聊、QQ私聊、任何通过本机器人进行的消息发送、工具调用等行为。

二、信息收集与使用规定
我们会收集以下信息：用户信息（用户UID，即QQ号）、聊天信息（与本机器人进行的全部对话内容）、协议信息（关于本协议的同意或拒绝状态）。
我们承诺：不会向第三方提供任何用户的个人信息，除非法律要求；不会收集与本服务无关的任何个人信息。

三、用户行为规范规定
用户不得进行以下行为：利用本机器人进行任何形式的违法活动；发布、宣传诈骗、赌博、色情、暴力、诽谤、侵权等信息；恶意破坏机器人正常运行，如刷屏、攻击本机器人等。

四、免责声明
本机器人不保证服务完全不中断、无错误或绝对安全。因用户自身行为、网络故障、第三方服务中断等不可抗力导致的服务异常，本机器人不承担责任。

五、协议修改
本协议有权根据法律法规变化或服务需要进行修改。修改后的协议将在首次私聊或群聊中通知用户。

六、未成年人保护
如你未满18周岁，请在法定监护人陪同下阅读本协议。

七、法律适用与争议解决
本协议的订立、执行和解释及争议的解决均适用中华人民共和国法律。

八、协议确认方式
回复「同意」视为用户已阅读、理解并同意本协议的全部内容。回复「不同意」将无法使用本机器人的全部功能。
"""

@register("astrbot_plugin_agreement", "星恒梦落", "用户协议签订插件", "1.0.0")
class AgreementPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        logger.info("协议签订插件已加载")

    @filter.regex(r".*")
    async def handle_all_messages(self, event: AstrMessageEvent):
        """处理所有消息，实现协议签订"""
        # 只处理私聊消息
        if event.get_message_type() != "private":
            return
        
        uid = event.get_sender_id()
        status = await self.context.get("agreed_" + uid)
        
        # 情况1：用户从未签订协议
        if status is None:
            yield event.plain_result(AGREEMENT_TEXT)
            await self.context.set("agreed_" + uid, "waiting")
            await self.context.set("last_agreement_sent_" + uid, time.time())
            event.stop_event()
            return
        
        # 情况2：用户已收到协议，等待确认
        if status == "waiting":
            msg = event.message_str
            
            if "同意" in msg:
                await self.context.set("agreed_" + uid, "yes")
                yield event.plain_result("已记录你的同意。现在可以正常使用本机器人。")
                event.stop_event()
                return
            
            if "不同意" in msg:
                await self.context.set("agreed_" + uid, "no")
                yield event.plain_result("已记录你的拒绝。本机器人将无法为你服务。")
                event.stop_event()
                return
            
            # 冷却机制：30秒内不重复发送完整协议
            last_sent = await self.context.get("last_agreement_sent_" + uid)
            now = time.time()
            
            if last_sent and (now - last_sent) < 30:
                yield event.plain_result("请回复「同意」或「不同意」接受协议。")
                event.stop_event()
                return
            
            await self.context.set("last_agreement_sent_" + uid, now)
            yield event.plain_result(AGREEMENT_TEXT)
            event.stop_event()
            return
        
        # 情况3：用户已拒绝协议，不回复任何消息
        if status == "no":
            event.stop_event()
            return
        
        # 情况4：用户已同意协议，正常放行
        return

    async def terminate(self):
        logger.info("协议签订插件已终止")
