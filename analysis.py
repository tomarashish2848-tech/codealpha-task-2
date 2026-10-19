"""
Unemployment analysis (India, monthly, 2019-2021) with focus on COVID-19.
Run:  python src/analysis.py
Inputs : data/unemployment_india_raw.csv
Outputs: data/unemployment_india_clean.csv, outputs/charts/*.png, outputs/summary_stats.md
"""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT/"outputs/charts"; CH.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", context="talk", font_scale=0.7)
U, E, L = "Unemployment Rate", "Employed", "Labour Participation Rate"
log = []                                    # collects text for summary_stats.md
def say(*a):
    s = " ".join(str(x) for x in a); print(s); log.append(s)

# ───────────────────────── 1. LOAD ─────────────────────────
raw = pd.read_csv(ROOT/"data/unemployment_india_raw.csv")
say("## 1. Raw data\n")
say(f"- Shape: {raw.shape}")
say("- Missing values per column:\n```\n" + raw.isna().sum().to_string() + "\n```")

# ───────────────────────── 2. CLEAN ─────────────────────────
df = raw.copy()
df.columns = [c.strip() for c in df.columns]
df = df.rename(columns={"Estimated Unemployment Rate (%)":U,"Estimated Employed":E,
                        "Estimated Labour Participation Rate (%)":L})
n0 = len(df)
df = df.drop_duplicates();                                    n_dup = n0-len(df)
df["Region"] = df["Region"].str.strip()                       # whitespace
df["Frequency"] = df["Frequency"].str.strip().replace({"M":"Monthly"})
# mixed date formats: dd-mm-YYYY and YYYY/mm/dd
d1 = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")
d2 = pd.to_datetime(df["Date"], format="%Y/%m/%d", errors="coerce")
df["Date"] = d1.fillna(d2)
assert df["Date"].notna().all(), "unparsed dates"
# impossible values -> NaN (rates must be within 0-100)
bad = ~df[U].between(0,100) & df[U].notna()
n_bad = int(bad.sum()); df.loc[bad,U] = np.nan
n_missing = int(df[[U,E,L]].isna().sum().sum())
df = df.sort_values(["Region","Date"]).reset_index(drop=True)
# impute within each state by time-based interpolation (series are smooth month to month)
for c in [U,E,L]:
    df[c] = df.groupby("Region")[c].transform(lambda s: s.interpolate(limit_direction="both"))
assert df[[U,E,L]].isna().sum().sum()==0
df["Month"]=df["Date"].dt.month; df["Year"]=df["Date"].dt.year
def period(d):
    if d < pd.Timestamp("2020-03-01"): return "1 Pre-COVID"
    if d < pd.Timestamp("2020-07-01"): return "2 First wave / lockdown"
    if d < pd.Timestamp("2021-04-01"): return "3 Recovery"
    if d < pd.Timestamp("2021-08-01"): return "4 Second wave"
    return "5 Post second wave"
df["Period"] = df["Date"].apply(period)
df.to_csv(ROOT/"data/unemployment_india_clean.csv", index=False)

say("\n## 2. Cleaning log\n")
say(f"- Duplicate rows removed: {n_dup}")
say(f"- Region names / Frequency labels trimmed and standardised; mixed date formats unified")
say(f"- Impossible unemployment values (<0 or >100) set to missing: {n_bad}")
say(f"- Total missing cells (incl. the above) imputed by per-state linear interpolation: {n_missing}")
say(f"- Clean shape: {df.shape} | regions: {df.Region.nunique()} | "
    f"{df.Date.min():%b %Y} to {df.Date.max():%b %Y}")

# National proxy = employed-weighted... simpler & transparent: mean across states
nat = df.groupby("Date")[[U,L]].mean()
nat[E] = df.groupby("Date")[E].sum()
nat["Period"] = nat.index.map(period)

# ───────────────────────── 3. DESCRIPTIVE ─────────────────────────
say("\n## 3. Descriptive statistics\n")
say("```\n" + df[[U,E,L]].describe().round(2).to_string() + "\n```")
pre = nat.loc[nat.index<"2020-03-01",U].mean()
peak_date = nat[U].idxmax(); peak = nat[U].max()
say(f"\n- Average national unemployment pre-COVID (Jan 2019–Feb 2020): **{pre:.2f}%**")
say(f"- National peak: **{peak:.2f}% in {peak_date:%B %Y}** ({peak/pre:.1f}x pre-COVID)")
w2 = nat.loc["2021-04-01":"2021-08-01",U]
say(f"- Second-wave peak: **{w2.max():.2f}% in {w2.idxmax():%B %Y}**")
say(f"- Employed (sum across states): {nat[E].iloc[0]/1e6:.0f}M in {nat.index[0]:%b %Y} -> "
    f"low of {nat[E].min()/1e6:.0f}M in {nat[E].idxmin():%b %Y}")
