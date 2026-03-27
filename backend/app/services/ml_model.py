from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import joblib
import numpy as np
from PIL import Image

from app.core.config import get_settings

LABELS = ['Crack', 'Dent', 'OK', 'Scratch', 'Stain']


@dataclass
class PredictionBundle:
    label: str
    confidence: float
    model_version: str
    metrics: dict
    overlay_path: str
    mask_path: str
    defect_score: float


class DefectModelService:
    def __init__(self) -> None:
        settings = get_settings()
        self.model_path = Path(settings.model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(
                f'Model artifact not found at {self.model_path}. Run scripts_train_model.py first.'
            )
        artifact = joblib.load(self.model_path)
        self.model = artifact['model']
        self.feature_names = artifact['feature_names']
        self.model_version = artifact.get('model_version', 'synthetic-rf-v3-localization')

    def extract_features(self, image_path: Path) -> tuple[np.ndarray, dict, np.ndarray, np.ndarray, np.ndarray]:
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError('Image could not be loaded for analysis.')

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        edges = cv2.Canny(blurred, 40, 120)
        laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
        _, dark_mask = cv2.threshold(gray, 135, 255, cv2.THRESH_BINARY_INV)
        _, bright_mask = cv2.threshold(gray, 190, 255, cv2.THRESH_BINARY)

        combined = cv2.bitwise_or(edges, dark_mask)
        kernel = np.ones((3, 3), np.uint8)
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=2)
        combined = cv2.dilate(combined, kernel, iterations=2)

        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        image_area = gray.shape[0] * gray.shape[1]
        filtered_contours = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            area_ratio = area / float(image_area)
            if 0.00015 < area_ratio < 0.2:
                filtered_contours.append(cnt)

        mask = np.zeros_like(gray)
        if filtered_contours:
            cv2.drawContours(mask, filtered_contours, -1, 255, thickness=cv2.FILLED)

        brightness_mean = float(gray.mean())
        brightness_std = float(gray.std())
        edge_density = float((edges > 0).mean())
        dark_spot_ratio = float((dark_mask > 0).mean())
        hotspot_ratio = float((bright_mask > 0).mean())
        contour_count = int(len(filtered_contours))
        largest_contour_area = max((cv2.contourArea(c) for c in filtered_contours), default=0.0)
        largest_contour_ratio = float(largest_contour_area / image_area) if image_area else 0.0
        texture_score = float(np.mean(np.abs(laplacian)) / 255.0)
        mask_pixel_ratio = float((mask > 0).mean())
        defect_score = float(min(1.0, edge_density * 2.4 + dark_spot_ratio * 1.8 + texture_score * 0.8 + mask_pixel_ratio * 2.0))

        feature_dict = {
            'brightness_mean': brightness_mean,
            'brightness_std': brightness_std,
            'edge_density': edge_density,
            'dark_spot_ratio': dark_spot_ratio,
            'hotspot_ratio': hotspot_ratio,
            'contour_count': contour_count,
            'largest_contour_ratio': largest_contour_ratio,
            'texture_score': texture_score,
            'mask_pixel_ratio': mask_pixel_ratio,
            'defect_score': defect_score,
        }

        vector = np.array(
            [feature_dict[name] for name in self.feature_names if name in feature_dict],
            dtype=float,
        ).reshape(1, -1)

        return vector, feature_dict, image, mask, filtered_contours

    def build_overlay_and_mask(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        contours: list[np.ndarray],
    ) -> tuple[Image.Image, Image.Image]:
        overlay = image.copy()

        heat = np.zeros_like(image)
        heat[mask > 0] = (30, 70, 255)  # orange-red in BGR
        blended = cv2.addWeighted(image, 0.72, heat, 0.55, 0)

        if contours:
            cv2.drawContours(blended, contours, -1, (0, 255, 255), 2)
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(blended, (x, y), (x + w, y + h), (0, 180, 255), 2)

        mask_preview = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        if contours:
            cv2.drawContours(mask_preview, contours, -1, (0, 255, 255), 2)

        overlay_image = Image.fromarray(cv2.cvtColor(blended, cv2.COLOR_BGR2RGB))
        mask_image = Image.fromarray(cv2.cvtColor(mask_preview, cv2.COLOR_BGR2RGB))
        return overlay_image, mask_image

    def predict(self, image_path: Path, overlay_output_path: Path, mask_output_path: Path) -> PredictionBundle:
        vector, metrics, image, mask, contours = self.extract_features(image_path)
        probabilities = self.model.predict_proba(vector)[0]
        label = self.model.predict(vector)[0]
        confidence = float(np.max(probabilities))

        overlay_image, mask_image = self.build_overlay_and_mask(image, mask, contours)
        overlay_image.save(overlay_output_path)
        mask_image.save(mask_output_path)

        return PredictionBundle(
            label=label,
            confidence=confidence,
            model_version=self.model_version,
            metrics=metrics,
            overlay_path=str(overlay_output_path),
            mask_path=str(mask_output_path),
            defect_score=metrics['defect_score'],
        )