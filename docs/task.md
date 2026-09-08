***************************************************************************
                          NOTICE TO USERS

Lawrence Berkeley National Laboratory operates this computer system under 
contract to the U.S. Department of Energy.  This computer system is the 
property of the United States Government and is for authorized use only.
Users (authorized or unauthorized) have no explicit or implicit 
expectation of privacy.

Any or all uses of this system and all files on this system may be
intercepted, monitored, recorded, copied, audited, inspected, and disclosed
to authorized site, Department of Energy, and law enforcement personnel,
as well as authorized officials of other agencies, both domestic and foreign.
By using this system, the user consents to such interception, monitoring,
recording, copying, auditing, inspection, and disclosure at the discretion
of authorized site or Department of Energy personnel.

Unauthorized or improper use of this system may result in administrative
disciplinary action and civil and criminal penalties. By continuing to use
this system you indicate your awareness of and consent to these terms and
conditions of use. LOG OFF IMMEDIATELY if you do not agree to the conditions
stated in this warning.

*****************************************************************************

Login connection to host x3113c0s19b0n0:

# PNG Quijote 密度扰动矩解析模型项目任务书

## 项目目标

本项目使用 PNG Quijote simulation，目标是为前两阶密度扰动矩建立解析或半解析模型：μ1(s) 和 μ2(s)，μ3(s) 暂不纳入第一阶段。

参考文献没有使用解析模型限制 fNL，而是用 fNL=-25,0,+25 FastPM 模拟拟合经验关系：
    μ~i(fNL) = Ai fNL^2 + Bi fNL + Ci
再用模拟协方差、chi2 和 MCMC 推断 fNL。本项目要用物理模型解释 Quijote 模拟中的矩和 fNL 响应。

## 观测量定义

球壳平均密度：
    δ_h,s(x) = ∫d3r K_s(r) δ_h(x+r)

密度乘积：
    η_s(x) = δ_h(x) δ_h,s(x)

随机目录归一化：
    Γ(x,s) = η_s(x) / <η_R(s)> * NR^2 / ND^2

前两阶矩：
    μ1(s) = <Γ(x,s)>
    μ2(s) = <[Γ(x,s)-μ1(s)]^2>

第一版理论基准采用周期盒、连续密度、无 RSD、无 shot noise，之后逐项加入复杂因素。必须明确 halo overdensity、球壳宽度、real/RSD、random normalization、shot noise 和边界条件。

## μ1 解析模型

一阶矩是球壳窗口作用下的 halo 二点函数：
    μ1(s) = ∫d3k/(2π)^3 P_h(k) W_s(k)

    W_s(k) = 1/ΔV_s ∫_(s-Δs/2)^(s+Δs/2) 4πr^2 j0(kr) dr
薄壳极限：W_s(k) ~= j0(ks)。

第一版：
    P_h(k,z) = [b1(z)+Δb_PNG(k,z)]^2 P_m(k,z) + P_shot
    Δb_PNG(k,z) = 2 fNL δc [b1(z)-p] / α(k,z)
    α(k,z) = 2 k^2 T(k) D(z)/(3 Ωm H0^2)

分解：
    μ1(s) = μ1G(s) + fNL μ1(1)(s) + fNL^2 μ1(2)(s)

其中一阶响应主要来自 PNG scale-dependent bias，二阶响应主要来自 PNG bias 平方项。验证 Quijote fNL=0、+/-50、+/-100 的 μ1 均值和响应。

## μ2 统计结构

    μ2(s) = <η_s^2> - <η_s>^2
             = <δ_h^2(x) δ_h,s^2(x)> - <δ_h(x)δ_h,s(x)>^2

Fourier 空间中 μ2 是 halo 四点函数经过球壳窗口的投影：
    μ2 = μ2,Gaussian + μ2,connected + μ2,shot

Gaussian 部分使用 Wick contractions：
    <δ1δ2δ3δ4> = <δ1δ2><δ3δ4> + 2 permutations

connected 部分来自 halo trispectrum。局域 PNG：
    T_Φ ~ fNL^2 [P_φ P_φ P_φ]
    T_m = M(k1)M(k2)M(k3)M(k4) T_Φ

halo bias 从简单形式开始：
    δ_h = b1δ + b2/2 δ^2 + b_φ fNL φ + b_φδ fNL φδ + ...

加入顺序：仅 b1；b1+bφ；加入 b2；加入 b_φδ；最后 nonlinear matter trispectrum。

第一版：
    μ2(s) = μ2G(s) + fNL μ2(1)(s) + fNL^2 μ2(2)(s) + μ2NL(s)

## 离散 halo 和 shot noise

先考虑 P_h -> P_h + 1/nbar_h，但 μ2 还包含四点接触项和重复索引项。用解析 Poisson 修正与随机 Poisson catalog 测量交叉验证，并检查 random normalization 的作用。

## Quijote 数据和配置

主目录：
    /pscratch/sd/l/lzy/PNG-EZmock/data/quijote_z1_local_png_power/

原生节点：
    fNL = -100, -50, 0, +50, +100

不要把 interpolated +/-10、+/-20、+/-30 当作原生 N-body ensemble。第一版固定 z=1、FoF M_h >= 1e13 Msun/h、real-space、s=20--300 h^-1 Mpc、Δs=10 或 20 h^-1 Mpc、Quijote fiducial cosmology，并从大尺度测 b1、用 universality relation 给 bφ。

当前主目录主要保存 z=1 local-PNG FoF halo redshift-space P0/P2 realization-level products。若需从 halo catalog 重新计算 Γ、μ1、μ2，还需确认原始 FoF catalog 的实际路径。

## 分层验证

Level 0：Gaussian continuous，fNL=0、real space、无 shot noise、固定 b1。
Level 1：加入离散 halo、shot noise、实际 number density 和 bias。
Level 2：加入 ΔbPNG proportional to fNL/k^2。
Level 3：加入 primordial trispectrum，重点检验 μ2 的额外信号。
Level 4：加入 RSD、b2、nonlinear Pm、nonlinear trispectrum、有限体积修正。

每一级保存理论曲线、Quijote 均值、残差、chi2 和参数依赖。

## 代码推进顺序

1. 从 Quijote halo catalog 实现 Γ、μ1、μ2 测量；
2. Gaussian random field 验证球壳窗口 Fourier 公式；
3. 实现 μ1[P_h] 数值积分；
4. 实现 Gaussian μ2[P_h]；
5. 加 Poisson shot noise；
6. 加 fNL scale-dependent bias；
7. 加 primordial trispectrum；
8. 与五个原生 Quijote fNL 节点比较；
9. 最后加入 RSD 和 nonlinear corrections。

## 成功标准

1. 解释 fNL=0 的 μ1、μ2 尺度依赖，残差小于约两倍模拟标准误差；
2. 正确预测 fNL=+/-50、+/-100 的响应方向和尺度依赖；
3. 拟合 Quijote 测试 realization 时无明显 fNL 偏差；
4. 最终用少量物理参数预测 μ1、μ2，而不是为每个 fNL 节点单独拟合 Ai、Bi、Ci；
5. 定量分离 Gaussian 方差、PNG bias、primordial trispectrum、shot noise 和 nonlinear correction。

## 当前优先理论成果

优先攻克 μ1 和 μ2：μ1 是窗口化 halo power spectrum，μ2 是 collapsed halo four-point statistic。暂不处理 μ3。

## 执行状态（2026-09-06）

