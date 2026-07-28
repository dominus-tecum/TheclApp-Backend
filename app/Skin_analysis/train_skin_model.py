#!/usr/bin/env python3
"""
Windows-friendly, robust training script for skin image classification using EfficientNetV2B0.

Key qualities:
- Environment variables that must be set before importing TensorFlow are applied early.
- Robust Windows-safe backup and file-move retry logic.
- Safe creation of a "latest" junction/hardlink with sensible fallbacks.
- Validation split (so TEST_DIR can be kept as a holdout).
- Separate checkpoints for feature-extraction and fine-tuning, timestamped artifact names.
- Callbacks: EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard, CSVLogger.
- Class weights computed to mitigate imbalance.
- Seeds for reproducibility (best-effort; true determinism depends on TF ops & versions).
- Saves model summary, training config, JSON+pickle histories, and test evaluation.
- Uses logging (instead of prints) for clearer multi-run records.

Notes:
- For deterministic hashing set PYTHONHASHSEED before process start if strict determinism is required.
- Some TensorFlow environment options must be set before importing TensorFlow (this script sets a few early;
  if you require other flags, provide them via environment before running).
- mklink may require Developer Mode or elevated privileges on Windows. This script falls back to copy/hardlink.
"""

# --- Early argument parsing for environment variables that must be set before importing TensorFlow ---
import os
import argparse as _argparse

_early_parser = _argparse.ArgumentParser(add_help=False)
_early_parser.add_argument("--seed", type=int, default=42, help="Random seed (early parsing)")
_early_parser.add_argument("--tf_gpu_thread_mode", type=str, default="gpu_private",
                           help="Optional TF_GPU_THREAD_MODE (set before TF import)")
_early_parser.add_argument("--tf_gpu_thread_count", type=str, default="1",
                           help="Optional TF_GPU_THREAD_COUNT (set before TF import)")
_early_args, _remaining_argv = _early_parser.parse_known_args()

# Set environment variables now (before importing tensorflow)
os.environ.setdefault("PYTHONHASHSEED", str(_early_args.seed))
os.environ.setdefault("TF_GPU_THREAD_MODE", str(_early_args.tf_gpu_thread_mode))
os.environ.setdefault("TF_GPU_THREAD_COUNT", str(_early_args.tf_gpu_thread_count))

# Now import the heavy libraries
import sys
import time
import math
import shutil
import json
import pickle
import random
import datetime
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

import numpy as np
import logging

# Import TensorFlow after the early env setup
import tensorflow as tf
import argparse
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetV2B0
from tensorflow.keras.callbacks import (
    EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard, CSVLogger
)
from sklearn.utils.class_weight import compute_class_weight

# -------------------------
# Logging configuration
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("train_skin_model")

# -------------------------
# Utility functions
# -------------------------
def set_seed(seed: int):
    """Set seeds for reproducibility (best-effort)."""
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)
    logger.info("Random seeds set (best-effort). Note: full determinism depends on TF ops and environment.")

def safe_move_with_retries(src: Path, dst: Path, max_retries: int = 3, delay: float = 1.0) -> bool:
    """Move a file or directory with simple retry logic to handle Windows file locks."""
    for attempt in range(1, max_retries + 1):
        try:
            # Ensure parent exists
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            logger.debug("Moved %s -> %s", src, dst)
            return True
        except PermissionError as e:
            logger.warning("PermissionError moving %s -> %s (attempt %d/%d): %s", src, dst, attempt, max_retries, e)
            if attempt < max_retries:
                time.sleep(delay)
            else:
                return False
        except Exception as e:
            logger.exception("Unexpected error moving %s -> %s: %s", src, dst, e)
            return False
    return False

def safe_backup(base_dir: Path, targets, max_retries: int = 3) -> Optional[Path]:
    """Move existing target files/folders into a timestamped backup folder (Windows safe)."""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = base_dir / f"backup_{ts}"
    moved_any = False
    for t in targets:
        p = base_dir / t
        if p.exists():
            dest = backup_dir / p.name
            success = safe_move_with_retries(p, dest, max_retries=max_retries)
            if success:
                moved_any = True
                logger.info("Backed up %s -> %s", p, dest)
            else:
                logger.warning("Failed to backup %s", p)
    return backup_dir if moved_any else None

