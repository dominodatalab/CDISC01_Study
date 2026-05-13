"""
Stage: Summary Statistics
Produces a self-contained HTML safety summary report from ADaM datasets.
Includes: study header, demographics table, AE rate by seriousness,
top-20 adverse events by frequency, and SOC breakdown.

Inputs:  adae (CSV), adsl (CSV), drug_name, study_id
Outputs: summary_report (HTML)
"""

import html
import pandas as pd
from pathlib import Path

INPUTS  = Path("/workflow/inputs")
OUTPUTS = Path("/workflow/outputs")
OUTPUTS.mkdir(parents=True, exist_ok=True)


def load_csv(name: str) -> pd.DataFrame:
    p = INPUTS / name
    if not p.exists():
        raise RuntimeError(f"Input '{name}' not found at {p}")
    return pd.read_csv(p)


def read_input(name: str) -> str:
    p = INPUTS / name
    if not p.exists():
        raise RuntimeError(f"Input '{name}' not found at {p}")
    return p.read_text().strip()


def df_to_html_table(df: pd.DataFrame, title: str) -> str:
    thead = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    rows = ""
    for _, row in df.iterrows():
        cells = "".join(f"<td>{html.escape(str(v))}</td>" for v in row)
        rows += f"<tr>{cells}</tr>"
    return f"""
    <h3>{title}</h3>
    <table>
      <thead><tr>{thead}</tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """


def main():
    adae      = load_csv("adae")
    adsl      = load_csv("adsl")
    drug_name = read_input("drug_name")
    study_id  = read_input("study_id")

    n_subjects = len(adsl)
    n_serious  = adsl["AESERFLT"].eq("Y").sum()
    n_fatal    = adsl["FATALFL"].eq("Y").sum()
    n_ae_total = len(adae)

    print(f"Summary: {n_subjects} subjects, {n_ae_total} AEs, {n_serious} serious, {n_fatal} fatal")

    # ── Demographics ──────────────────────────────────────────────────────────
    sex_counts = adsl["SEX"].value_counts().reset_index()
    sex_counts.columns = ["Sex", "N"]
    sex_counts["Pct"] = (sex_counts["N"] / n_subjects * 100).round(1).astype(str) + "%"

    # ── AE rate table ─────────────────────────────────────────────────────────
    ae_rate = pd.DataFrame({
        "Category": ["Any AE", "Any Serious AE", "Fatal AE"],
        "N subjects": [
            adsl[adsl["AECNT"] > 0].shape[0],
            n_serious,
            n_fatal,
        ],
    })
    ae_rate["Rate"] = (ae_rate["N subjects"] / n_subjects * 100).round(1).astype(str) + "%"

    # ── Top-20 reaction terms ─────────────────────────────────────────────────
    top_ae = (
        adae.groupby("AETERM").size()
        .reset_index(name="N events")
        .sort_values("N events", ascending=False)
        .head(20)
    )
    top_ae["Rate"] = (top_ae["N events"] / n_ae_total * 100).round(1).astype(str) + "%"

    # ── SOC breakdown ─────────────────────────────────────────────────────────
    soc_table = (
        adae.groupby("AEBODSYS").agg(
            N_events=("AETERM", "count"),
            N_subjects=("USUBJID", "nunique"),
            Pct_serious=("AESER", lambda x: f"{(x=='Y').mean()*100:.1f}%"),
        )
        .sort_values("N_events", ascending=False)
        .reset_index()
        .rename(columns={"AEBODSYS": "System Organ Class"})
    )

    # ── Render HTML ───────────────────────────────────────────────────────────
    report_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Safety Summary — {html.escape(study_id)}</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; color: #222; }}
  h1   {{ color: #1a3a5c; border-bottom: 2px solid #1a3a5c; padding-bottom: 8px; }}
  h2   {{ color: #1a3a5c; margin-top: 32px; }}
  h3   {{ color: #444; margin-top: 20px; }}
  table {{ border-collapse: collapse; width: 100%; max-width: 800px; margin-bottom: 24px; }}
  th   {{ background: #1a3a5c; color: #fff; padding: 8px 12px; text-align: left; }}
  td   {{ padding: 6px 12px; border-bottom: 1px solid #ddd; }}
  tr:hover td {{ background: #f5f8ff; }}
  .meta {{ color: #666; font-size: 14px; margin-bottom: 24px; }}
  .kpi  {{ display: inline-block; background: #f0f4ff; border: 1px solid #c0cfe8;
           border-radius: 6px; padding: 12px 20px; margin: 8px 8px 8px 0; }}
  .kpi .val {{ font-size: 28px; font-weight: bold; color: #1a3a5c; }}
  .kpi .lbl {{ font-size: 12px; color: #666; }}
</style>
</head>
<body>
<h1>Drug Safety Summary Report</h1>
<p class="meta">
  <strong>Study ID:</strong> {html.escape(study_id)} &nbsp;|&nbsp;
  <strong>Drug:</strong> {html.escape(drug_name)} &nbsp;|&nbsp;
  <strong>Source:</strong> FDA FAERS (OpenFDA API)
</p>

<h2>Key Safety Indicators</h2>
<div>
  <div class="kpi"><div class="val">{n_subjects}</div><div class="lbl">Cases</div></div>
  <div class="kpi"><div class="val">{n_ae_total}</div><div class="lbl">Total AEs</div></div>
  <div class="kpi"><div class="val">{n_serious} ({n_serious/n_subjects*100:.1f}%)</div><div class="lbl">Serious AEs</div></div>
  <div class="kpi"><div class="val">{n_fatal} ({n_fatal/n_subjects*100:.1f}%)</div><div class="lbl">Fatal</div></div>
</div>

{df_to_html_table(sex_counts, "Demographics: Sex Distribution")}
{df_to_html_table(ae_rate, "Adverse Event Rates")}
{df_to_html_table(top_ae, "Top 20 Adverse Events by Frequency")}
{df_to_html_table(soc_table, "Events by System Organ Class (SOC)")}

<p style="font-size:12px; color:#999; margin-top:40px;">
  Generated from {n_ae_total} adverse event records via Domino Flows.
  Data source: FDA Adverse Event Reporting System (FAERS) via OpenFDA.
</p>
</body>
</html>"""

    out_path = OUTPUTS / "summary_report"
    out_path.write_text(report_html)
    print(f"Report written to {out_path} ({len(report_html)} bytes)")


if __name__ == "__main__":
    main()