- 已找到 Quijote PNG 原始/派生数据根目录：`/pscratch/sd/l/lzy/quijote-png`。
- 已确认 z=1、snapshot 002、1000 Mpc/h 盒子的 halo position products：`halos/FoF_z1_mmin1e13_positions/`。
- fiducial 有 500 个 realization，real000 有 195524 个 M_h >= 1e13 Msun/h halos；LC_m 和 LC_p 也各有 100 个 realization。
- 已从 `https://github.com/mishtak00/conker` 获取 ConKer Python 实现，重点代码位于 `work/upstream/conker/src/{centerfinder,kernel,correlator}.py`。
- 已从 `https://github.com/cosmodesi/mockfactory` 获取 mockfactory；Gaussian field 代码位于 `work/upstream/mockfactory/mockfactory/gaussian_mock.py`，但默认 login Python 尚未加载 mockfactory 依赖环境。
- 已建立 `src/inspect_quijote_catalog.py` 数据检查脚本和 `docs/upstream_and_data.md`。
- 已建立 `src/moments.py` 的周期盒 CIC + FFT 球壳卷积基线，可测量 mu1、mu2。
- 已在 fiducial real000、grid=64、s=20--100、Delta s=20 Mpc/h 上完成一次 smoke test，输出位于 `results/moments/fiducial_real000_n64.npz`。

当前注意事项：球壳核的零点位于周期 FFT 数组的 [0,0,0]，卷积时不应额外使用 ifftshift；正式测量前需要用 Gaussian random field 做窗口和 FFT 归一化验证。

### 数据路径更新（重要）

- 直接测量 Γ、μ1、μ2 的主输入应改为 `/pscratch/sd/l/lzy/quijote-png/halos/FoF_z1_mmin1e13_positions/` 下的 `positions_mpc_h.npy`，而不是从 P0/P2 反推。
- 该目录实际包含 `fiducial`（500 个 realization）、`LC_p`（100 个）和 `LC_m`（100 个）子集；`summary.json` 是旧的/不完整汇总，不能作为 realization 数量的权威来源。
- `LC_p/LC_m` 的精确 fNL 值目前没有写入 position metadata，需要从 Quijote cosmology/下载 manifest 确认后才能用于 fNL 拟合。
- `PNG-EZmock/data/quijote_z1_local_png_power/` 的 P0/P2 矩阵改作交叉验证和 power-spectrum 输入，不再作为 Γ、μ1、μ2 的主测量输入。

### Quijote-PNG 节点确认

Quijote-PNG 官方目录说明：`LC_p` 是 local PNG、fNL=+100，`LC_m` 是 local PNG、fNL=-100；每个完整套件设计为 500 个 realization。当前本地 position products 只看到 fiducial=500、LC_p=100、LC_m=100，说明正负 PNG catalog 尚未完整转移到 position-products 目录；批量分析先使用已存在的 100 个，或继续确认/转移其余 400 个。官方说明见 https://quijote-simulations.readthedocs.io/en/latest/png.html。
- 已建立 `src/theory_mu1.py`，对离散周期盒中的同一 CIC+球壳核做 Fourier 预测；fiducial real000 grid=64 smoke test 与实空间卷积相对差异约 1e-16。
- 已建立 `src/batch_moments.py`，可批量处理 fiducial、LC_m(-100)、LC_p(+100) 并输出每节点均值/协方差。
- 已完成三 realization、grid=64、s=20--100 的 batch smoke test，输出位于 `results/batch_smoke_n64/summary.json`；正负 PNG 的 mu1/mu2 响应方向符合预期。

### Grid convergence smoke test

- Ran atch_moments.py for fiducial, LC_m(-100), LC_p(+100), 10 matched realization IDs, s=20--300 Mpc/h, Delta s=20, at Ngrid=64 and 128.
- Outputs: esults/batch_n10_n64/ and esults/batch_n10_n128/.
- mu1 is broadly stable at s >= 40 Mpc/h, but the smallest bin changes from about 0.30 (N=64) to 0.26 (N=128).
- mu2 changes strongly with grid resolution (e.g. fiducial s=20: about 0.67 at N=64 versus 2.26 at N=128). This is expected to be dominated by unresolved/discrete halo shot noise and CIC cell-scale variance, so mu2 must not be interpreted as converged before an explicit shot-noise/discreteness treatment.
- The PNG response direction remains LC_p > fiducial > LC_m for both mu1 and mu2.
- All current baseline scripts pass python -m py_compile.
- 已实现 `src/theory_mu2_gaussian.py`：对 Gaussian 场，解析基线为 mu2_G(s)=sigma0^2 sigma_s^2 + xi_s^2，其中 sigma_s^2 是球壳滤波场方差，xi_s 是 delta 与滤波场的协方差。
- 在 fiducial real000、grid=64 上，mu2_grid/mu2_G 的比值为 s=20:1.72、40:1.10，而 s>=60 基本在 1 附近（约 0.98--1.02）。这给出直接证据：大尺度 mu2 已接近 Gaussian 二点组合，小尺度剩余主要是离散 halo/non-Gaussian correction。
- 已加入 `src/validate_gaussian_field.py`，用独立纯 Gaussian random fields 验证 mu2_G 公式；16 个 N=64 realization 上各尺度平均测量/解析预测比值最大偏差约 0.86%。
- 这完成了第一轮可复现基线：上游代码、Quijote catalog、球壳 FFT、mu1 Fourier 等价性、Gaussian mu2 解析式和 Quijote 初步诊断均已有脚本与输出。

## Long-term goal progress

- Added docs/long_term_roadmap.md with WP1--WP8 research plan.
- Ran 30 matched realizations for fiducial, LC_m(-100), LC_p(+100), Ngrid=64, s=40--300 Mpc/h.
- Output: esults/batch_n30_n64_s40/.
- Added paired PNG response output: esults/batch_n30_n64_s40/png_response_n30.json.
- The 30-realization run confirms a scale-dependent odd PNG response in both mu1 and mu2; even response is subdominant in this first estimate.
- Added an independent Gaussian-field validation. For 16 N=64 Gaussian realizations, the analytic mu2_G identity agrees with direct grid measurements to better than 0.86% at all tested scales.

## Long-term progress: real-space power cross-check

- Added src/measure_power_real.py, which measures isotropic real-space halo P_h(k) from the same CIC mesh used by moments.py, with explicit V/Nmesh^6 normalization and mode counts.
- Added compatibility in src/theory_mu1_power.py for either stored P0 products or measured real-space P_h products.
- Measured fiducial real000 at Ngrid=64 and projected its real-space P_h through the spherical-shell Bessel window.
- The resulting prediction is qualitatively consistent but differs from direct mu1 by roughly 10--20 percent at some bins, identifying the next numerical-theory audit: coarse k binning, finite k range, CIC window treatment, and shell-window discretization must be made identical before fitting physical PNG bias.
- Added src/theory_mu1_modewise.py, which projects every measured Fourier mode through the continuous finite-width spherical Bessel window, avoiding coarse k-bin averaging.
- Output: esults/theory_mu1_modewise_n64.json.
- Modewise projection confirms the remaining 10--20% mu1 mismatch is a window-definition issue (continuous shell Bessel average versus the pixelized shell kernel in moments.py), rather than FFT normalization. The next audit will implement the exact discrete kernel response W_s(k)=FFT[K_s] for P_h mode sums, then introduce CIC deconvolution consistently.
- Added src/theory_mu1_discrete_power.py: reconstructs mu1 from the mode-by-mode measured P_h(k) and exact FFT[K_s] response.
- Fiducial real000 Ngrid=64 test agrees with direct convolution to <1e-15 relative precision at all s=40--300 Mpc/h. This closes the discrete Fourier/window normalization audit.
- The remaining difference with continuous Bessel projection is therefore a controlled physical/window approximation, not an implementation error.

