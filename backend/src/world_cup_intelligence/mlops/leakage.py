from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd


@dataclass(frozen=True)
class LeakageReport:
    duplicate_rows: int
    duplicate_feature_rows: int
    constant_features: list[str]
    leaked_feature_names: list[str]
    null_feature_counts: dict[str, int]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def inspect_supervised_frame(frame: pd.DataFrame, feature_columns: list[str], target_column: str) -> LeakageReport:
    null_feature_counts = {
        column: int(frame[column].isna().sum()) for column in feature_columns if int(frame[column].isna().sum()) > 0
    }
    return LeakageReport(
        duplicate_rows=int(frame.duplicated().sum()),
        duplicate_feature_rows=int(frame[feature_columns].duplicated().sum()),
        constant_features=[column for column in feature_columns if frame[column].nunique(dropna=False) <= 1],
        leaked_feature_names=[column for column in feature_columns if column == target_column],
        null_feature_counts=null_feature_counts,
    )
