"""
Multi-Provider API Client
支持多个AI服务提供商的统一接口
"""

import os
import requests
import base64
import json
from pathlib import Path
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config import PROVIDERS, DEFAULT_TEXT_PROVIDER, DEFAULT_IMAGE_PROVIDER


class BaseProvider(ABC):
    """提供商基类"""

    def __init__(self, config: Dict):
        self.config = config
        self.name = config.get("name", "Unknown")
        self.base_url = config.get("base_url", "")

        # API Key: 优先使用环境变量
        env_key = config.get("api_key_env")
        if env_key and os.environ.get(env_key):
            self.api_key = os.environ.get(env_key)
        else:
            self.api_key = config.get("api_key", "")

    @abstractmethod
    def generate_text(self, prompt: str, model: str = None) -> str:
        """生成文本"""
        pass

    @abstractmethod
    def generate_image(self, prompt: str, output_path: str = None, model: str = None) -> Dict:
        """生成图像"""
        pass

    def is_available(self) -> bool:
        """检查是否可用"""
        return bool(self.api_key) and self.config.get("enabled", False)


class GoogleProvider(BaseProvider):
    """Google AI Studio 提供商"""

    def generate_text(self, prompt: str, model: str = None) -> str:
        model = model or self.config.get("text_model", "gemini-2.0-flash-exp")
        url = f"{self.base_url}/models/{model}:generateContent"

        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key
        }

        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        response = requests.post(url, headers=headers, json=payload, timeout=120)

        if response.status_code != 200:
            raise Exception(f"Google API Error: {response.status_code} - {response.text[:200]}")

        data = response.json()

        if "candidates" in data and len(data["candidates"]) > 0:
            parts = data["candidates"][0]["content"]["parts"]
            for part in parts:
                if "text" in part:
                    return part["text"]

        return ""

    def generate_image(self, prompt: str, output_path: str = None, model: str = None,
                        aspect_ratio: str = "16:9") -> Dict:
        """
        生成图像

        Args:
            prompt: 图像生成提示词
            output_path: 输出路径
            model: 模型名称
            aspect_ratio: 宽高比，支持 "1:1", "16:9", "9:16", "4:3", "3:4"
        """
        model = model or self.config.get("image_model", "nano-banana-pro-preview")
        url = f"{self.base_url}/models/{model}:generateContent"

        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key
        }

        # 添加4K分辨率和宽高比指令到prompt
        enhanced_prompt = f"{prompt}\n\nIMPORTANT: Generate in 4K ultra-high resolution (3840x2160 or higher). Ensure all Chinese text is crystal clear, sharp, and correctly rendered."

        payload = {
            "contents": [{"parts": [{"text": enhanced_prompt}]}],
            "generationConfig": {
                "responseModalities": ["image", "text"]
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=180)

        if response.status_code != 200:
            raise Exception(f"Google API Error: {response.status_code} - {response.text[:200]}")

        data = response.json()

        if "candidates" in data and len(data["candidates"]) > 0:
            parts = data["candidates"][0]["content"]["parts"]

            for part in parts:
                if "inlineData" in part:
                    image_data = part["inlineData"]["data"]
                    mime_type = part["inlineData"]["mimeType"]

                    if output_path:
                        ext = "png" if "png" in mime_type else "jpg"
                        if not output_path.endswith(f".{ext}"):
                            output_path = f"{output_path}.{ext}"

                        with open(output_path, "wb") as f:
                            f.write(base64.b64decode(image_data))

                    return {
                        "success": True,
                        "image_data": image_data,
                        "mime_type": mime_type,
                        "output_path": output_path
                    }

        return {"success": False, "error": "No image in response"}

    def generate_with_images(self, prompt: str, images: list, model: str = None) -> str:
        """多模态生成：文本+图像输入"""
        model = model or self.config.get("text_model", "gemini-2.0-flash-exp")
        url = f"{self.base_url}/models/{model}:generateContent"

        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key
        }

        # 构建多模态内容
        parts = [{"text": prompt}]
        for img in images:
            parts.append({
                "inline_data": {
                    "mime_type": img.get("mime_type", "image/jpeg"),
                    "data": img.get("data")
                }
            })

        payload = {
            "contents": [{"parts": parts}]
        }

        response = requests.post(url, headers=headers, json=payload, timeout=180)

        if response.status_code != 200:
            raise Exception(f"Google API Error: {response.status_code} - {response.text[:500]}")

        data = response.json()

        if "candidates" in data and len(data["candidates"]) > 0:
            parts = data["candidates"][0]["content"]["parts"]
            for part in parts:
                if "text" in part:
                    return part["text"]

        return ""


