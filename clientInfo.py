import time
import yaml
from metric import LLM_RESPONSE_TIME, LLM_TOKENS_USED
from openai import OpenAI
from deepseek_tokenizer import tokenizer

class clientInfo:
    def __init__(
        self,
        api_key=None,
        base_url="https://api.example.com",
        model="gpt-4",
        dryRun=False,
    ):
        """
        初始化ApiClient

        参数:
            api_key (str): API密钥，默认为None
            base_url (str): 基础URL，默认为"https://api.example.com"
            model (str): 模型名称，默认为"gpt-4"
            dryRun (bool): 是否干跑模式，默认为False
        """
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        with open("config.yaml", "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)
        # 鲁棒性处理dryRun参数
        if isinstance(dryRun, str):
            self._dryRun = dryRun.lower() == "true"
        elif isinstance(dryRun, int):
            self._dryRun = bool(dryRun)
        else:
            self._dryRun = bool(dryRun)
        if not self._dryRun:
            self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)
        else:
            self._client = None

    # Getter方法
    def get_api_key(self):
        """获取API密钥"""
        return self._api_key

    def get_base_url(self):
        """获取基础URL"""
        return self._base_url

    def get_model(self):
        """获取模型名称"""
        return self._model

    def get_dryRun(self):
        """获取干跑模式状态"""
        return self._dryRun

    def get_legal_info(self):
        return (
            "Disclaimers: This content is powered by i18n-agent-action with LLM service "
            + self._base_url
            + " with model "
            + self._model
            + ", for some reason, (for example, we are not native speaker) we use LLM to provide this translate for you. If you find any corrections, please file an issue or raise a PR back to github, and switch back to default language."
        )

    def get_config(self):
        return self._config

    # 可选：添加一个显示所有配置的方法
    def show_config(self):
        """显示当前配置"""
        print("API Client Configuration:")
        print(f"  Base URL: {self._base_url}")
        print(f"  Model: {self._model}")
        print(f"  Dry Run: {self._dryRun}")

    def talk(self, messages, use_json=False):
        print(f"Request to LLM - Messages: {messages}")
        if not self._dryRun:
            start_time = time.time()

            # Prepare the request parameters
            request_params = {
                "model": self._model,
                "messages": messages,
                "stream": False,
            }

            # Add JSON response format if requested
            if use_json:
                request_params["response_format"] = {"type": "json_object"}

            # Make the API call
            response = self._client.chat.completions.create(**request_params)
            duration = time.time() - start_time
            LLM_RESPONSE_TIME.observe(duration)

            # Handle token usage metrics
            if response.usage:
                # If we have usage data, use accurate values
                prompt_tokens = response.usage.prompt_tokens
                prompt_cache_hit_tokens = response.usage.prompt_cache_hit_tokens
                prompt_cache_miss_tokens = response.usage.prompt_cache_miss_tokens
                completion_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens
                LLM_TOKENS_USED.labels(model=self._model, type="char_count").inc(
                    tokenizer(str(messages))
                )
                LLM_TOKENS_USED.labels(model=self._model, type="prompt_cache_hit").inc(
                    prompt_cache_hit_tokens
                )
                LLM_TOKENS_USED.labels(model=self._model, type="prompt_cache_miss").inc(
                    prompt_cache_miss_tokens
                )
                LLM_TOKENS_USED.labels(model=self._model, type="prompt").inc(
                    prompt_tokens
                )
                LLM_TOKENS_USED.labels(model=self._model, type="completion").inc(
                    completion_tokens
                )
                LLM_TOKENS_USED.labels(model=self._model, type="total").inc(
                    total_tokens
                )
            else:
                # Otherwise estimate token count for the response content
                content = response.choices[0].message.content
                char_count = len(content)
                LLM_TOKENS_USED.labels(model=self._model, type="char_count").inc(
                    char_count
                )
                # Note: You might want to add token estimation logic here
                # Currently this just increments total_tokens which isn't defined
                # You might want to use something like:
                # estimated_tokens = len(content.split()) // 0.75  # Rough estimation
                # LLM_TOKENS_USED.labels(model=self._model, type='total').inc(estimated_tokens)
                pass

            return response
        else:
            LLM_TOKENS_USED.labels(model=self._model, type="char_count").inc(
                    tokenizer(str(messages))
            )
            return None

    def talk_to_LLM(self, messages):
        return self.talk(messages, False)

    def talk_to_LLM_Json(self, messages):
        return self.talk(messages, True)
