# moment-png 科学审查与调整建议

## 总体判断

项目方向正确：目标不是拟合 PNG 响应，而是建立从独立 cosmology + halo physics + measurement window 到 ConKer μ1/μ2 的闭合预测链。当前仓库已经形成可靠 measurement/validation scaffold，但尚未达到 pure-analytic prediction。

## 1. 核心目标纠错

当前必须继续保持：

- 禁止使用同一 PNG realization 拟合 b_phi、响应系数或经验 A/k^2 模板。
- 所有 PNG 参数必须来自独立理论、外部模拟标定或文献输入。
- held-out 只能用于最终检验，不能反向调参。

建议增加 production guard：任何 prediction config 若缺少 b_phi/b_phidelta provenance，直接失败。

## 2. 方法链调整

推荐优先级：

1. measurement layer 固化：固定 CIC、FFT mesh、shell window、zero mode。
2. Gaussian baseline 完成：作为 μ2 正确性的底座。
3. Poisson/contact separation：不要将 shot noise 当作简单白噪声修正，需要验证离散 halo sampling contraction。
4. μ1 闭合：先解决 b_phi、b_phidelta 独立校准，再加入 loop。
5. μ2 闭合：优先 Gaussian + contact，再逐步加入 PNG trispectrum 和 bias connected terms。

## 3. 已实现模块评价

已有模块覆盖：

- moments.py：测量核心。
- exact_window.py：离散窗口投影。
- theory_mu2_gaussian.py：Wick baseline。
- halo kernel/P13/P22：loop scaffold。
- theory_mu1_bphi.py：独立 b_phi 接口。

其中 theory_mu1_bphi.py 的设计原则正确，但 universal mass function b_phi 只能作为 branch，不应成为默认 truth。

## 4. held-out 与 Ngrid=32 证据解释

当前证据说明：

- measurement pipeline 可重复。
- tree-level analytic model 缺少物理项，而不是代码简单 bug。
- Ngrid=32 composite smoke 成功证明代码路径可运行，但 RMS pull 仍大，不能作为模型改善证据。

不要用低分辨率 smoke 选择模型参数。

## 5. Stage 5/6 阻塞排序

建议按照以下顺序解除：

### 第一优先

独立 b_phi / b_phidelta calibration。

原因：μ1 的 leading PNG bias 若错误，所有后续 loop 比较没有意义。

### 第二优先

z=1 Pm、M(k,z)、CIC normalization audit。

### 第三优先

halo connected four-point/contact derivation。

### 第四优先

完整 MARISA-B K3/K4 和 PNG loop closure。

## 建议新增测试

- test_no_self_fit.py：扫描配置，禁止 response-derived parameter。
- test_input_provenance.py：要求理论输入记录来源。
- test_window_theory_consistency.py：mesh prediction 与 analytic window 一致性。

## 最终建议

当前项目状态应描述为：

"reproducible ConKer moment measurement and semi-analytic validation framework"

而不是：

"closed analytic PNG prediction"。

下一阶段重点不是增加更多 fitting flexibility，而是减少自由参数并建立每个理论输入的 provenance chain。
