"""
profiler.py
Funciones comunes para el EDA de los datasets del Top 10 (eda/NN_nombre/eda.ipynb).

Idea: cada notebook importa este módulo para cargar archivos, perfilar columnas
y guardar resultados en SU propia carpeta (figures/ y tables/), de modo que
todo lo de un dataset quede en un solo lugar.

Uso típico dentro de un notebook:

    from src.profiler import *
    ctx = eda_context(__file__ if "__file__" in globals() else None)
    df = load_table(ctx.data_dir / "archivo.jsonl", nrows=20_000)
    display(profile_df(df))
"""

from __future__ import annotations

import hashlib
import json
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional

import pandas as pd

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

TOP10_RELATIVE = Path("data") / "raw" / "top10_security"


def find_repo_root(start: Optional[Path] = None) -> Path:
    """Sube desde `start` (o el cwd) hasta encontrar la raíz del repo."""
    start = Path(start or Path.cwd()).resolve()
    for p in [start, *start.parents]:
        if (p / TOP10_RELATIVE).exists() or (p / "src" / "profiler.py").exists():
            return p
    raise FileNotFoundError(
        "No se encontró la raíz del repo (carpeta con data/raw/top10_security). "
        "Abre el notebook desde dentro del repositorio."
    )


def top10_dir(root: Optional[Path] = None) -> Path:
    return (root or find_repo_root()) / TOP10_RELATIVE


def dataset_dir(prefix: str, root: Optional[Path] = None) -> Path:
    """Devuelve la carpeta del dataset cuyo nombre empieza con `prefix` (ej. '04')."""
    base = top10_dir(root)
    matches = sorted(p for p in base.iterdir() if p.is_dir() and p.name.startswith(prefix))
    if not matches:
        raise FileNotFoundError(f"No hay carpeta que empiece con '{prefix}' en {base}")
    return matches[0]


@dataclass
class EDAContext:
    root: Path          # raíz del repo
    data_dir: Path      # carpeta del dataset en data/raw/top10_security
    out_dir: Path       # carpeta del notebook (eda/NN_nombre)
    figures: Path
    tables: Path

    def __repr__(self) -> str:
        return (
            f"Repo:     {self.root}\n"
            f"Datos:    {self.data_dir}\n"
            f"Salidas:  {self.out_dir}  (figures/, tables/)"
        )


def eda_context(dataset_prefix: Optional[str] = None, out_dir: Optional[Path] = None) -> EDAContext:
    """Prepara rutas para un notebook de EDA.

    dataset_prefix: número del dataset ('01'...'10') o None para el notebook general.
    out_dir: carpeta donde guardar resultados; por defecto, la carpeta del notebook (cwd).
    """
    out = Path(out_dir or Path.cwd()).resolve()
    root = find_repo_root(out)
    data = dataset_dir(dataset_prefix, root) if dataset_prefix else top10_dir(root)
    figures, tables = out / "figures", out / "tables"
    figures.mkdir(exist_ok=True)
    tables.mkdir(exist_ok=True)
    return EDAContext(root, data, out, figures, tables)


# ---------------------------------------------------------------------------
# Inventario de archivos
# ---------------------------------------------------------------------------

IGNORED_PARTS = {".cache", ".git", "__pycache__", ".ipynb_checkpoints"}


def list_files(folder: Path, recursive: bool = True) -> pd.DataFrame:
    """Tabla con los archivos de una carpeta (ruta relativa, extensión, tamaño en MB)."""
    folder = Path(folder)
    it = folder.rglob("*") if recursive else folder.glob("*")
    rows = []
    for p in it:
        if p.is_file() and not (IGNORED_PARTS & set(p.relative_to(folder).parts)):
            rows.append(
                {
                    "archivo": p.relative_to(folder).as_posix(),
                    "ext": p.suffix.lower(),
                    "size_mb": round(p.stat().st_size / 1e6, 3),
                }
            )
    df = pd.DataFrame(rows, columns=["archivo", "ext", "size_mb"])
    return df.sort_values("size_mb", ascending=False).reset_index(drop=True)


def summarize_extensions(files: pd.DataFrame) -> pd.DataFrame:
    return (
        files.groupby("ext")
        .agg(n_archivos=("archivo", "count"), size_mb=("size_mb", "sum"))
        .sort_values("size_mb", ascending=False)
    )


# ---------------------------------------------------------------------------
# Lectura (pensada para archivos grandes)
# ---------------------------------------------------------------------------

def count_lines(path: Path) -> int:
    """Cuenta líneas sin cargar el archivo en memoria."""
    n = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            n += chunk.count(b"\n")
    return n


