"""
JARVIS 5.0 - Emotion Voice Trainer (CNN 1D)
============================================
Sprint 1: Refinamento Fase 1
Treina modelo CNN 1D para classificar emoções vocais

DATASET: RAVDESS ou TESS (português)
OUTPUT: models/emotion_voice.pth (~500KB)
USAGE: python src/learning/emotion_voice_trainer.py
"""

import sys
import os
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import librosa
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class EmotionVoiceCNN(nn.Module):
    """
    CNN 1D para classificação de emoções vocais
    Input: features MFCC (40 coeficientes, 128 frames)
    Output: 7 emoções (neutro, feliz, triste, raiva, medo, surpresa, nojo)
    """
    def __init__(self, num_emotions=7):
        super(EmotionVoiceCNN, self).__init__()
        
        # Conv Block 1
        self.conv1 = nn.Conv1d(in_channels=40, out_channels=64, kernel_size=5, padding=2)
        self.bn1 = nn.BatchNorm1d(64)
        self.pool1 = nn.MaxPool1d(kernel_size=2)
        
        # Conv Block 2
        self.conv2 = nn.Conv1d(64, 128, kernel_size=5, padding=2)
        self.bn2 = nn.BatchNorm1d(128)
        self.pool2 = nn.MaxPool1d(kernel_size=2)
        
        # Conv Block 3
        self.conv3 = nn.Conv1d(128, 256, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm1d(256)
        self.pool3 = nn.MaxPool1d(kernel_size=2)
        
        # Global Average Pooling + Dense
        self.gap = nn.AdaptiveAvgPool1d(1)
        self.fc1 = nn.Linear(256, 128)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(128, num_emotions)
        
        self.relu = nn.ReLU()
        
    def forward(self, x):
        # x shape: (batch, 40, 128) - MFCC features
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.pool1(x)
        
        x = self.relu(self.bn2(self.conv2(x)))
        x = self.pool2(x)
        
        x = self.relu(self.bn3(self.conv3(x)))
        x = self.pool3(x)
        
        x = self.gap(x).squeeze(-1)  # (batch, 256)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x  # (batch, num_emotions) - logits


class AudioEmotionDataset(Dataset):
    """Dataset para emoções vocais com features MFCC"""
    
    def __init__(self, audio_paths, labels, sr=22050, n_mfcc=40, max_len=128):
        self.audio_paths = audio_paths
        self.labels = labels
        self.sr = sr
        self.n_mfcc = n_mfcc
        self.max_len = max_len
        
    def __len__(self):
        return len(self.audio_paths)
    
    def __getitem__(self, idx):
        try:
            # Load audio
            audio, _ = librosa.load(self.audio_paths[idx], sr=self.sr, duration=3.0)
            
            # Extract MFCC features
            mfcc = librosa.feature.mfcc(y=audio, sr=self.sr, n_mfcc=self.n_mfcc)
            
            # Pad or truncate to max_len
            if mfcc.shape[1] < self.max_len:
                pad_width = self.max_len - mfcc.shape[1]
                mfcc = np.pad(mfcc, ((0, 0), (0, pad_width)), mode='constant')
            else:
                mfcc = mfcc[:, :self.max_len]
            
            # Normalize
            mfcc = (mfcc - np.mean(mfcc)) / (np.std(mfcc) + 1e-8)
            
            return torch.FloatTensor(mfcc), self.labels[idx]
        
        except Exception as e:
            logger.error(f"Error loading {self.audio_paths[idx]}: {e}")
            # Return zero tensor on error
            return torch.zeros(self.n_mfcc, self.max_len), self.labels[idx]


def load_dataset(dataset_path):
    """
    Carrega dataset de emoções
    Suporta estrutura: dataset_path/emotion_name/*.wav
    
    Exemplo:
    dataset/
      neutral/*.wav
      happy/*.wav
      sad/*.wav
      angry/*.wav
      fear/*.wav
      surprise/*.wav
      disgust/*.wav
    """
    dataset_path = Path(dataset_path)
    
    if not dataset_path.exists():
        logger.error(f"Dataset path not found: {dataset_path}")
        return None, None, None
    
    audio_paths = []
    labels = []
    emotion_names = []
    
    # Scan emotion folders
    emotion_folders = [f for f in dataset_path.iterdir() if f.is_dir()]
    
    if not emotion_folders:
        logger.error(f"No emotion folders found in {dataset_path}")
        return None, None, None
    
    logger.info(f"Found {len(emotion_folders)} emotion categories")
    
    for emotion_folder in sorted(emotion_folders):
        emotion_name = emotion_folder.name
        emotion_names.append(emotion_name)
        
        # Find all audio files
        audio_files = list(emotion_folder.glob("*.wav")) + \
                     list(emotion_folder.glob("*.mp3")) + \
                     list(emotion_folder.glob("*.flac"))
        
        logger.info(f"  {emotion_name}: {len(audio_files)} files")
        
        for audio_file in audio_files:
            audio_paths.append(str(audio_file))
            labels.append(emotion_name)
    
    if not audio_paths:
        logger.error("No audio files found in dataset")
        return None, None, None
    
    logger.info(f"Total: {len(audio_paths)} audio files, {len(set(labels))} emotions")
    
    return audio_paths, labels, emotion_names


def train_emotion_model(dataset_path, output_path, epochs=50, batch_size=32, lr=0.001):
    """
    Treina modelo CNN 1D para classificação de emoções
    
    Args:
        dataset_path: Caminho para dataset de emoções
        output_path: Caminho para salvar modelo .pth
        epochs: Número de épocas
        batch_size: Tamanho do batch
        lr: Learning rate
    
    Returns:
        model: Modelo treinado
        label_encoder: Encoder de labels
    """
    logger.info("="*70)
    logger.info("🎭 JARVIS Emotion Voice Training - Sprint 1")
    logger.info("="*70)
    
    # Load dataset
    logger.info("\n📦 Loading dataset...")
    audio_paths, labels, emotion_names = load_dataset(dataset_path)
    
    if audio_paths is None:
        logger.error("❌ Failed to load dataset")
        return None, None
    
    # Encode labels
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)
    num_emotions = len(label_encoder.classes_)
    
    logger.info(f"\n🏷️  Emotions: {list(label_encoder.classes_)}")
    
    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        audio_paths, encoded_labels, test_size=0.2, random_state=42, stratify=encoded_labels
    )
    
    logger.info(f"📊 Train: {len(X_train)} | Test: {len(X_test)}")
    
    # Create datasets
    train_dataset = AudioEmotionDataset(X_train, y_train)
    test_dataset = AudioEmotionDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    
    # Create model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"\n🔧 Device: {device}")
    
    model = EmotionVoiceCNN(num_emotions=num_emotions).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)
    
    # Training loop
    logger.info(f"\n🏋️  Training for {epochs} epochs...")
    best_acc = 0.0
    
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = output.max(1)
            train_total += target.size(0)
            train_correct += predicted.eq(target).sum().item()
        
        train_loss /= len(train_loader)
        train_acc = 100. * train_correct / train_total
        
        # Validation
        model.eval()
        test_loss = 0.0
        test_correct = 0
        test_total = 0
        
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                loss = criterion(output, target)
                
                test_loss += loss.item()
                _, predicted = output.max(1)
                test_total += target.size(0)
                test_correct += predicted.eq(target).sum().item()
        
        test_loss /= len(test_loader)
        test_acc = 100. * test_correct / test_total
        
        # Update learning rate
        scheduler.step(test_loss)
        
        # Log progress
        if (epoch + 1) % 5 == 0 or epoch == 0:
            logger.info(f"Epoch {epoch+1}/{epochs} | "
                       f"Train Loss: {train_loss:.4f} Acc: {train_acc:.2f}% | "
                       f"Test Loss: {test_loss:.4f} Acc: {test_acc:.2f}%")
        
        # Save best model
        if test_acc > best_acc:
            best_acc = test_acc
            torch.save({
                'model_state_dict': model.state_dict(),
                'label_encoder': label_encoder,
                'num_emotions': num_emotions,
                'emotions': list(label_encoder.classes_),
                'accuracy': best_acc
            }, output_path)
    
    logger.info(f"\n✅ Training complete! Best accuracy: {best_acc:.2f}%")
    logger.info(f"💾 Model saved to: {output_path}")
    logger.info(f"📦 Model size: {os.path.getsize(output_path) / 1024:.2f} KB")
    
    return model, label_encoder


