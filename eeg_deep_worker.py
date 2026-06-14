import argparse
import gc
import json
import os
from pathlib import Path
import time
import warnings

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from sklearn.metrics import accuracy_score, auc, confusion_matrix, f1_score, precision_score, recall_score, roc_curve
from torch.utils.data import DataLoader, Dataset
from torchvision.models import googlenet, resnet18


warnings.filterwarnings("ignore")

PROJECT_DIR = Path(__file__).resolve().parent


VARIANTS = {
    "full": {"suffix": "", "reshape": (18, 14), "title": "Without Feature Reduction"},
    "anova": {"suffix": "_anova", "reshape": (18, 12), "title": "ANOVA"},
    "fi": {"suffix": "_fi", "reshape": (82, 1), "title": "Feature Importance"},
    "lcc": {"suffix": "_lcc", "reshape": (12, 9), "title": "Linear Correlation Coefficient"},
    "pca": {"suffix": "_pca", "reshape": (251, 1), "title": "PCA"},
}


class EEGImageDataset(Dataset):
    def __init__(self, x, y, input_shape, transform):
        self.x = np.asarray(x, dtype=np.float32)
        self.y = np.asarray(y, dtype=np.int64)
        self.input_shape = tuple(input_shape)
        self.transform = transform

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        sample = self.x[idx]
        if sample.size == int(np.prod(self.input_shape)):
            sample = sample.reshape(self.input_shape)
        else:
            sample = sample.reshape((-1, 1))
        sample = np.resize(sample, (224, 224))
        sample = np.repeat(sample[:, :, np.newaxis], 3, axis=2).astype(np.float32)
        return self.transform(sample), torch.tensor(self.y[idx], dtype=torch.long)


def logits_from_output(output):
    if hasattr(output, "logits"):
        return output.logits
    if isinstance(output, tuple):
        return output[0]
    return output


def build_model(model_name, pretrained):
    if model_name == "resnet18":
        try:
            model = resnet18(pretrained=pretrained)
        except Exception as exc:
            print(f"Warning: pretrained ResNet-18 failed ({exc}); retrying without pretrained weights.")
            model = resnet18(pretrained=False)
        model.fc = nn.Linear(model.fc.in_features, 2)
        return model

    if model_name == "googlenet":
        try:
            model = googlenet(pretrained=pretrained)
        except Exception as exc:
            print(f"Warning: pretrained GoogLeNet failed ({exc}); retrying without pretrained weights.")
            model = googlenet(pretrained=False)
        model.fc = nn.Linear(model.fc.in_features, 2)
        return model

    raise ValueError(f"Unknown model: {model_name}")


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    for inputs, labels in loader:
        inputs = inputs.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        optimizer.zero_grad(set_to_none=True)
        outputs = logits_from_output(model(inputs))
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    return running_loss / max(len(loader), 1)


