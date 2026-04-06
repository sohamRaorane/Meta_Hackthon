# data/routes.py
# ──────────────────────────────────────────────────────────────
# Upgraded: 8 real Mumbai multi-leg routes with waypoints.
# Each route has 2-3 legs. The agent must make a decision at
# each waypoint — budget and time carry over between legs.
# ──────────────────────────────────────────────────────────────

# ── CORRIDOR DATA ───────────────────────────────────────────────
# Each corridor = one leg of a journey.
# Properties per mode:
#   cost         → rupees
#   time_min     → fastest possible (minutes)
#   time_max     → slowest possible (minutes)
#   availability → probability mode actually shows up (0.0–1.0)

CORRIDORS = {

    # ── LEG 1 corridors ─────────────────────────────────────────

    "Andheri_East_to_Ghatkopar": {
        "train": {"cost": 10,  "time_min": 15, "time_max": 20, "availability": 0.85},
        "metro": {"cost": 40,  "time_min": 18, "time_max": 22, "availability": 0.95},
        "auto":  {"cost": 90,  "time_min": 25, "time_max": 50, "availability": 0.70},
        "bus":   {"cost": 10,  "time_min": 35, "time_max": 55, "availability": 0.85},
        "walk":  {"cost": 0,   "time_min": 80, "time_max": 100,"availability": 1.00},
    },
    "Ghatkopar_to_Kurla": {
        "metro": {"cost": 20,  "time_min": 8,  "time_max": 12, "availability": 0.95},
        "auto":  {"cost": 50,  "time_min": 10, "time_max": 20, "availability": 0.75},
        "bus":   {"cost": 10,  "time_min": 15, "time_max": 30, "availability": 0.80},
        "walk":  {"cost": 0,   "time_min": 25, "time_max": 35, "availability": 1.00},
        "train": {"cost": 10,  "time_min": 10, "time_max": 15, "availability": 0.80},
    },

    "Borivali_to_Andheri": {
        "train": {"cost": 10,  "time_min": 18, "time_max": 28, "availability": 0.80},
        "metro": {"cost": 40,  "time_min": 22, "time_max": 28, "availability": 0.92},
        "auto":  {"cost": 120, "time_min": 25, "time_max": 50, "availability": 0.65},
        "bus":   {"cost": 15,  "time_min": 35, "time_max": 60, "availability": 0.80},
        "walk":  {"cost": 0,   "time_min": 120,"time_max": 150,"availability": 1.00},
    },
    "Andheri_to_Ghatkopar_via_Metro": {
        "metro": {"cost": 40,  "time_min": 18, "time_max": 22, "availability": 0.95},
        "auto":  {"cost": 100, "time_min": 30, "time_max": 55, "availability": 0.60},
        "bus":   {"cost": 10,  "time_min": 40, "time_max": 65, "availability": 0.78},
        "walk":  {"cost": 0,   "time_min": 80, "time_max": 100,"availability": 1.00},
        "train": {"cost": 10,  "time_min": 20, "time_max": 28, "availability": 0.75},
    },
    "Ghatkopar_to_CST": {
        "train": {"cost": 15,  "time_min": 35, "time_max": 50, "availability": 0.82},
        "bus":   {"cost": 15,  "time_min": 55, "time_max": 80, "availability": 0.75},
        "auto":  {"cost": 200, "time_min": 45, "time_max": 75, "availability": 0.55},
        "walk":  {"cost": 0,   "time_min": 200,"time_max": 240,"availability": 1.00},
        "metro": {"cost": 50,  "time_min": 40, "time_max": 50, "availability": 0.90},
    },

    "Churchgate_to_Dadar": {
        "train": {"cost": 10,  "time_min": 18, "time_max": 25, "availability": 0.88},
        "bus":   {"cost": 10,  "time_min": 30, "time_max": 50, "availability": 0.80},
        "auto":  {"cost": 110, "time_min": 25, "time_max": 45, "availability": 0.70},
        "metro": {"cost": 40,  "time_min": 22, "time_max": 28, "availability": 0.90},
        "walk":  {"cost": 0,   "time_min": 90, "time_max": 110,"availability": 1.00},
    },
    "Dadar_to_Bandra": {
        "train": {"cost": 10,  "time_min": 12, "time_max": 18, "availability": 0.85},
        "bus":   {"cost": 10,  "time_min": 20, "time_max": 35, "availability": 0.82},
        "auto":  {"cost": 80,  "time_min": 18, "time_max": 30, "availability": 0.72},
        "metro": {"cost": 30,  "time_min": 15, "time_max": 20, "availability": 0.92},
        "walk":  {"cost": 0,   "time_min": 60, "time_max": 75, "availability": 1.00},
    },

    "CST_to_Kurla": {
        "train": {"cost": 10,  "time_min": 20, "time_max": 30, "availability": 0.80},
        "bus":   {"cost": 10,  "time_min": 35, "time_max": 55, "availability": 0.78},
        "auto":  {"cost": 150, "time_min": 30, "time_max": 55, "availability": 0.65},
        "metro": {"cost": 45,  "time_min": 28, "time_max": 35, "availability": 0.88},
        "walk":  {"cost": 0,   "time_min": 150,"time_max": 180,"availability": 1.00},
    },
    "Kurla_to_BKC": {
        "auto":  {"cost": 70,  "time_min": 12, "time_max": 22, "availability": 0.72},
        "bus":   {"cost": 10,  "time_min": 18, "time_max": 30, "availability": 0.80},
        "metro": {"cost": 30,  "time_min": 10, "time_max": 15, "availability": 0.90},
        "walk":  {"cost": 0,   "time_min": 30, "time_max": 40, "availability": 1.00},
        "train": {"cost": 10,  "time_min": 15, "time_max": 20, "availability": 0.75},
    },

    "Bandra_to_Andheri": {
        "train": {"cost": 10,  "time_min": 10, "time_max": 16, "availability": 0.87},
        "metro": {"cost": 30,  "time_min": 12, "time_max": 18, "availability": 0.93},
        "auto":  {"cost": 90,  "time_min": 15, "time_max": 30, "availability": 0.68},
        "bus":   {"cost": 10,  "time_min": 20, "time_max": 38, "availability": 0.80},
        "walk":  {"cost": 0,   "time_min": 70, "time_max": 90, "availability": 1.00},
    },
    "Andheri_to_Juhu": {
        "auto":  {"cost": 60,  "time_min": 10, "time_max": 20, "availability": 0.75},
        "bus":   {"cost": 10,  "time_min": 15, "time_max": 28, "availability": 0.82},
        "walk":  {"cost": 0,   "time_min": 35, "time_max": 45, "availability": 1.00},
        "metro": {"cost": 20,  "time_min": 12, "time_max": 18, "availability": 0.88},
        "train": {"cost": 10,  "time_min": 12, "time_max": 18, "availability": 0.78},
    },

    "Ghatkopar_to_Mankhurd": {
        "train": {"cost": 10,  "time_min": 12, "time_max": 18, "availability": 0.82},
        "metro": {"cost": 30,  "time_min": 15, "time_max": 20, "availability": 0.90},
        "auto":  {"cost": 80,  "time_min": 18, "time_max": 30, "availability": 0.68},
        "bus":   {"cost": 10,  "time_min": 22, "time_max": 38, "availability": 0.78},
        "walk":  {"cost": 0,   "time_min": 55, "time_max": 70, "availability": 1.00},
    },
    "Mankhurd_to_Vashi": {
        "train": {"cost": 15,  "time_min": 18, "time_max": 25, "availability": 0.85},
        "bus":   {"cost": 15,  "time_min": 28, "time_max": 45, "availability": 0.75},
        "auto":  {"cost": 110, "time_min": 22, "time_max": 38, "availability": 0.60},
        "walk":  {"cost": 0,   "time_min": 120,"time_max": 150,"availability": 1.00},
        "metro": {"cost": 40,  "time_min": 20, "time_max": 28, "availability": 0.88},
    },

    "Dadar_to_Sion": {
        "train": {"cost": 10,  "time_min": 8,  "time_max": 14, "availability": 0.85},
        "auto":  {"cost": 60,  "time_min": 12, "time_max": 22, "availability": 0.73},
        "bus":   {"cost": 10,  "time_min": 18, "time_max": 30, "availability": 0.80},
        "metro": {"cost": 25,  "time_min": 10, "time_max": 15, "availability": 0.90},
        "walk":  {"cost": 0,   "time_min": 35, "time_max": 45, "availability": 1.00},
    },
    "Sion_to_Kurla": {
        "train": {"cost": 10,  "time_min": 6,  "time_max": 10, "availability": 0.83},
        "auto":  {"cost": 50,  "time_min": 8,  "time_max": 18, "availability": 0.72},
        "bus":   {"cost": 10,  "time_min": 12, "time_max": 22, "availability": 0.80},
        "walk":  {"cost": 0,   "time_min": 20, "time_max": 28, "availability": 1.00},
        "metro": {"cost": 20,  "time_min": 8,  "time_max": 12, "availability": 0.88},
    },

    # Fallback used if corridor_key not found
    "default": {
        "train": {"cost": 10,  "time_min": 20, "time_max": 30, "availability": 0.85},
        "auto":  {"cost": 100, "time_min": 30, "time_max": 50, "availability": 0.65},
        "bus":   {"cost": 10,  "time_min": 40, "time_max": 60, "availability": 0.80},
        "metro": {"cost": 45,  "time_min": 25, "time_max": 35, "availability": 0.92},
        "walk":  {"cost": 0,   "time_min": 120,"time_max": 150,"availability": 1.00},
    },
}

