"""Downloader module for managing and downloading the top curated cybersecurity datasets."""

import os
import sys
import json
import shutil
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from huggingface_hub import HfApi, snapshot_download

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("HFSecurityDownloader")

load_dotenv()

# Definition of the Top 10 Curated Cybersecurity & AI Datasets
TOP_10_DATASETS: List[Dict[str, Any]] = [
    {
        "rank": 1,
        "id": "jackhhao/jailbreak-classification",
        "folder_name": "01_jackhhao__jailbreak-classification",
        "category": "Defensa de LLMs / Jailbreaks",
        "estimated_mb": 7.3,
        "description": "Benchmark histórico #1 en descargas para clasificar intentos de jailbreak y manipulación adversarial en LLMs.",
        "key_features": ["55k+ descargas", "Etiquetas de jailbreak vs benigno", "Referencia en seguridad de LLMs"]
    },
    {
        "rank": 2,
        "id": "deadbits/vigil-jailbreak-all-mpnet-base-v2",
        "folder_name": "02_deadbits__vigil-jailbreak-all-mpnet-base-v2",
        "category": "Guardrails en Producción",
        "estimated_mb": 3.1,
        "description": "Base de datos de Vigil, el framework open source líder para filtrado en tiempo real de inyecciones de prompts.",
        "key_features": [">10k descargas/mes", "Embeddings mpnet-base", "Protección de aplicaciones con LLMs"]
    },
    {
        "rank": 3,
        "id": "CyberNative/Code_Vulnerability_Security_DPO",
        "folder_name": "03_CyberNative__Code_Vulnerability_Security_DPO",
        "category": "Alineación de Código Seguro (DPO)",
        "estimated_mb": 6.6,
        "description": "Dataset con técnica Direct Preference Optimization (DPO) con pares de código vulnerable vs código parchado.",
        "key_features": ["Formato chosen/rejected", "Múltiples lenguajes", "170 likes (top en HF)"]
    },
    {
        "rank": 4,
        "id": "AlicanKiraz0/All-CVE-Records-Training-Dataset",
        "folder_name": "04_AlicanKiraz0__All-CVE-Records-Training-Dataset",
        "category": "Base de Conocimiento CVE",
        "estimated_mb": 453.3,
        "description": "Catálogo completo de vulnerabilidades oficiales (CVE / NVD) estructurado con métricas CVSS y taxonomía CWE.",
        "key_features": ["Registro histórico completo", "Estructura para LLM Training", "Mapeo CWE/CVSS"]
    },
    {
        "rank": 5,
        "id": "AlicanKiraz0/Cybersecurity-Dataset-Fenrir-v2.1",
        "folder_name": "05_AlicanKiraz0__Cybersecurity-Dataset-Fenrir-v2.1",
        "category": "Instruction Tuning Especializado",
        "estimated_mb": 413.5,
        "description": "Dataset masivo de instrucciones complejas: análisis de malware, ingeniería inversa, análisis forense y redes.",
        "key_features": ["32k+ descargas", "147 likes", "Instrucciones de alta complejidad"]
    },
    {
        "rank": 6,
        "id": "Trendyol/Trendyol-Cybersecurity-Instruction-Tuning-Dataset",
        "folder_name": "06_Trendyol__Trendyol-Cybersecurity-Instruction-Tuning-Dataset",
        "category": "Fine-Tuning Corporativo",
        "estimated_mb": 186.0,
        "description": "Dataset corporativo desarrollado por ingenieros de Trendyol para modelos defensivos y ofensivos en producción.",
        "key_features": ["Nivel corporativo", "134 likes", "Tareas defensivas y ofensivas"]
    },
    {
        "rank": 7,
        "id": "WNT3D/Ultimate-Offensive-Red-Team",
        "folder_name": "07_WNT3D__Ultimate-Offensive-Red-Team",
        "category": "Red Teaming y Pentesting",
        "estimated_mb": 377.8,
        "description": "Dataset ofensivo #1 en valoraciones de HF. Mapeado a técnicas MITRE ATT&CK, generación de exploits y evasión.",
        "key_features": ["163 likes", "MITRE ATT&CK", "Exploitation & Pentesting"]
    },
    {
        "rank": 8,
        "id": "zstanjj/ClawTrojan",
        "folder_name": "08_zstanjj__ClawTrojan",
        "category": "Detección de Malware y Backdoors",
        "estimated_mb": 87.2,
        "description": "Colección de 72.000 muestras de código con troyanos y puertas traseras inyectadas para detección estática con IA.",
        "key_features": ["72k archivos de código", "Puertas traseras y troyanos", "Análisis estático"]
    },
    {
        "rank": 9,
        "id": "darkknight25/Advanced_SIEM_Dataset",
        "folder_name": "09_darkknight25__Advanced_SIEM_Dataset",
        "category": "Operaciones SOC y Logs SIEM",
        "estimated_mb": 89.4,
        "description": "Registros de eventos de seguridad (Syslog, firewall, alertas) etiquetados para entrenar modelos de detección en SOC.",
        "key_features": ["29k+ descargas", "Logs estructurados de red", "Incidentes y anomalías"]
    },
    {
        "rank": 10,
        "id": "ethanolivertroy/nist-cybersecurity-training",
        "folder_name": "10_ethanolivertroy__nist-cybersecurity-training",
        "category": "Gobernanza y Cumplimiento NIST",
        "estimated_mb": 10657.6,
        "description": "Publicaciones y normativas oficiales del NIST procesadas para cumplimiento corporativo y estándares de seguridad.",
        "key_features": ["Dataset grande (~10.6 GB)", "Estándares federales y NIST CSF", "Auditoría y gobernanza"]
    }
]

