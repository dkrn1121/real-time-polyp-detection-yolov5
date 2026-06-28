"""
YOLOv5 息肉检测 - 视频追踪和推理脚本
基于 Track_save_frame.ipynb 转换
保持原有的追踪逻辑和参数配置
"""

import cv2
import os
from ultralytics import YOLO

def track_polyps_in_video(model_path, video_path, output_dir='./report'):
    """
    在视频中进行息肉追踪（保持原始 Notebook 逻辑）
    
    Args:
        model_path: YOLO模型路径 (best.pt 或 last.pt)
        video_path: 输入视频路径
        output_dir: 输出目录，用于保存追踪帧和结果视频
    """
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 加载模型
    print(f"加载模型: {model_path}")
    model = YOLO(model_path)
    
    # 打开视频
    print(f"打开视频: {video_path}")
    cap = cv2.VideoCapture(video_path)
    
    # 获取视频参数
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # 创建视频写入器
    output_video = os.path.join(output_dir, 'tracked_output_video.mp4')
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))
    
    print(f"输出视频: {output_video}")
    print(f"视频参数: {frame_width}x{frame_height} @ {fps} FPS")
    print("开始追踪...")
    
    frame_count = 0
    
    # 视频追踪循环（保持原始 Notebook 逻辑）
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        
        # 追踪息肉（参数与原始 Notebook 一致）
        results = model.track(frame, persist=True, conf=0.8, verbose=False)
        annotated_frame = results[0].plot()
        
        # 如果检测到息肉，保存帧（保持原始逻辑）
        if results[0].boxes.id is not None:
            current_time_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            current_time_sec = current_time_ms / 1000.0
            
            # 文件名格式：秒.毫秒.jpg（保持原始命名规则）
            filename = f"{int(current_time_sec)}.{int((current_time_sec * 100) % 100):02d}.jpg"
            output_path = os.path.join(output_dir, filename)
            
            cv2.imwrite(output_path, annotated_frame)
            frame_count += 1
        
        # 写入视频
        video_writer.write(annotated_frame)
        
        # 显示实时追踪（可选，与原始 Notebook 保持一致）
        # cv2.imshow("YOLOv5 Live Tracking", annotated_frame)
        # if cv2.waitKey(1) & 0xFF == ord("q"):
        #     break
    
    # 释放资源
    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()
    
    print(f"\n追踪完成！")
    print(f"保存了 {frame_count} 帧检测结果")
    print(f"输出视频: {output_video}")
    print(f"输出帧目录: {output_dir}")

def main():
    """主函数"""
    # 模型路径（训练后生成的最佳模型）
    MODEL_PATH = 'runs/detect/train/weights/best.pt'
    
    # 视频路径（需要准备医学视频）
    VIDEO_PATH = 'tracked_output_video.mp4'
    
    # 检查文件是否存在
    if not os.path.exists(MODEL_PATH):
        print(f"错误: 模型文件不存在 {MODEL_PATH}")
        print("请先运行 train_polyp.py 进行训练")
        return
    
    if not os.path.exists(VIDEO_PATH):
        print(f"错误: 视频文件不存在 {VIDEO_PATH}")
        print("请准备一个医学视频文件（如 endoscopy.mp4）")
        return
    
    # 运行追踪
    track_polyps_in_video(MODEL_PATH, VIDEO_PATH)

if __name__ == "__main__":
    main()