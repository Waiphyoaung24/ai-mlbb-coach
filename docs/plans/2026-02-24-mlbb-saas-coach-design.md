# MLBB AI Coach SaaS - Design Document

**Date:** 2026-02-24
**Status:** Approved
**Target Market:** Myanmar (MM), later SEA

---

## 1. Product Overview

A SaaS AI coaching platform for Mobile Legends Bang Bang (MLBB) targeting two user segments:

- **Solo ranked players (Free tier):** Gameplay weakness detection, rank progression tracking, personalized coaching plans, AI coaching chat.
- **Esports teams (Paid tier):** Competitor pick/ban tracking, team composition analysis, AI-generated scouting reports, plus all solo features.

Primary market is Myanmar. UI supports Burmese + English. Freemium model: solo players free, teams pay.

---

## 2. Architecture

**Approach:** Monolith First. Single FastAPI application with clean domain boundaries. PostgreSQL for persistent data, Pinecone for vector search (RAG), Redis for sessions/cache. React frontend with Vite.

**LLM Providers:** Anthropic Claude + Google Gemini (user-selectable per request).

**Context7:** Used during development (MCP server for up-to-date docs) and in product (additional knowledge retrieval for live meta updates).

---

## 3. User Model

### Free Tier (Solo Players)
- AI coaching chat (rate-limited, e.g. 20 queries/day)
- MLBB Academy integration for auto-fetching match data
- Gameplay weakness detection
- Rank progression tracking
- Weekly coaching plans
- Hero guides and build recommendations

### Paid Tier (Teams / Pro)
- Everything in Free, unlimited queries
- Competitor pick/ban tracking dashboard
- Team composition analysis
- AI-generated scouting reports on opponents
- Manual scrim data input + automated tournament data scraping
- Team management (invite members, assign roles: owner, coach, analyst, player)
- Export reports as PDF

### Authentication
- Email/password + social login
- JWT-based tokens
- Team entity with multi-member support and role-based access

---

## 4. Project Structure

```
app/
├── api/
│   ├── v1/
│   │   ├── auth.py           # Login, register, token refresh
│   │   ├── chat.py           # AI coaching chat
│   │   ├── heroes.py         # Hero info, builds
│   │   ├── matchup.py        # Matchup analysis
│   │   ├── players.py        # Solo player profile, stats, tracking
│   │   ├── teams.py          # Team management
│   │   ├── competitors.py    # Competitor analysis, pick/ban
│   │   ├── scouting.py       # Scouting reports
│   │   └── coaching.py       # Coaching plans, weakness detection
│   └── deps.py               # Shared dependencies (auth, DB session)
├── core/
│   ├── config.py
│   ├── security.py           # JWT, password hashing
│   └── database.py           # SQLAlchemy engine, session
├── models/
│   ├── db/                   # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── team.py
│   │   ├── match.py
│   │   ├── pick_ban.py
│   │   └── coaching_plan.py
│   └── schemas/              # Pydantic request/response schemas
│       ├── auth.py
│       ├── chat.py
│       ├── player.py
│       ├── team.py
│       ├── competitor.py
│       └── coaching.py
├── services/
│   ├── llm/                  # LLM providers (Claude + Gemini)
│   ├── rag/                  # RAG retrieval (Pinecone)
│   ├── langgraph/            # Coaching conversation workflows
│   ├── analytics/            # Pick/ban analysis, trends
│   ├── scouting/             # Competitor scouting reports
│   ├── coaching/             # Weakness detection, coaching plans
│   ├── scraper/              # Tournament data scraping
│   └── mlbb_academy/         # MLBB Academy API integration
├── data/                     # MLBB knowledge base (heroes, items, strategies)
├── utils/
│   ├── session_manager.py
│   └── rate_limiter.py
└── main.py

frontend/                     # React + Vite + TypeScript
├── src/
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Chat.tsx
│   │   ├── TeamDashboard.tsx
│   │   ├── PickBan.tsx
│   │   ├── Scouting.tsx
│   │   ├── CoachingPlan.tsx
│   │   └── Profile.tsx
│   ├── components/
│   │   ├── ChatBox.tsx
│   │   ├── HeroCard.tsx
│   │   ├── PickBanChart.tsx
│   │   ├── RankProgressChart.tsx
│   │   └── MatchInputForm.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── i18n.ts           # Burmese + English
│   └── App.tsx
├── package.json
└── vite.config.ts
```

