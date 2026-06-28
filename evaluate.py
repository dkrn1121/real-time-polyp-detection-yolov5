"""
YOLOv5 息肉检测模型评估脚本
在验证集上计算各类性能指标
包括：mAP、Precision、Recall、F1-Score、混淆矩阵等
"""

from ultralytics import YOLO
import os
import json
import pandas as pd
from pathlib import Path

if __name__ == '__main__':
    print("=" * 70)
    print("YOLOv5 息肉检测模型评估")
    print("=" * 70)

    # 模型路径配置
    MODEL_PATH = 'runs/detect/train/weights/best.pt'
    DATA_PATH = './polyp_dataset/data.yaml'

    # 检查文件是否存在
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] 模型文件不存在: {MODEL_PATH}")
        print("请先运行 train_polyp.py 进行训练")
        exit(1)

    if not os.path.exists(DATA_PATH):
        print(f"[ERROR] 数据集配置文件不存在: {DATA_PATH}")
        print("请先运行 download_dataset_fixed.py 下载数据集")
        exit(1)

    print(f"\n[检查] 模型文件: {MODEL_PATH} ✓")
    print(f"[检查] 数据集配置: {DATA_PATH} ✓")

    # 加载模型
    print("\n[步骤 1] 加载训练好的模型...")
    model = YOLO(MODEL_PATH)

    # 在验证集上进行评估
    print("\n[步骤 2] 在验证集上进行评估...")
    print("评估指标包括：")
    print("- Precision (精确率)")
    print("- Recall (召回率)")
    print("- F1-Score (F1分数)")
    print("- mAP@0.5 (IoU阈值0.5的平均精度)")
    print("- mAP@0.5:0.95 (IoU阈值0.5-0.95的平均精度)")

    # 运行验证评估
    metrics = model.val(
        data=DATA_PATH,
        split='val',          # 使用验证集
        conf=0.001,           # 置信度阈值（与训练一致）
        iou=0.7,              # IoU阈值
        plots=True,           # 生成评估图表
        save_json=True,       # 保存JSON结果
        verbose=True          # 详细输出
    )

    print("\n" + "=" * 70)
    print("[SUCCESS] 评估完成！")
    print("=" * 70)

    # 提取评估结果
    print("\n[步骤 3] 提取评估指标...")
    # 处理 numpy 数组，提取平均值或单个值
    precision = metrics.box.p.mean() if hasattr(metrics.box.p, 'mean') else metrics.box.p
    recall = metrics.box.r.mean() if hasattr(metrics.box.r, 'mean') else metrics.box.r
    f1_score = metrics.box.f1.mean() if hasattr(metrics.box.f1, 'mean') else metrics.box.f1
    map50 = metrics.box.map50.mean() if hasattr(metrics.box.map50, 'mean') else metrics.box.map50
    map50_95 = metrics.box.map.mean() if hasattr(metrics.box.map, 'mean') else metrics.box.map
    
    results = {
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1_score),
        'map50': float(map50),
        'map50_95': float(map50_95)
    }

    # 打印详细结果
    print("\n详细评估结果:")
    print(f"Precision (精确率): {results['precision']:.4f}")
    print(f"Recall (召回率): {results['recall']:.4f}")
    print(f"F1-Score: {results['f1_score']:.4f}")
    print(f"mAP@0.5: {results['map50']:.4f}")
    print(f"mAP@0.5:0.95: {results['map50_95']:.4f}")

    # 保存评估结果到文件
    print("\n[步骤 4] 保存评估结果...")
    output_dir = Path('evaluation_results')
    output_dir.mkdir(exist_ok=True)

    # 保存JSON格式结果
    json_file = output_dir / 'metrics.json'
    with open(json_file, 'w') as f:
        json.dump({
            'precision': results['precision'],
            'recall': results['recall'],
            'f1_score': results['f1_score'],
            'map50': results['map50'],
            'map50_95': results['map50_95'],
            'model_path': MODEL_PATH,
            'dataset': DATA_PATH
        }, f, indent=2)
    print(f"评估结果已保存: {json_file}")

    # 保存CSV格式结果
    csv_file = output_dir / 'metrics.csv'
    df = pd.DataFrame({
        'Metric': ['Precision', 'Recall', 'F1-Score', 'mAP@0.5', 'mAP@0.5:0.95'],
        'Value': [
            results['precision'],
            results['recall'],
            results['f1_score'],
            results['map50'],
            results['map50_95']
        ]
    })
    df.to_csv(csv_file, index=False)
    print(f"评估结果已保存: {csv_file}")

    # 显示生成的图表位置
    print("\n[步骤 5] 生成的评估图表:")
    print(f"- 混淆矩阵: runs/detect/val/confusion_matrix.png")
    print(f"- F1曲线: runs/detect/val/F1_curve.png")
    print(f"- PR曲线: runs/detect/val/PR_curve.png")
    print(f"- P曲线: runs/detect/val/P_curve.png")
    print(f"- R曲线: runs/detect/val/R_curve.png")

    print("\n" + "=" * 70)
    print("评估完成总结")
    print("=" * 70)
    print("\n模型性能分析:")
    if results['map50'] > 0.8:
        print("✓ 模型性能优秀 (mAP@0.5 > 0.8)")
    elif results['map50'] > 0.6:
        print("✓ 模型性能良好 (mAP@0.5 > 0.6)")
    else:
        print("⚠ 模型性能需要改进 (mAP@0.5 < 0.6)")
        print("建议：")
        print("1. 增加训练轮数")
        print("2. 调整数据增强参数")
        print("3. 检查数据集质量")

    print("\n下一步操作:")
    print("1. 查看 evaluation_results/ 目录中的评估报告")
    print("2. 查看 runs/detect/val/ 目录中的可视化图表")
    print("3. 运行 inference_track.py 在实际视频上测试模型")