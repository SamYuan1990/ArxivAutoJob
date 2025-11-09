import json
import os
import threading
import time

from filelock import FileLock
from openai.types.chat import ChatCompletion


class ExpiringDictStorage:
    def __init__(self, filename="data_store.json", expiry_days=7):
        self.filename = filename
        self.expiry_days = expiry_days
        self.lock = threading.Lock()
        self.file_lock = FileLock(filename + ".lock")
        self.data = self._load_data()

    def _load_data(self):
        """加载数据并清理过期项"""
        with self.file_lock:
            if not os.path.exists(self.filename):
                return {"_metadata": {"last_clean": time.time()}, "data": {}}

            try:
                with open(self.filename, "r") as f:
                    data = json.load(f)

                # 清理过期数据（每7天执行一次）
                current_time = time.time()
                if (
                    current_time - data["_metadata"]["last_clean"]
                    > self.expiry_days * 86400
                ):
                    data["data"] = {
                        k: v
                        for k, v in data["data"].items()
                        if current_time - v["timestamp"] <= self.expiry_days * 86400
                    }
                    data["_metadata"]["last_clean"] = current_time
                    self._save_data(data)

                return data
            except (json.JSONDecodeError, KeyError):
                # 文件损坏时创建新文件
                return {"_metadata": {"last_clean": time.time()}, "data": {}}

    def _save_data(self, data):
        """保存数据到文件"""
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=2)

    def get(self, key, update_timestamp=True):
        """获取值
        :param key: 要获取的键
        :param update_timestamp: 是否更新访问时间戳，默认为True
        """
        with self.lock:
            if key not in self.data["data"]:
                return None

            item = self.data["data"][key]
            value = item["value"]

            # 如果配置为更新时间戳，则更新
            if update_timestamp:
                item["timestamp"] = time.time()
                self._save_data(self.data)

            if item.get("_type") == "ChatCompletion":
                return ChatCompletion.model_validate_json(value)
            else:
                return value

    def set(self, key, value):
        """设置值"""
        with self.lock:
            if isinstance(value, ChatCompletion):
                storage_item = {
                    "value": value.model_dump_json(),
                    "timestamp": time.time(),
                    "_type": "ChatCompletion",
                }
            else:
                storage_item = {
                    "value": value,
                    "timestamp": time.time(),
                    "_type": "string",
                }

            self.data["data"][key] = storage_item
            self._save_data(self.data)

    def clean_expired(self):
        """手动清理过期数据"""
        with self.lock:
            current_time = time.time()
            self.data["data"] = {
                k: v
                for k, v in self.data["data"].items()
                if current_time - v["timestamp"] <= self.expiry_days * 86400
            }
            self.data["_metadata"]["last_clean"] = current_time
            self._save_data(self.data)

    def __contains__(self, key):
        with self.lock:
            return key in self.data["data"]

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)


# 使用示例
if __name__ == "__main__":
    # 安装依赖: pip install filelock
    storage = ExpiringDictStorage(expiry_days=7)

    # 设置值
    storage["user1"] = {"name": "Alice", "age": 30}
    storage["user2"] = {"name": "Bob", "age": 25}

    # 获取值
    print("当前存储内容:")
    print(storage.data)
    print("user1的值:", storage["user1"])  # 输出: {'name': 'Alice', 'age': 30}

    # 检查键是否存在
    print("user2是否存在:", "user2" in storage)  # 输出: True

    # 模拟7天前的数据
    print("\n模拟7天前的数据...")
    old_time = time.time() - 8 * 86400  # 8天前(超过7天有效期)
    old_data = {
        "_metadata": {"last_clean": old_time},
        "data": {
            "user1": {"value": {"name": "Alice", "age": 30}, "timestamp": old_time},
            "user2": {"value": {"name": "Bob", "age": 25}, "timestamp": old_time},
        },
    }
    with open(storage.filename, "w") as f:
        json.dump(old_data, f)

    # 重新加载会自动清理过期数据
    print("\n重新加载存储(应自动清理过期数据)...")
    storage = ExpiringDictStorage(expiry_days=7)
    print("清理后的存储内容:")
    print(storage.data)  # 现在应该看到空字典，因为所有数据都过期了

    # 添加新数据验证功能正常
    print("\n添加新数据验证功能正常...")
    storage["user3"] = "afda"
    print("添加后的存储内容:")
    print(storage.data)
