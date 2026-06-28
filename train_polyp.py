"""
YOLOv5 息肉检测模型训练脚本
使用 YOLOv5 模型进行息肉检测训练
参数配置与原始 Notebook (yolo11psc.ipynb) 一致
"""

from ultralytics import YOLO
import os

if __name__ == '__main__':
    print("=" * 70)
    print("YOLOv5 息肉检测模型训练")
    print("=" * 70)

    # 检查数据集是否存在
    dataset_path = "./polyp_dataset/data.yaml"
    if not os.path.exists(dataset_path):
        print(f"[ERROR] 数据集配置文件不存在: {dataset_path}")
        print("请先运行 download_dataset_fixed.py 下载数据集")
        exit(1)

    print(f"\n[检查] 数据集配置文件: {dataset_path} ✓")

    # 创建 YOLOv5 模型（改为 YOLOv5 nano）
    print("\n[步骤 1] 加载 YOLOv5n 模型...")
    model = YOLO("yolov5nu.pt")  # YOLOv5 nano 模型（最新版本）

    print("\n[步骤 2] 开始训练...")
    print("训练配置:")
    print("- 模型: YOLOv5n (Nano)")
    print("- 数据集: polyp_dataset")
    print("- 训练轮数: 100")
    print("- 批次大小: 8")
    print("- 图像尺寸: 640")
    print("- 数据增强: 启用（与原始 Notebook 一致）")

    # 开始训练（参数配置与原始 Notebook 一致）
    results = model.train(
        data=dataset_path,
        epochs=100,
        batch=8,
        imgsz=640,
        
        # 数据增强参数（与原始 Notebook yolo11psc.ipynb 一致）
        augment=True,
        auto_augment=None,
        degrees=0.15,          # 旋转角度范围 ±15°
        translate=0.0,         # 平移范围（无平移）
        scale=0.0,             # 缩放范围（无缩放）
        shear=0.0,             # 剪切变换（无剪切）
        perspective=0.0,       # 透视变换（无透视）
        flipud=0.5,            # 上下翻转概率 50%
        fliplr=0.5,            # 左右翻转概率 50%
        mosaic=0.0,            # Mosaic 数据增强（禁用）
        mixup=0.0,             # Mixup 数据增强（禁用）
        copy_paste=0.0,        # Copy-Paste 增强（禁用）
        hsv_h=0.0,             # HSV 色调调整（无色调调整）
        hsv_s=0.3,             # HSV 饱和度调整 ±30%
        hsv_v=0.3,             # HSV 明度调整 ±30%
        
        # 其他训练参数
        patience=100,          # 早停耐心值（与原始一致）
        save=True,             # 保存模型
        plots=True,            # 生成训练图表
        verbose=True           # 详细输出
    )

    print("\n" + "=" * 70)
    print("[SUCCESS] 训练完成！")
    print("=" * 70)

    print("\n训练结果:")
    print(f"- 最佳模型: runs/detect/train/weights/best.pt")
    print(f"- 最后模型: runs/detect/train/weights/last.pt")
    print(f"- 训练图表: runs/detect/train/")
    print(f"- 混淆矩阵: runs/detect/train/confusion_matrix.png")
    print(f"- F1 曲线: runs/detect/train/BoxF1_curve.png")
    print(f"- PR 曲线: runs/detect/train/BoxPR_curve.png")

    print("\n下一步:")
    print("1. 查看训练结果和性能指标")
    print("2. 运行 evaluate.py 在验证集上评估模型")
    print("3. 运行 inference_track.py 在视频上进行息肉追踪")
