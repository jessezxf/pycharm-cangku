"""
讯飞星火翻译程序
使用讯飞星火大模型的API进行翻译
需要先注册讯飞开放平台并获取API Password
"""

import requests
import json
from datetime import datetime


class XunFeiTranslator:
    """讯飞星火翻译器封装类"""

    def __init__(self, api_password):
        """
        初始化翻译器

        参数:
            api_password: 讯飞星火的API Password（Bearer Token）
        """
        self.api_password = api_password
        self.api_url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
        self.model = "4.0Ultra"  # 使用最新模型，免费额度内可用

        # 支持的语言
        self.languages = {
            'zh': '中文',
            'en': '英语',
            'ja': '日语',
            'ko': '韩语',
            'fr': '法语',
            'de': '德语',
            'es': '西班牙语',
            'ru': '俄语',
            'it': '意大利语',
            'pt': '葡萄牙语',
            'ar': '阿拉伯语'
        }

        # 对话历史（用于多轮对话模式）
        self.conversation_history = []

    def translate(self, text, target_lang='zh', source_lang=None):
        """
        翻译单段文本

        参数:
            text: 要翻译的文本
            target_lang: 目标语言代码，默认'zh'（中文）
            source_lang: 源语言代码，默认None（自动检测）

        返回:
            翻译结果文本，失败返回None
        """
        # 获取语言名称
        target_name = self.languages.get(target_lang, target_lang)

        # 构造翻译提示词
        if source_lang and source_lang != 'auto':
            source_name = self.languages.get(source_lang, source_lang)
            prompt = f"""请将以下{source_name}文本翻译成{target_name}。
要求：
1. 只输出翻译结果，不要添加任何解释、注释或额外内容
2. 保持原文的语气和风格
3. 如果原文有专业术语，请使用标准译法

原文：{text}"""
        else:
            prompt = f"""请将以下文本翻译成{target_name}。
要求：
1. 只输出翻译结果，不要添加任何解释、注释或额外内容
2. 如果原文不是{target_name}，请翻译；如果原文已经是{target_name}，请原文输出
3. 保持原文的语气和风格

原文：{text}"""

        # 调用API
        return self._call_api(prompt)

    def translate_with_context(self, text, target_lang='zh', context=""):
        """
        带上下文的翻译（用于处理需要语境理解的翻译）

        参数:
            text: 要翻译的文本
            target_lang: 目标语言代码
            context: 上下文信息，帮助更准确翻译

        返回:
            翻译结果
        """
        target_name = self.languages.get(target_lang, target_lang)

        prompt = f"""请结合以下上下文，将文本翻译成{target_name}。

上下文：{context}

待翻译文本：{text}

要求：只输出翻译结果，不要添加解释。"""

        return self._call_api(prompt)

    def translate_batch(self, texts, target_lang='zh'):
        """
        批量翻译

        参数:
            texts: 文本列表
            target_lang: 目标语言代码

        返回:
            翻译结果列表
        """
        results = []
        total = len(texts)

        print(f"\n📦 开始批量翻译 {total} 条文本...")

        for i, text in enumerate(texts, 1):
            print(f"  [{i}/{total}] 翻译中: {text[:30]}..." if len(text) > 30 else f"  [{i}/{total}] 翻译中: {text}")
            result = self.translate(text, target_lang)
            results.append(result if result else "[翻译失败]")

        print("✅ 批量翻译完成")
        return results

    def chat_translate(self):
        """
        交互式翻译模式（支持多轮对话）
        """
        print("\n" + "=" * 50)
        print("🤖 进入交互翻译模式")
        print("=" * 50)
        print("使用说明:")
        print("  直接输入文本 → 自动翻译成中文")
        print("  格式: [语言代码] 文本 → 翻译成指定语言")
        print("  例如: [en] 你好 → 将'你好'翻译成英文")
        print("  输入 'quit' 退出翻译模式")
        print("  输入 '/clear' 清空对话历史")
        print("=" * 50)

        while True:
            user_input = input("\n📝 请输入文本: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 退出翻译模式")
                break

            if user_input.lower() == '/clear':
                self.conversation_history = []
                print("🗑️ 对话历史已清空")
                continue

            if not user_input:
                continue

            # 解析输入格式
            target_lang = 'zh'
            text = user_input

            if user_input.startswith('[') and ']' in user_input:
                end_idx = user_input.find(']')
                lang_code = user_input[1:end_idx].lower()
                if lang_code in self.languages:
                    target_lang = lang_code
                    text = user_input[end_idx+1:].strip()
                else:
                    print(f"❌ 不支持的语言: {lang_code}")
                    print(f"   支持: {', '.join(self.languages.keys())}")
                    continue

            # 执行翻译
            print(f"🔄 正在翻译: {text[:50]}..." if len(text) > 50 else f"🔄 正在翻译: {text}")
            result = self.translate(text, target_lang)

            if result:
                print(f"✅ 翻译结果: {result}")
                # 保存到对话历史
                self.conversation_history.append({
                    "input": text,
                    "output": result,
                    "target": target_lang,
                    "time": datetime.now().strftime("%H:%M:%S")
                })
            else:
                print("❌ 翻译失败，请检查网络或API配置")

    def _call_api(self, prompt):
        """
        调用讯飞星火API（内部方法）

        参数:
            prompt: 完整的提示词

        返回:
            API返回的文本
        """
        headers = {
            "Authorization": f"Bearer {self.api_password}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的翻译助手，严格按照用户要求输出翻译结果，不添加任何额外解释。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # 降低随机性，使翻译更稳定
            "max_tokens": 2000
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                self._handle_error(response)
                return None

        except requests.exceptions.Timeout:
            print("❌ 请求超时，请检查网络连接")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ 网络连接失败，请检查网络")
            return None
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            return None

    def _handle_error(self, response):
        """处理API错误"""
        status_code = response.status_code

        if status_code == 401:
            print("❌ 认证失败：请检查API Password是否正确")
        elif status_code == 429:
            print("❌ 请求频率过高：免费版有QPS限制，请稍后重试")
        elif status_code == 500:
            print("❌ 服务器错误：讯飞服务暂时不可用，请稍后重试")
        else:
            print(f"❌ HTTP错误 {status_code}: {response.text[:200]}")

    def show_languages(self):
        """显示支持的语言"""
        print("\n🌐 支持的语言:")
        print("-" * 30)
        for code, name in self.languages.items():
            print(f"  {code}: {name}")
        print("-" * 30)

    def test_connection(self):
        """测试API连接是否正常"""
        print("🔍 正在测试API连接...")
        result = self.translate("Hello", "zh")

        if result:
            print(f"✅ API连接正常！测试结果: 'Hello' → '{result}'")
            return True
        else:
            print("❌ API连接失败，请检查API Password")
            return False


# ========== 全局变量：API Password（请在这里配置） ==========
API_PASSWORD = "juIOWjehPFefnDyiSgGz:zwjRBFdPXFSfSklRKcvG"  # 👈 请在这里填写你的API Password


def main():
    """主程序入口（交互模式）"""
    print("=" * 50)
    print("🤖 讯飞星火翻译程序 v1.0")
    print("=" * 50)

    # 检查是否已填写密钥
    if API_PASSWORD == "你的API_Password" or not API_PASSWORD:
        print("\n⚠️  请先填写你的 API Password！")
        print("   获取方式：讯飞开放平台控制台 → 我的应用 → API Password")
        print("   ⚠️ 注意：不是 APIKey 或 APISecret，是 API Password！\n")
        return

    # 创建翻译器实例
    translator = XunFeiTranslator(API_PASSWORD)

    # 显示支持的语言
    translator.show_languages()

    # 测试连接
    print("\n" + "=" * 50)
    translator.test_connection()

    # 启动交互翻译
    translator.chat_translate()


# ========== 命令行直接翻译 ==========
if __name__ == "__main__":
    import sys

    # 检查API Password是否配置
    if API_PASSWORD == "你的API_Password" or not API_PASSWORD:
        print("❌ 请先在代码顶部配置 API Password")
        print("   找到代码中的 API_PASSWORD = '...' 这一行，填入你的API Password")
        sys.exit(1)

    # 如果没有命令行参数，进入交互模式
    if len(sys.argv) == 1:
        main()
    else:
        # 解析命令行参数
        args = sys.argv[1:]
        translator = XunFeiTranslator(API_PASSWORD)

        # 处理 -t 参数（指定目标语言）
        target_lang = 'zh'
        text_start = 1

        if args[0] == '-t' and len(args) >= 2:
            target_lang = args[1]
            text_start = 2

        if text_start < len(args):
            text = " ".join(args[text_start:])
            print(f"🔄 翻译: {text}")
            print(f"🎯 目标语言: {target_lang}")
            result = translator.translate(text, target_lang)
            if result:
                print(f"\n✅ 翻译结果: {result}")
            else:
                print("❌ 翻译失败")
        else:
            print("用法:")
            print("  交互模式: python xunfei_translator-指定目标语言类型.py")
            print("  命令行翻译: python xunfei_translator-指定目标语言类型.py '要翻译的文本'")
            print("  指定语言: python xunfei_translator-指定目标语言类型.py -t en '要翻译成英文的文本'")
            print("\n支持的语言代码: zh, en, ja, ko, fr, de, es, ru, it, pt, ar")