def evaluate(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    predicted_labels = []
    true_labels = []
    predicted_proba = []

    with torch.no_grad():
        for inputs, labels in loader:
            inputs = inputs.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            outputs = logits_from_output(model(inputs))
            loss = criterion(outputs, labels)
            running_loss += loss.item()

            _, predicted = torch.max(outputs.data, 1)
            predicted_labels.extend(predicted.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())
            predicted_proba.extend(torch.softmax(outputs, dim=1).cpu().numpy())

    accuracy = accuracy_score(true_labels, predicted_labels)
    precision = precision_score(true_labels, predicted_labels, pos_label=1)
    recall = recall_score(true_labels, predicted_labels, pos_label=1)
    f1 = f1_score(true_labels, predicted_labels, pos_label=1)
    cm = confusion_matrix(true_labels, predicted_labels)
    return running_loss / max(len(loader), 1), accuracy, precision, recall, f1, cm, np.asarray(predicted_proba)


def output_paths(model_name, variant):
    suffix = VARIANTS[variant]["suffix"]
    base = f"{model_name}_part_detrend_plr_stft_bin_win{suffix}"
    return {
        "model": PROJECT_DIR / "model" / f"{model_name}_model_part_detrend_plr_stft_bin_win{suffix}.pth",
        "xlsx": PROJECT_DIR / "result" / f"train_info_{base}.xlsx",
        "roc": PROJECT_DIR / "result" / "roc_artifacts" / f"{base}.npz",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["resnet18", "googlenet"], required=True)
    parser.add_argument("--variant", choices=list(VARIANTS), required=True)
    parser.add_argument("--cache-dir", default=str(PROJECT_DIR / "cache"))
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--no-pretrained", action="store_true")
    args = parser.parse_args()

    (PROJECT_DIR / "model").mkdir(exist_ok=True)
    (PROJECT_DIR / "result").mkdir(exist_ok=True)
    (PROJECT_DIR / "result" / "roc_artifacts").mkdir(parents=True, exist_ok=True)
    progress_dir = PROJECT_DIR / "result" / "progress"
    progress_dir.mkdir(parents=True, exist_ok=True)
    progress_path = progress_dir / f"{args.model}_{args.variant}.json"
    log_path = progress_dir / f"{args.model}_{args.variant}.log"

    paths = output_paths(args.model, args.variant)
    if args.skip_existing and os.path.exists(paths["xlsx"]) and os.path.exists(paths["roc"]):
        print(f"Skip existing: {args.model} {args.variant}")
        return

    cache_path = Path(args.cache_dir).resolve() / f"{args.variant}.npz"
    data = np.load(cache_path)
    x_train = data["X_train"]
    x_test = data["X_test"]
    y_train = data["y_train"]
    y_test = data["y_test"]

    torch.manual_seed(2024)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(2024)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pin_memory = device.type == "cuda"

    transform = transforms.Compose([transforms.ToTensor()])
    input_shape = VARIANTS[args.variant]["reshape"]
    train_dataset = EEGImageDataset(x_train, y_train, input_shape, transform)
    test_dataset = EEGImageDataset(x_test, y_test, input_shape, transform)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, pin_memory=pin_memory, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, pin_memory=pin_memory, num_workers=0)

    model = build_model(args.model, pretrained=not args.no_pretrained).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate, weight_decay=1e-6)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)

    train_info = pd.DataFrame(columns=["epoch", "train_loss", "lr", "test_loss", "test_acc", "precision", "recall", "f1", "time"])
    best_accuracy = -1.0
    best_cm = None
    best_proba = None

    start_message = f"Training {args.model} ({args.variant}) on {device}..."
    log_path.write_text(start_message + "\n", encoding="utf-8")
    print(start_message, flush=True)
    for epoch in range(args.epochs):
        start_time = time.time()
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, device)
        test_loss, test_accuracy, precision, recall, f1, cm, proba = evaluate(model, test_loader, criterion, device)
        epoch_time = time.time() - start_time

        train_info.loc[epoch] = [
            epoch + 1,
            train_loss,
            optimizer.state_dict()["param_groups"][0]["lr"],
            test_loss,
            test_accuracy,
            precision,
            recall,
            f1,
            epoch_time,
        ]
        scheduler.step()
        progress = {
            "model": args.model,
            "variant": args.variant,
            "epoch": epoch + 1,
            "total_epochs": args.epochs,
            "train_loss": float(train_loss),
            "test_loss": float(test_loss),
            "test_accuracy": float(test_accuracy),
            "best_accuracy": float(max(best_accuracy, test_accuracy)),
            "epoch_seconds": float(epoch_time),
            "status": "running",
        }
        progress_path.write_text(json.dumps(progress, indent=2), encoding="utf-8")
        epoch_message = (
            f"[Epoch {epoch + 1}/{args.epochs}] "
            f"train_loss={train_loss:.4f}, test_loss={test_loss:.4f}, "
            f"acc={test_accuracy:.4f}, time={epoch_time:.1f}s"
        )
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(epoch_message + "\n")
            log_file.flush()
        print(epoch_message, flush=True)

        if test_accuracy > best_accuracy:
            best_accuracy = test_accuracy
            best_cm = cm
            best_proba = proba
            torch.save(model.state_dict(), paths["model"])

    positive_probs = best_proba[:, 1]
    negative_probs = 1 - positive_probs
    y_proba = np.column_stack((negative_probs, positive_probs))
    fpr, tpr, _ = roc_curve(y_test, y_proba[:, 1])
    roc_auc = auc(fpr, tpr)

    train_info.to_excel(paths["xlsx"], index=False)
    np.savez_compressed(paths["roc"], fpr=fpr, tpr=tpr, roc_auc=roc_auc, y_test=y_test, y_proba=y_proba, best_cm=best_cm)
    progress["status"] = "completed"
    progress["best_accuracy"] = float(best_accuracy)
    progress["roc_auc"] = float(roc_auc)
    progress_path.write_text(json.dumps(progress, indent=2), encoding="utf-8")
    print(f"Saved {paths['xlsx']}", flush=True)
    print(f"Saved {paths['roc']}", flush=True)
    print(f"Best accuracy: {best_accuracy:.4f}; ROC AUC: {roc_auc:.4f}", flush=True)

    model.to("cpu")
    del model, train_loader, test_loader, train_dataset, test_dataset
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


if __name__ == "__main__":
    main()