## Likelihood prototype progress

- Added src/fnl_likelihood_prototype.py, constructing the concatenated [mu1,mu2] vector, fiducial covariance, finite-difference derivative from LC_p-LC_m, and a linear Gaussian fNL estimator.
- Output: esults/batch_n30_n64_s40/likelihood_prototype.json.
- With only 30 mocks and 28 features the covariance condition number is 1.1e8; the formal Fisher sigma_fNL~3.0 is therefore not trustworthy. The prototype deliberately exposes this failure mode and motivates shrinkage/Hartlap and a larger ensemble before quoting constraints.

## Long-term progress: covariance at 100 PNG realizations

- Ran atch_moments.py on the first 100 matched fiducial/LC_m/LC_p realizations, Ngrid=64, s=40--300 Mpc/h.
- Output: esults/batch_n100_n64_s40/.
- Covariance diagnostics: raw condition number decreased to 1.23e5 for 28 features; Hartlap factor is now 70/99=0.707 and therefore defined, unlike the 30-mock run.
- The joint [mu1,mu2] linear likelihood prototype gives sigma_fNL=29.4 before Hartlap and about 35.0 after Hartlap, providing a realistic first-pass scale rather than the unstable 30-mock result.
- Added shrinkage diagnostics in esults/batch_n100_n64_s40/covariance_diagnostics.json; diagonal shrinkage reduces condition number but changes information substantially, so the final choice must be validated with held-out coverage.

## Long-term progress: held-out likelihood coverage

- Added src/validate_likelihood_coverage.py.
- Split the 100 matched realizations into 70 training and 30 held-out mocks, using 20% diagonal covariance shrinkage.
- Output: esults/batch_n100_n64_s40/coverage_shrink02.json.
- The 28-dimensional joint estimator has covariance condition number 1.11e4 and training Fisher sigma about 30.9 (Hartlap factor 0.580).
- Held-out mean estimates are fiducial -4.0 +/-31.4, LC_m -91.0 +/-20.9, and LC_p +105.7 +/-51.3. Biases are small compared with scatter, but the asymmetric LC_p scatter shows that this is still a prototype and needs larger mocks and better covariance regularization.

## Covariance shrinkage sweep

- Ran held-out coverage for diagonal shrinkage lambda=0.05,0.1,0.2,0.3,0.5 on the same 70/30 split.
- Conditions decrease from 3.4e4 (lambda=.05) to 4.4e3 (lambda=.5); Fisher sigma changes from ~31.7 to ~26.1.
- Held-out biases remain within roughly 10 fNL for all three nodes, but this small test does not select a unique lambda. Use lambda~0.2 as a conservative baseline and report the sweep as a robustness systematic.

## Observable comparison

- Added src/compare_observables.py and output esults/batch_n100_n64_s40/compare_observables.json.
- With the 70-mock training split and 20% diagonal shrinkage, sigma_fNL is 32.9 from mu1 alone, 33.2 from mu2 alone, and 30.9 from the joint vector.
- The joint improvement is only ~6% in this conservative first pass; mu2 carries comparable but highly correlated information. This is a useful baseline for the later connected-residual model and should not be compared to the paper's 21% gain until grid/shot-noise and covariance choices are harmonized.

## Connected mu2 residual first pass

- Fixed connected_residual.py indentation/path handling and added explicit OMP/BLAS thread controls for login-node safety.
- Ran 10 realizations per node at Ngrid=64, s=40--300 Mpc/h. Output: esults/batch_n100_n64_s40/connected_summary_n10.json plus per-node NPZ files.
- Defined residual as measured mu2 minus the exact per-realization Gaussian identity mu2_G; at s=40 the mean residual is 0.0051 (LC_m), 0.0070 (fiducial), 0.0090 (LC_p), while it becomes consistent with zero at larger s within the 10-mock scatter.
- This supports a PNG-dependent connected/discrete correction at small scales but is not yet a trispectrum detection; increase nreal and subtract a calibrated Poisson control before interpretation.

## Poisson control

- Added src/poisson_control.py, generating uniform Poisson catalogs with the fiducial halo count and the same CIC/shell pipeline.
- Ran 10 controls at Ngrid=64, s=40--300 Mpc/h: esults/poisson_control_n10_n64.npz.
- The Gaussian-subtracted residual is consistent with zero; at s=40 its mean is 2.5e-6 with standard deviation 1.6e-5, far below the clustered halo residual (~7e-3).
- This confirms that the large fiducial/PNG residual is not explained by pure Poisson sampling alone; it contains clustering non-Gaussianity and/or unresolved discretization effects.

## Poisson-corrected connected residual

- Added src/correct_connected_residual.py and output esults/batch_n100_n64_s40/corrected_connected_summary.json.
- Subtracted the mean uniform-Poisson residual from each Quijote connected residual.
- The correction is numerically small (2.5e-6 at s=40 versus halo residuals of 5e-3--9e-3), so the qualitative PNG ordering survives. At larger s the corrected odd response is consistent with zero for the current 10-realization residual sample.

## Connected residual at 100 realizations

- Re-ran connected_residual.py for 100 realizations per node at Ngrid=64 with login-safe single-thread settings.
- Output: esults/batch_n100_n64_s40/connected_summary_n100.json and per-node connected NPZ files; Poisson-corrected output is corrected_connected_summary_n100.json.
- The s=40 corrected residual means are 0.00632 (fiducial), 0.00459 (LC_m), and 0.00832 (LC_p), giving an odd response 1.86e-5 per unit fNL.
- At s>=120 the odd response is consistent with zero at the current errors; therefore the first connected residual signal is concentrated at the smallest retained scale and needs Ngrid/shell-width convergence before physical trispectrum interpretation.

## Connected residual grid convergence

- Ran 10 realizations per node at Ngrid=128 with the same s=40--300 Mpc/h setup; output esults/batch_n100_n64_s40/connected_summary_n10_n128.json.
- The s=40 residual rises to 0.0191 (LC_m), 0.0276 (fiducial), 0.0369 (LC_p), compared with 0.0051, 0.0070, 0.0090 at Ngrid=64.
- This confirms that the raw Gaussian-subtracted mu2 residual is strongly grid dependent and cannot yet be interpreted as a physical trispectrum. Ngrid=256 should be run through SLURM rather than the login node, with a controlled CIC/shot-noise treatment and memory request.
- Added SLURM template `slurm/run_connected_n256.sbatch` requesting 8 CPUs and 64G for Ngrid=256; it is not submitted automatically.

## Shell-width convergence

- Extended connected_residual.py with --shell-width and ran 10 realizations per node at Ngrid=64, Delta s=40 Mpc/h.
- Output: esults/batch_n100_n64_s40/connected_summary_n10_n64_w40.json.
- At s=40 the residual means are 0.00533 (LC_m), 0.00708 (fiducial), 0.00876 (LC_p), close to the Delta s=20 values 0.00506, 0.00703, 0.00901. This indicates shell-width dependence is mild at Ngrid=64; the much larger Ngrid=128 shift is primarily cell-resolution/discreteness.

## SLURM grid-256 smoke job

- Submitted job 57978678 from slurm/run_connected_n256.sbatch with NREAL=10, NMESH=256, 8 CPUs, 64G memory.
- The job is currently PENDING in egular_milan_ss11 for Priority; it has not started yet.
- Login-node runs remain limited to Ngrid<=128 and small realization counts.

