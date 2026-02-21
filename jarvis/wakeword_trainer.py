"""Train a tiny wake-word classifier.

Usage:
  python -m jarvis.wakeword_trainer --data-dir jarvis/wake_data --epochs 10

Data layout expected:
  jarvis/wake_data/pos/  <-- wav samples containing the wakeword
  jarvis/wake_data/neg/  <-- negative samples (speech / noise without wakeword)

Outputs:
  - Trained scripted model saved to `jarvis/models/wakeword.pth`

Notes:
- Requires: torch, librosa, numpy
- This is a minimal example to get you started. Expand/replace as needed.
"""
import os
import argparse
import random
import time


def _fail(msg: str):
    raise RuntimeError(msg)


def _ensure_deps():
    try:
        import torch
        import librosa
        import numpy as np
    except Exception as e:
        _fail("Missing dependencies for wakeword training. Install: torch, librosa, numpy\n" + str(e))


def collect_files(datadir: str):
    pos = []
    neg = []
    for root, _, files in os.walk(datadir):
        for f in files:
            if not f.lower().endswith(".wav"):
                continue
            p = os.path.join(root, f)
            if "/pos" in root.replace("\\", "/"):
                pos.append(p)
            elif "/neg" in root.replace("\\", "/"):
                neg.append(p)
    return pos, neg


def load_feature(path: str, sr=16000, n_mels=64, frames=64):
    import librosa
    import numpy as np
    y, _ = librosa.load(path, sr=sr, mono=True)
    mels = librosa.feature.melspectrogram(y, sr=sr, n_mels=n_mels)
    mels_db = librosa.power_to_db(mels)
    # normalize
    mels_db = (mels_db - mels_db.mean()) / (mels_db.std() + 1e-9)
    # pad or crop time axis
    if mels_db.shape[1] < frames:
        pad_width = frames - mels_db.shape[1]
        mels_db = np.pad(mels_db, ((0, 0), (0, pad_width)), mode="constant")
    else:
        mels_db = mels_db[:, :frames]
    return mels_db.astype("float32")


def build_dataset(pos_files, neg_files, frames=64):
    import numpy as np
    X = []
    y = []
    for p in pos_files:
        X.append(load_feature(p, frames=frames))
        y.append(1.0)
    for n in neg_files:
        X.append(load_feature(n, frames=frames))
        y.append(0.0)
    X = np.stack(X)
    y = np.array(y, dtype="float32")
    # shuffle
    idx = np.arange(len(X))
    np.random.shuffle(idx)
    return X[idx], y[idx]


def train(args):
    _ensure_deps()
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import numpy as np

    pos, neg = collect_files(args.data_dir)
    if len(pos) == 0 or len(neg) == 0:
        _fail(f"Need samples in {args.data_dir}/pos and {args.data_dir}/neg to train")

    X, y = build_dataset(pos, neg, frames=args.frames)
    X = torch.from_numpy(X).unsqueeze(1)  # (N, 1, n_mels, frames)
    y = torch.from_numpy(y).unsqueeze(1)

    class WakeNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(
                nn.Conv2d(1, 8, kernel_size=(3, 3), padding=1),
                nn.ReLU(),
                nn.MaxPool2d((2, 2)),
                nn.Conv2d(8, 16, kernel_size=(3, 3), padding=1),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d((1, 1)),
                nn.Flatten(),
                nn.Linear(16, 1),
            )

        def forward(self, x):
            return self.net(x)

    model = WakeNet()
    opt = optim.Adam(model.parameters(), lr=args.lr)
    crit = nn.BCEWithLogitsLoss()

    dataset = torch.utils.data.TensorDataset(X, y)
    loader = torch.utils.data.DataLoader(dataset, batch_size=args.batch_size, shuffle=True)

    model.train()
    for epoch in range(args.epochs):
        epoch_loss = 0.0
        correct = 0
        total = 0
        for xb, yb in loader:
            opt.zero_grad()
            out = model(xb)
            loss = crit(out, yb)
            loss.backward()
            opt.step()
            epoch_loss += loss.item() * xb.size(0)
            preds = (torch.sigmoid(out) > 0.5).float()
            correct += (preds == yb).sum().item()
            total += xb.size(0)
        print(f"Epoch {epoch+1}/{args.epochs} — loss: {epoch_loss/total:.4f} — acc: {correct/total:.3f}")

    # export scripted model for runtime inference
    model.eval()
    example = torch.zeros(1, 1, 64, args.frames)
    scripted = torch.jit.trace(model, example)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    scripted.save(args.output)
    print("Saved scripted model to", args.output)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", default=os.path.join(os.path.dirname(__file__), "wake_data"))
    p.add_argument("--output", default=os.path.join(os.path.dirname(__file__), "models", "wakeword.pth"))
    p.add_argument("--epochs", type=int, default=12)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--frames", type=int, default=64)
    args = p.parse_args()
    train(args)