def save_json_serializable(obj: Any, path: Path):
    """Save an object to JSON after converting numpy/Path types to native types."""
    def convert(o):
        if isinstance(o, Path):
            return str(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, (np.integer, np.floating)):
            return o.item()
        if isinstance(o, dict):
            return {convert(k): convert(v) for k, v in o.items()}
        if isinstance(o, list):
            return [convert(x) for x in o]
        return o
    with open(path, "w", encoding="utf-8") as f:
        json.dump(convert(obj), f, indent=2, ensure_ascii=False)
    logger.info("Wrote JSON to %s", path)

def count_images_per_class(directory: Path) -> Dict[str, int]:
    """Count image files per class folder using case-insensitive suffix check (no double counting)."""
    valid_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    counts = {}
    for class_dir in directory.iterdir():
        if not class_dir.is_dir():
            continue
        n = 0
        for file in class_dir.rglob('*'):
            if file.is_file() and file.suffix.lower() in valid_exts:
                n += 1
        counts[class_dir.name] = n
    return counts

def create_windows_link_or_copy(source: Path, link: Path) -> bool:
    """
    Try to create a link for the latest model:
    - If source is a file: try hard link (os.link) then fallback to copy.
    - If source is a directory: try mklink /J (junction) then fallback to copytree.
    Returns True on success, False otherwise.
    """
    try:
        # Remove existing target if present
        if link.exists() or link.is_symlink():
            try:
                if link.is_dir() and not link.is_symlink():
                    shutil.rmtree(link)
                else:
                    link.unlink()
            except Exception as e:
                logger.debug("Could not remove existing link %s: %s", link, e)
                # continue; may still succeed later

        src = Path(source)
        if not src.exists():
            logger.warning("Source for link does not exist: %s", src)
            return False

        if src.is_file():
            try:
                os.link(str(src), str(link))
                logger.info("Created hard link %s -> %s", link, src)
                return True
            except Exception:
                try:
                    shutil.copy2(src, link)
                    logger.info("Copied file as fallback: %s", link)
                    return True
                except Exception as e:
                    logger.error("Failed to copy file fallback: %s", e)
                    return False

        if src.is_dir():
            # Use mklink /J for junctions (requires shell); if it fails, copytree
            cmd = f'mklink /J "{str(link)}" "{str(src)}"'
            try:
                subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                logger.info("Created junction %s -> %s", link, src)
                return True
            except subprocess.CalledProcessError as e:
                logger.warning("mklink junction failed: %s; falling back to copytree", e)
                try:
                    shutil.copytree(src, link)
                    logger.info("Copied directory as fallback: %s", link)
                    return True
                except Exception as copy_err:
                    logger.error("Failed to copy directory fallback: %s", copy_err)
                    return False
        logger.warning("Source is neither file nor directory: %s", src)
        return False
    except Exception as e:
        logger.exception("Unexpected error creating link: %s", e)
        return False

def save_model_with_retry(model: tf.keras.Model, path: Path, retries: int = 3, delay: float = 1.0) -> bool:
    """Attempt to save the model, retrying on failure (useful on Windows with file locks)."""
    for i in range(1, retries + 1):
        try:
            model.save(path)
            logger.info("Model saved to %s", path)
            return True
        except Exception as e:
            logger.warning("model.save failed (attempt %d/%d): %s", i, retries, e)
            if i < retries:
                time.sleep(delay)
    logger.error("Failed to save model to %s after %d attempts", path, retries)
    return False

def setup_gpu_memory_growth() -> int:
    """Turn on memory growth for available GPUs (Windows safe API). Returns number of GPUs."""
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if not gpus:
        logger.info("No GPUs detected; training will run on CPU.")
        return 0
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logger.info("Enabled TensorFlow GPU memory growth; %d GPU(s) available", len(gpus))
        return len(gpus)
    except RuntimeError as e:
        logger.warning("Could not set memory growth for GPUs: %s", e)
        return len(gpus)