def test_inference(model_path, test_audio_path):
    """
    Testa inferência do modelo com um áudio
    
    Args:
        model_path: Caminho para modelo .pth
        test_audio_path: Caminho para áudio de teste
    """
    logger.info("\n🧪 Testing inference...")
    
    if not os.path.exists(model_path):
        logger.error(f"Model not found: {model_path}")
        return
    
    if not os.path.exists(test_audio_path):
        logger.error(f"Test audio not found: {test_audio_path}")
        return
    
    # Load model
    checkpoint = torch.load(model_path, map_location='cpu')
    model = EmotionVoiceCNN(num_emotions=checkpoint['num_emotions'])
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    emotions = checkpoint['emotions']
    
    # Load audio and extract MFCC
    audio, sr = librosa.load(test_audio_path, sr=22050, duration=3.0)
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40)
    
    # Pad/truncate
    if mfcc.shape[1] < 128:
        pad_width = 128 - mfcc.shape[1]
        mfcc = np.pad(mfcc, ((0, 0), (0, pad_width)), mode='constant')
    else:
        mfcc = mfcc[:, :128]
    
    # Normalize
    mfcc = (mfcc - np.mean(mfcc)) / (np.std(mfcc) + 1e-8)
    mfcc_tensor = torch.FloatTensor(mfcc).unsqueeze(0)  # (1, 40, 128)
    
    # Inference
    with torch.no_grad():
        output = model(mfcc_tensor)
        probs = torch.softmax(output, dim=1)[0]
    
    # Results
    logger.info(f"🎭 Emotion prediction for: {test_audio_path}")
    for emotion, prob in zip(emotions, probs):
        logger.info(f"  {emotion}: {prob.item()*100:.2f}%")
    
    predicted_emotion = emotions[probs.argmax().item()]
    confidence = probs.max().item()
    logger.info(f"\n✨ Predicted: {predicted_emotion} (confidence: {confidence*100:.2f}%)")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="JARVIS Emotion Voice Training")
    parser.add_argument('--dataset', type=str, default='data/training_dataset/emotions',
                       help='Path to emotion dataset')
    parser.add_argument('--output', type=str, default='models/emotion_voice.pth',
                       help='Output model path')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size')
    parser.add_argument('--lr', type=float, default=0.001,
                       help='Learning rate')
    parser.add_argument('--test-audio', type=str, default=None,
                       help='Test audio file after training')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Train model
    model, label_encoder = train_emotion_model(
        dataset_path=args.dataset,
        output_path=args.output,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr
    )
    
    # Test inference if test audio provided
    if args.test_audio and model:
        test_inference(args.output, args.test_audio)