# Definition of Complementary Datasets for Specialized Roles (Real Network Traffic & Autonomous Agents)
COMPLEMENTARY_DATASETS: List[Dict[str, Any]] = [
    {
        "rank": 11,
        "id": "c01dsnap/CIC-IDS2017",
        "folder_name": "11_c01dsnap__CIC-IDS2017",
        "category": "Tráfico de Red Real / IDS (Nivel 1)",
        "estimated_mb": 843.7,
        "description": "Benchmark internacional de tráfico de red real capturado con ataques DoS, PortScan, Infiltración y Web Attacks para detección tabular (XGBoost/Isolation Forest).",
        "key_features": ["Tráfico de red real", "Desbalance realista de clases", "Estándar de oro IDS"]
    },
    {
        "rank": 12,
        "id": "walledai/CyberSecEval",
        "folder_name": "12_walledai__CyberSecEval",
        "category": "Evaluación de Agentes y Explotación (Nivel 5)",
        "estimated_mb": 2.3,
        "description": "Benchmark de Meta y WalledAI para evaluar capacidades de explotación, generación de código inseguro y evasión en modelos y agentes de IA.",
        "key_features": ["Pruebas de explotación", "Evaluación de agentes", "8 lenguajes de programación"]
    },
    {
        "rank": 13,
        "id": "jordan-taylor-aisi/normal_llama_31_8b_instruct_gdm_intercode_ctf",
        "folder_name": "13_aisi_gdm__intercode-ctf",
        "category": "Trazas Autónomas de Terminal CTF (Nivel 5)",
        "estimated_mb": 2.6,
        "description": "Evaluaciones y trazas agénticas de Google DeepMind y UK AI Safety Institute (AISI) para resolución autónoma de CTF con herramientas bash y python.",
        "key_features": ["Trazas paso a paso en bash", "Tool calling (Bash, Python, Submit)", "Google DeepMind & AISI"]
    }
]

ALL_DATASETS: List[Dict[str, Any]] = TOP_10_DATASETS + COMPLEMENTARY_DATASETS


