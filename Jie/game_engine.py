import time


class GameEngine:
    """游戏引擎：管理能量、连击、发波逻辑"""

    def __init__(self):
        self.energy = 0
        self.combo = 0
        self.score = 0
        self.blast_trigger = False

        # 状态记录
        self.charge_start_time = 0
        self.last_blast_time = 0

        # 配置参数
        self.MAX_ENERGY = 100
        self.BLAST_COST = 30
        self.CHARGE_RATE = 1.5  # 每帧增加的能量基数
        self.COMBO_WINDOW = 2.0  # 连击判定窗口 (秒)
        self.COOLDOWN = 0.5  # 发波冷却时间 (秒)

    def update(self, gesture: str, dt: float = 0.033) -> dict:
        """
        主更新函数
        :param gesture: "charge", "blast", or "none"
        :param dt: 帧间隔时间
        :return: 状态字典
        """
        now = time.time()
        self.blast_trigger = False  # 每帧重置触发信号

        if gesture == "charge":
            # 聚气逻辑
            self.energy = min(self.energy + int(self.CHARGE_RATE), self.MAX_ENERGY)
            if self.charge_start_time == 0:
                self.charge_start_time = now

        elif gesture == "blast":
            # 检查冷却
            if now - self.last_blast_time >= self.COOLDOWN:
                if self.energy >= self.BLAST_COST:
                    # 执行发波
                    self.energy -= self.BLAST_COST
                    self.blast_trigger = True
                    self.last_blast_time = now

                    # 连击判定
                    # 如果之前聚过气，且在时间窗口内
                    if self.charge_start_time > 0 and (now - self.last_blast_time) < (self.COMBO_WINDOW + 3.0):
                        self.combo += 1
                        self.score += 100 * self.combo
                    else:
                        self.combo = 1
                        self.score += 100

                    self.charge_start_time = 0  # 重置聚气计时

        return {
            "energy": int(self.energy),
            "combo": self.combo,
            "score": self.score,
            "blast_trigger": self.blast_trigger
        }

    def reset(self):
        """重置游戏状态"""
        self.__init__()