import base64
import io
from pygame import mixer


# Base64音效池
class BaseSoundPool:
    def __init__(self):
        self.pool = {}

    def load(self, name: str, base64_str: str) -> bool:
        """载入音频到池 load(sound,base64)"""
        if not name or not base64_str:
            return False

        try:
            # 兼容 Data URI：data:audio/wav;base64,<真正base64>
            if base64_str.startswith("data:"):
                base64_str = base64_str.split(",", 1)[1]

            raw = base64.b64decode(base64_str)
            if not raw:
                return False

            # 用 BytesIO 包装 供 mixer.Sound 直接读
            buf = io.BytesIO(raw)
            buf.seek(0)  # 指针归零 否则 Sound() 可能读空

            self.pool[name] = buf
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
        buf = self.get(name, default)
        if buf is None:
            return None
        try:
            # 首次使用前最好初始化一次
            if not mixer.get_init():
                mixer.init()
            sound = mixer.Sound(buf)
            sound.play(loops=loops)
            return sound
        except Exception as e:
            print(f"[SoundPool] 播放失败 {name}: {e}")
            return None

    def unload(self, name: str):
        buf = self.pool.pop(name, None)
        if buf is not None:
            buf.close()

    def clear(self):
        for buf in self.pool.values():
            buf.close()
        self.pool.clear()


# 单例
BSP = BaseSoundPool()