def iter_jsonl(path: Path) -> Iterator[dict]:
    """Itera registros de un .jsonl, saltando líneas vacías o corruptas."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def read_jsonl(path: Path, nrows: Optional[int] = None, sample: Optional[int] = None,
               seed: int = 42) -> pd.DataFrame:
    """Lee un .jsonl.

    - nrows:  primeras N filas (rápido, pero puede estar sesgado por el orden del archivo).
    - sample: muestra aleatoria de N filas (reservoir sampling: recorre el archivo
              completo pero solo guarda N en memoria).
    - ninguno: carga todo (cuidado con archivos de cientos de MB).
    """
    if sample:
        rng = random.Random(seed)
        reservoir: list = []
        for i, rec in enumerate(iter_jsonl(path)):
            if i < sample:
                reservoir.append(rec)
            else:
                j = rng.randint(0, i)
                if j < sample:
                    reservoir[j] = rec
        return pd.DataFrame(reservoir)
    rows = []
    for i, rec in enumerate(iter_jsonl(path)):
        if nrows is not None and i >= nrows:
            break
        rows.append(rec)
    return pd.DataFrame(rows)


def _looks_like_jsonl(path: Path) -> bool:
    """True si el archivo tiene un objeto JSON por línea (aunque su extensión sea .json)."""
    with open(path, "r", encoding="utf-8") as f:
        first = f.readline().strip()
        if not first.startswith("{"):
            return False
        try:
            json.loads(first)
        except json.JSONDecodeError:
            return False  # JSON "bonito" que ocupa varias líneas
        for line in f:
            if line.strip():
                return True  # hay más de un objeto, uno por línea
    return False


def read_json_any(path: Path):
    """Carga un .json (lista, dict o jsonl disfrazado de .json)."""
    path = Path(path)
    if _looks_like_jsonl(path):
        return list(iter_jsonl(path))
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_table(path: Path, nrows: Optional[int] = None, sample: Optional[int] = None) -> pd.DataFrame:
    """Carga CSV, Parquet, JSON o JSONL como DataFrame."""
    path = Path(path)
    ext = path.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(path, nrows=nrows)
    if ext == ".parquet":
        df = pd.read_parquet(path)
        return df.head(nrows) if nrows else df
    if ext == ".jsonl" or (ext == ".json" and _looks_like_jsonl(path)):
        return read_jsonl(path, nrows=nrows, sample=sample)
    if ext == ".json":
        data = read_json_any(path)
        if isinstance(data, list):
            df = pd.json_normalize(data, max_level=0)
        elif isinstance(data, dict):
            df = pd.DataFrame([{"clave": k, "tipo": type(v).__name__,
                                "n_elementos": len(v) if hasattr(v, "__len__") else None}
                               for k, v in data.items()])
        else:
            df = pd.DataFrame({"valor": [data]})
        return df.head(nrows) if nrows else df
    raise ValueError(f"Formato no soportado: {ext}")


def peek_record(path: Path, max_chars: int = 300) -> dict:
    """Primer registro de un JSON/JSONL con los valores truncados (para ver el esquema)."""
    path = Path(path)
    if path.suffix.lower() == ".jsonl" or _looks_like_jsonl(path):
        rec = next(iter_jsonl(path), {})
    else:
        data = read_json_any(path)
        rec = data[0] if isinstance(data, list) and data else data
    if not isinstance(rec, dict):
        return {"valor": str(rec)[:max_chars]}
    return {k: (str(v)[:max_chars] + ("…" if len(str(v)) > max_chars else "")) for k, v in rec.items()}


def describe_json_structure(obj, max_depth: int = 3, _depth: int = 0, _key: str = "raíz") -> pd.DataFrame:
    """Recorre un JSON anidado y devuelve una tabla con claves, tipo y tamaño."""
    rows = []
    kind = type(obj).__name__
    size = len(obj) if hasattr(obj, "__len__") and not isinstance(obj, str) else None
    rows.append({"ruta": _key, "nivel": _depth, "tipo": kind, "n_elementos": size})
    if _depth < max_depth:
        if isinstance(obj, dict):
            for k, v in obj.items():
                rows += describe_json_structure(v, max_depth, _depth + 1, f"{_key}.{k}").to_dict("records")
        elif isinstance(obj, list) and obj:
            rows += describe_json_structure(obj[0], max_depth, _depth + 1, f"{_key}[0]").to_dict("records")
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Perfilado
# ---------------------------------------------------------------------------

def _is_text(s: pd.Series) -> bool:
    return s.dtype == object or pd.api.types.is_string_dtype(s)


def profile_df(df: pd.DataFrame) -> pd.DataFrame:
    """Resumen por columna: tipo, nulos, únicos y largo de texto."""
    rows = []
    n = len(df)
    for col in df.columns:
        s = df[col]
        hashable = s.map(lambda x: x if isinstance(x, (str, int, float, bool, type(None))) else str(x))
        row = {
            "columna": col,
            "dtype": str(s.dtype),
            "nulos": int(s.isna().sum()),
            "%nulos": round(100 * s.isna().mean(), 2) if n else 0,
            "vacíos": int((s.astype(str).str.strip() == "").sum()) if _is_text(s) else 0,
            "únicos": int(hashable.nunique(dropna=True)),
        }
        if _is_text(s):
            lens = s.dropna().astype(str).str.len()
            row.update({"len_media": round(lens.mean(), 1) if len(lens) else None,
                        "len_mediana": lens.median() if len(lens) else None,
                        "len_max": lens.max() if len(lens) else None})
        rows.append(row)
    return pd.DataFrame(rows).set_index("columna")


def duplicates_report(df: pd.DataFrame, subsets: Optional[dict] = None) -> pd.DataFrame:
    """Cuenta duplicados exactos. `subsets` = {"nombre": [columnas]}."""
    subsets = subsets or {"fila completa": list(df.columns)}
    safe = df.apply(lambda c: c.map(lambda x: x if isinstance(x, (str, int, float, bool, type(None))) else str(x)))
    rows = []
    for name, cols in subsets.items():
        d = int(safe.duplicated(subset=cols).sum())
        rows.append({"criterio": name, "duplicados": d, "%": round(100 * d / max(len(df), 1), 2)})
    return pd.DataFrame(rows).set_index("criterio")


def text_lengths(df: pd.DataFrame, cols: Iterable[str], unit: str = "chars") -> pd.DataFrame:
    """Largo de cada columna de texto (caracteres o palabras aproximadas)."""
    out = {}
    for c in cols:
        s = df[c].fillna("").astype(str)
        out[c] = s.str.len() if unit == "chars" else s.str.split().str.len()
    return pd.DataFrame(out)


def normalize_text(t: str) -> str:
    return re.sub(r"\s+", " ", str(t)).strip().lower()


def text_hash(t: str) -> str:
    return hashlib.md5(normalize_text(t).encode("utf-8")).hexdigest()


def hashes_from_jsonl(path: Path, field: str, limit: Optional[int] = None) -> set:
    """Conjunto de hashes (texto normalizado) de un campo, recorriendo el archivo en streaming.
    Útil para comparar solapamiento entre datasets sin cargarlos completos."""
    hs = set()
    for i, rec in enumerate(iter_jsonl(path)):
        if limit and i >= limit:
            break
        if field in rec and rec[field]:
            hs.add(text_hash(rec[field]))
    return hs


def show_examples(df: pd.DataFrame, n: int = 3, cols: Optional[list] = None,
                  max_chars: int = 600, seed: int = 0) -> None:
    """Imprime n filas al azar con los textos truncados (más legible que df.head())."""
    cols = cols or list(df.columns)
    sub = df.sample(min(n, len(df)), random_state=seed) if len(df) else df
    for idx, row in sub.iterrows():
        print("=" * 100)
        print(f"fila {idx}")
        for c in cols:
            v = str(row[c])
            print(f"--- {c} ---")
            print(v[:max_chars] + (" […]" if len(v) > max_chars else ""))
    print("=" * 100)


# ---------------------------------------------------------------------------
# Guardado de resultados (siempre dentro de la carpeta del notebook)
# ---------------------------------------------------------------------------

def save_fig(fig, ctx: EDAContext, name: str, dpi: int = 150) -> Path:
    path = ctx.figures / f"{name}.png"
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    return path


def save_table(df: pd.DataFrame, ctx: EDAContext, name: str, index: bool = True) -> Path:
    path = ctx.tables / f"{name}.csv"
    df.to_csv(path, index=index, encoding="utf-8")
    return path


def save_summary(ctx: EDAContext, dataset: str, df: pd.DataFrame, total_rows: Optional[int] = None,
                 dup_cols: Optional[list] = None, notas: str = "") -> pd.DataFrame:
    """Guarda tables/resumen.csv (una fila) para que eda/00_general lo pueda consolidar."""
    safe = df.apply(lambda c: c.map(lambda x: x if isinstance(x, (str, int, float, bool, type(None))) else str(x)))
    dups = int(safe.duplicated(subset=dup_cols).sum()) if len(df) else 0
    row = pd.DataFrame([{
        "dataset": dataset,
        "filas_totales": total_rows if total_rows is not None else len(df),
        "filas_analizadas": len(df),
        "columnas": df.shape[1],
        "duplicados_%": round(100 * dups / max(len(df), 1), 2),
        "criterio_duplicados": ", ".join(dup_cols) if dup_cols else "fila completa",
        "notas": notas,
    }])
    row.to_csv(ctx.tables / "resumen.csv", index=False, encoding="utf-8")
    return row
