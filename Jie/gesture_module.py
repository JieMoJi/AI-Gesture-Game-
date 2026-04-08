import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
import math
import os


def find_model_path():
    """自动搜索模型文件"""
    possible_paths = [
        'hand_landmarker.task',
        os.path.join(os.path.dirname(__file__), 'hand_landmarker.task'),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    # 如果当前目录找不到，尝试上级目录（防止层级过深）
    parent = os.path.dirname(os.path.dirname(__file__))
    for root, dirs, files in os.walk(parent):
        if 'hand_landmarker.task' in files:
            return os.path.join(root, 'hand_landmarker.task')
    raise FileNotFoundError("找不到 hand_landmarker.task，请确保文件在同一目录下")


class GestureRecognizer:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = find_model_path()

        options = vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self.cap = cv2.VideoCapture(0)
        self.timestamp_ms = 0

        # 调优后的阈值
        self.CHARGE_MAX = 0.28  # 放宽一点，防止握拳漏检
        self.BLAST_MIN_DIST = 0.45
        self.BLAST_MIN_EXT = 0.25

    def get_gesture(self):
        ret, frame = self.cap.read()
        if not ret:
            return "none", None, {}

        frame = cv2.flip(frame, 1)  # 镜像
        self.timestamp_ms += 33

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        )
        result = self.landmarker.detect_for_video(mp_image, self.timestamp_ms)

        gesture = "none"
        debug = {"dist": 0, "ext": 0}

        if result.hand_landmarks:
            landmarks = result.hand_landmarks[0]
            gesture, debug = self._classify(landmarks)

            # 绘制关键点（可选，调试用）
            h, w = frame.shape[:2]
            for lm in landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

        return gesture, frame, debug

    def _classify(self, landmarks):
        WRIST = 0
        FINGER_TIPS = [8, 12, 16, 20]
        FINGER_PIPS = [6, 10, 14, 18]

        def dist(p1, p2):
            return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

        wrist = landmarks[WRIST]

        # 计算平均指尖距离
        tip_dists = [dist(landmarks[t], wrist) for t in FINGER_TIPS]
        avg_dist = sum(tip_dists) / len(tip_dists)

        # 计算平均伸展度
        exts = []
        for tip, pip in zip(FINGER_TIPS, FINGER_PIPS):
            d_tip_pip = dist(landmarks[tip], landmarks[pip])
            d_pip_wrist = dist(landmarks[pip], wrist)
            if d_pip_wrist > 0.001:
                exts.append(d_tip_pip / d_pip_wrist)
        avg_ext = sum(exts) / len(exts) if exts else 0

        # 判定逻辑
        if avg_dist < self.CHARGE_MAX:
            gesture = "charge"
        elif avg_dist > self.BLAST_MIN_DIST and avg_ext > self.BLAST_MIN_EXT:
            gesture = "blast"
        else:
            gesture = "none"

        return gesture, {"dist": round(avg_dist, 3), "ext": round(avg_ext, 3)}

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()