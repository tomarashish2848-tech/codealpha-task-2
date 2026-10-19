# Unemployment Analysis in India — Trends & COVID-19 Impact

Python analysis of monthly unemployment rates across 28 Indian states/UTs (Jan 2019 – Dec 2021):
data cleaning, visualisation, COVID-19 impact, seasonality, regional comparison and policy insights.

> ⚠️ **Data note.** The bundled CSV is a **simulated dataset** that follows the schema of the Kaggle
> *"Unemployment in India"* (CMIE) file and is calibrated to the shape of national CMIE figures
> (lockdown spike in Apr–May 2020, second wave in May 2021). State-level numbers and the seasonal
> pattern are **illustrative, not official statistics**. To reproduce with real data, download the Kaggle
> CSV, rename the columns as in `data/unemployment_india_raw.csv` (or adjust the rename step in
> `src/analysis.py`), place it in `data/`, and re-run.

## Project structure
```
data/        unemployment_india_raw.csv  (dirty input)   unemployment_india_clean.csv (output)
src/         generate_dataset.py         analysis.py
outputs/     charts/*.png                summary_stats.md
```

## Run
```bash
pip install -r requirements.txt
python src/generate_dataset.py   # optional: rebuild the simulated raw data
python src/analysis.py           # cleans data, makes charts, writes outputs/summary_stats.md
```

## 1. Data cleaning
| Issue found | Handling |
|---|---|
| 10 duplicate rows | dropped |
| Region names / frequency labels with stray whitespace, `M` vs `Monthly` | trimmed and standardised |
| Two date formats (`dd-mm-YYYY`, `YYYY/mm/dd`) | parsed both into one datetime column |
| 13 impossible unemployment values (−1, 250) | set to missing |
| 83 missing cells in total (incl. the above) | linear interpolation within each state's time series |

## 2. Visualisations (`outputs/charts/`)
| File | Shows |
|---|---|
| `01_national_trend.png` | Average rate over time with COVID waves shaded |
| `02_state_heatmap.png` | State × month heatmap |
| `03_state_covid_impact.png` | Pre-COVID average vs lockdown peak per state |
| `04_zone_trends.png` | Regional (zone) trends |
| `05_seasonality_precovid.png` | Month-of-year pattern before COVID |
| `06_unemployment_vs_participation.png` | Unemployment vs labour participation |
| `07_period_boxplot.png` | Distribution by COVID phase |

## 3. Findings (from the bundled dataset)
**COVID-19 impact**
- Average unemployment was **7.2%** before COVID (Jan 2019–Feb 2020). It peaked at **20.5% in April 2020**, about **2.8×** the baseline (the simple state-average understates the ~23.5% reported nationally because it isn't population-weighted).
- Employment summed across states fell from ~674M to a low of ~534M (≈ −21%) in April 2020.
- Recovery was fast: rates were back within 10% of baseline by **July 2020**. A **second wave** lifted the average to **11.5% in May 2021**, a smaller and shorter shock.
- Pre-COVID vs lockdown difference is statistically significant (Welch t ≈ 8.6, p < 0.001).
- Labour participation fell as unemployment rose (correlation ≈ −0.97): part of the shock was people leaving the labour force, not only being counted as unemployed.

**Regional patterns**
- Biggest point increases: Delhi (+23 pp), Haryana (+22), Himachal Pradesh (+21), Bihar (+21), Rajasthan (+20).
- Low-baseline states were hit hardest *proportionally* (Tamil Nadu ≈ 6.7×, Puducherry ≈ 5×) but from tiny bases; Meghalaya was the least affected.
- The North zone had the highest unemployment before and during COVID; the South had the largest multiple.

**Seasonality**
- Unemployment is higher around spring/summer (peak May) and lowest around January in this data. Only ~14 pre-COVID months exist, so treat this as indicative; with real data, use several years of history.

## 4. Policy insights
1. **Shock-absorbing safety nets.** The first-wave spike was sharp but short; rapid income support and employment guarantees (e.g. expanding MGNREGA-type work) matter most in the first 2–3 months.
2. **Target high-impact states.** Urban/service-heavy and migrant-sending states (Delhi, Bihar, Jharkhand, Rajasthan) saw the largest jumps: pre-position relief and portable benefits.
3. **Watch participation, not just unemployment.** A falling participation rate hides discouraged workers; policies should track both.
4. **Time public works to seasons.** Scale seasonal job programmes in the months where unemployment typically rises.
5. **Prepare for repeat waves.** The second wave was milder; localised, rather than blanket, restrictions reduce economic damage.

## Limitations
Simulated data; unweighted state averages; short seasonal window; interpolation of missing values assumes smooth series.