class OpenAIProvider(BaseProvider):
    """OpenAI 提供商"""

    def generate_text(self, prompt: str, model: str = None) -> str:
        model = model or self.config.get("text_model", "gpt-4o")
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post(url, headers=headers, json=payload, timeout=120)

        if response.status_code != 200:
            raise Exception(f"OpenAI API Error: {response.status_code} - {response.text[:200]}")

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def generate_image(self, prompt: str, output_path: str = None, model: str = None) -> Dict:
        model = model or self.config.get("image_model", "dall-e-3")
        url = f"{self.base_url}/images/generations"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": model,
            "prompt": prompt,
            "n": 1,
            "size": "1792x1024",
            "response_format": "b64_json"
        }

        response = requests.post(url, headers=headers, json=payload, timeout=180)

        if response.status_code != 200:
            raise Exception(f"OpenAI API Error: {response.status_code} - {response.text[:200]}")

        data = response.json()
        image_data = data["data"][0]["b64_json"]

        if output_path:
            if not output_path.endswith(".png"):
                output_path = f"{output_path}.png"

            with open(output_path, "wb") as f:
                f.write(base64.b64decode(image_data))

        return {
            "success": True,
            "image_data": image_data,
            "mime_type": "image/png",
            "output_path": output_path
        }


class AnthropicProvider(BaseProvider):
    """Anthropic Claude 提供商（仅文本）"""

    def generate_text(self, prompt: str, model: str = None) -> str:
        model = model or self.config.get("text_model", "claude-sonnet-4-20250514")
        url = f"{self.base_url}/messages"

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": model,
            "max_tokens": 8192,
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post(url, headers=headers, json=payload, timeout=120)

        if response.status_code != 200:
            raise Exception(f"Anthropic API Error: {response.status_code} - {response.text[:200]}")

        data = response.json()
        return data["content"][0]["text"]

    def generate_image(self, prompt: str, output_path: str = None, model: str = None) -> Dict:
        # Claude不支持图像生成
        return {"success": False, "error": "Anthropic Claude does not support image generation"}


class OllamaProvider(BaseProvider):
    """Ollama 本地模型提供商"""

    def generate_text(self, prompt: str, model: str = None) -> str:
        model = model or self.config.get("text_model", "llama3")
        url = f"{self.base_url}/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(url, json=payload, timeout=300)

        if response.status_code != 200:
            raise Exception(f"Ollama API Error: {response.status_code} - {response.text[:200]}")

        data = response.json()
        return data.get("response", "")

    def generate_image(self, prompt: str, output_path: str = None, model: str = None) -> Dict:
        return {"success": False, "error": "Ollama does not support image generation"}


class StabilityProvider(BaseProvider):
    """Stability AI 提供商（仅图像）"""

    def generate_text(self, prompt: str, model: str = None) -> str:
        return ""  # Stability AI 不支持文本生成

    def generate_image(self, prompt: str, output_path: str = None, model: str = None) -> Dict:
        model = model or self.config.get("image_model", "stable-diffusion-xl-1024-v1-0")
        url = f"{self.base_url}/generation/{model}/text-to-image"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

        payload = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "steps": 30,
            "samples": 1
        }

        response = requests.post(url, headers=headers, json=payload, timeout=180)

        if response.status_code != 200:
            raise Exception(f"Stability API Error: {response.status_code} - {response.text[:200]}")

        data = response.json()
        image_data = data["artifacts"][0]["base64"]

        if output_path:
            if not output_path.endswith(".png"):
                output_path = f"{output_path}.png"

            with open(output_path, "wb") as f:
                f.write(base64.b64decode(image_data))

        return {
            "success": True,
            "image_data": image_data,
            "mime_type": "image/png",
            "output_path": output_path
        }


