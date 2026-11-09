# 与旧版本的对应关系

旧版本（2026-09-06 至 09-11，主要由 AI agent 生成）有两份：

- `/pscratch/sd/l/lzy/byd2pcf`：NERSC 工作根目录。254 个脚本、113 篇 docs、约 1.8 GB 产品。**原样保留，作为归档。**
- 本仓库 `main` 分支（≤ `134a267`）：它的子集，而且漏掉了 92 个脚本（包括 `local_trispectrum.py`、`marisa_b_kernels.py` 等被 import 的模块），所以本身就跑不起来。

2026-11-09 的重整（`cleanup` 分支）从 byd2pcf 出发，保留物理和数值，去掉了审计官僚层。

## 保留并合并的部分

| 新位置 | 旧来源 |
|---|---|
| `momentpng/mesh.py` | `moments.cic_mesh`、`exact_window.{cic_window, mesh_wavevectors}`、`measure_power_real.isotropic_power`、`measure_mode_power` |
| `momentpng/moments.py` | `moments.{shell_kernel, measure}`、`theory_mu2_gaussian.gaussian_mu2_from_field`、`connected_residual` |
| `momentpng/window.py` | `exact_window.{shell_window, mu1_discrete, mu2_gaussian_discrete}` |
| `momentpng/theory/tree.py` | `theory_mu1_marisa_b.predict`、`theory_mu1_bphi.universal_bphi`、`fit_bphi_disjoint_response` 的响应模板 |
| `momentpng/theory/loops.py` | `marisa_b_power_loop`、`halo_kernels`、`halo_p13.halo_P13_bias_collapsed`、`halo_two_point`、`compare_mu1_binned_loops` |
| `momentpng/theory/contact.py` | `discrete_contact_terms`、`analyze_cic_poisson_contact.cic_contact` |
| `momentpng/catalogs.py` | `reconstruct_fof_positions.read_group_tab`、`make_quijote_manifest`、`inventory_bphi_disjoint_catalogs_v2` |
| `momentpng/stats.py` | 各脚本里重复实现的 cov/Hartlap/χ²/GLS（`fit_bphi_disjoint_response.fit_response`、`validate_mu1_nodes`、`audit_b1_pshot_covariance_scan`…） |
| `scripts/measure.py` | `batch_moments`、`batch_power_real`、`connected_residual`、`poisson_control`、`measure_disjoint_png_moments`、`measure_fiducial_disjoint_power`、`build_nbody_baseline`、`load_nbody_nodes` |
| `scripts/fit_b1.py` | `fit_b1_linear_pk`、`fit_disjoint_fiducial_b1{,_v2}`、`audit_b1_pshot_covariance_scan`、`scan_mu1_training_theory_conventions`（b1 部分） |
| `scripts/fit_response.py` | `fit_bphi_training_response`、`fit_bphi_disjoint_response`、`scan_bphi_response_scale_windows` |
| `scripts/validate_mu1.py` | `validate_mu1_nodes`、`validate_mu1_analytic_holdout`、`scan_mu1_training_theory_conventions`（验证部分）、`validate_mu1_shotnoise_variants` |
| `scripts/loop_mu1.py` | `compare_mu1_binned_loops`、`make_loop_*audit`、`make_stage4_loop_cutoff_gate` |
| `scripts/mu2_connected.py` | `analyze_cic_poisson_contact`、`analyze_halo_contact_excess`、`analyze_stage5_scale_stability`、`compare_resolution_mu1_mu2`、`normalized_mu2_response` |
| `scripts/fnl_likelihood.py` | `mcmc_grid_likelihood`、`mcmc_quadratic_likelihood`、`mcmc_student_t`、`compare_observables` |
| `tests/` | `test_exact_window`、`test_discrete_contact_terms`、`validate_gaussian_field`、`test_p13_directional`、`test_halo_p13`、`test_bphi_response_normalization` 的核心断言 |

## 数值回归（2026-11-09）

新代码在同样的输入和同样的方法下，复现了旧产品的结果：

| 量 | 结果 |
|---|---|
| n64 的 μ1、μ2、μ2_G、P_h（三个节点 real000–099，LC± real100–499，Poisson seeds 0–9） | 相对差 ≤ 1e-12 |
| group_tab 读取器重建的位置目录（LC_m real100、fiducial real000） | 逐字节一致 |
| disjoint bφ | 3.74848，χ²/dof = 207.04；窗口 180–240 的 Hartlap χ²/dof = 0.22 |
| 训练集 bφ | 3.7636 |
| 留出集 μ1：universal tree（无 CIC、Pshot=0） | χ²/dof = 253.10 / 367.22 / 185.72 |
| 留出集 μ1：training CIC-both | Hartlap χ²/dof = 1.96 / 4.41 / 2.46 |
| 旧 b1 协方差扫描 | 0.03: 2.6424 / 1.143 … 0.15: 2.8965 / 218.227（用旧方法：在 bin 中心插值 lattice 上的 P_m） |
| loop P22、P13、PNG 响应 | P22 逐位一致；P13 和 PNG 响应相对差 ~1e-14 |
| Student-t 似然 | 中位数 −8.85 / −102.47 / 91.38；旧的单侧指标 0.90 / 0.93 / 0.77 |

## 删除的部分和原因

| 类别 | 例子 | 原因 |
|---|---|---|
| 审计/门控链（约 120 个） | `make_provenance_v69..v88`、`check_main_nersc_alignment_v2..v14`、`release_gate*`、`make_stage_progress_v19..v31`、`assemble_stage8_holdout_report*`、`freeze_manifest*`、`make_completion_audit`、`make_stage*_gate*`、`audit_pipeline`、`stage_audit`、`release_audit` | 自我引用的流程记录，不产生物理结果。provenance 现在由 git commit 加上每个结果 JSON 头部的参数承担 |
| 被取代的经验模板 | `fit_png_kminus2`、`fit_real_png_k_sweep`、`fit_response_corrected`、`project_*_png_mu1`、`fit_mu1_template_*`、`fit_mu1_two_basis`、`fit_mu2_response_quadratic`、`fit_normalized_mu2_response` | A/k² 系列的经验拟合，已被精确窗口加 tree 模型取代；结论记在 findings |
| 连续近似和重复实现 | `theory_mu1{,_power,_modewise,_binned_discrete,_discrete_power,_kmax_sweep}`、`theory_mu2_halo_analytic`、`theory_mu2_gaussian_discrete`、`work/exact_window.py` | 被精确离散投影 `window.py` 取代 |
| 错误或未使用的理论模块 | `local_trispectrum`、`halo_connected_fourpoint`、`theory_mu2_marisa_b`、`audit_primordial_mu2*` | trispectrum 的通道写错，投影也只覆盖 collapsed 构型（见 theory.md §5.1） |
| | `marisa_b_kernels`、`marisa_b_native_kernels`、`marisa_b_higher_kernels` | 没有被任何前向模型使用；`A_kernel` 里还有 `np.math.comb(n,1) if False else 1.0` 这类残留 |
| | `analytic_bias_covariance`、`analytic_input_cov`、`propagate_universal_bias_covariance`、`load_bias_inputs` | 只用于门控链 |
| 一次性检查 | `inspect_*`、`scan_reference_json*`、`search_bphi`、`fix_report`、`update_report_final`、`compare_loop` | 交互式的临时脚本 |
| 绘图 | `plot_*`（约 15 个） | 依赖旧产品路径；需要时按新产品重写 |

旧的 docs（113 篇）中有物理内容的部分，已经浓缩进 `docs/findings.md` 和 `docs/theory.md`。原始任务书在 `byd2pcf/ref/task.md`。
