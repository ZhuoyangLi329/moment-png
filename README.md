# moment-png

对 Quijote local-PNG 的 halo 场做 ConKer 式球壳密度矩 **μ1(s)** 和 **μ2(s)** 的测量，并为它们建立解析或半解析模型。参考文献的做法是在少数几个 fNL 节点上拟合 μ̃ = A fNL² + B fNL + C。本项目想用物理模型来解释矩对 fNL 的响应：bias 参数只能来自独立标定，不能拿同一批 PNG 响应去拟合。

- 样本：Quijote-PNG，z = 1，FoF M_h ≥ 1e13 M⊙/h，实空间，1 Gpc/h 周期盒。fiducial（fNL=0）、LC_m（−100）、LC_p（+100）各 500 个 realization，三者配对。
- 协议：`configs/protocol.yaml`（冻结的 v1）
- 公式和约定：[`docs/theory.md`](docs/theory.md)
- 结果和现状：[`docs/findings.md`](docs/findings.md)
- 和旧版本（`/pscratch/sd/l/lzy/byd2pcf`）的对应关系：[`docs/legacy.md`](docs/legacy.md)

## 结构

```
configs/protocol.yaml      冻结协议：路径、样本、网格、壳、realization 分块、独立 bias 输入
data/                      z=1 线性理论表 (k, P_L, P_phi, M)
momentpng/                 库
  config.py                协议加载、realization 编号、带 provenance 头的 JSON 输出
  catalogs.py              位置目录、Poisson 对照目录、Quijote group_tab 读取器
  mesh.py                  CIC 赋值、FFT lattice、CIC transfer、模式功率与分 bin
  moments.py               壳核、μ1/μ2/Wick 分量的测量
  window.py                精确离散窗口投影 μ1[P]、μ2_G[P]
  products.py              测量产品的存取
  stats.py                 协方差、Hartlap、χ² 比较、GLS
  theory/inputs.py         理论表 → lattice
  theory/tree.py           tree 级 P_h(fNL)、universal bφ、响应模板
  theory/loops.py          固定截断 one-loop（诊断用）
  theory/contact.py        Poisson contact 项（iid / 精确 CIC）
scripts/                   流水线，每个脚本做一件事，输出到 results/
tests/                     估计量恒等式和模型代数的测试
slurm/run.sbatch           通用计算节点包装
```

## 运行

```bash
export PYTHONPATH=$PWD            # 或 pip install -e .
python -m pytest -q               # 15 个测试，约 1 秒

# 1. 数据
python scripts/manifest.py                                         # 目录清单与配对检查
python scripts/reconstruct_catalogs.py --start 100 --stop 500      # 只在需要扩展 LC± 时运行

# 2. 测量（n64 全部约 1 分钟；4 进程）
for node in fiducial LC_m LC_p; do
  python scripts/measure.py --node $node --start 0 --stop 500 --workers 4
done
python scripts/measure.py --node poisson --start 0 --stop 10
for n in 128 256; do for node in fiducial LC_m LC_p poisson; do
  python scripts/measure.py --node $node --start 0 --stop 10 --nmesh $n --workers 4
done; done

# 3. 标定（只用 train 或 disjoint 块）
python scripts/fit_b1.py --block disjoint [--fix-shot] [--convention cic_matter]
python scripts/fit_bphi.py --block disjoint --b1 2.7413 --scan

# 4. 留出验证与诊断
python scripts/validate_mu1.py --b1 2.7413 --pshot 5467.76 --bphi 3.7636 --tag training_bphi
python scripts/loop_mu1.py --bphi 3.7636 --pshot 5467.76 --qmax 0.03 0.05 0.08 --tag training
python scripts/mu2_connected.py
python scripts/fnl_likelihood.py --observables mu1 R
```

在登录节点上最多用 6 个核（`--workers ≤ 6`）。更大的任务先 `mkdir -p results/slurm`，再 `sbatch slurm/run.sbatch python scripts/...`。

## 现状（一句话）

测量和精确窗口都已闭合，已验证到机器精度。μ1 的 tree 模型在节点均值上大体可用，但 PNG 响应的**尺度形状**和 tree 模板不一致。μ2 的 connected 部分除了 iid Poisson contact 以外都没有模型。详见 `docs/findings.md`。
