from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.model_selection import train_test_split


@dataclass(frozen=True)
class ClassificationSplit:
    train_x: pd.DataFrame
    validation_x: pd.DataFrame
    test_x: pd.DataFrame
    train_y: pd.Series
    validation_y: pd.Series
    test_y: pd.Series
    cv_folds: int
    used_stratify: bool
    random_seed: int

    @property
    def split_sizes(self) -> dict[str, int]:
        return {
            "train": int(len(self.train_x)),
            "validation": int(len(self.validation_x)),
            "test": int(len(self.test_x)),
        }


def _can_stratify(labels: pd.Series) -> bool:
    if labels.nunique() < 2:
        return False
    return int(labels.value_counts().min()) >= 2


def _test_size(rows: int, fraction: float, minimum_rows: int) -> int:
    requested_rows = max(minimum_rows, int(round(rows * fraction)))
    requested_rows = min(requested_rows, rows - 1)
    return max(1, requested_rows)


def build_classification_split(
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    *,
    random_seed: int = 2026,
    test_fraction: float = 0.2,
    validation_fraction: float = 0.2,
    requested_cv_folds: int = 5,
) -> ClassificationSplit:
    if len(frame) < 6:
        raise ValueError("Need at least 6 rows to create train, validation, and test splits.")

    features = frame[feature_columns].copy()
    target = frame[target_column].copy()

    first_stratify = target if _can_stratify(target) else None
    test_size = _test_size(len(frame), test_fraction, minimum_rows=max(1, target.nunique()))
    train_validation_x, test_x, train_validation_y, test_y = train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=random_seed,
        stratify=first_stratify,
    )

    validation_ratio = validation_fraction / max(1e-6, 1.0 - test_fraction)
    second_stratify = train_validation_y if _can_stratify(train_validation_y) else None
    validation_size = _test_size(
        len(train_validation_x),
        validation_ratio,
        minimum_rows=max(1, train_validation_y.nunique()),
    )
    train_x, validation_x, train_y, validation_y = train_test_split(
        train_validation_x,
        train_validation_y,
        test_size=validation_size,
        random_state=random_seed,
        stratify=second_stratify,
    )

    min_class_count = int(train_y.value_counts().min()) if train_y.nunique() > 1 else 1
    cv_folds = max(2, min(requested_cv_folds, min_class_count))

    return ClassificationSplit(
        train_x=train_x.reset_index(drop=True),
        validation_x=validation_x.reset_index(drop=True),
        test_x=test_x.reset_index(drop=True),
        train_y=train_y.reset_index(drop=True),
        validation_y=validation_y.reset_index(drop=True),
        test_y=test_y.reset_index(drop=True),
        cv_folds=cv_folds,
        used_stratify=first_stratify is not None and second_stratify is not None,
        random_seed=random_seed,
    )
