"""
YOLOv5 息肉检测 FPS 基准测试脚本。

默认使用训练得到的 best.pt 和项目中的演示视频，分别统计普通检测
predict() 与带目标跟踪 track() 的 CPU/GPU 推理速度。
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path
from typing import Any


def compute_speed_summary(frame_count: int, elapsed_seconds: float) -> dict[str, float]:
    """Return average latency and FPS for a measured video inference loop."""
    if frame_count <= 0:
        raise ValueError("frame_count must be greater than zero")
    if elapsed_seconds <= 0:
        raise ValueError("elapsed_seconds must be greater than zero")

    return {
        "avg_ms_per_frame": elapsed_seconds / frame_count * 1000.0,
        "fps": frame_count / elapsed_seconds,
    }


def load_video_frames(video_path: str | Path) -> tuple[list[Any], dict[str, float]]:
    """Load all frames from a video so detection and tracking use identical input."""
    import cv2

    video_path = Path(video_path)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise FileNotFoundError(f"无法打开视频文件: {video_path}")

    frames: list[Any] = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)

    metadata = {
        "source_fps": float(cap.get(cv2.CAP_PROP_FPS) or 0.0),
        "width": float(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0.0),
        "height": float(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0.0),
        "frame_count": float(len(frames)),
    }
    cap.release()

    if not frames:
        raise RuntimeError(f"视频中没有可读取帧: {video_path}")
    return frames, metadata


def synchronize_if_cuda() -> None:
    """Synchronize CUDA before timing when GPU is available."""
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.synchronize()
    except Exception:
        return


def benchmark_mode(model: Any, frames: list[Any], mode: str, imgsz: int, conf: float, warmup: int) -> dict[str, float]:
    """Benchmark YOLO predict or track on an in-memory frame list."""
    warmup_frames = frames[: min(warmup, len(frames))]
    for frame in warmup_frames:
        if mode == "detect":
            model.predict(frame, imgsz=imgsz, conf=conf, verbose=False)
        elif mode == "track":
            model.track(frame, persist=True, conf=conf, verbose=False)
        else:
            raise ValueError(f"unsupported mode: {mode}")

    synchronize_if_cuda()
    start = time.perf_counter()
    for frame in frames:
        if mode == "detect":
            model.predict(frame, imgsz=imgsz, conf=conf, verbose=False)
        else:
            model.track(frame, persist=True, conf=conf, verbose=False)
    synchronize_if_cuda()

    elapsed = time.perf_counter() - start
    summary = compute_speed_summary(len(frames), elapsed)
    summary["elapsed_seconds"] = elapsed
    return summary


def write_results(output_dir: str | Path, results: dict[str, Any]) -> None:
    """Write benchmark results as JSON and CSV files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "fps_benchmark.json"
    csv_path = output_dir / "fps_benchmark.csv"

    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    rows = []
    for mode in ("detect", "track"):
        metrics = results[mode]
        rows.append(
            {
                "mode": mode,
                "device": results["device"],
                "frames": results["video"]["frame_count"],
                "avg_ms_per_frame": metrics["avg_ms_per_frame"],
                "fps": metrics["fps"],
                "elapsed_seconds": metrics["elapsed_seconds"],
            }
        )

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["mode", "device", "frames", "avg_ms_per_frame", "fps", "elapsed_seconds"],
        )
        writer.writeheader()
        writer.writerows(rows)


def run_benchmark(args: argparse.Namespace) -> dict[str, Any]:
    """Load model/video, run both benchmark modes, and save results."""
    from ultralytics import YOLO

    frames, video_metadata = load_video_frames(args.video)
    model = YOLO(args.model)

    detect = benchmark_mode(model, frames, "detect", args.imgsz, args.detect_conf, args.warmup)
    track = benchmark_mode(model, frames, "track", args.imgsz, args.track_conf, args.warmup)

    results = {
        "model_path": str(Path(args.model)),
        "video_path": str(Path(args.video)),
        "device": str(model.device),
        "imgsz": args.imgsz,
        "warmup_frames": min(args.warmup, len(frames)),
        "video": video_metadata,
        "detect": detect,
        "track": track,
    }
    write_results(args.output_dir, results)
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark YOLOv5 polyp detection FPS.")
    parser.add_argument("--model", default="runs/detect/train/weights/best.pt", help="训练后的模型权重路径")
    parser.add_argument("--video", default="tracked_output_video.mp4", help="用于 FPS 测试的视频路径")
    parser.add_argument("--output-dir", default="evaluation_results", help="结果输出目录")
    parser.add_argument("--imgsz", type=int, default=640, help="推理图像尺寸")
    parser.add_argument("--warmup", type=int, default=10, help="计时前预热帧数")
    parser.add_argument("--detect-conf", type=float, default=0.25, help="普通检测置信度阈值")
    parser.add_argument("--track-conf", type=float, default=0.8, help="跟踪推理置信度阈值")
    return parser.parse_args()


if __name__ == "__main__":
    benchmark_results = run_benchmark(parse_args())
    print(json.dumps(benchmark_results, ensure_ascii=False, indent=2))
