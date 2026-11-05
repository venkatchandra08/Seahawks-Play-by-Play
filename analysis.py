"""
Seattle Seahawks Play-by-Play Analysis (2024-2026)
Data: nflverse play-by-play (public). Metrics: EPA/play, success rate,
early-down pass rate in neutral game scripts.

Run:  .venv/bin/python analysis.py
Outputs: charts/*.png and findings.txt
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEA_COLOR = "#002244"   # Seahawks navy
SEA_GREEN = "#69BE28"   # Seahawks action green
GREY = "#8A8D8F"

COLS = ["season", "week", "season_type", "game_id", "posteam", "defteam",
        "play_type", "epa", "success", "down", "ydstogo", "yardline_100",
        "score_differential", "qtr", "half_seconds_remaining",
        "passer_player_name", "rusher_player_name", "receiver_player_name",
        "yards_gained", "touchdown", "interception", "wp"]

frames = []
for y in (2024, 2025, 2026):
    df = pd.read_parquet(f"data/play_by_play_{y}.parquet", columns=COLS)
    frames.append(df)
pbp = pd.concat(frames, ignore_index=True)
reg = pbp[pbp.season_type == "REG"].copy()
# scrimmage plays only
plays = reg[reg.play_type.isin(["pass", "run"]) & reg.epa.notna()].copy()
plays["success"] = (plays.epa > 0).astype(float)

lines = []
def out(s=""):
    lines.append(s)
    print(s)

# ---------- 1. Team EPA/play: offense and defense, by season ----------
out("=" * 70)
out("1) TEAM EPA PER PLAY (regular season, pass+run plays)")
for season in (2024, 2025, 2026):
    s = plays[plays.season == season]
    off = s.groupby("posteam").epa.mean().sort_values(ascending=False)
    deff = s.groupby("defteam").epa.mean().sort_values()  # lower = better defense
    sea_o = off["SEA"]; sea_d = deff["SEA"]
    out(f"{season}: SEA offense EPA/play {sea_o:+.3f} (rank {list(off.index).index('SEA')+1} of {len(off)}), "
        f"defense EPA/play allowed {sea_d:+.3f} (rank {list(deff.index).index('SEA')+1} of {len(deff)})")

# ---------- 2. Seahawks pass vs run ----------
out()
out("=" * 70)
out("2) SEAHAWKS PASS vs RUN (EPA/play, success rate)")
sea = plays[plays.posteam == "SEA"]
for season in (2024, 2025, 2026):
    for pt in ("pass", "run"):
        g = sea[(sea.season == season) & (sea.play_type == pt)]
        out(f"{season} {pt:4s}: n={len(g):4d}  EPA/play {g.epa.mean():+.3f}  success {g.success.mean():.1%}")

# ---------- 3. Seahawks QB play ----------
out()
out("=" * 70)
out("3) SEAHAWKS QUARTERBACKS (dropback EPA, min 100 dropbacks)")
db = reg[(reg.play_type == "pass") & reg.epa.notna()]
for season in (2024, 2025, 2026):
    sea_db = db[(db.season == season) & (db.posteam == "SEA")]
    # approximate dropbacks = pass plays grouped by passer
    g = sea_db.groupby("passer_player_name").agg(n=("epa", "size"), epa=("epa", "mean"),
                                                  td=("touchdown", "sum"),
                                                  inter=("interception", "sum")).reset_index()
    g = g[g.n >= 100].sort_values("n", ascending=False)
    for _, r in g.iterrows():
        out(f"{season} {r.passer_player_name}: {int(r.n)} pass plays, EPA/play {r.epa:+.3f}, "
            f"{int(r.td)} TD, {int(r.inter)} INT")

# ---------- 4. Early-down pass rate, neutral script ----------
out()
out("=" * 70)
out("4) EARLY-DOWN (1st & 2nd) PASS RATE, NEUTRAL SCRIPT")
out("   (Q1-Q3 + Q4 within one score, win prob 20-80%)")
neu = plays[(plays.down <= 2) & (plays.wp.between(0.2, 0.8))]
for season in (2024, 2025, 2026):
    rates = neu[neu.season == season].groupby("posteam").play_type.apply(
        lambda x: (x == "pass").mean()).sort_values(ascending=False)
    sea_g = neu[(neu.season == season) & (neu.posteam == "SEA")]
    sea_rate = (sea_g.play_type == "pass").mean()
    sea_epa = sea_g.epa.mean()
    lg_epa = neu[neu.season == season].groupby("posteam").epa.mean()
    out(f"{season}: SEA early-down pass rate {sea_rate:.1%} (rank {list(rates.index).index('SEA')+1} of {len(rates)}), "
        f"early-down EPA/play {sea_epa:+.3f} (rank {list(lg_epa.sort_values(ascending=False).index).index('SEA')+1})")

# ---------- 5. Red zone ----------
out()
out("=" * 70)
out("5) RED ZONE OFFENSE (plays inside the 20)")
rz = plays[plays.yardline_100 <= 20]
for season in (2024, 2025, 2026):
    r = rz[rz.season == season]
    team = r.assign(td_play=(r.epa.notna()))  # placeholder
    sea_rz = r[r.posteam == "SEA"]
    sea_td = sea_rz.groupby("game_id")  # not drives; use success + EPA instead
    lg = r.groupby("posteam").epa.mean().sort_values(ascending=False)
    out(f"{season}: SEA red-zone EPA/play {sea_rz.epa.mean():+.3f} "
        f"(rank {list(lg.index).index('SEA')+1} of {len(lg)}), plays: {len(sea_rz)}")

# ---------- 6. 2026 weekly trend ----------
out()
out("=" * 70)
out("6) SEAHAWKS 2026 WEEKLY OFFENSIVE EPA/PLAY")
sea26 = sea[sea.season == 2026]
wk = sea26.groupby("week").epa.mean()
for w, v in wk.items():
    out(f"  Week {int(w)}: {v:+.3f}  (n={int((sea26.week==w).sum())})")

# ---------- Charts ----------
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GREY})

# Chart 1: SEA offense vs defense EPA by season
seasons = [2024, 2025, 2026]
off_v, def_v = [], []
for season in seasons:
    s = plays[plays.season == season]
    off_v.append(s.groupby("posteam").epa.mean()["SEA"])
    def_v.append(s.groupby("defteam").epa.mean()["SEA"])
x = np.arange(len(seasons)); wdt = 0.38
fig, ax = plt.subplots(figsize=(7.5, 4.2))
ax.bar(x - wdt/2, off_v, wdt, color=SEA_COLOR, label="Offense (EPA/play)")
ax.bar(x + wdt/2, def_v, wdt, color=SEA_GREEN, label="Defense (EPA/play allowed, lower = better)")
ax.axhline(0, color=GREY, lw=1)
ax.set_xticks(x); ax.set_xticklabels([str(s) for s in seasons])
ax.set_title("Seattle Seahawks — offensive vs defensive EPA per play")
ax.legend(frameon=False)
for bars in ax.containers:
    ax.bar_label(bars, fmt="%+.3f", padding=2, fontsize=9)
fig.tight_layout(); fig.savefig("charts/epa_by_season.svg"); plt.close(fig)

# Chart 2: 2026 weekly offensive EPA trend
fig, ax = plt.subplots(figsize=(7.5, 4.2))
ax.plot(wk.index, wk.values, marker="o", color=SEA_COLOR, lw=2, label="Weekly offensive EPA/play")
ax.plot(wk.index, wk.rolling(3, min_periods=1).mean(), color=SEA_GREEN, lw=2, ls="--", label="3-week rolling avg")
ax.axhline(0, color=GREY, lw=1)
ax.set_xlabel("2026 regular-season week"); ax.set_ylabel("EPA/play")
ax.set_title("Seahawks 2026 — weekly offensive EPA per play")
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig("charts/weekly_off_epa_2026.svg"); plt.close(fig)

# Chart 3: Early-down pass rate vs early-down EPA, 2025+2026 combined, all teams
neu2 = neu[neu.season >= 2025]
agg = neu2.groupby("posteam").agg(pr=("play_type", lambda x: (x == "pass").mean()),
                                  epa=("epa", "mean"), n=("epa", "size")).reset_index()
fig, ax = plt.subplots(figsize=(7.5, 4.6))
ax.scatter(agg.pr * 100, agg.epa, color=GREY, s=45)
sea_row = agg[agg.posteam == "SEA"].iloc[0]
ax.scatter([sea_row.pr * 100], [sea_row.epa], color=SEA_GREEN, edgecolor=SEA_COLOR, s=170, zorder=5)
ax.annotate("SEA", (sea_row.pr * 100, sea_row.epa), textcoords="offset points",
            xytext=(8, 8), fontweight="bold", color=SEA_COLOR)
ax.axhline(0, color=GREY, lw=0.8)
ax.set_xlabel("Early-down pass rate % (neutral script)")
ax.set_ylabel("Early-down EPA/play")
ax.set_title("Early-down tendencies, 2025-2026 — all 32 teams")
fig.tight_layout(); fig.savefig("charts/early_down_scatter.svg"); plt.close(fig)

with open("findings.txt", "w") as f:
    f.write("\n".join(lines))
print("\nCharts written to charts/ and findings to findings.txt")