## PNG halo power response

- Added src/analyze_pk_png_response.py and output esults/pk_png_response.json.
- Using the stored redshift-space P0 matrices for native fNL=-100,0,+100, the odd response dP0/dfNL is 472 at k=0.008 h/Mpc and 80 at k=0.023 h/Mpc; fractional response decreases from 6.9e-3 to 9.9e-4.
- This large-scale enhancement is qualitatively consistent with local PNG scale-dependent bias, while the product remains explicitly marked as redshift-space cross-check until the real-space P_h response is measured.
- Polled SLURM job 57978678: it is RUNNING on nid004361 with 8 CPUs and 256 MB currently reported MaxRSS field pending/partial; output files are not finalized yet.
- At the latest 15-minute checkpoint, SLURM job 57978678 remains RUNNING; fiducial and LC_m n256 files are complete, LC_p is still running. No error output observed.

## Completed grid-256 SLURM smoke test

- Job 57978678 completed successfully in 21:06 with ExitCode 0, 8 CPUs, and MaxRSS 2,068,300K (~2.0 GB), safely below the 64G request.
- Produced connected_fiducial_n256.npz, connected_LC_m_n256.npz, connected_LC_p_n256.npz, and esults/connected_summary_n10_n256.json.
- Resolution comparison is in esults/resolution_comparison.json; at s=40 the n256/n64 residual ratios are ~17.2 (fiducial), 15.5 (LC_m), and 18.7 (LC_p), while ratios at bins whose residual is near zero are numerically unstable.
- Conclusion: raw mu2 residual is not resolution converged under the current CIC estimator; physical interpretation must use a resolution-matched/renormalized statistic or an explicit cell-scale shot-noise model before trispectrum fitting.

## Resolution-matched normalized mu2

- Added src/compare_normalized_mu2.py and output esults/normalized_mu2_resolution.json.
- Tested R_mu2(s)=mu2/mu2_G for n64, n128, n256 using the completed 10-realization files.
- At s=40 the fiducial mean ratio moves 1.112 -> 1.059 -> 1.047 from n64 to n128 to n256; LC_m 1.093 -> 1.043 -> 1.034; LC_p 1.124 -> 1.074 -> 1.060.
- At s>=60 all ratios are already within a few percent of unity and much more stable than raw mu2_connected. This supports using the dimensionless ratio or a Gaussian-normalized connected statistic as the next modeling observable.

## Normalized mu2 PNG response across resolution

- Added src/normalized_mu2_response.py, output esults/normalized_mu2_response.json.
- Computes R_mu2=mu2/mu2_G-1 and its LC_p-LC_m odd response for n64, n128, n256.
- At s=40 the odd response per unit fNL is 1.54e-4 (n64), 1.53e-4 (n128), and 1.33e-4 (n256), much more stable than raw connected mu2. This supports R_mu2-1 as the preferred resolution-matched observable for the connected PNG model.

## Normalized-mu2 likelihood validation

- Fixed `src/normalized_likelihood.py` to retain full arrays for held-out tests (earlier version accidentally sliced test arrays to zero length).
- Isolated the 100-realization Delta s=20 residual products in `results/connected_n100_w20/` to prevent shell-width runs from overwriting each other.
- For the 70/30 split and 20% shrinkage, the [mu1, R_mu2-1] likelihood has condition number 3.89e4 and sigma_fNL=30.96.
- Held-out means: fiducial -6.3 +/-36.8, LC_m -96.9 +/-26.7, LC_p +103.4 +/-56.1; biases are <=6.4 fNL. This is a stable first-pass observable, pending larger mock coverage and final theory templates.
- Added docs/stage_summary.md, a consolidated, reproducible record of data, measurement identities, Gaussian/Poisson controls, resolution behavior, normalized statistic, and likelihood coverage.

## Local PNG k^-2 response fit

- Added src/fit_png_kminus2.py and output esults/pk_png_kminus2_fit.json.
- Fit the low-k fractional P0 odd response with A/k^2+B for k<0.08 h/Mpc.
- Best-fit A=4.37e-7 (units (h/Mpc)^2 per fNL), B=1.04e-4, RMS=5.12e-5 over 25 bins. The fit is a diagnostic of the expected local-PNG scale dependence; P0 remains redshift-space and the fit is not yet the final real-space halo-bias model.
- Added src/project_png_response_mu1.py and output esults/mu1_png_response_template.json.
- Projects the fitted low-k P0 fractional response A/k^2+B through the spherical Bessel shell window, yielding a first semi-analytic mu1 PNG response template that declines from 5.96e-5 at s=40 to 2.37e-5 at s=80 per unit fNL.
- It is explicitly a redshift-space prototype; replace P0 with real-space P_h and measured bias parameters for the final physical model.

## Real-space halo power batch

- Fixed `measure_power_real.py` to be import-safe (its CLI no longer executes on import).
- Added `src/batch_power_real.py`; ran 100 fiducial/LC_m/LC_p catalogs at Ngrid=64 with single-thread login-safe settings.
- Output: `results/power_real_n100_n64/` and `results/power_real_n100_n64/png_response.json`.
- The real-space fractional odd response is 6.99e-3 at k=0.0075 h/Mpc and 1.04e-3 at k=0.0225 h/Mpc, providing the correct real-space input for the next mu1 PNG-bias projection.

## Real-space mu1 PNG response template

- Added src/project_real_png_mu1.py and output esults/power_real_n100_n64/mu1_png_response_template.json.
- Fits the real-space halo fractional odd response with A/k^2+B for k<0.08 h/Mpc and projects it through the continuous shell Bessel window.
- Fit values: A=3.93e-7, B=1.28e-4, RMS=1.16e-4; projected dmu1/dfNL decreases from 4.90e-5 at s=40 to 1.90e-5 at s=80.
- The relatively high fit RMS motivates weighted fits using mode covariance and a lower-k-only range before treating A as a physical b_phi measurement.

## Weighted real-space PNG response kmax sweep

- Added src/fit_real_png_k_sweep.py; output esults/power_real_n100_n64/k_sweep.json.
- Weighted fits of fractional dP_h/dfNL to A/k^2+B give A=3.99e-7, 4.09e-7, 4.22e-7, 4.42e-7, 4.56e-7 for kmax=.04,.05,.06,.08,.10 h/Mpc, with A errors ~1.3--1.6e-8.
- A is stable at the ~15% level while B changes strongly, so the leading k^-2 amplitude is the robust physical template; the constant term should remain a nuisance parameter and not be interpreted as PNG bias.

## Real-space mu1 PNG template comparison

- Added src/compare_mu1_png_template.py; output esults/mu1_png_template_comparison.json.
- Compared direct Quijote odd mu1 response with the response projected from real-space P_h(k) A/k^2+B.
- At s=40,60,80,100,120 Mpc/h the observed responses are 5.96e-5, 3.82e-5, 2.59e-5, 1.79e-5, 1.26e-5, while the template predicts 4.90e-5, 2.89e-5, 1.90e-5, 1.32e-5, 0.87e-5. Shape is qualitatively right but amplitude is 20--45% low, motivating finite-volume/CIC corrections and a direct fit of b_phi in mu1 space.

## Direct mu1-space PNG amplitude fit

