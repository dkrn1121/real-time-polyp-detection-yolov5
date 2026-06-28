"""
下载数据集到合法的目录名（避免 Windows 特殊字符问题）
"""
import os
import warnings
warnings.filterwarnings('ignore')

try:
    from roboflow import Roboflow
    
    print("=" * 70)
    print("开始下载息肉检测数据集")
    print("=" * 70)
    
    # 连接 Roboflow
    print("\n[步骤 1] 连接 Roboflow...")
    api_key = os.environ.get("ROBOFLOW_API_KEY")
    if not api_key:
        raise RuntimeError(
            "未检测到 ROBOFLOW_API_KEY 环境变量。请先在终端设置 Roboflow API Key，"
            "例如 PowerShell: $env:ROBOFLOW_API_KEY='你的APIKey'"
        )

    rf = Roboflow(api_key=api_key)
    
    print("[步骤 2] 获取项目信息...")
    project = rf.workspace("bsc-9d5aw").project("bsc-train_psc1toc5")
    
    print("[步骤 3] 获取数据集版本...")
    version = project.version(7)
    
    print("[步骤 4] 开始下载数据集...")
    print("注意：数据集可能较大，请耐心等待...")
    
    # 指定合法的本地目录名（不含特殊字符）
    # Windows 不允许目录名包含冒号，所以我们自定义路径
    custom_location = "polyp_dataset"
    
    dataset = version.download(
        model_format="yolov5",
        location=custom_location  # 指定本地路径
    )
    
    print("\n" + "=" * 70)
    print("[SUCCESS] 数据集下载成功！")
    print("=" * 70)
    print(f"数据集保存位置: {os.path.abspath(custom_location)}")
    print(f"数据集配置文件: {os.path.abspath(custom_location)}/data.yaml")
    
    # 检查数据集结构
    dataset_path = os.path.abspath(custom_location)
    print("\n数据集结构检查：")
    
    train_images = os.path.join(dataset_path, "train", "images")
    train_labels = os.path.join(dataset_path, "train", "labels")
    val_images = os.path.join(dataset_path, "valid", "images")
    val_labels = os.path.join(dataset_path, "valid", "labels")
    
    if os.path.exists(train_images):
        num_train = len(os.listdir(train_images))
        print(f"  训练图像数量: {num_train}")
    
    if os.path.exists(val_images):
        num_val = len(os.listdir(val_images))
        print(f"  验证图像数量: {num_val}")
    
    print("\n下一步：")
    print("1. 确认数据集路径为: './polyp_dataset/data.yaml'")
    print("2. 运行 train_polyp.py 开始训练")
    
except Exception as e:
    print("\n" + "=" * 70)
    print("[ERROR] 数据集下载失败")
    print("=" * 70)
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {e}")
    
    print("\n可能的原因:")
    print("1. ROBOFLOW_API_KEY 未设置或 API Key 可能已失效")
    print("2. 数据集可能是私有项目")
    print("3. 需要注册 Roboflow 账号")
    
    print("\n替代方案:")
    print("-> 访问 https://roboflow.com 注册账号")
    print("-> 手动搜索并下载公开的息肉检测数据集")
    print("-> 使用其他公开医学数据集 (CVC-ClinicDB, Kvasir-SEG)")

print("\n脚本执行完毕")
