import base64
import io
import json

from pygame import mixer


# Base64音效池
class BaseSoundPool:
    def __init__(self):
        self.pool = {}
        self._raw = {}

    def load(self, name: str, base64_str: str) -> bool:
        """载入音频到池 load(sound,base64)"""
        if not name or not base64_str:
            return False
        try:
            if base64_str.startswith("data:"):
                base64_str = base64_str.split(",", 1)[1]

            raw = base64.b64decode(base64_str)
            if not raw:
                return False

            if not mixer.get_init():
                mixer.init()

            # 一次性构造 Sound 之后完全脱离 BytesIO
            self.pool[name] = mixer.Sound(io.BytesIO(raw))
            self._raw[name] = base64_str
            return True
        except Exception as e:
            print(f"载入失败 {name}: {e}")
            return False

    def get(self, name: str, default=None):
        """取 BytesIO 取不到返回 default（默认 None）"""
        buf = self.pool.get(name, default)
        if buf is not None:
            buf.seek(0)  # 每次播放前归零，避免重复 play 只读一半
        return buf

    def play(self, name: str, loops: int = 0, default=None):
        """一行播放 play("important_tip")"""
        snd = self.pool.get(name)
        if snd is None:
            print(f"[SoundPool] 未载入音效: {name}")
            return None
        try:
            return snd.play(loops=loops)
        except Exception as e:
            print(f"[SoundPool] 播放失败 {name}: {e}")
            return None

    def unload(self, name: str):
        """卸载池 unload(name)"""
        self.pool.pop(name, None)
        self._raw.pop(name, None)

    def clear(self):
        """清空池与缓存池 clear()"""
        self.pool.clear()
        self._raw.clear()

    def older(self):
        """获取原始池 older()"""
        return self.pool

# 单例
BSP = BaseSoundPool()