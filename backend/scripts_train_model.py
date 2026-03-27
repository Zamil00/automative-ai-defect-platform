from __future__ import annotations

import random
from pathlib import Path

import cv2
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

OUTPUT_PATH = Path('data/models/defect_classifier.joblib')
FEATURE_NAMES = [
    'brightness_mean',
    'brightness_std',
    'edge_density',
    'dark_spot_ratio',
    'hotspot_ratio',
    'contour_count',
    'largest_contour_ratio',
    'texture_score',
    'defect_score',
]
LABELS = ['OK', 'Scratch', 'Crack', 'Stain', 'Dent']


def draw_synthetic(label: str, size: int = 160) -> np.ndarray:
    canvas = np.full((size, size, 3), random.randint(165, 215), dtype=np.uint8)
    noise = np.random.normal(0, 10, canvas.shape).astype(np.int16)
    canvas = np.clip(canvas.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    if label == 'Scratch':
        for _ in range(random.randint(1, 2)):
            cv2.line(
                canvas,
                (random.randint(10, size - 20), random.randint(10, size - 20)),
                (random.randint(10, size - 20), random.randint(10, size - 20)),
                (40, 40, 40),
                thickness=random.randint(1, 3),
            )
    elif label == 'Crack':
        points = [(random.randint(20, size - 20), random.randint(20, size - 20))]
        for _ in range(5):
            px, py = points[-1]
            points.append(
                (
                    min(size - 10, max(10, px + random.randint(-25, 25))),
                    min(size - 10, max(10, py + random.randint(-20, 20))),
                )
            )
        for p1, p2 in zip(points, points[1:]):
            cv2.line(canvas, p1, p2, (20, 20, 20), thickness=random.randint(2, 4))
    elif label == 'Stain':
        for _ in range(random.randint(2, 4)):
            cv2.circle(
                canvas,
                (random.randint(25, size - 25), random.randint(25, size - 25)),
                random.randint(10, 24),
                (50, 50, 50),
                thickness=-1,
            )
    elif label == 'Dent':
        center = (size // 2 + random.randint(-15, 15), size // 2 + random.randint(-15, 15))
        radius = random.randint(18, 34)
        cv2.circle(canvas, center, radius, (235, 235, 235), thickness=-1)
        cv2.circle(canvas, center, radius // 2, (120, 120, 120), thickness=-1)

    return canvas


def extract_features(image: np.ndarray) -> list[float]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
    _, dark_mask = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)
    _, bright_mask = cv2.threshold(gray, 190, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour_area = max((cv2.contourArea(c) for c in contours), default=0.0)

    brightness_mean = float(gray.mean())
    brightness_std = float(gray.std())
    edge_density = float((edges > 0).mean())
    dark_spot_ratio = float((dark_mask > 0).mean())
    hotspot_ratio = float((bright_mask > 0).mean())
    contour_count = int(len(contours))
    largest_contour_ratio = float(largest_contour_area / (gray.shape[0] * gray.shape[1]))
    texture_score = float(np.mean(np.abs(laplacian)) / 255.0)
    defect_score = float(min(1.0, edge_density * 2.8 + dark_spot_ratio * 2.1 + texture_score * 0.9))

    return [
        brightness_mean,
        brightness_std,
        edge_density,
        dark_spot_ratio,
        hotspot_ratio,
        contour_count,
        largest_contour_ratio,
        texture_score,
        defect_score,
    ]


def main() -> None:
    random.seed(42)
    np.random.seed(42)

    X, y = [], []
    for label in LABELS:
        for _ in range(50):
            X.append(extract_features(draw_synthetic(label)))
            y.append(label)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(n_estimators=80, max_depth=10, random_state=42)),
    ])
    pipeline.fit(X_train, y_train)
    score = pipeline.score(X_test, y_test)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            'model': pipeline,
            'feature_names': FEATURE_NAMES,
            'model_version': f'synthetic-rf-v2-acc-{score:.3f}',
            'holdout_accuracy': score,
        },
        OUTPUT_PATH,
    )
    print(f'Saved model to {OUTPUT_PATH} with holdout accuracy {score:.3f}')


if __name__ == '__main__':
    main()
