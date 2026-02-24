# MLBB Real Data Integration Design

**Date:** 2026-02-25
**Status:** Approved

## Goal

Replace stubbed MLBB Academy client with real data integrations:
1. Validate player accounts using Game ID + Zone ID (returns in-game username)
2. Fetch real-time hero meta data (win rates, counters, synergies) from Moonton GMS API
3. Inject meta data into AI coaching graph for current, data-driven advice

## APIs Discovered

### Player ID Validation (moogold proxy to Moonton)
- **URL:** `POST https://moogold.com/wp-content/plugins/id-validation-new/id-validation-ajax.php`
- **Headers:** `Referer: https://moogold.com/product/mobile-legends/`, `Origin: https://moogold.com`
- **Body:** URL-encoded form with `text-5f6f144f8ffee={game_id}`, `text-1601115253775={zone_id}`, plus fixed product params
- **Response:** `{"title":"Validation","message":"User ID: 73128166\nServer ID: 2218\nIn-Game Nickname: Caeden+William\nCountry: TH","icon":"success","status":"true"}`

### Moonton GMS API (Academy data)
- **Base URL:** `https://api.gms.moontontech.com`
- **Auth:** None required
- **Method:** POST with JSON payload

#### Endpoints:
| Endpoint | Source ID | Use |
|----------|-----------|-----|
| Hero Rankings | `/api/gms/source/2669606/2756567` | Win/pick/ban rates by rank tier & time period |
| Hero Positions | `/api/gms/source/2669606/2756564` | Heroes by role + lane, full detail |
| Hero Counters | `/api/gms/source/2669606/2756569` (match_type=0) | Who counters this hero |
| Hero Synergies | `/api/gms/source/2669606/2756569` (match_type=1) | Best teammate heroes |
| Hero Skill Combos | `/api/gms/source/2669606/2674711` | Ability combos |
| Hero Rate (7d) | `/api/gms/source/2669606/2674709` | Win rate trend |
| Hero Rate (15d) | `/api/gms/source/2669606/2687909` | Win rate trend |
| Hero Rate (30d) | `/api/gms/source/2669606/2690860` | Win rate trend |

#### Payload format:
```json
{
  "pageSize": 20,
  "filters": [
    {"field": "bigrank", "operator": "eq", "value": "7"},
    {"field": "match_type", "operator": "eq", "value": "0"}
  ],
  "sorts": [{"data": {"field": "main_hero_win_rate", "order": "desc"}, "type": "sequence"}],
  "pageIndex": 1,
  "fields": ["main_hero", "main_hero_appearance_rate", "main_hero_ban_rate", "main_hero_win_rate", "main_heroid"]
}
```

#### Rank filter values:
- `101` = all ranks, `5` = epic, `6` = legend, `7` = mythic, `8` = honor, `9` = glory

#### Hero ID map (127 heroes):
127=Lukas, 126=Suyou, 125=Zhuxin, ... 1=Miya (full map in code)

## Architecture

### New Files
1. `app/services/mlbb_academy/validator.py` — Player ID validation
2. `app/services/mlbb_academy/meta_client.py` — Moonton GMS hero meta client with caching

### Modified Files
3. `app/services/mlbb_academy/client.py` — Simplified orchestration
4. `app/api/v1/players.py` — 2-step flow: validate → confirm → link
5. `app/models/schemas/player.py` — New validation/confirmation schemas
6. `frontend/src/pages/Profile.tsx` — Username confirmation UI
7. `app/services/langgraph/coaching_graph.py` — Inject real meta data into context
8. `app/core/config.py` — Add GMS base URL setting

## Account Linking Flow

```
1. User enters Game ID + Zone ID → clicks "Validate"
2. Backend calls moogold API → returns username + country
3. Frontend shows: "Is this your account: Caeden+William (TH)?"
4. User clicks "Confirm & Link"
5. Backend saves game_id, server_id, mlbb_username to User record
```

## AI Coaching Enhancement

When a user asks about a hero:
1. Coaching graph detects hero name in query
2. Calls MLBBMetaClient to get real-time data (counters, win rates, synergies)
3. Formats data as structured context
4. Appends to LLM prompt alongside RAG results
5. LLM gives advice grounded in current meta data

## Caching Strategy

- Hero rankings: cache 1 hour (data updates ~daily)
- Hero details: cache 6 hours (static-ish)
- Hero counters/synergies: cache 1 hour
- Player validation: no cache (always fresh)

## Implementation Tasks

1. Create validator.py with moogold API call
2. Create meta_client.py with all GMS endpoints + in-memory cache
3. Update players.py with validate → confirm → link flow
4. Update player schemas
5. Update Profile.tsx with confirmation step
6. Update coaching_graph.py to fetch and inject meta data
7. Update config.py with new settings
8. Test end-to-end