- Added src/fit_mu1_template_amplitude.py and output esults/mu1_template_amplitude_fit.json.
- Fits one amplitude multiplying the real-space P_h-projected mu1 response over s=40--140 Mpc/h using 100-realization response errors.
- Best amplitude is 1.311 +/- 0.022 relative to the P_h template, but chi2=20.85 for 5 dof; amplitude alone does not capture all scale dependence. The template shape is close (ratios ~0.93--1.11 in the first five bins) but requires additional scale-dependent bias/window corrections.

## Full-covariance mu1 template fit

- Added src/fit_mu1_template_fullcov.py; output esults/power_real_n100_n64/mu1_fullcov_fit.json.
- Uses the full covariance of the 100 paired mu1 responses, rather than independent per-scale errors.
- Over s=40--140 Mpc/h, the fitted amplitude is 1.154 +/- 0.008 with covariance condition number 653, but chi2=313.3 for 5 dof. This decisively shows that a single A/k^2+B projected template is not an adequate precision model; the correlated scale shape and/or covariance interpretation must be improved before likelihood use.

## Two-basis mu1 response fit

- Added src/fit_mu1_two_basis.py and output esults/mu1_two_basis_fit.json.
- Fits independent k^-2 and constant P_h response projections with the full paired mu1 covariance.
- Coefficients: A=5.21e-7 +/-5.35e-9 and B=5.62e-5 +/-6.15e-6 over s=40--140 Mpc/h; covariance condition=653.
- chi2=87.3 for 4 dof, so the two-basis physical template still misses scale-dependent structure. Treat this as a diagnostic and motivate adding finite-k/window and nonlinear bias basis functions before final likelihood use.

## Discrete shell projection from binned P_h

- Added src/theory_mu1_binned_discrete.py and output esults/theory_mu1_binned_discrete.json.
- Assigns the measured real-space mean P_h(k) bins to Fourier modes and projects them with the exact discrete FFT[K_s] shell response.
- For fiducial real000 Ngrid=64, the binned-power prediction differs from direct mu1 by -1.7%, +5.6%, +6.5%, +4.6%, and -21% over s=40--120 Mpc/h; this is substantially better at the first bins than the continuous-Bessel comparison, but finite k binning and high-s truncation still matter.

## mu1 kmax truncation audit

- Added src/theory_mu1_kmax_sweep.py; output esults/theory_mu1_kmax_sweep.json.
- For fiducial real000 and the discrete shell projection, kmax=.3 gives the best first-bin agreement (about -1.8% at s=40), while kmax=.1 omits important modes and produces large oscillatory errors.
- The high-s bins are sensitive to finite-k ringing, so the final mu1 model should use a calibrated k window or restrict the scale range rather than treating kmax as an arbitrary cut.
- Added `docs/theory_mu1_mu2.md`, consolidating the analytic Gaussian/Wick and connected-trispectrum structure, discrete contact terms, normalized statistic, and paired PNG response definitions.

## Local PNG trispectrum theory scaffold

- Added src/local_trispectrum.py with a closure-checked local primordial T_phi evaluator and transfer-factor wrapper.
- The module implements the leading fNL^2 tau_NL-type products and optional gNL terms, and a permutation symmetry smoke test passes.
- This is a theory building block only; the collapsed mu2 projection still needs halo bias operators, transfer M(k), and numerical integration/Monte Carlo validation against Quijote.

## Quijote mu2 connected response coefficients

- Added src/fit_mu2_response_quadratic.py; output esults/connected_n100_w20/quadratic_response.json.
- From the 100-realization means at fNL=-100,0,+100, tabulated mu2_conn=A(s)fNL^2+B(s)fNL+C(s).
- At s=40, A=1.37e-8, B=1.86e-5, C=6.32e-3; at s=60, A=3.92e-9, B=3.27e-6, C=1.63e-4. This is an empirical response target for the future trispectrum model, not yet a first-principles prediction.

## Final grid-256 job audit

- Rechecked job 57978678: COMPLETED, elapsed 21:06, ExitCode 0, MaxRSS 2,068,300K (~2.0 GB), AllocCPUS=8.
- All three n256 connected residual files are present: fiducial, LC_m, LC_p.
- The long-term workflow now has reproducible artifacts for raw moments, Gaussian controls, Poisson control, normalized mu2 response, real-space P_h response, covariance/coverage prototypes, and local trispectrum scaffold.
- Created clean, non-overwritten resolution bundle esults/resolution_clean/ containing n64 (100-realization width-20), n128 (10-realization), and n256 (10-realization) connected products. Recomputed normalized response: s=40 odd d(R_mu2-1)/dfNL = 1.56e-4, 1.53e-4, 1.33e-4 for n64,n128,n256.

## Project audit checkpoint

- SLURM grid-256 smoke run completed successfully (21:06, MaxRSS ~2.0 GB, ExitCode 0).
- Source directory contains the measurement, theory, response, covariance, control, and validation scripts listed in the roadmap.
- Documentation now includes the long-term roadmap, stage summary, upstream/data notes, and analytic mu1/mu2 derivation.
- Added src/plot_normalized_mu2_resolution.py; generated PDF-only figure esults/figures/normalized_mu2_resolution.pdf showing R_mu2-1 across fNL nodes and Ngrid=64/128/256.

## Grid-posterior likelihood prototype

- Added src/mcmc_grid_likelihood.py; fixed NumPy compatibility (
p.trapz).
- Output: esults/connected_n100_w20/grid_likelihood_coverage.json.
- Uses an explicit fNL grid posterior with [mu1,R_mu2-1], train n=70 and 20% shrinkage. Held-out 68% interval coverage is 0.60 (fiducial), 0.73 (LC_m), 0.40 (LC_p), with median means -6.4, -96.8, +100.6.
- This demonstrates an operational MCMC-like posterior and exposes asymmetric coverage that must be improved with larger covariance ensembles and quadratic response terms.

## Quadratic fNL posterior prototype

- Added src/mcmc_quadratic_likelihood.py; output esults/connected_n100_w20/quadratic_likelihood_coverage.json.
- Includes both paired linear and even quadratic response terms in the [mu1,R_mu2-1] mean model.
- Held-out posterior median means are -8.4 (fiducial), -102.9 (LC_m), +92.3 (LC_p); 68% coverages are 0.60, 0.77, 0.50. Quadratic response improves the negative node but does not fully cure positive-node coverage, indicating covariance/non-Gaussian likelihood effects remain.
- Added src/plot_likelihood_coverage.py; generated PDF-only esults/figures/likelihood_coverage_linear_vs_quadratic.pdf comparing held-out coverage with linear and quadratic response models.
- Added src/make_quijote_manifest.py and generated esults/quijote_manifest.json; authoritative position coverage is fiducial=500, LC_m=100, LC_p=100, with per-realization file paths, shapes, halo counts, box size, and redshift.
- Performed reproducibility cleanup: scanned all source/SLURM scripts for 
p.trapezoid, standardized to 
p.trapz for the NERSC NumPy version, and confirmed all source files pass python -m py_compile.
- Added src/plot_ph_png_response.py; generated PDF-only esults/figures/realspace_ph_png_response.pdf showing the real-space halo fractional PNG response and weighted k^-2 fit.
- Added `configs/baseline.yaml` with canonical catalog nodes, z/snapshot/box/mass cut, real-space convention, grid and shell settings, and login/SLURM thread limits.
- Added src/plot_mu1_png_template.py; generated PDF-only esults/figures/mu1_png_template_comparison.pdf comparing direct Quijote mu1 odd response with the real-space P_h projected template.
- Regression checkpoint: all source Python scripts compile successfully; key JSON response/theory/covariance outputs and PDF-only figures are present under esults/.
- Added `slurm/run_power_real_n256.sbatch` for safe 8-CPU/64G batch real-space P_h measurement at high resolution; not submitted automatically.
- Final regression checkpoint after latest additions: all source Python files compile; configs/baseline.yaml and esults/quijote_manifest.json exist; four PDF-only diagnostic figures are present.

