"""Inspector module for analyzing dataset schema, structure, and sampling without large downloads."""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd
from dotenv import load_dotenv
from huggingface_hub import HfApi, hf_hub_download

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()


class HFDatasetInspector:
    """Inspects file structure, readme cards, and sample rows of specific Hugging Face datasets."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("HF_TOKEN")
        self.api = HfApi(token=self.token)
        self.samples_dir = Path(__file__).resolve().parent.parent / "data" / "samples"
        self.samples_dir.mkdir(parents=True, exist_ok=True)

    def get_repo_files(self, repo_id: str) -> List[str]:
        """List files inside a dataset repo without downloading them."""
        try:
            files = self.api.list_repo_files(repo_id=repo_id, repo_type="dataset")
            return files
        except Exception as e:
            logger.error(f"Error listing files for {repo_id}: {e}")
            return []

    def get_dataset_card(self, repo_id: str) -> str:
        """Download and return the content of README.md (dataset card)."""
        try:
            readme_path = hf_hub_download(
                repo_id=repo_id,
                filename="README.md",
                repo_type="dataset",
                token=self.token
            )
            with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not fetch README for {repo_id}: {e}")
            return ""

    def download_sample(
        self,
        repo_id: str,
        n_rows: int = 20
    ) -> Optional[pd.DataFrame]:
        """
        Locates a data file (parquet, json, jsonl, csv) in the repo and reads a small sample.
        Saves the sample to data/samples/{sanitized_repo_id}_sample.csv.
        """
        files = self.get_repo_files(repo_id)
        # Prioritize formats: parquet -> jsonl -> json -> csv
        data_files = [f for f in files if f.endswith(".parquet")]
        if not data_files:
            data_files = [f for f in files if f.endswith(".jsonl")]
        if not data_files:
            data_files = [f for f in files if f.endswith(".json") and f != "dataset_info.json"]
        if not data_files:
            data_files = [f for f in files if f.endswith(".csv")]

        if not data_files:
            logger.info(f"No recognizable tabular data files (.parquet, .jsonl, .json, .csv) in {repo_id}.")
            return None

        target_file = data_files[0]
        logger.info(f"Sampling file from {repo_id}: {target_file}...")

        try:
            local_path = hf_hub_download(
                repo_id=repo_id,
                filename=target_file,
                repo_type="dataset",
                token=self.token
            )
            
            # Read first n rows according to format
            if target_file.endswith(".parquet"):
                df_full = pd.read_parquet(local_path)
                df_sample = df_full.head(n_rows)
            elif target_file.endswith(".jsonl"):
                df_sample = pd.read_json(local_path, lines=True, nrows=n_rows)
            elif target_file.endswith(".json"):
                try:
                    df_full = pd.read_json(local_path)
                    df_sample = df_full.head(n_rows)
                except Exception:
                    # Often HF datasets name jsonl files as .json
                    df_sample = pd.read_json(local_path, lines=True, nrows=n_rows)
            elif target_file.endswith(".csv"):
                df_sample = pd.read_csv(local_path, nrows=n_rows)
            else:
                return None

            # Save sample to data/samples/
            safe_name = repo_id.replace("/", "__")
            out_file = self.samples_dir / f"{safe_name}_sample.csv"
            df_sample.to_csv(out_file, index=False)
            logger.info(f"Sample with {len(df_sample)} rows and columns {list(df_sample.columns)} saved to {out_file}")
            return df_sample

        except Exception as e:
            logger.error(f"Failed to read/sample {target_file} for {repo_id}: {e}")
            return None


if __name__ == "__main__":
    inspector = HFDatasetInspector()
    test_repo = "CyberNative/Code_Vulnerability_Security_DPO"
    print(f"Testing inspector on: {test_repo}")
    files = inspector.get_repo_files(test_repo)
    print(f"Files found ({len(files)}): {files[:5]}")
    sample = inspector.download_sample(test_repo, n_rows=5)
    if sample is not None:
        print("\nColumnas del dataset:")
        print(sample.columns.tolist())
        print("\nPrimeras 2 filas:")
        print(sample.head(2).to_dict(orient="records"))