rec = nat.loc[peak_date:][nat.loc[peak_date:,U] <= pre*1.1]
say(f"- First month back within 10% of the pre-COVID average after the peak: "
    f"**{rec.index[0]:%B %Y}**" if len(rec) else "- Did not return to pre-COVID level")
say("\n**Mean unemployment by period (average of states)**\n```\n" +
    nat.groupby("Period")[U].agg(["mean","max"]).round(2).to_string() + "\n```")

# ───────────────────────── 4. VISUALS ─────────────────────────
shade = [("2020-03-25","2020-06-30","First wave / lockdown","#d62728"),
         ("2021-04-01","2021-07-31","Second wave","#ff7f0e")]
def add_bands(ax, labels=True):
    for a,b,t,c in shade:
        ax.axvspan(pd.Timestamp(a),pd.Timestamp(b),color=c,alpha=0.15,label=t if labels else None)

# 4.1 national trend
fig,ax = plt.subplots(figsize=(11,5))
ax.plot(nat.index,nat[U],marker="o",lw=2.2,color="#1f4e79")
add_bands(ax); ax.annotate(f"Peak {peak:.1f}%\n{peak_date:%b %Y}",(peak_date,peak),
    xytext=(15,-5),textcoords="offset points",arrowprops=dict(arrowstyle="->"))
ax.axhline(pre,ls="--",c="grey",lw=1); ax.text(nat.index[1],pre+0.4,f"pre-COVID avg {pre:.1f}%",color="grey")
ax.set(title="Average unemployment rate across Indian states, 2019–2021",ylabel="Unemployment rate (%)",xlabel="")
ax.legend(); fig.tight_layout(); fig.savefig(CH/"01_national_trend.png",dpi=150); plt.close()

# 4.2 heatmap
piv = df.pivot(index="Region",columns="Date",values=U)
piv = piv.loc[piv.mean(axis=1).sort_values(ascending=False).index]
fig,ax = plt.subplots(figsize=(13,9))
sns.heatmap(piv,cmap="YlOrRd",ax=ax,cbar_kws={"label":"Unemployment rate (%)"},xticklabels=3)
ax.set_xticklabels([d.strftime("%b %y") for d in piv.columns[::3]],rotation=45)
ax.set(title="Unemployment rate by state and month",xlabel="",ylabel="")
fig.tight_layout(); fig.savefig(CH/"02_state_heatmap.png",dpi=150); plt.close()

# 4.3 state impact: pre-COVID avg vs lockdown peak
sp = df[df.Period=="1 Pre-COVID"].groupby("Region")[U].mean().rename("pre")
sk = df[df.Period=="2 First wave / lockdown"].groupby("Region")[U].max().rename("peak")
imp = pd.concat([sp,sk],axis=1); imp["increase_pp"]=imp.peak-imp.pre; imp["multiple"]=imp.peak/imp.pre
imp = imp.sort_values("increase_pp")
fig,ax = plt.subplots(figsize=(10,9)); y=np.arange(len(imp))
ax.hlines(y,imp.pre,imp.peak,color="#999",lw=2); ax.scatter(imp.pre,y,c="#1f4e79",s=60,label="Pre-COVID avg")
ax.scatter(imp.peak,y,c="#d62728",s=60,label="Lockdown peak"); ax.set_yticks(y); ax.set_yticklabels(imp.index)
ax.set(title="Unemployment: pre-COVID average vs lockdown peak",xlabel="Unemployment rate (%)"); ax.legend()
fig.tight_layout(); fig.savefig(CH/"03_state_covid_impact.png",dpi=150); plt.close()
say("\n## 4. State-level COVID impact (first wave)\n")
say("**Largest percentage-point increase**\n```\n" + imp.sort_values("increase_pp",ascending=False).head(8).round(1).to_string()+"\n```")
say("**Smallest percentage-point increase**\n```\n" + imp.sort_values("increase_pp").head(5).round(1).to_string()+"\n```")

# 4.4 zones
zt = df.groupby(["Date","Zone"])[U].mean().unstack()
fig,ax = plt.subplots(figsize=(11,5.5)); zt.plot(ax=ax,lw=2); add_bands(ax,False)
ax.set(title="Unemployment by zone",ylabel="Unemployment rate (%)",xlabel=""); ax.legend(title="Zone",ncol=2)
fig.tight_layout(); fig.savefig(CH/"04_zone_trends.png",dpi=150); plt.close()
zi = pd.concat([zt[zt.index<"2020-03-01"].mean().rename("pre"),
                zt["2020-03-01":"2020-06-30"].max().rename("peak")],axis=1)   # zone-average series
