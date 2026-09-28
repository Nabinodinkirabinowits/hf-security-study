"""Generates key insight charts for the security study report."""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ROOT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA = ROOT_DIR / "data" / "processed" / "security_datasets_classified.csv"
FIGURES_DIR = ROOT_DIR / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", font_scale=1.1)


def generate_all_charts():
    if not PROCESSED_DATA.exists():
        print(f"Processed file not found at {PROCESSED_DATA}")
        return

    df = pd.read_csv(PROCESSED_DATA)

    # 1. Top 12 Datasets by 30-day downloads
    top_12 = df.sort_values(by="downloads_30d", ascending=False).head(12)
    plt.figure(figsize=(12, 7))
    ax = sns.barplot(
        data=top_12,
        x="downloads_30d",
        y="id",
        hue="primary_category",
        dodge=False,
        palette="mako"
    )
    plt.title("Top 12 Datasets de Seguridad por Descargas (Últimos 30 días)", fontsize=14, weight="bold")
    plt.xlabel("Descargas mensuales")
    plt.ylabel("Dataset ID")
    plt.tight_layout()
    chart1_path = FIGURES_DIR / "top_downloads_datasets.png"
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"Generado: {chart1_path}")

    # 2. Distribution by Security Domain
    cat_counts = df["primary_category"].value_counts().reset_index()
    cat_counts.columns = ["Categoría", "Cantidad"]

    plt.figure(figsize=(10, 5))
    sns.barplot(data=cat_counts, x="Cantidad", y="Categoría", palette="viridis")
    plt.title("Distribución de Datasets por Dominio de Seguridad", fontsize=14, weight="bold")
    plt.xlabel("Número de Datasets")
    plt.tight_layout()
    chart2_path = FIGURES_DIR / "categories_distribution.png"
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"Generado: {chart2_path}")

    # 3. Likes vs Downloads (Log-Log)
    plt.figure(figsize=(10, 6))
    # Filter datasets with at least 1 download for log scale
    df_valid = df[df["downloads_30d"] > 0].copy()
    df_valid["likes_display"] = df_valid["likes"] + 1

    sns.scatterplot(
        data=df_valid,
        x="likes_display",
        y="downloads_30d",
        hue="primary_category",
        alpha=0.7,
        palette="tab10"
    )
    plt.xscale("log")
    plt.yscale("log")
    plt.title("Likes vs Descargas Reales (30d) - Demostración de Discrepancia", fontsize=14, weight="bold")
    plt.xlabel("Likes (+1, escala logarítmica)")
    plt.ylabel("Descargas en 30 días (escala logarítmica)")
    plt.tight_layout()
    chart3_path = FIGURES_DIR / "likes_vs_downloads_correlation.png"
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    print(f"Generado: {chart3_path}")


if __name__ == "__main__":
    generate_all_charts()
