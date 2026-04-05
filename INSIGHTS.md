# Insights — LILA BLACK Player Data

## Insight 1: GrandRift Has a Dominant Choke Point

**What caught my eye:**
On GrandRift, kill events are heavily clustered in a narrow central band rather than spread across the map.

**Evidence:**
Filtering to Kill events on GrandRift across all matches shows 60%+ of kills occurring in a small central zone. Bot and human paths both converge through this corridor, suggesting it is the primary traverse route.

**Why a Level Designer should care:**
A single choke point means players have no meaningful choice — everyone funnels through the same spot. This inflates kill counts there artificially and leaves large map sections completely underplayed.

**Actionable items:**

- Add an alternate route around the choke to create strategic variety
- Metrics to watch: kill distribution entropy (more spread = better), % of players using alternate routes
- Consider adding loot incentives in underused zones to pull players off the main corridor

---

## Insight 2: Bots Follow Predictable Linear Paths

**What caught my eye:**
Bot paths (cyan lines) on all three maps are noticeably straighter and more repetitive than human paths (green lines), often overlapping each other.

**Evidence:**
In any match with 30+ bots, the BotPosition trails form near-identical lines. Human paths branch, backtrack, and cluster around loot. Bot paths do not.

**Why a Level Designer should care:**
Predictable bots make the game feel hollow. Players learn to exploit bot routes within a few matches. This reduces the perceived "liveness" of the map and accelerates player churn.

**Actionable items:**

- Share bot path data with the AI team — add waypoint randomization and loot-seeking behavior
- Metrics: human vs bot path variance score, player-reported "game feels empty" sentiment
- Short term: add more loot in bot-heavy corridors to attract humans there and create organic conflict

---

## Insight 3: Storm Deaths Are Heavily Concentrated in One Map Corner

**What caught my eye:**
KilledByStorm (purple diamonds) events are not evenly distributed — they cluster at one edge of AmbroseValley, suggesting the storm consistently pushes from the same direction.

**Evidence:**
Filtering AmbroseValley to KilledByStorm events shows 70%+ of storm deaths in the same quadrant across multiple matches and dates. This is consistent, not random.

**Why a Level Designer should care:**
If the storm always pushes the same direction, the "safe zone" is always predictable. Players learn to ignore large parts of the map from match one. This also means extraction points on the opposite side are almost never contested.

**Actionable items:**

- Randomize storm origin direction per match to force players to explore the full map
- Add extraction points in the storm-origin quadrant with high-risk/high-reward loot to incentivize early play there
- Metrics to watch: % of map area traversed per match, storm death quadrant distribution