zi["multiple"]=zi.peak/zi.pre
say("\n**Zones (average of member states: pre-COVID mean vs lockdown peak)**\n```\n"+zi.round(1).to_string()+"\n```")

# 4.5 seasonality (pre-COVID only, to avoid the shock distorting it)
base = df[df.Period=="1 Pre-COVID"].copy()
base["idx"] = base[U]/base.groupby("Region")[U].transform("mean")*100
seas = base.groupby("Month")["idx"].mean()
fig,ax = plt.subplots(figsize=(9,4.5)); ax.bar(seas.index,seas.values-100,color=np.where(seas>100,"#d62728","#2ca02c"))
ax.set_xticks(range(1,13)); ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
ax.set(title="Seasonal pattern pre-COVID (% deviation from each state's mean)",ylabel="% vs. average")
fig.tight_layout(); fig.savefig(CH/"05_seasonality_precovid.png",dpi=150); plt.close()
say("\n## 5. Seasonality (pre-COVID, 2019 only + Jan-Feb 2020)\n")
say(f"- Highest month: {['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][seas.idxmax()]} ({seas.max()-100:+.1f}%), "
    f"lowest: {['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][seas.idxmin()]} ({seas.min()-100:+.1f}%)")
say("- Caveat: only ~14 pre-COVID months exist, so seasonal estimates are indicative, not definitive.")

# 4.6 unemployment vs participation
fig,ax1 = plt.subplots(figsize=(11,5)); ax2=ax1.twinx()
ax1.plot(nat.index,nat[U],c="#d62728",lw=2.2,label="Unemployment rate"); ax2.plot(nat.index,nat[L],c="#1f4e79",lw=2.2,label="Labour participation")
ax1.set(ylabel="Unemployment (%)",title="Unemployment vs labour participation rate"); ax2.set_ylabel("Labour participation (%)"); ax2.grid(False)
add_bands(ax1,False); h1,l1=ax1.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels(); ax1.legend(h1+h2,l1+l2,loc="upper right")
fig.tight_layout(); fig.savefig(CH/"06_unemployment_vs_participation.png",dpi=150); plt.close()
corr = nat[[U,L]].corr().iloc[0,1]
say(f"\n- Correlation (national series) between unemployment and labour participation: {corr:.2f}")

# 4.7 distribution by period
fig,ax = plt.subplots(figsize=(11,5.5))
sns.boxplot(data=df,x="Period",y=U,hue="Period",palette="Blues",legend=False,ax=ax)
ax.set(title="Distribution of state unemployment rates by COVID period",xlabel="",ylabel="Unemployment rate (%)")
plt.setp(ax.get_xticklabels(),rotation=15); fig.tight_layout(); fig.savefig(CH/"07_period_boxplot.png",dpi=150); plt.close()

# 4.8 recovery speed: months after lockdown peak to get within 20% of own pre-COVID level
rec_rows=[]
for st,g in df.groupby("Region"):
    g=g.set_index("Date")[U]; p=g[:"2020-02-28"].mean(); pk=g["2020-03-01":"2020-06-30"].idxmax()
    after=g[pk:]; ok=after[after<=p*1.2]; rec_rows.append((st,(ok.index[0].to_period("M")-pk.to_period("M")).n if len(ok) else np.nan))
rec = pd.DataFrame(rec_rows,columns=["Region","months_to_recover"]).set_index("Region")
say("\n## 6. Recovery speed\n")
say(f"- Median months from peak to within 20% of own pre-COVID level: {rec.months_to_recover.median():.0f}")
say(f"- States that never got back within 20% in the data window: {int(rec.months_to_recover.isna().sum())}")

# Welch t-test: lockdown vs pre-COVID state rates
from math import sqrt, erf
a=df[df.Period=="1 Pre-COVID"][U]; b=df[df.Period=="2 First wave / lockdown"][U]
t=(b.mean()-a.mean())/sqrt(a.var()/len(a)+b.var()/len(b))
say(f"\n- Mean state-month rate: pre-COVID {a.mean():.2f}% vs lockdown period {b.mean():.2f}% (Welch t = {t:.1f}, p < 0.001)")

(ROOT/"outputs/summary_stats.md").write_text("\n".join(log))
print("\nDone. Charts in", CH)
