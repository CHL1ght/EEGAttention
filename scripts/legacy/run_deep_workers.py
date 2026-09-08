import argparse
import os
from pathlib import Path
import subprocess
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = Path(__file__).resolve().parents[2]
WORKER_PATH = SCRIPT_DIR / "eeg_deep_worker.py"


TASKS = [
    ("resnet18", "full"),
    ("googlenet", "full"),
    ("resnet18", "anova"),
    ("googlenet", "anova"),
    ("resnet18", "fi"),
    ("googlenet", "fi"),
    ("resnet18", "lcc"),
    ("googlenet", "lcc"),
    ("resnet18", "pca"),
    ("googlenet", "pca"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--cache-dir", default="artifacts/reproductions/upstream_pipeline/feature_cache")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--no-pretrained", action="store_true")
    parser.add_argument("--only", nargs="*", default=None, help="Optional task filters like resnet18:full or googlenet:pca.")
    args = parser.parse_args()

    print(f"Python executable: {sys.executable}")
    print(f"Project directory: {PROJECT_DIR}")
    try:
        import torch
        import torchvision
    except ImportError as exc:
        raise SystemExit(
            "\nPyTorch environment check failed.\n"
            f"Current Python: {sys.executable}\n"
            "Install torch and torchvision into this exact Python environment, "
            "or switch the Jupyter kernel to the Conda environment that contains them.\n"
            f"Original error: {exc}"
        ) from exc

    print(f"torch: {torch.__version__}")
    print(f"torchvision: {torchvision.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    cache_dir = Path(args.cache_dir)
    if not cache_dir.is_absolute():
        cache_dir = PROJECT_DIR / cache_dir
    cache_dir = cache_dir.resolve()

    selected = TASKS
    if args.only:
        wanted = set(args.only)
        selected = [task for task in TASKS if f"{task[0]}:{task[1]}" in wanted]

    for model_name, variant in selected:
        cmd = [
            sys.executable,
            "-u",
            str(WORKER_PATH),
            "--model",
            model_name,
            "--variant",
            variant,
            "--epochs",
            str(args.epochs),
            "--batch-size",
            str(args.batch_size),
            "--cache-dir",
            str(cache_dir),
        ]
        if args.skip_existing:
            cmd.append("--skip-existing")
        if args.no_pretrained:
            cmd.append("--no-pretrained")

        print("\n" + "=" * 80, flush=True)
        print(f"Running {model_name}:{variant}", flush=True)
        print("=" * 80, flush=True)
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        subprocess.run(cmd, check=True, cwd=PROJECT_DIR, env=env)


if __name__ == "__main__":
    main()