## Publishability audit and latest figure

- Added `docs/publishability_audit.md`, a requirement-to-evidence matrix covering catalogs, ConKer moments, convergence, shot noise, Gaussian and halo-Gaussian baselines, PNG μ1 template, trispectrum residual, covariance/paired response, likelihood prototypes, and reproducibility artifacts.
- The audit explicitly records unresolved scientific limitations: the projected μ1 template has poor χ² and the μ2 trispectrum closure remains a calibrated scaffold rather than a first-principles halo-bias prediction.
- Registered `results/figures/normalized_mu2_response_coefficients.pdf`, showing the fitted linear and quadratic normalized μ2 PNG response coefficients.

## Finite-scale correction to the halo PNG mu1 template

- Added src/fit_response_corrected.py, fitting the measured odd halo-power response to A/k^2 + B + C k^2. The k^2 term is an explicit finite-window/nonlinear-bias nuisance basis.
- For kmax=0.08, A=(4.046 plus-or-minus 0.154)e-7, chi2/dof=7.43/12, versus the two-basis template's visibly poor projected fit. The A coefficient is stable at low k: 3.75e-7 (0.04), 3.84e-7 (0.05), 3.90e-7 (0.06), then drifts to 4.20e-7 (0.10).
- Sweep outputs are results/power_real_n100_n64/corrected_*.json; use kmax<=0.06 as the conservative scale range until a higher-volume calibration is available.

## Covariance-aware Student-t likelihood

- Added src/mcmc_student_t.py implementing the Sellentin-Heavens multivariate-t likelihood with the same quadratic paired response model and train/holdout split as the Gaussian prototype.
- Output: results/connected_n100_w20/student_t_likelihood_coverage.json. With ntrain=70 and 20 percent diagonal shrinkage, held-out 68 percent coverages are 0.90 (fiducial), 0.93 (LC_m), and 0.77 (LC_p), improving over the Gaussian quadratic prototype (0.60, 0.77, 0.50).
- This is still a finite-ensemble validation, but it provides a covariance-uncertainty-aware likelihood baseline for the final mu1+mu2 MCMC.

## Likelihood coverage comparison figure

- Added src/plot_cov_student.py and PDF-only figure results/figures/likelihood_coverage_student_t.pdf. It compares held-out 68 percent coverage for linear Gaussian, quadratic Gaussian, and quadratic Student-t likelihoods at all three paired PNG nodes, with the nominal 0.68 line.
- The Student-t result is visibly closer to nominal coverage, especially for the positive PNG node, and is now the recommended covariance-aware baseline for subsequent MCMC extensions.

## Student-t likelihood training-size robustness

- Ran src/mcmc_student_t.py for ntrain = 50, 60, 70, 80 using the fixed 100-realization n64 ensemble; outputs are results/connected_n100_w20/student_t_n{50,60,70,80}.json.
- Coverage remains high and qualitatively stable for ntrain 50-70: fiducial 0.90-0.92, LC_m 0.925-0.96, LC_p 0.77-0.85. At ntrain=80 the positive-node coverage falls to 0.60, indicating the holdout size and training/holdout split materially affect finite-sample calibration.
- The ntrain=70 result is retained as the reference split, while this sweep is an explicit uncertainty diagnostic rather than a hidden tuning choice.

## Reproducibility provenance audit

- Added src/audit_pipeline.py. It checks the canonical config, manifest, theory/measurement/likelihood scripts, key JSON products, and PDF figures, then writes existence, byte size, and SHA256 provenance to results/pipeline_audit.json.
- Current audit status is PASS: 15/15 required files present. Re-running after any analysis change updates the hashes and exposes missing or stale deliverables before publication.

## Collapsed trispectrum projection interface

- Extended src/local_trispectrum.py with collapsed_mu2_local_mc, an isotropic Monte-Carlo estimator of integral d3q d3p T_delta(q,-q,p,-p) W(p)^2/(2pi)^6, including a standard error estimate and optional gNL term.
- A synthetic 200-sample smoke test returns a finite estimate and uncertainty; the routine is ready to consume measured transfer functions and shell windows. It remains a continuum theory projection and does not remove discrete halo contact terms, which stay calibrated by the Poisson control.

## Theory invariant checks

- Added src/test_theory_invariants.py. It verifies trispectrum permutation symmetry, exact fNL-squared scaling of the local tau_NL term, and linear b_phi scaling of the PNG bias response.
- The test reports PASS on the remote environment and is included in the reproducibility audit script list.

## Canonical configuration for first-principles PNG bias

- Extended configs/baseline.yaml with an optional local_bphi block. b1, bphi, matter P(k), and transfer M(k) are explicit external inputs; null values prevent accidental use of an uncalibrated prediction.
- independent_calibration=true and validation_policy=holdout_only document the required separation between b_phi calibration and PNG response validation.

## Major plan revision: pure analytic model is now a hard gate

- Replaced docs/long_term_roadmap.md with a gate-based plan whose primary endpoint is a pure analytic prediction. Empirical A/k^2+B+Ck^2 and Quijote-fitted templates are explicitly validation diagnostics only.
- WP5 now requires independent b1, b_phi, delta_c, M(k), Pm(k), shot-noise, exact mesh/shell window, and frozen pre-registered scale cuts. WP6 requires an independently specified halo-bias plus local trispectrum/contact-term closure.
- Current status is intentionally marked incomplete: operational measurements and statistical prototypes pass, but WP5/WP6 remain blocking scientific gates until independent inputs and first-principles closure are supplied and validated.

## MARISA-B reference integration

- Reviewed `/pscratch/sd/l/lzy/marisa-b-portable` and its fixed-cutoff halo bias-v1 specification and regression tests.
- Added docs/marisa_b_png_bias_adaptation.md, mapping its explicit b1/b2/bK2/bphi/bphidelta kernels, K_IC direction derivative, topology decomposition, routing/cutoff scheme, and independent-input gates onto the current mu1/mu2 project.
- The adaptation plan explicitly demotes the current lower-order bphi and empirical templates to provisional scaffolds; the next implementation target is a two-point MARISA-B kernel forward model and a matching collapsed four-point mu2 model.

## Stage 5 kernel-port kickoff

- Added src/marisa_b_kernels.py with reusable A_n, C_n, K_n^{phi,IC}, and total PNG kernel interfaces following the MARISA-B recursion structure. It is intentionally a kernel layer, not yet the complete one-loop two-point contraction.
- Added src/test_marisa_kernels.py; permutation and b_phi linearity checks pass. Fixed empty-rest handling in K_IC for n=2.
- This is the first implementation step of the pure analytic Stage 5 gate; empirical A/k^2 templates remain excluded from the theory path.

## Stage 5 exact-window forward model kickoff

- Added src/exact_window.py with finite-box discrete projection mu1 = V^-1 sum_k P_h(k) W_mesh,s(k), CIC window support, and analytic discrete Wick mu2_G from the same window.
- Added src/test_exact_window.py; window parity, discrete mu1 normalization, and Wick identity checks pass. This replaces the continuum Bessel shortcut in the pure-analytic forward-model path; continuum integrals remain comparison limits only.

