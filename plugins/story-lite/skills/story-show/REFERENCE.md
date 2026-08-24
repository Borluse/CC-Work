# 参数测试 HTML 参考

仅在需求包含实时计算、参数控件或 SVG 几何投影时读取。

## 页面结构

推荐保持一个状态源：

```javascript
function render() {
  const state = calculateState(readInputs());
  updateSummary(state);
  renderSideView(state);
  renderTopView(state);
}
```

- `readInputs()`：读取、解析并限制输入。
- `calculateState()`：只负责计算，不操作 DOM。
- `updateSummary()`：更新指标、公式、判定和样式。
- `render*View()`：只消费状态进行绘制。

输入控件统一监听 `input`；模式切换同时监听 `change`。重置按钮恢复全部默认值后调用一次 `render()`。

## SVG 几何

三维方向向量和圆锥底面可按以下方式构造：

```javascript
const baseCenter = add(apex, scale(axis, height));
const reference = Math.abs(axis.z) < 0.9
  ? { x: 0, y: 0, z: 1 }
  : { x: 0, y: 1, z: 0 };
const basisU = normalize(cross(reference, axis));
const basisV = normalize(cross(axis, basisU));
const baseRadius = height * Math.tan(halfAngleRadians);

for (let index = 0; index < 72; ++index) {
  const angle = index / 72 * Math.PI * 2;
  const radial = add(
    scale(basisU, Math.cos(angle)),
    scale(basisV, Math.sin(angle))
  );
  baseRing.push(add(baseCenter, scale(radial, baseRadius)));
}
```

投影规则：

- 侧视图：`(X, Y, Z) → (X, Z)`。
- 俯视图：`(X, Y, Z) → (X, Y)`。
- 将锥顶与底面采样点求二维凸包，作为视锥投影轮廓。
- 底面采样点按原顺序绘制折线，表达底面圆的投影。
- 根据所有投影点计算统一比例，X/Y 使用相同缩放值。

## PilotSight 示例语义

当前 PilotSight 测试工具采用以下输入：

- 怪物离地高度。
- 地面玩家的 X/Y 位置。
- `AlertRadius`。
- `AlertAngle` 总角度。
- 距离综合倍率。
- 动态朝向玩家或手动设置中轴。

有效圆锥高度：

```javascript
const effectiveHeight = alertRadius * radiusMultiplier;
```

角度阈值与形状判定：

```javascript
const halfAngle = alertAngle * 0.5;
const alertCos = Math.cos(halfAngle * Math.PI / 180);
const cosValue = dot(axis, targetDirection);
const axialProjection = distance * cosValue;

const anglePass = cosValue > alertCos;
const rangePass = axialProjection < effectiveHeight;
const inside = distance > epsilon && anglePass && rangePass;
```

`AlertRadius` 表示圆锥轴向高度。目标方向与中轴夹角为 `θ` 时，轴向投影为 `Distance × cos(θ)`。

动态朝向模式模拟 PilotSight：

- 根据目标方向计算 Pitch/Yaw。
- Pitch 和 Yaw 分别限制在 `[-80°, 80°]`。
- 目标超出 Clamp 后，中轴只朝限制后的方向旋转。

绘图半角限制到 `89°`，避免 `tan(90°)` 发散；运行时角度判定仍使用真实配置半角。

默认示例：

- 怪物：`(0, 0, 2000) cm`。
- 玩家：`(1000, 0, 0) cm`。
- `AlertRadius = 1500 cm`。
- `AlertAngle = 120°`。
- 综合倍率为 `1`。

默认直线距离约为 `2236.07 cm`。中轴朝向玩家时目标夹角为 `0°`，轴向投影超过有效圆锥高度，因此判定在警戒视锥外。

## 边界检查

生成相似工具时至少检查：

- `AlertRadius = 0`：没有有效视锥体积。
- `AlertAngle = 0`：严格余弦条件无法命中。
- `AlertAngle = 180`：判定使用 `90°` 半角，绘图使用 `89°`。
- 目标与对象重合：方向退化时稳定返回范围外。
- 目标恰好位于底面：严格 `<` 条件判定范围外。
- 手动中轴与目标反向：角度条件失败。
- 倍率为 `0`：有效高度归零。

## 常见错误

- 把圆锥高度画成球形半径。
- 使用二维距离进行三维圆锥判定。
- 输入变化后只更新数字，图形仍使用旧参数。
- 俯视投影重叠时直接判断目标在三维视锥内。
- 将厘米值标成米，或修改标签但未修改计算单位。
- 自动朝向直接对准目标，遗漏运行时代码中的轴角 Clamp。
