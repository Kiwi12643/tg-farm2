# -*- coding: utf-8 -*-
import re
import requests


class QwenAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = (
            "https://dashscope-intl.aliyuncs.com/api/v1/services/"
            "aigc/multimodal-generation/generation"
        )

    def solve_captcha(self, image_base64: str, question: str):
        if not self.api_key:
            return []

        prompt = (
            "Вот картинка-сетка 3×3. Номера секций:\n"
            "1 2 3 (верхний ряд)\n"
            "4 5 6 (средний ряд)\n"
            "7 8 9 (нижний ряд)\n\n"
            f'Вопрос: "{question}"\n\n'
            "Верни ТОЛЬКО номера через запятую. Без пояснений."
        )

        payload = {
            "model": "qwen-vl-plus",
            "input": {
                "messages": [{
                    "role": "user",
                    "content": [
                        {"image": f"data:image/png;base64,{image_base64}"},
                        {"text": prompt}
                    ]
                }]
            },
            "parameters": {"max_tokens": 50, "temperature": 0.1}
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            resp = requests.post(self.url, json=payload, headers=headers, timeout=15)
            data = resp.json()
            answer = data["output"]["choices"][0]["message"]["content"]
            return list(set(int(n) for n in re.findall(r'[1-9]', answer)))
        except Exception as e:
            print(f"Qwen error: {e}")
            return []

    def solve_captcha_text(self, captcha_text: str) -> str:
        """Для текстовых капч"""
        if not self.api_key:
            return ""

        url = (
            "https://dashscope-intl.aliyuncs.com/api/v1/services/"
            "aigc/text-generation/generation"
        )
        payload = {
            "model": "qwen-plus",
            "input": {
                "messages": [{
                    "role": "user",
                    "content": (
                        f"Реши эту капчу. Верни ТОЛЬКО ответ без пояснений:\n"
                        f"{captcha_text}"
                    )
                }]
            },
            "parameters": {"max_tokens": 20, "temperature": 0.1}
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            data = resp.json()
            return data["output"]["choices"][0]["message"]["content"].strip()
        except:
            return ""