class HFSecurityDownloader:
    """Manages downloading, verifying, and tracking the Top 10 security datasets."""

    def __init__(self, target_dir: Optional[Path] = None, token: Optional[str] = None):
        self.root_dir = Path(__file__).resolve().parent.parent
        self.target_dir = target_dir or (self.root_dir / "data" / "raw" / "top10_security")
        self.target_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.target_dir / "manifest.json"
        self.token = token or os.getenv("HF_TOKEN")
        self.api = HfApi(token=self.token)
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        """Loads or initializes the manifest tracking file."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error reading manifest: {e}. Reinitializing.")
        
        # Initial scaffold
        return {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "datasets": {}
        }

    def _save_manifest(self):
        """Persists the manifest file to disk."""
        self.manifest["updated_at"] = datetime.now().isoformat()
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)

    def get_free_disk_space_gb(self) -> float:
        """Returns free disk space in Gigabytes for the target directory."""
        total, used, free = shutil.disk_usage(self.target_dir)
        return free / (1024 ** 3)

    def check_dataset_status(self, repo_id: str, folder_name: str) -> Dict[str, Any]:
        """Checks whether a dataset is already downloaded and calculates local size."""
        dataset_folder = self.target_dir / folder_name
        is_downloaded = False
        size_bytes = 0
        file_count = 0

        if dataset_folder.exists() and dataset_folder.is_dir():
            all_files = [f for f in dataset_folder.rglob("*") if f.is_file()]
            if len(all_files) > 0:
                is_downloaded = True
                file_count = len(all_files)
                size_bytes = sum(f.stat().st_size for f in all_files)

        return {
            "is_downloaded": is_downloaded,
            "file_count": file_count,
            "size_mb": round(size_bytes / (1024 * 1024), 2),
            "local_path": str(dataset_folder) if is_downloaded else None
        }

    def list_datasets_info(self):
        """Prints a well-formatted summary table of all curated and complementary datasets."""
        free_gb = self.get_free_disk_space_gb()
        print("\n" + "=" * 95)
        print(" DATASETS DE CIBERSEGURIDAD E IA (HUGGING FACE)")
        print(f" Espacio libre en disco: {free_gb:.1f} GB | Directorio: {self.target_dir}")
        print("=" * 95)

        total_est_mb = 0
        total_local_mb = 0

        print("\n--- CORE TOP 10 DATASETS ---")
        for item in TOP_10_DATASETS:
            status_info = self.check_dataset_status(item["id"], item["folder_name"])
            status_str = f" DESCARGADO ({status_info['size_mb']} MB, {status_info['file_count']} archivos)" if status_info["is_downloaded"] else "[PENDIENTE]"
            total_est_mb += item["estimated_mb"]
            total_local_mb += status_info["size_mb"]

            print(f"\n[#{item['rank']}] {item['id']}")
            print(f"     Categoría:  {item['category']}")
            print(f"     Tamaño Est: {item['estimated_mb']:.1f} MB | Estado: {status_str}")
            print(f"     Detalles:   {item['description']}")
            print(f"     Destacados: {', '.join(item['key_features'])}")

        print("\n--- DATASETS COMPLEMENTARIOS (RED REAL & AGENTES AUTÓNOMOS) ---")
        for item in COMPLEMENTARY_DATASETS:
            status_info = self.check_dataset_status(item["id"], item["folder_name"])
            status_str = f" DESCARGADO ({status_info['size_mb']} MB, {status_info['file_count']} archivos)" if status_info["is_downloaded"] else "[PENDIENTE]"
            total_est_mb += item["estimated_mb"]
            total_local_mb += status_info["size_mb"]

            print(f"\n[#{item['rank']}] {item['id']}")
            print(f"     Categoría:  {item['category']}")
            print(f"     Tamaño Est: {item['estimated_mb']:.1f} MB | Estado: {status_str}")
            print(f"     Detalles:   {item['description']}")
            print(f"     Destacados: {', '.join(item['key_features'])}")

        print("-" * 95)
        print(f"Total estimado: {total_est_mb / 1024:.2f} GB | Total descargado localmente: {total_local_mb / 1024:.2f} GB")
        print("=" * 95 + "\n")

    def download_dataset(self, item: Dict[str, Any], force: bool = False) -> bool:
        """
        Downloads a single dataset using snapshot_download with verification.
        
        Args:
            item: Dataset dictionary definition from ALL_DATASETS.
            force: If True, re-downloads even if already present.
        """
        repo_id = item["id"]
        folder_name = item["folder_name"]
        dest_folder = self.target_dir / folder_name

        status_info = self.check_dataset_status(repo_id, folder_name)
        if status_info["is_downloaded"] and not force:
            logger.info(f"[#{item['rank']}] Ya descargado: {repo_id} ({status_info['size_mb']} MB). Omitiendo.")
            return True

        # Check free disk space before download (with a 5 GB buffer)
        required_gb = (item["estimated_mb"] / 1024) + 1.0
        free_gb = self.get_free_disk_space_gb()
        if free_gb < required_gb:
            logger.error(f"Espacio insuficiente en disco. Se requieren {required_gb:.2f} GB, pero solo hay {free_gb:.2f} GB libres.")
            return False

        logger.info(f"\n---> Iniciando descarga de [#{item['rank']}] {repo_id} (~{item['estimated_mb']:.1f} MB)...")
        dest_folder.mkdir(parents=True, exist_ok=True)

        try:
            downloaded_dir = snapshot_download(
                repo_id=repo_id,
                repo_type="dataset",
                local_dir=str(dest_folder),
                token=self.token,
                resume_download=True,
                max_workers=4
            )

            # Post-download verification
            updated_status = self.check_dataset_status(repo_id, folder_name)
            logger.info(
                f" [#{item['rank']}] Descarga completada: {repo_id} "
                f"({updated_status['size_mb']} MB, {updated_status['file_count']} archivos)."
            )

            # Record in manifest
            self.manifest["datasets"][repo_id] = {
                "rank": item["rank"],
                "category": item["category"],
                "description": item["description"],
                "local_dir": str(dest_folder),
                "downloaded_at": datetime.now().isoformat(),
                "file_count": updated_status["file_count"],
                "size_mb": updated_status["size_mb"]
            }
            self._save_manifest()
            return True

        except Exception as e:
            logger.error(f"Error descargando {repo_id}: {e}")
            return False

    def download_all(self, target_datasets: Optional[List[Dict[str, Any]]] = None, skip_large: bool = False, force: bool = False):
        """
        Downloads all specified datasets (defaults to ALL_DATASETS).
        
        Args:
            target_datasets: List of dataset dicts to download. Defaults to ALL_DATASETS.
            skip_large: If True, skips datasets larger than 1 GB (e.g. NIST).
            force: If True, overwrites existing downloads.
        """
        dataset_list = target_datasets or ALL_DATASETS
        free_gb = self.get_free_disk_space_gb()
        logger.info(f"Iniciando descarga en lote ({len(dataset_list)} datasets). Espacio libre en disco: {free_gb:.1f} GB.")
        
        successes = 0
        skipped = 0
        failures = 0

        for item in dataset_list:
            if skip_large and item["estimated_mb"] > 1024:
                logger.info(f"[#{item['rank']}] Omitiendo {item['id']} por exceder 1 GB (--skip-large activo).")
                skipped += 1
                continue

            success = self.download_dataset(item, force=force)
            if success:
                successes += 1
            else:
                failures += 1

        logger.info(f"\nProceso finalizado. Exitosos: {successes} | Omitidos: {skipped} | Fallidos: {failures}")
        logger.info(f"Manifiesto guardado en: {self.manifest_path}")


def main():
    parser = argparse.ArgumentParser(description="Gestor de descarga para datasets de Ciberseguridad e IA.")
    parser.add_argument("--info", "--list", action="store_true", help="Muestra la lista de datasets, tamaños y estado actual.")
    parser.add_argument("--all", action="store_true", help="Descarga todos los datasets (Top 10 + complementarios).")
    parser.add_argument("--top10", action="store_true", help="Descarga únicamente los datasets del Top 10 original.")
    parser.add_argument("--complementary", action="store_true", help="Descarga únicamente los datasets complementarios (#11, #12, #13).")
    parser.add_argument("--skip-large", action="store_true", help="Omite datasets mayores a 1 GB (útil para descargar primero los más ligeros).")
    parser.add_argument("--index", type=int, choices=range(1, 14), help="Descarga un dataset específico por su número de ranking (1 al 13).")
    parser.add_argument("--force", action="store_true", help="Fuerza la descarga incluso si el dataset ya existe localmente.")

    args = parser.parse_args()

    downloader = HFSecurityDownloader()

    if args.info or len(sys.argv) == 1:
        downloader.list_datasets_info()
        print("Para descargar:")
        print("  python -m src.downloader --all            # Descargar todos (Top 10 + Complementarios)")
        print("  python -m src.downloader --top10          # Descargar los 10 originales")
        print("  python -m src.downloader --complementary  # Descargar los 3 complementarios (#11, #12, #13)")
        print("  python -m src.downloader --index 11       # Descargar sólo el #11")
        return

    if args.index:
        target_item = next((item for item in ALL_DATASETS if item["rank"] == args.index), None)
        if target_item:
            downloader.download_dataset(target_item, force=args.force)
        else:
            logger.error(f"Ranking {args.index} no encontrado.")
    elif args.complementary:
        downloader.download_all(target_datasets=COMPLEMENTARY_DATASETS, skip_large=args.skip_large, force=args.force)
    elif args.top10:
        downloader.download_all(target_datasets=TOP_10_DATASETS, skip_large=args.skip_large, force=args.force)
    elif args.all or args.skip_large:
        downloader.download_all(target_datasets=ALL_DATASETS, skip_large=args.skip_large, force=args.force)


if __name__ == "__main__":
    main()
