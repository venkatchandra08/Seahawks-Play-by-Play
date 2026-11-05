# Seattle Seahawks Play-by-Play Analysis, 2024–2026

**Author:** Venkatram Chandra — freshman, Informatics, University of Washington; UW Sports Analytics Club
**Data:** [nflverse](https://github.com/nflverse) public play-by-play data (EPA model included in the dataset)
**Tools:** Python, pandas, matplotlib
**Snapshot:** Regular-season plays through Week 8 of the 2026 season (data pulled November 5, 2026). 2024 and 2025 are full seasons; 2026 is partial, so treat its numbers as noisier.

## The question

Seattle has rebuilt its identity under head coach Mike Macdonald. Using expected points added (EPA) per play — the standard efficiency metric in NFL analytics — this project asks: *what kind of team are the Seahawks now, and where is the offense leaving value on the table?*

## Headline findings

**1. The defense is the identity now — and it's elite.**
Defensive EPA per play allowed, league rank: **11th in 2024 → 2nd in 2025 → 5th in 2026**. In 2025 Seattle allowed **−0.116 EPA/play**, second-best in the NFL. Whatever else changes year to year, the defense has been a top-tier unit for two straight seasons.

**2. The 2025 passing jump was real — and it has cooled in 2026.**
Pass EPA/play went from **−0.015 (2024, Geno Smith)** to **+0.112 (2025, Sam Darnold's first season)**, with Darnold posting +0.126 EPA per pass play, 26 TDs against 14 INTs. In 2026 so far, pass EPA has slipped to **+0.026**, and Darnold's per-play EPA is negative (−0.071) with 9 interceptions in 228 pass plays.

**3. The 2026 problem is the run game and early downs.**
- Rushing EPA/play has collapsed to **−0.154** in 2026 (37.4% success rate), down from −0.049 in 2025.
- On early downs (1st & 2nd) in neutral game scripts, Seattle's EPA/play ranks **31st of 32** in 2026 (−0.144) — while calling runs *more* often than most teams (49.0% early-down pass rate, 22nd). Running more into a failing run game is the clearest play-calling tension in the data.
- Red-zone EPA has also regressed: 30th (2024) → 17th (2025) → 23rd (2026 so far).

**4. 2026 has been a roller coaster.**
Weekly offensive EPA swings from **+0.156 (Week 7)** to **−0.425 (Week 5)** — the offense is volatile week to week in a way the defense is not.

## Charts

- `charts/epa_by_season.svg` — offensive vs defensive EPA/play by season
- `charts/weekly_off_epa_2026.svg` — 2026 weekly offensive EPA with 3-week rolling average
- `charts/early_down_scatter.svg` — early-down pass rate vs early-down EPA, all 32 teams, 2025–26 (Seahawks highlighted)

Full numeric output is in `findings.txt`.

## How to run it

```bash
python3 -m venv .venv && .venv/bin/pip install pandas matplotlib pyarrow
mkdir -p data
for y in 2024 2025 2026; do
  curl -L -o data/play_by_play_$y.parquet \
    "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_$y.parquet"
done
.venv/bin/python analysis.py
```

## Methods & definitions

- **EPA/play:** mean expected points added per scrimmage play (pass + run plays only), regular season.
- **Success rate:** share of plays with EPA > 0.
- **Neutral script:** win probability between 20% and 80% (per nflverse's `wp`), early downs only — removes garbage-time and desperation play-calling from tendency stats.
- **Ranks** are among all 32 teams in the same season/sample.

## Limitations

- 2026 is a partial season (through Week 8): smaller samples, no opponent adjustment, and no bye-week correction.
- EPA is nflverse's model output, not raw outcomes; it doesn't separate QB, line, and receiver contributions.
- Play-calling findings are descriptive — they show *what happened*, not what *would* happen if Seattle passed more (defenses would adjust).

## Next steps

- Add opponent-adjusted EPA and split by personnel/down-and-distance buckets.
- Extend the same framework to the NFL Big Data Bowl 2027 (Combine → NFL performance).
- Re-run at the end of the 2026 season and compare the partial-season signal against the full-year result.

## One-line version (for applications / LinkedIn)

> Built a Python/pandas analysis of ~150K NFL plays (nflverse) evaluating the Seahawks' offensive and defensive efficiency with EPA/play, success rate, and neutral-script play-calling tendencies; found an elite top-5 defense paired with a bottom-ranked early-down offense driven by rushing inefficiency in 2026.