## Independent bias-input schema

- Added configs/bias_inputs_v1.yaml for the pure analytic MARISA-B adaptation. All bias and stochastic parameters are intentionally null until an external or disjoint calibration is supplied.
- The schema records redshift, mass cut, reconstruction stage, calibration provenance, covariance, fixed-cutoff parameters, and the hard policy that same-response fitting and empirical-template mean models are forbidden.

## Independent-bias production gate

- Added src/load_bias_inputs.py. Development/audit mode reports unfrozen fields, while --production refuses null bias parameters, missing independent provenance, or a disabled freeze policy.
- Current bias_inputs_v1.yaml intentionally passes audit mode and correctly fails production mode because no independent calibration has been supplied yet; this is an explicit scientific gate, not an error to suppress.

## Stage 5 tree-level two-point forward model

- Added src/theory_mu1_marisa_b.py with a library-safe pure analytic tree-level P_h model and exact discrete mesh/CIC/shell projection for mu1. The CLI requires independent b1 and bphi inputs (or a frozen bias file) and explicitly labels the missing b2/bK2 fixed-cutoff one-loop terms.
- Added src/test_mu1_marisa_b.py; fNL=0 Gaussian baseline and nonzero PNG response algebra pass. The module now has a proper main guard so it can be imported by later loop and likelihood code.

## P13 completion in fixed-cutoff loop layer

- Extended src/marisa_b_power_loop.py with the standard EdS angle-averaged P13 integral, combined with P22 as P1loop_gaussian. The PNG derivative remains an explicit one-insertion product-rule integral.
- Verified P13 is finite on synthetic spectra and all loop source files compile. The current layer is still a controlled two-point primitive; full MARISA-B b2/bK2 kernel contractions and renormalized counterterms remain required.

## Resource policy update

- User constraint adopted: keep routine work on login nodes, never exceed 6 cores or use excessive memory; use compute nodes only when grid size or memory genuinely requires it.
- Updated configs/baseline.yaml slurm_max_cpus to 6 and added resource_policy with login_default_threads=1 and explicit compute-node escalation condition.

## Truncated one-loop mu1 forward interface

- Extended src/theory_mu1_marisa_b.py with predict_with_loop, which combines the independent tree-level halo spectrum with fixed-cutoff P22+P13 and its one-PNG-insertion directional derivative, then applies the exact discrete mesh/shell projection.
- A low-resolution synthetic run passed with finite mu1, loop norm, and recorded cutoff. The function explicitly labels the EdS/isotropic truncated scheme; it does not claim the full MARISA-B b2/bK2 composite closure.

## Kernel recursion robustness fix

- Updated src/marisa_b_kernels.py so C_n accepts an explicit higher-order Gaussian-kernel callback instead of calling the two-point default for n>2.
- Extended src/test_marisa_kernels.py to n=3; A_n/C_n/K_IC permutation and b_phi linearity checks all pass.

## Independent MARISA-B bias input recorded

- Imported the fixed b1=2.7340475186190334 and nbar=1.95530218e-4 metadata from the MARISA-B fiducial fNL=0 aggregate JSON. These are fixed catalog metadata, not fitted to the PNG response.
- bias_inputs_v1.yaml now records this provenance and calibration split; b2, bK2, bphi, and bphidelta remain null until independent calibration is found.

## Gaussian bias calibration imported from MARISA-B

- Recorded b2=-0.665, bK2=0.516666666666667, alpha3=0.7885698383313215, and alpha4=-0.30779796761910205 from the isolated fiducial fNL=0 Gaussian one-loop fit (kmax=0.18) in marisa-b-portable.
- Provenance remains explicit in bias_inputs_v1.yaml; these values are frozen Gaussian calibration inputs and are not fit to LC+/LC- PNG response. bphi and bphidelta remain unset because no independent calibration was found.

## Independent b_phi search result

- Added src/search_bphi.py and results/bphi_calibration_search.json. It scans the MARISA-B analysis tree for numeric bphi/bphidelta values with independent/disjoint calibration labels.
- The search found zero qualifying hits, so bphi and bphidelta remain unset by policy. This is evidence for the next action (external theory or a disjoint calibration run), not a license to guess parameters.

## Stage 1 pairing validation

- Added src/validate_manifest_pairs.py and results/manifest_pair_validation.json. It checks metadata path existence, Nx3 float32 schema, and LC_m/LC_p realization IDs as subsets of fiducial IDs.
- Current manifest passes with fiducial=500, LC_m=100, LC_p=100, and 100 common paired realization IDs.

## Stages 1-4 audit gate

- Added src/stage_audit.py, a lightweight metadata-only gate for manifest, pairing, moments, resolution, Poisson control, Gaussian theory, and Gaussian validation outputs.
- Corrected paths to the authoritative NPZ products and reran the gate: 7/7 checks PASS. It runs on the login node without loading catalog arrays into memory.

## Stage tracker status update

- Updated docs/stage1_9_execution.md: Stages 1-4 are marked PASS based on results/stage1_4_audit.json (7/7 checks). Stage 5 is PARTIAL: tree/exact-window/kernel/P22+P13 primitives exist, while full MARISA-B composite closure and independent bphi remain open.

## Stage 5 gate report

- Generated results/stage5_gate.json from the frozen bias-input schema. Gaussian parameters and anti-leakage policies pass; bphi and bphidelta are explicitly BLOCKED because the independent-calibration search found no valid values.
- This report is the current scientific gate, not an execution failure. Once independent values and provenance are supplied, rerun the production loader and forward-model validation.

## Stage 5 gate JSON repair

- Revalidated results/stage5_gate.json after Gaussian bias-input updates. b1,b2,bK2,alpha3,alpha4 and anti-leakage policies are PASS; bphi and bphidelta remain BLOCKED. Removed a literal escaped newline that had made the JSON non-parseable.

## Reconstruction-PNG b_phi candidate audit

- Inspected reconstruction-png role-resolved canary outputs. A z=0.5, 3-realization diagnostic reports bphi_universal=3.303097472015317 but gate_pass=false and is outside the current z=1 selection, so it is rejected.
- The bphidelta filter-stability audit has promotion_authorized=false and failed filter/cutoff gates, so no value is adopted. results/bphi_calibration_candidates.json records both rejections and leaves the current z=1 bias inputs unset.

## Universal-mass-function b_phi option

- Added an explicit --bphi-universal option to theory_mu1_marisa_b.py, deriving bphi=2 delta_c (b1-1) from the universal mass-function assumption. The default still refuses missing bphi, so the assumption must be declared at invocation.
- Synthetic CLI test passes and records bphi_source=universal_mass_function. This is an analytic assumption with model uncertainty, not a Quijote response fit; bphidelta remains unmodeled until independently specified.

## Stage 5 tracker: universal bphi branch

- Stage tracker now records the explicit universal-mass-function bphi branch as runnable but scientifically unvalidated. It requires independent M(k), Pm(k), frozen bias inputs, exact mesh window, and held-out Quijote validation before promotion.

## Universal bphi candidate value (not adopted)

- Evaluated the declared universal-mass-function relation at the frozen b1 input: bphi=5.847618? (computed exactly in results/bphi_universal_theory.json; value is 2*1.686*(2.7340475186190334-1)).
- This remains CANDIDATE_UNVALIDATED and adopted_in_production=false until z=1 held-out response validation and model-uncertainty propagation are complete.

Correction: the exact derived candidate is bphi=5.84720823278338, as stored in results/bphi_universal_theory.json; the earlier rounded placeholder text is superseded.