# =============================================================================
# Provider Factory
# =============================================================================

PROVIDER_CLASSES = {
    "google": GoogleProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "ollama": OllamaProvider,
    "stability": StabilityProvider
}


class ProviderFactory:
    """提供商工厂"""

    _instances: Dict[str, BaseProvider] = {}

    @classmethod
    def get_provider(cls, provider_id: str) -> Optional[BaseProvider]:
        """获取提供商实例"""
        if provider_id not in cls._instances:
            if provider_id not in PROVIDERS:
                return None

            config = PROVIDERS[provider_id]
            provider_class = PROVIDER_CLASSES.get(provider_id)

            if provider_class:
                cls._instances[provider_id] = provider_class(config)

        return cls._instances.get(provider_id)

    @classmethod
    def get_text_provider(cls, provider_id: str = None) -> BaseProvider:
        """获取文本生成提供商"""
        provider_id = provider_id or DEFAULT_TEXT_PROVIDER
        provider = cls.get_provider(provider_id)

        if not provider or not provider.is_available():
            # 尝试找一个可用的
            for pid, config in PROVIDERS.items():
                if config.get("enabled") and config.get("text_model"):
                    provider = cls.get_provider(pid)
                    if provider and provider.is_available():
                        return provider

        return provider

    @classmethod
    def get_image_provider(cls, provider_id: str = None) -> BaseProvider:
        """获取图像生成提供商"""
        provider_id = provider_id or DEFAULT_IMAGE_PROVIDER
        provider = cls.get_provider(provider_id)

        if not provider or not provider.is_available():
            # 尝试找一个可用的
            for pid, config in PROVIDERS.items():
                if config.get("enabled") and config.get("image_model"):
                    provider = cls.get_provider(pid)
                    if provider and provider.is_available():
                        return provider

        return provider

    @classmethod
    def list_available(cls) -> Dict[str, Dict]:
        """列出可用的提供商"""
        available = {}
        for pid, config in PROVIDERS.items():
            provider = cls.get_provider(pid)
            if provider:
                available[pid] = {
                    "name": config.get("name"),
                    "enabled": config.get("enabled"),
                    "has_text": bool(config.get("text_model")),
                    "has_image": bool(config.get("image_model")),
                    "is_available": provider.is_available()
                }
        return available


# =============================================================================
# Unified Client (向后兼容)
# =============================================================================

class GeminiClient:
    """统一客户端（向后兼容 + 多提供商支持）"""

    def __init__(self, text_provider: str = None, image_provider: str = None):
        self.text_provider_id = text_provider or DEFAULT_TEXT_PROVIDER
        self.image_provider_id = image_provider or DEFAULT_IMAGE_PROVIDER

    @property
    def text_provider(self) -> BaseProvider:
        return ProviderFactory.get_text_provider(self.text_provider_id)

    @property
    def image_provider(self) -> BaseProvider:
        return ProviderFactory.get_image_provider(self.image_provider_id)

    def generate_text(self, prompt: str, model: str = None) -> str:
        """生成文本"""
        provider = self.text_provider
        if not provider:
            raise Exception("No text provider available")
        return provider.generate_text(prompt, model)

    def generate_image(self, prompt: str, output_path: str = None, model: str = None) -> Dict:
        """生成图像"""
        provider = self.image_provider
        if not provider:
            raise Exception("No image provider available")
        return provider.generate_image(prompt, output_path, model)

    def generate_with_images(self, prompt: str, images: list, model: str = None) -> str:
        """多模态生成：文本+图像输入"""
        provider = self.text_provider
        if not provider:
            raise Exception("No text provider available")

        # 检查是否支持多模态
        if hasattr(provider, 'generate_with_images'):
            return provider.generate_with_images(prompt, images, model)
        else:
            # 降级为纯文本
            return provider.generate_text(prompt + "\n\n[Note: Images provided but not supported by this provider]", model)

    def set_text_provider(self, provider_id: str):
        """设置文本提供商"""
        self.text_provider_id = provider_id

    def set_image_provider(self, provider_id: str):
        """设置图像提供商"""
        self.image_provider_id = provider_id


# 默认客户端实例
client = GeminiClient()
