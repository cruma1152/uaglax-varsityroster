# UAGLAX — Postseason Bracket

What got built for the 2026 OHSAA D1 Girls Lacrosse State Tournament, and what
needs to happen to ship it.

## What changed

**Airtable** (UAGLAX base, `appsmS3D5vAFqTSTm`)
- New table: **Tournament** (`tblVubZUK2cXhJZz4`)
- 70 records pre-loaded: 7 play-ins, 32 R1 District Semis, 16 R2 District Finals, 8 R3 Regional Semis, 4 R4 Regional Finals, 2 State Semis, 1 State Final
- Region 3 is UA's region. Region 4 (Cincinnati) seeds are best-known from MaxPreps; OHSAA hadn't published their Region 4 page yet at build time — if anything looks off there, edit directly in Airtable.
- Two play-ins were already completed at build time and are pre-marked Final:
  - **P3b**: Cleveland Heights 18, Perrysburg 13 → Cleveland Heights advances to G3
  - **P5b**: Mentor 11, Canton GlenOak 1 → Mentor advances to G5
- One row was added to the existing **Schedule** table: UA's R1 game vs Northmont (5/14 7:00 PM), so the regular in-app PIN-gated score entry works for UA's first playoff game.

**Worker** (`Portal/vh-api-worker.js`)
- New endpoint **`GET /lacrosse/bracket`** — returns all 70 games in a clean JSON shape, same wildcard CORS as the schedule feed.
- New endpoint **`PATCH /lacrosse/bracket/{recordId}`** — PIN-gated (same `X-UAGLAX-PIN` header / same `UAGLAX_SCORE_PIN` secret as the schedule). Accepts `topScore`, `bottomScore`, `final`. When `final` is true, it computes the winner, writes the `Winner` field, then PATCHes the next round's matching slot (Top Team or Bottom Team) with the winner's name and seed — so the bracket auto-advances.

**App** (`Lacrosse Roster/index.html`)
- New **Tournament** card below the Schedule & Results card.
- Three views, switchable via tabs at the top of the card:
  - **UA Path** (default) — UA's 6-step climb to the state championship. Each step shows the round, the opponent (or "Winner of G27 vs G28" placeholder for unknowns), date/time, and score once played. The current round is highlighted gold.
  - **Region** (Region 1 / Region 2 / Region 3 (UA) / Region 4) — lined-bracket view of one region's 4 rounds, horizontal-scrollable on phones. Region 3 auto-scrolls to UA's game on load.
  - **Final Four** — state semis + state final, with location shown for the final (Historic Crew Stadium).
- A "Tournament" jump button was added next to the existing "Schedule & Results" jump button at the top.
- The card auto-refreshes every 90 seconds so parents see brackets fill in throughout game days.

**Service worker** (`Lacrosse Roster/sw.js`)
- Cache version bumped from `uaglax-v5` → `uaglax-v6` so installed PWAs pick up the new HTML on next launch.

## What you need to do before this works

### 1. Deploy the worker
From wherever you deploy:
```
wrangler deploy
```

The two existing UAGLAX env vars (`UAGLAX_AIRTABLE_KEY` and `UAGLAX_SCORE_PIN`) are reused — no new secrets required. The PAT just needs `data.records:read` and `data.records:write` on the Tournament table, which it inherits from being scoped to the whole base.

Smoke tests after deploy:
```
# GET bracket — should return 70 games
curl -s https://vh-api.charles-9e5.workers.dev/lacrosse/bracket | head -c 300

# PATCH a game without PIN — should 401
curl -i -X PATCH https://vh-api.charles-9e5.workers.dev/lacrosse/bracket/recDJvM86zqZUsSoK \
  -H "Content-Type: application/json" \
  -H "X-UAGLAX-PIN: WRONG" \
  -d '{"topScore": 10}'
```

(That record ID is UA's G25 vs Northmont — replace with another from the GET response if you want to test on something else.)

### 2. Push the updated app
Push `Lacrosse Roster/index.html` and `Lacrosse Roster/sw.js` to GitHub Pages. Installed PWAs will see the new SW on their next launch and the new HTML on the next online load.

### 3. (Optional) Verify Region 4 data
OHSAA hadn't published Region 4 at build time. I used MaxPreps for seeds/teams/times. If anything looks wrong in Region 4 when you view it in the app, edit the rows directly in Airtable → Tournament. The same goes for any future schedule changes — Airtable is the source of truth.

## How to use it during a game

For **UA's playoff games**, the existing flow works:
- Tap the lock icon on the Schedule card, type your PIN, edit Our/Opp/Final on UA's row, tap Save.
- UA's game on 5/14 vs Northmont is already in the Schedule.
- After each round, add UA's next opponent to the Schedule manually (same as you do for regular-season scheduling). Or skip that and just enter scores via the Tournament approach below.

For **bracket games (any of the 70 games, including UA's)**:
- The new PATCH endpoint accepts the same `X-UAGLAX-PIN` header. There's no inline score-entry UI for bracket games yet — for v1 you can either:
  - Edit the Tournament table directly in Airtable (Top Score, Bottom Score, Final). This works fine but **won't auto-advance the winner** to the next round (the worker only auto-advances on PATCH, not on Airtable direct edits).
  - To get the auto-advance, send a quick PATCH from the command line, like:
    ```
    curl -X PATCH https://vh-api.charles-9e5.workers.dev/lacrosse/bracket/{recordId} \
      -H "Content-Type: application/json" -H "X-UAGLAX-PIN: <your-pin>" \
      -d '{"topScore": 14, "bottomScore": 8, "final": true}'
    ```
- Either way the bracket display in the app updates within 90 seconds.

## Future polish (not in this build)

- **In-app score entry for bracket games** — wiring the bracket cards to the existing lock/PIN UI so Charles can update bracket scores from the phone the same way as schedule scores. Best next step.
- **Auto-sync between Schedule and Tournament for UA games** — when Charles enters UA's score on the Schedule card, automatically mirror it to the matching Tournament row (and trigger auto-advance). Removes the dual-edit dance for UA's games.
- **Live "you're playing tonight" banner** — extend the existing `liveNow` banner to surface UA's tournament game when one is in progress.
- **State Final at Crew Stadium hype card** — once UA makes it.
