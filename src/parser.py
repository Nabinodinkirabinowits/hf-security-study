"""Parser and categorization module for security datasets."""

import re
from typing import List, Dict, Any, Optional
import pandas as pd


CATEGORIES = {
    "prompt_injection_safety": [
        "jailbreak", "prompt-injection", "prompt_injection", "red-teaming",
        "redteaming", "safety", "harmful", "adversarial", "guardrail", "defense"
    ],
    "code_vulnerability": [
        "vulnerability", "cve", "cwe", "vuln", "secure-code", "secure_coding",
        "patch", "exploit", "buffer-overflow", "injection"
    ],
    "threat_intel_mitre": [
        "mitre", "att&ck", "ttp", "threat-intel", "cyber-threat", "apt", "stix"
    ],
    "network_malware_logs": [
        "malware", "ransomware", "intrusion", "ids", "nids", "pcap",
        "network-traffic", "phishing", "firewall", "log"
    ],
    "dpo_rlhf_alignment": [
        "dpo", "rlhf", "preference", "chosen", "rejected", "alignment"
    ]
}


def classify_dataset(row: pd.Series) -> List[str]:
    """
    Classifies a dataset into one or more cybersecurity categories
    based on its id, tags, and description.
    """
    text_corpus = f"{row.get('id', '')} {' '.join(row.get('tags', []) or [])} {row.get('description', '')}".lower()
    
    assigned = []
    for cat_name, keywords in CATEGORIES.items():
        for kw in keywords:
            # Match keyword as word or substring with boundary
            if re.search(r'\b' + re.escape(kw) + r'\b', text_corpus):
                assigned.append(cat_name)
                break

    if not assigned:
        assigned.append("other_security")
    return assigned


def enrich_dataset_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds analytical columns to the metadata DataFrame:
    - categories: List of matched categories
    - primary_category: Main dominant category
    - downloads_per_like: Ratio downloads / (likes + 1)
    - days_since_last_modified: Time freshness indicator
    """
    if df.empty:
        return df

    df_copy = df.copy()

    # Classification
    df_copy["categories"] = df_copy.apply(classify_dataset, axis=1)
    df_copy["primary_category"] = df_copy["categories"].apply(lambda cats: cats[0] if cats else "other")

    # Metrics
    df_copy["downloads_per_like"] = df_copy["downloads_30d"] / (df_copy["likes"] + 1)
    
    # Freshness
    if "last_modified" in df_copy.columns:
        last_mod_dt = pd.to_datetime(df_copy["last_modified"], errors="coerce", utc=True)
        now_dt = pd.Timestamp.now(tz="UTC")
        df_copy["days_since_update"] = (now_dt - last_mod_dt).dt.days

    return df_copy


if __name__ == "__main__":
    from pathlib import Path
    raw_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "security_datasets_metadata.csv"
    if raw_path.exists():
        df = pd.read_csv(raw_path)
        # Parse tags from string representation if needed
        import ast
        if "tags" in df.columns and isinstance(df["tags"].iloc[0], str):
            df["tags"] = df["tags"].apply(lambda x: ast.literal_eval(x) if str(x).startswith("[") else [])
            
        enriched = enrich_dataset_dataframe(df)
        print("Distribución por categoría principal:")
        print(enriched["primary_category"].value_counts())
        
        # Save to processed
        proc_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
        proc_dir.mkdir(parents=True, exist_ok=True)
        enriched.to_csv(proc_dir / "security_datasets_classified.csv", index=False)
        print(f"\nGuardado en {proc_dir / 'security_datasets_classified.csv'}")