# ── WEATHER MODIFIERS ────────────────────────────────────────────
# Multipliers applied on top of corridor data during simulation.
WEATHER_MODIFIERS = {
    "clear": {},
    "light_rain": {
        "auto_availability": 0.5,
        "auto_time_factor":  1.2,
        "bus_availability":  0.9,
        "bus_time_factor":   1.1,
    },
    "heavy_rain": {
        "auto_availability":  0.2,
        "auto_time_factor":   1.5,
        "bus_availability":   0.7,
        "bus_time_factor":    1.3,
        "train_availability": 0.85,
        "metro_availability": 0.95,
    },
}

# ── TASKS ────────────────────────────────────────────────────────
# Each task now has a `legs` list.
# Each leg = one step the agent must take.
# The agent decides transport mode at each leg separately.
# Budget and time carry over between legs.
#
# leg keys:
#   from_location  → where agent starts this leg
#   to_location    → where agent ends this leg
#   corridor_key   → which CORRIDORS entry to use
#   description    → shown to agent as context

TASKS = {

    # ── EASY: 2-leg, clear weather, generous budget/time ─────────
    "easy": {
        "origin":      "Andheri East",
        "destination": "Kurla Station",
        "legs": [
            {
                "from_location": "Andheri East",
                "to_location":   "Ghatkopar",
                "corridor_key":  "Andheri_East_to_Ghatkopar",
                "description":   "First leg: reach Ghatkopar as a transfer point",
            },
            {
                "from_location": "Ghatkopar",
                "to_location":   "Kurla Station",
                "corridor_key":  "Ghatkopar_to_Kurla",
                "description":   "Final leg: Ghatkopar to Kurla Station",
            },
        ],
        "time_limit":  60,
        "budget":      120.0,
        "seed":        42,
        "weather":     "clear",
        "disruptions": ["Harbour line delayed 20 min"],
        # sensor_reliability per mode [train, auto, bus, metro, walk]
        "sensor_reliability":        [0.9, 1.0, 1.0, 1.0, 1.0],
        "mid_journey_inject_step":   None,
        "mid_journey_event":         None,
        "max_steps":                 4,
    },

    # ── MEDIUM: 2-leg, heavy rain, tighter budget ────────────────
    "medium": {
        "origin":      "Borivali Station",
        "destination": "CST",
        "legs": [
            {
                "from_location": "Borivali Station",
                "to_location":   "Andheri",
                "corridor_key":  "Borivali_to_Andheri",
                "description":   "First leg: reach Andheri as transfer point",
            },
            {
                "from_location": "Andheri",
                "to_location":   "Ghatkopar",
                "corridor_key":  "Andheri_to_Ghatkopar_via_Metro",
                "description":   "Second leg: Andheri to Ghatkopar via Metro",
            },
            {
                "from_location": "Ghatkopar",
                "to_location":   "CST",
                "corridor_key":  "Ghatkopar_to_CST",
                "description":   "Final leg: Ghatkopar to CST",
            },
        ],
        "time_limit":  90,
        "budget":      80.0,
        "seed":        7,
        "weather":     "heavy_rain",
        "disruptions": [
            "Heavy rain — auto availability very low",
            "Western line slow — signal issues reported",
        ],
        "sensor_reliability":        [0.6, 0.3, 0.7, 1.0, 1.0],
        "mid_journey_inject_step":   2,
        "mid_journey_event":         "Bus service suspended on Andheri-Ghatkopar route. Re-plan now.",
        "max_steps":                 5,
    },

    # ── HARD: 3-leg, cascading failures, tight budget+time ───────
    "hard": {
        "origin":      "Churchgate",
        "destination": "BKC",
        "legs": [
            {
                "from_location": "Churchgate",
                "to_location":   "Dadar",
                "corridor_key":  "Churchgate_to_Dadar",
                "description":   "First leg: Churchgate to Dadar",
            },
            {
                "from_location": "Dadar",
                "to_location":   "CST",
                "corridor_key":  "CST_to_Kurla",
                "description":   "Second leg: Dadar area to CST junction",
            },
            {
                "from_location": "CST",
                "to_location":   "Kurla",
                "corridor_key":  "CST_to_Kurla",
                "description":   "Third leg: CST to Kurla transfer",
            },
            {
                "from_location": "Kurla",
                "to_location":   "BKC",
                "corridor_key":  "Kurla_to_BKC",
                "description":   "Final leg: Kurla to BKC",
            },
        ],
        "time_limit":  85,
        "budget":      75.0,
        "seed":        13,
        "weather":     "heavy_rain",
        "disruptions": [
            "Western line signal failure — severe delays",
            "Heavy rain across Mumbai",
            "Harbour line running 25 min late",
            "Auto strike reported in South Mumbai",
        ],
        "sensor_reliability":        [0.3, 0.2, 0.6, 0.8, 1.0],
        "mid_journey_inject_step":   2,
        "mid_journey_event":         "Kurla station flooded — trains not stopping at Kurla. Re-plan your final leg.",
        "max_steps":                 6,
    },

    # ── BONUS: Bandra to Juhu via Andheri (budget crisis) ────────
    "bonus": {
        "origin":      "Bandra Station",
        "destination": "Juhu Beach",
        "legs": [
            {
                "from_location": "Bandra Station",
                "to_location":   "Andheri",
                "corridor_key":  "Bandra_to_Andheri",
                "description":   "First leg: Bandra to Andheri",
            },
            {
                "from_location": "Andheri",
                "to_location":   "Juhu",
                "corridor_key":  "Andheri_to_Juhu",
                "description":   "Final leg: Andheri to Juhu Beach",
            },
        ],
        "time_limit":  40,
        "budget":      30.0,      # Very tight budget — auto impossible
        "seed":        99,
        "weather":     "light_rain",
        "disruptions": [
            "Light rain — auto fares surging",
            "Bus delays of 10 min expected",
        ],
        "sensor_reliability":        [0.8, 0.4, 0.9, 1.0, 1.0],
        "mid_journey_inject_step":   None,
        "mid_journey_event":         None,
        "max_steps":                 4,
    },
}