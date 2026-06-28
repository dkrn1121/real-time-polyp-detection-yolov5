# 基于 YOLOv5 的息肉实时目标检测

本项目用于课堂作业“基于 YOLOv5 的实时目标检测”。项目基于公开 Roboflow 医学图像数据集训练 YOLOv5n 模型，实现内镜息肉类别与位置检测，并给出 mAP、FPS、训练曲线、混淆矩阵和视频帧检测截图。

## 1. 项目特点

- 检测类别：`polyp`
- 模型：YOLOv5n，权重入口为 `yolov5nu.pt`
- 数据集：Roboflow Universe 项目 `bsc-train_psc1toc5` Version 7，许可为 CC BY 4.0
- 训练配置：100 epochs，batch 8，输入尺寸 640
- 输出内容：最佳权重、评估指标、FPS 测试结果、检测视频帧截图

## 2. 项目结构

```text
.
├── benchmark_fps.py                 # FPS 基准测试脚本
├── download_dataset_fixed.py         # 数据集下载脚本，API Key 从环境变量读取
├── evaluate.py                       # 验证集评估脚本
├── inference_track.py                # 视频检测与跟踪脚本
├── train_polyp.py                    # YOLOv5n 训练脚本
├── requirements.txt                  # Python 依赖
├── evaluation_results/               # mAP 与 FPS 结果
├── report/                           # 视频检测帧截图
└── runs/detect/                      # 训练和验证可视化结果
```

说明：完整 `polyp_dataset/` 数据集体积较大，默认不提交到 GitHub；可通过脚本重新下载或按 `polyp_dataset/data.yaml` 的格式自行准备。

## 3. 环境安装

建议使用 Python 3.10 或更高版本。

```bash
pip install -r requirements.txt
```

如需要重新下载 Roboflow 数据集，请先设置环境变量：

```powershell
$env:ROBOFLOW_API_KEY="你的Roboflow API Key"
python download_dataset_fixed.py
```

数据集下载后应形成如下结构：

```text
polyp_dataset/
├── data.yaml
├── train/images
├── train/labels
├── valid/images
└── valid/labels
```

本实验本地数据划分为训练集 2166 张、验证集 545 张，当前未使用独立 test 子集。

## 4. 训练模型

```bash
python train_polyp.py
```

训练完成后主要输出：

- 最佳模型：`runs/detect/train/weights/best.pt`
- 训练曲线：`runs/detect/train/results.png`
- 混淆矩阵：`runs/detect/train/confusion_matrix.png`
- PR/F1/P/R 曲线：`runs/detect/train/BoxPR_curve.png` 等

## 5. 评估 mAP

```bash
python evaluate.py
```

当前验证集评估结果如下：

| 指标 | 数值 |
|---|---:|
| Precision | 0.8581 |
| Recall | 0.8322 |
| F1-Score | 0.8450 |
| mAP@0.5 | 0.8913 |
| mAP@0.5:0.95 | 0.6791 |

结果文件：

- `evaluation_results/metrics.json`
- `evaluation_results/metrics.csv`

## 6. 测试 FPS

```bash
python benchmark_fps.py
```

该脚本使用 `tracked_output_video.mp4`，先预热 10 帧，再统计普通检测 `predict()` 与跟踪推理 `track()` 的速度。当前本机 CPU 实测结果：

| 模式 | 平均耗时 | FPS |
|---|---:|---:|
| detect | 34.15 ms/帧 | 29.28 |
| track | 35.91 ms/帧 | 27.85 |

结果文件：

- `evaluation_results/fps_benchmark.json`
- `evaluation_results/fps_benchmark.csv`

## 7. 视频推理与截图

```bash
python inference_track.py
```

脚本会读取 `tracked_output_video.mp4`，调用 `model.track(frame, persist=True, conf=0.8)`，并将检测到息肉的帧保存到 `report/`。示例截图包括：

- `report/0.23.jpg`
- `report/4.50.jpg`
- `report/6.63.jpg`
- `report/7.16.jpg`

## 8. 结果分析简述

训练曲线显示，box loss、cls loss 和 dfl loss 随 epoch 增加整体下降，mAP@0.5 在后期稳定在 0.84 到 0.89 左右。验证集 mAP@0.5 达到 0.8913，说明模型对息肉区域定位较好；mAP@0.5:0.95 为 0.6791，表明在更严格 IoU 阈值下，小目标边界仍有提升空间。

失败案例主要来自以下因素：

- 内镜高光、反光和运动模糊会干扰纹理判断。
- 息肉边界与正常黏膜颜色相近，模型容易出现漏检或框偏移。
- 小息肉、遮挡区域、画面边缘目标更难稳定检测。
- 单类别数据集缺少更丰富的负样本和复杂场景，可能造成部分误检。

## 9. GitHub 获取代码

项目默认发布地址：

```text
https://github.com/dkrn1121/real-time-polyp-detection-yolov5
```

获取代码：

```bash
git clone https://github.com/dkrn1121/real-time-polyp-detection-yolov5.git
cd real-time-polyp-detection-yolov5
pip install -r requirements.txt
```

如果仓库尚未创建，可先在 GitHub 创建同名空仓库，再将本地项目推送到该地址。

## 10. 注意事项

- 完整数据集默认不纳入仓库，可通过 `download_dataset_fixed.py` 重新下载。
- `best.pt` 为本实验最佳训练权重，`last.pt` 和完整训练缓存默认不提交。
- 医学目标检测结果仅用于课程实验展示，不能直接作为临床诊断依据。
