"""Extractor module for querying Hugging Face API and collecting dataset metadata."""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd
from dotenv import load_dotenv
from huggingface_hub import HfApi

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Load optional .env
load_dotenv()


class HFSecurityExtractor:
    """Extracts security-related dataset metadata from Hugging Face Hub."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("HF_TOKEN")
        self.api = HfApi(token=self.token)
        self.data_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def fetch_datasets(
        self,
        filter_tag: str = "security",
        sort_by: str = "downloads",
        limit: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Fetch dataset metadata matching the given filter tag.
        
        Args:
            filter_tag: Tag to filter datasets by (e.g. 'security', 'cybersecurity').
            sort_by: Field to sort by ('downloads', 'likes', 'last_modified', 'created_at', 'trending_score').
            limit: Maximum number of datasets to retrieve.
        """
        logger.info(f"Querying HF API: filter='{filter_tag}', sort='{sort_by}', limit={limit}...")
        
        expand_fields = [
            "author",
            "cardData",
            "createdAt",
            "description",
            "downloads",
            "downloadsAllTime",
            "gated",
            "lastModified",
            "likes",
            "private",
            "tags",
            "trendingScore",
        ]

        datasets_iter = self.api.list_datasets(
            filter=filter_tag,
            sort=sort_by,
            limit=limit,
            expand=expand_fields
        )

        records = []
        for d in datasets_iter:
            # Handle potential None or missing attributes gracefully
            created_at = d.created_at.isoformat() if getattr(d, "created_at", None) else None
            last_modified = d.last_modified.isoformat() if getattr(d, "last_modified", None) else None
            
            # Detect pipeline_tag from tags or attributes
            pipeline_tag = getattr(d, "pipeline_tag", None)
            tags = getattr(d, "tags", []) or []
            if not pipeline_tag:
                for tag in tags:
                    if tag.startswith("pipeline_tag:"):
                        pipeline_tag = tag.split(":", 1)[1]
                        break

            # Detect format / files info if available
            has_parquet = any("format:parquet" in t or "parquet" in t.lower() for t in tags)
            
            records.append({
                "id": d.id,
                "author": getattr(d, "author", d.id.split("/")[0] if "/" in d.id else None),
                "name": d.id.split("/")[-1] if "/" in d.id else d.id,
                "downloads_30d": getattr(d, "downloads", 0) or 0,
                "downloads_all_time": getattr(d, "downloads_all_time", None) or getattr(d, "downloadsAllTime", None),
                "likes": getattr(d, "likes", 0) or 0,
                "created_at": created_at,
                "last_modified": last_modified,
                "tags": tags,
                "pipeline_tag": pipeline_tag,
                "has_parquet": has_parquet,
                "private": getattr(d, "private", False),
                "gated": getattr(d, "gated", False),
                "description": getattr(d, "description", None)
            })

        logger.info(f"Extracted metadata for {len(records)} datasets.")
        return records

    def fetch_multi_tag(
        self,
        tags: Optional[List[str]] = None,
        limit_per_tag: int = 300
    ) -> pd.DataFrame:
        """
        Fetch datasets across multiple security tags and deduplicate by dataset ID.
        """
        if tags is None:
            tags = ["security", "cybersecurity", "vulnerability"]

        all_records: Dict[str, Dict[str, Any]] = {}
        for tag in tags:
            try:
                results = self.fetch_datasets(filter_tag=tag, limit=limit_per_tag)
                for item in results:
                    item_id = item["id"]
                    if item_id not in all_records:
                        item["queried_tags"] = [tag]
                        all_records[item_id] = item
                    else:
                        if tag not in all_records[item_id].get("queried_tags", []):
                            all_records[item_id]["queried_tags"].append(tag)
            except Exception as e:
                logger.error(f"Error querying tag '{tag}': {e}")

        df = pd.DataFrame(list(all_records.values()))
        if not df.empty:
            # Sort by downloads_30d descending
            df = df.sort_values(by="downloads_30d", ascending=False).reset_index(drop=True)
        return df

    def save_metadata(
        self,
        df: pd.DataFrame,
        base_filename: str = "security_datasets_metadata"
    ) -> Dict[str, Path]:
        """Save DataFrame to CSV and JSON formats in data/raw/."""
        csv_path = self.data_dir / f"{base_filename}.csv"
        json_path = self.data_dir / f"{base_filename}.json"

        # CSV
        df.to_csv(csv_path, index=False)
        
        # JSON (orient='records' with readable formatting)
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(df.to_json(orient="records", indent=2, date_format="iso"))

        logger.info(f"Saved CSV snapshot: {csv_path} ({len(df)} rows)")
        logger.info(f"Saved JSON snapshot: {json_path}")
        return {"csv": csv_path, "json": json_path}


if __name__ == "__main__":
    extractor = HFSecurityExtractor()
    df_datasets = extractor.fetch_multi_tag()
    saved = extractor.save_metadata(df_datasets)
    print("\n--- RESUMEN DE EXTRACCIÓN ---")
    print(f"Total datasets encontrados: {len(df_datasets)}")
    if not df_datasets.empty:
        print("\nTop 5 por descargas recientes:")
        print(df_datasets[["id", "downloads_30d", "likes", "last_modified"]].head(5).to_string())
