from __future__ import annotations

"""Shared settings for utils_zp commands."""

from pathlib import Path


TARGET_EXP_PATH = Path("/mnt/bn/motor-search2/wzp/repos/msr/exp")
TARGET_DATASET_VERSIONS_PATH = Path("/mnt/bn/motor-search2/wzp/repos/msr/data/dataset_versions.yaml")
TARGET_PRETRAINED_MODEL_VERSIONS_PATH = Path(
    "/mnt/bn/motor-search2/wzp/pretrained_models/model_versions.yaml"
)
TARGET_MSR_MODEL_PATH = Path("/mnt/bn/motor-search2/wzp/repos/motor_search_relevance/model")
TARGET_CHECKPOINT_VERSIONS_PATH = TARGET_MSR_MODEL_PATH / "checkpoint_versions.yaml"
