## 📂 3. `render_module.py` (渲染模块)
**负责人**：赵智诚  
**状态**：🟡 开发中 (v2.0 - 粒子特效)

```markdown
# 🎨 渲染模块 (Rendering)

## ⚠️ 重要公告 (2024-04-13)
- **本模块是游戏的“脸面”**，负责将数据转化为视觉画面。
- **依赖预警**：完全依赖 `game_engine` 输出的 `state` 字典。
- **协作须知**：若需要新数据（如 `"particle_count"`），**必须提前向丁佳妮提出需求**，由她在引擎中计算后返回，不要在此模块硬算。

## 🎯 当前任务 
1. [ ] 实现粒子系统基础框架
2. [ ] 为 6 种技能设计不同视觉特效 (颜色/形状/运动轨迹)
3. [ ] 优化绘图性能，确保帧率 > 20fps

## 🔌 接口定义 (严禁随意修改)
- **输入**: 
  - `frame`: 摄像头原始画面 (numpy array)
  - `state`: 游戏状态字典 (来自引擎模块)
- **输出**: `display_frame`: 绘制完成的画面 (numpy array)
- **调用示例**:
  ```python
  from render_module import render_game
  final_frame = render_game(camera_frame, state)