---

## 5. Database Schema

### users
| Column | Type | Notes |
|--------|------|-------|
| id | UUID, PK | |
| email | VARCHAR, unique | |
| username | VARCHAR, unique | |
| hashed_password | VARCHAR | |
| tier | ENUM(free, pro) | |
| mlbb_game_id | VARCHAR, nullable | Link to in-game account |
| mlbb_server_id | VARCHAR, nullable | |
| language | VARCHAR, default 'my' | Burmese |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### teams
| Column | Type | Notes |
|--------|------|-------|
| id | UUID, PK | |
| name | VARCHAR | |
| owner_id | FK → users | |
| tier | ENUM(free, pro) | |
| region | VARCHAR, default 'MM' | |
| created_at | TIMESTAMP | |

### team_members
| Column | Type | Notes |
|--------|------|-------|
| team_id | FK → teams | |
| user_id | FK → users | |
| role | ENUM(owner, coach, analyst, player) | |
| joined_at | TIMESTAMP | |

### matches
| Column | Type | Notes |
|--------|------|-------|
| id | UUID, PK | |
| team_id | FK → teams, nullable | |
| user_id | FK → users | |
| source | ENUM(manual, mlbb_academy, scraped) | |
| match_type | ENUM(ranked, tournament, scrim, custom) | |
| result | ENUM(win, loss) | |
| duration_seconds | INTEGER | |
| hero_played | VARCHAR | |
| role_played | VARCHAR | |
| kills, deaths, assists | INTEGER | |
| gold_earned | INTEGER | |
| damage_dealt | INTEGER | |
| match_date | TIMESTAMP | |
| opponent_team_name | VARCHAR, nullable | |
| notes | TEXT, nullable | |
| raw_data | JSONB, nullable | Full MLBB Academy response |
| created_at | TIMESTAMP | |

### pick_ban_records
| Column | Type | Notes |
|--------|------|-------|
| id | UUID, PK | |
| team_id | FK → teams | |
| opponent_team_name | VARCHAR | |
| tournament_name | VARCHAR, nullable | |
| match_date | TIMESTAMP | |
| source | ENUM(manual, scraped) | |
| phase | ENUM(first_ban, second_ban, first_pick, second_pick) | |
| hero_name | VARCHAR | |
| action | ENUM(pick, ban) | |
| side | ENUM(blue, red) | |
| created_at | TIMESTAMP | |

### coaching_plans
| Column | Type | Notes |
|--------|------|-------|
| id | UUID, PK | |
| user_id | FK → users | |
| plan_type | ENUM(daily, weekly) | |
| focus_areas | JSONB | |
| tasks | JSONB | [{task, completed, notes}] |
| generated_by | ENUM(ai, manual) | |
| valid_from | DATE | |
| valid_until | DATE | |
| created_at | TIMESTAMP | |

### player_stats_snapshot
| Column | Type | Notes |
|--------|------|-------|
| id | UUID, PK | |
| user_id | FK → users | |
| rank_tier | VARCHAR | |
| rank_stars | INTEGER | |
| win_rate | FLOAT | |
| top_heroes | JSONB | |
| weaknesses_detected | JSONB | |
| snapshot_date | DATE | |
| created_at | TIMESTAMP | |

### scouting_reports
| Column | Type | Notes |
|--------|------|-------|
| id | UUID, PK | |
| team_id | FK → teams | |
| opponent_team_name | VARCHAR | |
| generated_by_llm | ENUM(claude, gemini) | |
| report_content | TEXT | |
| pick_ban_summary | JSONB | |
| key_players | JSONB | |
| recommended_strategy | TEXT | |
| created_at | TIMESTAMP | |

---

## 6. Key Feature Flows

### Flow 1: MLBB Academy Data Integration (Solo Players)

```
Player enters Game ID + Server ID in our app
    → Backend calls MLBB Academy verification endpoint
    → Player receives verification code in in-game mail
    → Player enters verification code
    → Backend authenticates with MLBB Academy
    → Fetch: rank, hero stats, match history, win rates
    → Store in matches + player_stats_snapshot tables
    → Trigger AI weakness analysis
    → Periodic re-sync (daily/on-demand) for fresh data
```

Fallback: manual match input form if Academy API is unavailable.