# -------------------------
# Main training flow
# -------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Windows-optimized skin image classification training (EfficientNetV2B0)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("--base_dir", type=str,
                        default=r"D:\PWA and MobileAPP\hospiapp for web\BACKEND\ModelTraining\combined_skin_analysis_dataset2",
                        help="Base dataset/artifact directory (contains train/ and optional test/)")
    parser.add_argument("--img_size", type=int, default=224, help="Square input image size")
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--validation_split", type=float, default=0.2)
    parser.add_argument("--epochs_feature", type=int, default=20)
    parser.add_argument("--epochs_finetune", type=int, default=10)
    parser.add_argument("--learning_rate_feature", type=float, default=1e-3)
    parser.add_argument("--learning_rate_finetune", type=float, default=1e-5)
    parser.add_argument("--unfreeze_top_n", type=int, default=20,
                        help="Number of top layers in base model to unfreeze during fine-tuning. If <=0, unfreeze all.")
    parser.add_argument("--dropout", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=_early_args.seed)
    parser.add_argument("--cleanup", action="store_true", help="Backup previous artifacts in base_dir before running.")
    parser.add_argument("--early_stop_patience", type=int, default=3)
    parser.add_argument("--create_latest_link", action="store_true",
                        help="Create or update a 'skin_model_finetuned_latest' link/junction to the latest model.")
    args = parser.parse_args()

    # Configure logging level (could be made into an arg)
    logger.setLevel(logging.INFO)

    # Resolve paths
    base_dir = Path(args.base_dir).expanduser().resolve()
    train_dir = base_dir / "train"
    test_dir = base_dir / "test"

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    img_size = (args.img_size, args.img_size)

    checkpoint_dir = base_dir / "checkpoints"
    log_dir = base_dir / "logs" / timestamp
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    feature_ckpt = checkpoint_dir / f"feature_stage_best_{timestamp}.keras"
    finetune_ckpt = checkpoint_dir / f"finetune_stage_best_{timestamp}.keras"
    final_model_path = base_dir / f"skin_model_finetuned_{timestamp}.keras"
    class_json = base_dir / "class_indices.json"
    history_pkl = base_dir / f"training_history_{timestamp}.pkl"
    history_json = base_dir / f"training_history_{timestamp}.json"
    model_summary_txt = base_dir / f"model_summary_{timestamp}.txt"
    training_config_json = base_dir / f"training_config_{timestamp}.json"
    csv_log_path = log_dir / f"training_log_{timestamp}.csv"

    # Artifact list for optional backup
    artifact_files = [
        "skin_model_finetuned.keras",
        "best_model_feature.keras",
        "best_model_finetune.keras",
        "training_history.pkl",
        "training_history.json",
        "class_indices.json",
        "test_evaluation.json",
        "model_summary.txt",
    ]
    artifact_folders = ["logs", "checkpoints"]

    logger.info("Starting training run (timestamp=%s)", timestamp)
    logger.info("Base dir: %s", base_dir)

    # Check directories
    if not base_dir.exists():
        logger.error("Base directory does not exist: %s", base_dir)
        sys.exit(1)
    if not train_dir.exists():
        logger.error("Train directory does not exist: %s", train_dir)
        sys.exit(1)

    # Optional safe backup
    if args.cleanup:
        logger.info("Backing up previous artifacts (if present)...")
        backup = safe_backup(base_dir, artifact_files + artifact_folders)
        if backup:
            logger.info("Artifacts moved to backup: %s", backup)
        else:
            logger.info("No artifacts found to backup.")

    # Seeds
    set_seed(args.seed)

    # GPU setup
    gpu_count = setup_gpu_memory_growth()

    # Dataset diagnostics
    logger.info("Inspecting training dataset directory: %s", train_dir)
    train_classes = sorted([p.name for p in train_dir.iterdir() if p.is_dir()])
    counts = count_images_per_class(train_dir)
    total_train = sum(counts.values()) if counts else 0
    for cname in train_classes:
        logger.info("Class %s: %d images", cname, counts.get(cname, 0))
    logger.info("Total training images: %d", total_train)

    if test_dir.exists() and any(test_dir.iterdir()):
        test_counts = count_images_per_class(test_dir)
        total_test = sum(test_counts.values())
        logger.info("Test set detected: %d images across %d classes", total_test, len(test_counts))
    else:
        logger.info("No test directory found or empty; final evaluation will be skipped.")

    # Data generators (with validation split)

    from tensorflow.keras.applications.efficientnet_v2 import preprocess_input

    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,  # ← USE THIS INSTEAD!
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest',
        validation_split=args.validation_split
    )

    val_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,  # ← USE THIS INSTEAD!
        validation_split=args.validation_split
    )

    seed = args.seed
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=img_size,
        batch_size=args.batch_size,
        class_mode='categorical',
        color_mode='rgb',
        subset='training',
        shuffle=True,
        seed=seed
    )
    val_generator = val_datagen.flow_from_directory(
        train_dir,
        target_size=img_size,
        batch_size=args.batch_size,
        class_mode='categorical',
        color_mode='rgb',
        subset='validation',
        shuffle=False,
        seed=seed
    )

    # ⭐⭐⭐ CRITICAL DEBUG CODE - DATA PIPELINE ⭐⭐⭐
    logger.info("=== DEBUGGING DATA PIPELINE ===")
    
    # Check training data
    logger.info("Checking training data generator...")
    for images, labels in train_generator:
        logger.info("TRAINING DATA:")
        logger.info("  Image shape: %s", images.shape)
        logger.info("  Image dtype: %s", images.dtype)
        logger.info("  Pixel range: %.3f to %.3f", np.min(images), np.max(images))
        logger.info("  Label shape: %s", labels.shape)
        logger.info("  Label range: %d to %d", np.min(labels), np.max(labels))
        
        # Check if labels are properly one-hot encoded
        unique_labels = np.unique(np.argmax(labels, axis=1))
        logger.info("  Unique labels in batch: %s", unique_labels)
        
        # Check first image details
        first_image = images[0]
        logger.info("  First image - Min: %.3f, Max: %.3f, Mean: %.3f", 
                   np.min(first_image), np.max(first_image), np.mean(first_image))
        
        # Check if we have the expected number of classes
        logger.info("  Number of classes in batch labels: %d", labels.shape[1])
        break
    
    # Check validation data
    logger.info("Checking validation data generator...")
    for images, labels in val_generator:
        logger.info("VALIDATION DATA:")
        logger.info("  Image shape: %s", images.shape)
        logger.info("  Pixel range: %.3f to %.3f", np.min(images), np.max(images))
        logger.info("  Label shape: %s", labels.shape)
        break
    
    # Reset generators after inspection
    train_generator.on_epoch_end()
    val_generator.on_epoch_end()
    logger.info("=== END DATA DEBUGGING ===")
    # ⭐⭐⭐ END CRITICAL DEBUG CODE ⭐⭐⭐

    test_generator = None
    if test_dir.exists() and any(test_dir.iterdir()):
        test_datagen = ImageDataGenerator(
            preprocessing_function=preprocess_input  # ← USE THIS INSTEAD!
        
        )

    # Save class indices
    with open(class_json, "w", encoding="utf-8") as f:
        json.dump(train_generator.class_indices, f, indent=2, ensure_ascii=False)
    logger.info("Saved class indices to %s", class_json)

    # Class weights
    train_labels = train_generator.classes
    classes = np.unique(train_labels)
    class_weights_vals = compute_class_weight(class_weight='balanced', classes=classes, y=train_labels)
    class_weights = {int(c): float(w) for c, w in zip(classes, class_weights_vals)}
    logger.info("Computed class weights: %s", class_weights)

    # Build model (feature extraction)
    logger.info("Building EfficientNetV2B0 base model (imagenet weights)")
    base_model = EfficientNetV2B0(include_top=False, weights='imagenet', input_shape=(img_size[0], img_size[1], 3))
    base_model.trainable = False

    # ⭐⭐⭐ IMPROVED MODEL ARCHITECTURE ⭐⭐⭐
    logger.info("Creating enhanced model architecture...")
    inputs = tf.keras.Input(shape=(img_size[0], img_size[1], 3))
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(512, activation='relu')(x)
    x = layers.Dropout(args.dropout)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(args.dropout * 0.7)(x)
    outputs = layers.Dense(train_generator.num_classes, activation='softmax')(x)
    
    model = tf.keras.Model(inputs, outputs)
    # ⭐⭐⭐ END IMPROVED ARCHITECTURE ⭐⭐⭐

    # Compile feature-stage model
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=args.learning_rate_feature),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    # ⭐⭐⭐ CRITICAL DEBUG CODE - MODEL VERIFICATION ⭐⭐⭐
    logger.info("=== DEBUGGING MODEL ===")
    logger.info("Model output shape: %s", model.output_shape)
    logger.info("Number of classes: %d", train_generator.num_classes)
    logger.info("Class indices: %s", train_generator.class_indices)
    
    # Test model on one batch to verify forward pass
    logger.info("Testing model forward pass...")
    for images, labels in train_generator:
        predictions = model.predict(images[:2], verbose=0)  # Predict on first 2 images
        logger.info("Prediction shape: %s", predictions.shape)
        logger.info("Sample predictions:")
        for i in range(2):
            logger.info("  Image %d - Prediction: %s", i, predictions[i])
            logger.info("  Image %d - Argmax prediction: %d", i, np.argmax(predictions[i]))
            logger.info("  Image %d - True label: %s", i, labels[i])
            logger.info("  Image %d - Argmax true label: %d", i, np.argmax(labels[i]))
        break
    
    # Verify the model can learn (small sanity check)
    logger.info("Running quick learning sanity check...")
    test_loss_before = model.evaluate(val_generator, steps=1, verbose=0)
    logger.info("Initial validation loss: %.4f, accuracy: %.4f", test_loss_before[0], test_loss_before[1])
    logger.info("=== END MODEL DEBUGGING ===")
    # ⭐⭐⭐ END CRITICAL DEBUG CODE ⭐⭐⭐

    # Save model summary and training config
    with open(model_summary_txt, "w", encoding="utf-8") as f:
        model.summary(print_fn=lambda s: f.write(s + "\n"))
    logger.info("Model summary saved to %s", model_summary_txt)

    training_config = {
        "timestamp": timestamp,
        "platform": "windows" if os.name == "nt" else "posix",
        "gpu_count": gpu_count,
        "base_dir": str(base_dir),
        "img_size": img_size,
        "batch_size": args.batch_size,
        "validation_split": args.validation_split,
        "seed": args.seed,
        "epochs_feature": args.epochs_feature,
        "epochs_finetune": args.epochs_finetune,
        "learning_rate_feature": args.learning_rate_feature,
        "learning_rate_finetune": args.learning_rate_finetune,
        "unfreeze_top_n": args.unfreeze_top_n,
        "dropout": args.dropout,
        "early_stop_patience": args.early_stop_patience,
        "train_samples": train_generator.samples,
        "class_weights": class_weights,
        "class_indices": train_generator.class_indices
    }
    save_json_serializable(training_config, Path(training_config_json))

    # Callbacks
    early_stop = EarlyStopping(monitor='val_loss', patience=args.early_stop_patience, restore_best_weights=True, verbose=1)
    checkpoint_feat = ModelCheckpoint(str(feature_ckpt), save_best_only=True, monitor='val_loss', verbose=1)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2, min_lr=1e-7, verbose=1)
    tensorboard_cb = TensorBoard(log_dir=str(log_dir), histogram_freq=1, write_graph=True)
    csv_logger = CSVLogger(str(csv_log_path), append=True)

    callbacks_feat = [early_stop, checkpoint_feat, reduce_lr, tensorboard_cb, csv_logger]

    # Steps calculation (avoid zero)
    steps_per_epoch = max(1, math.ceil(train_generator.samples / args.batch_size))
    validation_steps = max(1, math.ceil(val_generator.samples / args.batch_size))

    logger.info("Training configuration: steps_per_epoch=%d, validation_steps=%d", steps_per_epoch, validation_steps)

    # Feature extraction training
    logger.info("Starting feature-extraction training for up to %d epochs", args.epochs_feature)
    history_feat = model.fit(
        train_generator,
        epochs=args.epochs_feature,
        validation_data=val_generator,
        callbacks=callbacks_feat,
        class_weight=class_weights,
        steps_per_epoch=steps_per_epoch,
        validation_steps=validation_steps,
        verbose=1,
              
    )

    # Fine-tuning setup
    logger.info("Preparing for fine-tuning stage (unfreeze_top_n=%s)", args.unfreeze_top_n)
    if args.unfreeze_top_n is None or args.unfreeze_top_n <= 0:
        base_model.trainable = True
        logger.info("Unfreezing entire base model for fine-tuning.")
    else:
        base_model.trainable = True
        total_layers = len(base_model.layers)
        n = int(args.unfreeze_top_n)
        keep_frozen = max(0, total_layers - n)
        for i, layer in enumerate(base_model.layers):
            layer.trainable = (i >= keep_frozen)
        logger.info("Unfroze top %d layers (frozen first %d layers)", n, keep_frozen)

    # Recompile with lower LR
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=args.learning_rate_finetune),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    checkpoint_ft = ModelCheckpoint(str(finetune_ckpt), save_best_only=True, monitor='val_loss', verbose=1)
    early_stop_ft = EarlyStopping(monitor='val_loss', patience=args.early_stop_patience, restore_best_weights=True, verbose=1)
    reduce_lr_ft = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2, min_lr=1e-8, verbose=1)
    callbacks_ft = [early_stop_ft, checkpoint_ft, reduce_lr_ft, tensorboard_cb, csv_logger]

    logger.info("Starting fine-tuning for up to %d epochs", args.epochs_finetune)
    history_ft = model.fit(
        train_generator,
        epochs=args.epochs_finetune,
        validation_data=val_generator,
        callbacks=callbacks_ft,
        class_weight=class_weights,
        steps_per_epoch=steps_per_epoch,
        validation_steps=validation_steps,
        verbose=1,
    )

    # Save final model (with retry)
    saved_ok = save_model_with_retry(model, final_model_path)
    if not saved_ok:
        logger.error("Failed to save final model to %s", final_model_path)

    # Save histories
    history_combined = {
        "feature_extraction": history_feat.history,
        "fine_tuning": history_ft.history,
        "timestamp": timestamp
    }
    with open(history_pkl, "wb") as f:
        pickle.dump(history_combined, f)
    save_json_serializable(history_combined, Path(history_json))
    logger.info("Saved training history to %s and %s", history_pkl, history_json)

    # Final evaluation on test set if available
    if test_generator is not None:
        logger.info("Evaluating model on held-out test set...")
        test_results = model.evaluate(test_generator, verbose=1)
        metrics = dict(zip(model.metrics_names, test_results))
        metrics['timestamp'] = timestamp
        metrics['test_samples'] = test_generator.samples
        metrics['platform'] = "windows" if os.name == "nt" else "posix"
        save_json_serializable(metrics, base_dir / f"test_evaluation_{timestamp}.json")
        logger.info("Saved test evaluation results.")

    # Optionally create/update latest model link/junction
    if args.create_latest_link:
        latest_link = base_dir / "skin_model_finetuned_latest"
        # If we saved final model, prefer that; else fall back to finetune checkpoint
        src_candidate = final_model_path if final_model_path.exists() else (finetune_ckpt if finetune_ckpt.exists() else None)
        if src_candidate:
            create_windows_link_or_copy(src_candidate, latest_link)
            logger.info("Updated latest model link to %s", latest_link)
        else:
            logger.warning("No model file found to link for latest_model.")

    logger.info("Training run complete. Artifacts saved in %s", base_dir)
    logger.info("TensorBoard logs: tensorboard --logdir \"%s\"", base_dir / "logs")

if __name__ == "__main__":
    main()