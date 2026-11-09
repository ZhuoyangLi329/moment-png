# 观测量、约定与模型

## 1. 观测量

halo 计数场经 CIC 赋值得到 δ(x) = n(x)/⟨n⟩ − 1（周期盒，N³ 网格）。对每个壳半径 s，K_s 是离散周期 top-hat 壳核（|r| ∈ [s − Δs/2, s + Δs/2)，归一到 Σ K = 1），δ_s = K_s ∗ δ：

    η_s(x) = δ(x) δ_s(x)
    μ1(s)  = ⟨η_s⟩
    μ2(s)  = ⟨(η_s − μ1)²⟩
    μ3(s)  = ⟨(η_s − μ1)³⟩

这就是 ConKer 的 Γ 矩在周期盒、无 random catalog 时的形式（random 归一化退化为常数）。μ3 暂不做。

冻结的 v1 协议（`configs/protocol.yaml`）：z = 1（snap 002），FoF M_h ≥ 1e13 M⊙/h，实空间，L = 1000 Mpc/h，主网格 N = 64（另有 128/256 做分辨率检查），Δs = 20，s = 40–300（步长 20）。realization 分块：real000–069 训练，real070–099 留出，real100–499 独立标定。

## 2. 精确的 Fourier 投影

估计量对场是双线性的，所以对每模功率 P(k) = V/N⁶ |FFT δ|²（去掉零模）有**精确**的恒等式：

    μ1(s)    = V⁻¹ Σ_k P(k) W_s(k)
    μ2_G(s)  = σ0² σ_s² + μ1(s)²,  σ0² = V⁻¹ Σ P,  σ_s² = V⁻¹ Σ P W_s²

其中 W_s = FFT[K_s]，必须用**同一个离散壳核**，不能换成连续的 j0 近似（旧版本的连续窗口在 N=12 的测试里偏差达到 0.087）。网格效应（CIC、混叠）只进 P，不进 W。μ2 − μ2_G 定义为 connected 部分。对三阶矩，相关高斯变量 X、Y 满足 ⟨(XY − c)³⟩ = 6cσx²σy² + 2c³，所以 μ3_G = 6 μ1 σ0² σ_s² + 2 μ1³，μ3 − μ3_G 是 connected 的三阶部分（`tests/test_estimator.py` 有点态和场两种检验）。若用"样本均值中心化"的 μ2，还要再减 Var(⟨η⟩) = 2 Σ (PW)² / V²。这些恒等式都由 `tests/test_estimator.py` 独立验证（roll-sum、平面波、单模 Gauss–Hermite）。

## 3. μ1 模型：tree 级 PNG 偏置

    P_h(k) = [b1 + fNL (bφ / M(k) + Δb1)]² P_m(k) T_m(k) + P_shot T_s(k)

- **bφ 是完整的 PNG 偏置系数**：Δb = fNL bφ / M(k)，其中 δ_L = M φ。universal mass function 关系给出 bφ = 2 δ_c (b1 − p)，δ_c = 1.686，p = 1.12（tracer）或 1.0。
- **Δb1 = ∂b1/∂fNL 是尺度无关的 PNG 偏置**：在固定质量阈值下，质量函数本身随 fNL 改变，样本的 b1 也随之线性变化。对 z=1、M ≥ 1e13 的 FoF halo，P(k) 层面拟合给出 Δb1 ≈ −4×10⁻⁴（见 findings）。漏掉这一项，μ1 的 PNG 响应在 s ≲ 120 处就会被系统性高估。
- 网格约定：`cic_both` 是 T_m = T_s = Π sinc⁴(k_i H/2)；`cic_matter` 是 T_s = 1；`none` 是都取 1。这几种都不是严格的：Poisson 点做 CIC 赋值后，shot 项实际是 (1/n̄) Σ_n W²(k + 2k_N n)。
- 配对的奇响应对 c = b1 bφ 和 Δb1 都是线性的：[X(+f) − X(−f)]/(2f) = c · T_c + Δb1 · T_b，其中 T_c、T_b 分别是 2 P_m T_m / M 和 2 b1 P_m T_m 的分 bin 平均（X = P_h）或精确窗口投影（X = μ1）。数据真正约束的是 c，bφ = c/b1 依赖于 b1 的取值。

## 4. loop（诊断用）

    δ_h = b1 δ + b2/2 δ² + bK2 K² (+ PNG 项)
    K2(q, r) = b1 F2 + b2/2 + bK2 S2,   S2 = μ² − 1/3
    P_loop = P22[K2] + b1² P13 + b1 b2 D3 + b1 bK2 T3（collapsed），以及单条 PNG 腿的方向导数

固定截断 [qmin, qmax]，**没有 counterterm**，所以结果强烈依赖截断。缺失的项：PNG kernel 偏置插入（bφδ 等）、IR resummation、counterterm。

## 5. μ2 的 connected 部分

    μ2 = μ2_G + μ2_contact + μ2_clustered,NG + μ2_PNG,connected

- **iid Poisson contact**（已验证）：NGP 理想化下是 K0²/λ³；精确的 CIC 版本是 I/λ³，其中 I = ∫_[0,1]³ d³u w0(u)² [Σ_e K_e w_e(u)]²，λ 为每格平均 halo 数。
- **halo 的聚集或重复指标项**：没有模型。
- **原初 trispectrum**：没有可用实现，见下一节。

### 5.1 原初 trispectrum：旧实现的两处错误（模块已删除）

局域模型 Φ = φ + fNL(φ² − ⟨φ²⟩) 在 fNL² 阶的 trispectrum 是

    T_Φ(k1..k4) = 4 fNL² Σ_{(a,b) 一阶腿, c,d 二阶腿} P(k_a) P(k_b) [ P(|k_a + k_c|) + P(|k_a + k_d|) ]   (共 12 项)

两条一阶腿的功率，乘上"一阶腿 + 二阶腿"的交叉动量（t/u 通道）。旧的 `local_trispectrum_phi` 用的是 P(k_i) P(k_j) P(|k_i + k_j|)，即那一对腿自身的和动量（s 通道），只有 6 项。在 collapsed 构型 (q, −q, p, −p) 下，这正好给出 P(0)。旧审计里"预测比测量大 ~10²⁰"的现象，以及后来的"零模修正"，都源于这个错误。

另一个问题：旧实现只在 (q, −q, p, −p) 上做 6 维 MC 积分。但 μ2 的 connected 项是

    μ2_c = ∫ d³k1 d³k2 d³k3 /(2π)⁹  W_s(k3) W_s(k4) T_h(k1, k2, k3, k4),  k4 = −k1 − k2 − k3

这是一个 9 维积分，collapsed 构型只是其中的一个极限。所以旧模块在结构上就是错的，已经删除，以后需要按上面的公式重写。

## 6. 经验 fNL 似然（统计基线）

均值用训练集三个节点的均值插值：m(f) = m0 + f (m₊ − m₋)/200 + f² [(m₊ + m₋)/2 − m0]/100²。协方差取 fiducial 训练集的样本协方差，并做对角 shrinkage。似然用 Gaussian 或 Sellentin–Heavens 的 t 分布。这一节只用来衡量信息量和覆盖率，不是解析模型。
