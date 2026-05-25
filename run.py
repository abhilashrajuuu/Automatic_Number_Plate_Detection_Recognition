import os
import subprocess
import argparse
import sys
import glob

try:
    from moviepy import VideoFileClip
except ImportError:
    print("moviepy is not installed. Please run: pip install moviepy")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Run Automatic Number Plate Detection and Recognition")
    parser.add_argument("--source", type=str, default="ultralytics/yolo/v8/detect/demo.mp4", help="Path to input video or image")
    parser.add_argument("--model", type=str, default="ultralytics/yolo/v8/detect/best.pt", help="Path to model weights")
    args = parser.parse_args()

    project_dir = os.path.abspath("runs")
    
    # The original script relies on being run from this directory
    detect_dir = os.path.join(os.getcwd(), "ultralytics", "yolo", "v8", "detect")
    
    source_abs = os.path.abspath(args.source)
    model_abs = os.path.abspath(args.model)

    if not os.path.exists(source_abs):
        print(f"Error: Source file not found at {source_abs}")
        sys.exit(1)
        
    if not os.path.exists(model_abs):
        print(f"Error: Model weights not found at {model_abs}")
        sys.exit(1)

    # Force utf-8 encoding to avoid Windows EasyOCR console errors
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    cmd = [
        sys.executable,
        "predict.py",
        f"model='{model_abs}'",
        f"source='{source_abs}'",
        f"project='{project_dir}'",
        "name='predict'",
    ]
    
    print(f"==================================================")
    print(f" Starting Plate Detection & Recognition")
    print(f"==================================================")
    print(f"Source: {args.source}")
    print(f"Model:  {args.model}\n")
    
    result = subprocess.run(cmd, cwd=detect_dir, env=env)
    
    if result.returncode != 0:
        print("\n[Error] Prediction script failed!")
        sys.exit(1)

    # Search for the latest generated video in the runs directory
    print("\nLocating output video...")
    list_of_files = glob.glob(os.path.join(project_dir, '**', '*.mp4'), recursive=True)
    
    if not list_of_files:
        print("Could not find any output .mp4 files. The prediction might not have generated a video.")
        sys.exit(1)
        
    # Exclude previously converted files from the search
    list_of_files = [f for f in list_of_files if not f.endswith("_playable.mp4")]
    
    if not list_of_files:
        sys.exit(1)
        
    latest_vid = max(list_of_files, key=os.path.getctime)
    
    print(f"Original output saved at: {latest_vid}")
    
    # Convert video to h264 for standard media player compatibility
    output_playable = os.path.splitext(latest_vid)[0] + "_playable.mp4"
    print(f"\n==================================================")
    print(f" Converting video to playable format (h264)...")
    print(f"==================================================")
    
    try:
        clip = VideoFileClip(latest_vid)
        clip.write_videofile(output_playable, codec='libx264', audio=False)
        print(f"\n[Success] Final playable video saved to:\n{output_playable}")
    except Exception as e:
        print(f"\n[Error] Failed to convert video: {e}")

if __name__ == "__main__":
    main()