### Flow 2: Gameplay Weakness Detection

```
After 5+ matches synced from MLBB Academy:
    → Aggregate stats (KDA, win rate by hero, role distribution)
    → RAG retrieval: compare against ideal stats for rank
    → LLM analysis: identify patterns
        "High deaths = poor positioning"
        "Low farm = inefficient rotation"
    → Generate weakness report with specific tips
    → Store in player_stats_snapshot
    → Feed into coaching plan generation
```

### Flow 3: Competitor Pick/Ban Analysis (Teams)

```
Team inputs pick/ban data (manual form OR scraper)
    → Store in pick_ban_records
    → On request:
        → Aggregate opponent history
        → Calculate: pick rate, ban rate, first-pick priority, flex picks
        → Detect patterns
        → LLM generates natural language summary
        → Display in dashboard with charts
```

### Flow 4: Scouting Report Generation

```
Team requests scouting report on opponent
    → Pull pick_ban_records for that opponent
    → Pull any match records against them
    → RAG retrieval: current meta, hero matchups
    → LangGraph workflow:
        1. Analyze opponent hero pool and preferences
        2. Identify win conditions and strategies
        3. Find exploitable weaknesses
        4. Recommend draft strategy
        5. Suggest counter-picks and bans
    → Generate report → Store → Allow PDF export
```

### Flow 5: Rank Progression Tracking

```
After each MLBB Academy data sync:
    → Update player_stats_snapshot (daily)
    → Track rank changes over time
    → Calculate trends (climbing, stagnating, dropping)
    → Weekly: LLM generates progress summary
    → Integrate with coaching plan adjustments
```

---

## 7. Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI (Python 3.11+) |
| Frontend | React + Vite + TypeScript |
| Database | PostgreSQL + Alembic migrations |
| Cache | Redis |
| Vector DB | Pinecone |
| Embeddings | HuggingFace (all-MiniLM-L6-v2) |
| LLM | Anthropic Claude + Google Gemini |
| AI Framework | LangChain + LangGraph |
| Knowledge | Context7 MCP (dev + product) |
| Auth | JWT (python-jose) + passlib |
| Charts | Recharts |
| i18n | react-i18next (Burmese + English) |
| Deployment | Docker + Docker Compose + Nginx |
| PDF Export | WeasyPrint or ReportLab |
| Scraping | httpx + BeautifulSoup |

---

## 8. MVP Phasing

### Phase 1 - Foundation
1. Git init + proper .gitignore + secure .env
2. Restructure project to new layout
3. Auth system (register, login, JWT)
4. PostgreSQL models + Alembic migrations
5. MLBB Academy integration (Game ID + Server ID + verification)
6. AI coaching chat (port existing, with auth)
7. React frontend (login, dashboard, chat)
8. Burmese language support (UI strings)

### Phase 2 - Solo Features
9. Weakness detection from synced match data
10. Rank progression tracking + charts
11. Personalized weekly coaching plans
12. Expanded hero database (all heroes, not just MM)

### Phase 3 - Team Features
13. Team creation + member management
14. Pick/ban data input form
15. Pick/ban analysis dashboard with charts
16. Scouting report generation
17. Team composition analysis

### Phase 4 - Scale
18. Tournament data scraper
19. PDF export for reports
20. Rate limiting for free tier
21. Payment integration (Myanmar market)
22. Context7 for live meta knowledge updates

---

## 9. What's Explicitly Out of Scope

- Mobile app (ship web first)
- Discord/Telegram bots
- Real-time WebSocket features
- AI image/replay analysis
- Languages beyond Burmese + English
- Hero pool analysis feature (cut for MVP simplicity)

---

## 10. Testing Strategy

- **Unit tests:** Service layer (analytics calculations, weakness detection)
- **Integration tests:** API endpoints with test database
- **E2E:** Critical flows (register → link MLBB account → view analysis)
- pytest + pytest-asyncio

---

## 11. Data Sources

- **Player data:** MLBB Academy (mobilelegends.com/academy/self) via Game ID + Server ID + verification code
- **Hero/item data:** Local knowledge base + community APIs ([ridwaanhall/api-mobilelegends](https://github.com/ridwaanhall/api-mobilelegends))
- **Tournament data:** Web scraping from public tournament sites (Phase 4)
- **Meta/strategy:** RAG from curated knowledge base + Context7 for live updates