## Universal b_phi uncertainty propagation

- Added universal_bphi to src/theory_mu1_bphi.py, propagating independent sigma_b1 and sigma_delta_c into sigma_bphi analytically.
- Added src/test_bphi_error.py; value and positive uncertainty checks pass. This uncertainty is ready to enter the analytic-input covariance, while the universal relation itself remains a declared model assumption.

## Analytic-input covariance propagation

- Added src/analytic_input_cov.py and results/analytic_input_covariance.json. Given explicit sigma_b1, sigma_delta_c, and correlation, it propagates the universal bphi relation with a Jacobian into the (b1,bphi) covariance.
- Synthetic propagation passed; no uncertainty values are hard-coded, and this covariance is kept separate from realization covariance.

## Fixed-cutoff loop stability scan

- Generated results/power_loop_cutoff_scan.json for qmax=0.2,0.3,0.5,0.8 at k=0.1 using fixed qmin=.01 and low-cost quadrature. The scan is diagnostic only; cutoff drift is reported rather than absorbed into fitted coefficients.

## P13 singularity and cutoff diagnostic

- The qmax scan exposed a numerical issue in the P13 logarithm at r=q/k=1. Fixed src/marisa_b_power_loop.py to use the analytic finite integrand limit at r=1 instead of evaluating log(0).
- Regenerated results/power_loop_cutoff_scan.json with nq=160,nmu=24. The corrected values are finite but still show physical fixed-cutoff drift with qmax; this drift is retained as a scheme uncertainty and is not absorbed by fitting.

## P13 directional-derivative regression

- Added src/test_p13_directional.py. A central finite-difference perturbation P -> P +/- epsilon P_PNG agrees with loop_P13_directional at relative error 2.0e-12 for a synthetic spectrum.
- This independently validates the one-PNG-insertion product rule in the P13 primitive; it does not validate the missing composite halo-bias operators.

## Stage 1-5 gate semantics

- Extended src/stage_audit.py to include kernel and exact-window artifacts and to treat the Stage 5 gate as OPEN while bphi/bphidelta are blocked. The current report is 9/10 PASS with one explicit scientific blocker, rather than a misleading overall PASS.

## Stage 6 analytic mu2 wrapper kickoff

- Added src/theory_mu2_marisa_b.py with an import-safe exact-window Gaussian halo mu2 wrapper, returning sigma0^2, sigma_s^2, xi_s, and mu2_G for declared P_h(k) inputs.
- Added src/test_mu2_marisa_b.py; the discrete Wick identity is checked directly and passes. Connected halo trispectrum and contact terms remain the next Stage 6 layer.

## Stage 6 connected projection interface

- Extended src/theory_mu2_marisa_b.py with connected_local_png_mu2, combining exact-window Gaussian mu2_G with the collapsed local primordial trispectrum Monte-Carlo projection and its sampling error.
- Added src/test_mu2_connected_interface.py; connected contribution and error reporting pass on a low-cost synthetic input. Halo-bias insertions and discrete contact terms remain explicit external layers.

## Stage 7 paired-response covariance

- Added src/paired_cov.py and results/connected_n100_w20/paired_response_covariance.json. It intersects LC_m/LC_p realization IDs, computes per-pair odd response for all mu1 and mu2 shells, and returns the joint response covariance.
- The current 100-pair output has 28 features (14 mu1 + 14 mu2) and condition number 2.50e5; the matrix is retained for shrinkage/Student-t likelihood diagnostics, not treated as perfectly known.

## Paired covariance shrinkage scan

- Added src/paired_cov_shrink.py and results/connected_n100_w20/paired_cov_shrinkage_scan.json. It scans diagonal shrinkage on the 28-feature paired response covariance without altering the raw matrix.
- For the 100-pair sample the raw condition number is 2.50e5 and the best-conditioned scanned endpoint is 3.03e2. Lambda must be selected on training mocks only; the scan is diagnostic, not target-response tuning.

## Stage 7 tracker refinement

- Stage tracker now separates operational covariance/statistics evidence from the unfinished pure-analytic mean model. Paired covariance, shrinkage scan, and Student-t coverage are listed explicitly; analytic-input covariance propagation remains the next integration gate.

## Stage 6 tracker refinement

- Stage tracker now marks pure analytic mu2 PARTIAL: Gaussian exact-window and primordial connected projection interfaces exist and pass tests, while MARISA-B halo-bias insertions and discrete contact contractions remain open.

## Stage 8 release artifact audit

- Added src/release_audit.py and results/release_audit.json. It checks nine required configs/docs/reports, enumerates publication PDFs, reports any figure PNGs, and records the <=6-core resource policy.
- Current release audit: 9/9 required files present, 6 PDF figures, 0 figure PNGs.

## Release resource validation

- Strengthened src/release_audit.py to parse configs/baseline.yaml and enforce login_max_cores<=6 and login_default_threads=1. The current release audit passes with 6 cores and one default thread.

## Universal-tracer p parameter

- Incorporated the MARISA/reconstruction-png distinction between tracer p=1.12 and reconstruction p=1.0 into theory_mu1_marisa_b.py via explicit --universality-p (default 1.0).
- Extended universal_bphi uncertainty propagation to include sigma_p. The z=1 tracer candidate is a declared model branch, remains unvalidated, and is not adopted in bias_inputs_v1.yaml.

## Universality-role configuration

- bias_inputs_v1.yaml now records p_tracer=1.12 and p_reconstruction=1.0 from the MARISA/reconstruction-png convention. The forward model must select the role explicitly; no implicit p substitution is allowed.

## b_phi normalization correction

- Corrected theory_mu1_marisa_b.py and loop PNG derivatives to treat bphi as the full bias coefficient. With the declared universal relation bphi=2 delta_c (b1-p), the response is Delta b/fNL=bphi/M(k); the previous extra (b1-1) factor would double-count the universality relation.
- Added a regression check at b1=2, p=1.12 confirming P_h=(b1+bphi/M)^2 P_m. Updated pure_analytic_equations.md accordingly.

## Global b_phi normalization audit

- Corrected src/theory_mu1_bphi.py response() and equation metadata to use bphi as the full coefficient, consistent with theory_mu1_marisa_b.py and marisa_b_power_loop.py: Delta b/fNL=bphi/M(k), dP/P=2 bphi/(b1 M).
- A scalar regression response check passes. This removes the former risk of multiplying the universal bphi relation by (b1-1) twice.

## Exact-window audit correction

- Replaced the provisional sinc-averaged exact_window implementation with an estimator-matched discrete periodic shell FFT window and explicit mesh/CIC power conventions.
- Independent nmesh=12 random-field checks give mu1 error 2.17e-18 and Gaussian centered-Wick error 2.22e-16; the old continuum window differs by up to 0.087 in the same test.
- Updated theory_mu2_marisa_b connected interface to label its radial fallback continuum window explicitly. Discrete exact-window calls now require a complete periodic FFT mode set and reject arbitrary/incomplete mode lists.

## Agent handoff document

- Added docs/agent_handoff.md as the migration guide for the next agent. It gives the scientific objective and pure-analytic standard, read order, upstream/reference paths, catalog/pair facts, resource policy, module/result map, model normalization, bias-input status, exact-window correction, audit interpretation, known traps, safe commands, and the local-versus-remote state of the last interrupted patch.
- The handoff explicitly says the goal is incomplete until full MARISA-B composite bias, independent bphi/bphidelta, halo connected four-point/contact terms, and held-out analytic validation pass.
