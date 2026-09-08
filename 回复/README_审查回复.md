# moment-png 项目审查回复

## 1. 总体判断

根据当前仓库状态，项目方向是正确的：目标不是训练拟合器，而是构造一个由 PNG density field 独立输入、通过测量与解析理论闭合得到 shell moment 预测的框架。

当前 README 已明确：测量引擎、Gaussian/Poisson controls、离散 shell window、paired realization products、covariance diagnostics 和 held-out mu1 validation 已运行；但是纯解析 production gate 仍未关闭，需要独立 b_phi/b_phi-delta calibration 与 halo connected four-point closure。

## 2. 核心原则修正

必须保持：

- 输入 PNG realization 后，只进行统计测量。
- 理论预测不能使用同一个 PNG realization 的 response 拟合参数。
- calibration 数据必须与 held-out validation 数据严格隔离。
- 任何机器学习或回归步骤只能用于诊断，不能成为最终科学闭合。

## 3. 推荐理论流程

建议固定 pipeline：

1. 测量阶段
   - 从 halo catalog / density field 测量 mu1(s)、mu2(s)。
   - 保存窗口函数、binning、shot-noise 修正。

2. Gaussian/Poisson 控制
   - Gaussian initial condition 与 Poisson sampling control 必须作为 null test。
   - 检查 estimator 是否引入非 PNG bias。

3. Shell window 验证
   - 对所有离散 shell 使用 exact window integration。
   - 避免连续近似造成 mu2 偏差。

4. 理论闭合
   - mu1: 优先完成 b1、b_phi、b_phi-delta 独立输入。
   - mu2: 明确 connected four-point contribution，不能只保留 disconnected Gaussian term。

## 4. 已有结果的解释

已有 held-out mu1 validation 和 Ngrid=32 composite smoke test 是必要证据，但只能证明 measurement pipeline 稳定，不能证明完整 PNG theory closure。

建议增加：

- held-out realization ID 固化记录。
- calibration/validation manifest。
- 每个理论项的误差预算表。

## 5. Stage 5/6 主要阻塞

### Stage 5

阻塞点：外部 z=1 theory input 的独立性和一致性。

建议：

- 将 b_phi 与 b_phi-delta 输入作为 versioned external data。
- 增加 checksum 和 provenance 文件。
- 禁止从目标 PNG sample 反推 bias。

### Stage 6

阻塞点：mu2 理论闭合。

必须解决：

- halo connected four-point term。
- shot noise 与 PNG coupling 的交叉项。
- finite shell window 对高阶项的修正。

## 6. 建议新增测试

新增 tests:

- test_no_same_realization_fit.py
- test_external_bias_provenance.py
- test_mu2_connected_term_toggle.py
- test_window_discretization_convergence.py

## 7. 优先级

P0:
- 完成独立 bias input 管理。
- 固化 held-out protocol。

P1:
- 完成 mu1 analytic closure。
- 建立 mu2 term-by-term audit。

P2:
- 扩展 Ngrid convergence 和 publication figures。

结论：当前代码基础适合作为 measurement engine，但下一阶段重点不是增加拟合能力，而是删除任何潜在 circular inference，完成严格理论闭合。