# data/routes.py
# ──────────────────────────────────────────────────────────────
# This file is the "database" for the environment.
# It contains all Mumbai transport data: routes, costs, times,
# weather effects, and the 3 task configurations.
# No logic runs here — it's pure data that environment.py reads.
# ──────────────────────────────────────────────────────────────

# CORRIDORS defines each possible route in the simulation.
# For each route, we list every transport mode and its properties:
#   cost        → how many rupees it costs
#   time_min    → fastest possible time (in minutes)
#   time_max    → slowest possible time (in minutes)
#   availability → probability (0.0 to 1.0) that this mode is actually available
#                  Example: 0.90 means 90% chance the train is running
CORRIDORS = {
    "Andheri_East_to_Kurla_Station": {
        "train": {"cost": 10,  "time_min": 18, "time_max": 22, "availability": 0.90},
        "auto":  {"cost": 85,  "time_min": 25, "time_max": 45, "availability": 0.70},
        "bus":   {"cost": 10,  "time_min": 35, "time_max": 55, "availability": 0.85},
        "metro": {"cost": 40,  "time_min": 20, "time_max": 24, "availability": 0.95},
        "walk":  {"cost": 0,   "time_min": 90, "time_max": 110, "availability": 1.00},
    },
    "Borivali_Station_to_CST": {
        "train": {"cost": 15,  "time_min": 55, "time_max": 70,  "availability": 0.85},
        "auto":  {"cost": 400, "time_min": 75, "time_max": 110, "availability": 0.50},
        "bus":   {"cost": 15,  "time_min": 90, "time_max": 120, "availability": 0.80},
        "metro": {"cost": 60,  "time_min": 50, "time_max": 65,  "availability": 0.90},
        "walk":  {"cost": 0,   "time_min": 300, "time_max": 360, "availability": 1.00},
    },
    # "default" is a fallback used if a corridor_key isn't found
    "default": {
        "train": {"cost": 10,  "time_min": 20, "time_max": 30, "availability": 0.85},
        "auto":  {"cost": 100, "time_min": 30, "time_max": 50, "availability": 0.65},
        "bus":   {"cost": 10,  "time_min": 40, "time_max": 60, "availability": 0.80},
        "metro": {"cost": 45,  "time_min": 25, "time_max": 35, "availability": 0.92},
        "walk":  {"cost": 0,   "time_min": 120, "time_max": 150, "availability": 1.00},
    },
}

# WEATHER_MODIFIERS tells the simulation how rain changes each mode.
# These are multiplier factors applied on top of the CORRIDORS data.
# Example: in heavy_rain, auto_availability becomes 0.2 (very rare to find one)
# and auto_time_factor = 1.5 means it takes 50% longer than normal.
# If a mode isn't listed here, it's unaffected by the weather.
WEATHER_MODIFIERS = {
    "clear": {},  # No changes in clear weather
    "light_rain": {
        "auto_availability": 0.5,   # Harder to find an auto
        "auto_time_factor": 1.2,    # 20% slower
        "bus_availability": 0.9,
        "bus_time_factor": 1.1,
    },
    "heavy_rain": {
        "auto_availability": 0.2,   # Almost impossible to find an auto
        "auto_time_factor": 1.5,    # 50% slower
        "bus_availability": 0.7,
        "bus_time_factor": 1.3,
        "train_availability": 0.85,
        "metro_availability": 0.95, # Metro is mostly weather-proof
    },
}

# TASKS defines the 3 challenge levels (easy, medium, hard).
# Each task is a scenario the AI agent must solve.
# The environment reads this to know: where does the agent start?
# What's the time limit? What disruptions exist?
TASKS = {
    "easy": {
        "origin": "Andheri East",
        "destination": "Kurla Station",
        "corridor_key": "Andheri_East_to_Kurla_Station",
        "time_limit": 45,           # Agent has 45 minutes to reach destination
        "budget": 100.0,            # ₹100 to spend
        "seed": 42,                 # Fixed seed = reproducible randomness
        "weather": "clear",
        "disruptions": ["Harbour line delayed 20 min"],
        # sensor_reliability: how trustworthy is the data for each mode?
        # [train, auto, bus, metro, walk] → 1.0 = perfect info, 0.3 = very uncertain
        "sensor_reliability": [0.9, 1.0, 1.0, 1.0, 1.0],
        "mid_journey_inject_step": None,  # No surprise event mid-journey
        "mid_journey_event": None,
        "max_steps": 3,             # Agent gets 3 chances to make decisions
    },
    "medium": {
        "origin": "Andheri East",
        "destination": "Kurla Station",
        "corridor_key": "Andheri_East_to_Kurla_Station",
        "time_limit": 40,           # Tighter time limit
        "budget": 80.0,             # ₹80 — tighter budget
        "seed": 7,
        "weather": "heavy_rain",    # Harder weather
        "disruptions": ["Heavy rain — auto availability very low"],
        "sensor_reliability": [0.9, 0.3, 0.7, 1.0, 1.0],  # Auto data is uncertain (0.3)
        "mid_journey_inject_step": None,
        "mid_journey_event": None,
        "max_steps": 3,
    },
    "hard": {
        "origin": "Borivali Station",
        "destination": "CST",
        "corridor_key": "Borivali_Station_to_CST",
        "time_limit": 75,
        "budget": 80.0,
        "seed": 13,
        "weather": "heavy_rain",
        "disruptions": [
            "Western line signal failure — severe delays",
            "Heavy rain",
            "Metro queue: 15 min wait at Borivali",
        ],
        "sensor_reliability": [0.3, 0.4, 0.6, 0.7, 1.0],  # Most data is uncertain
        "mid_journey_inject_step": 2,   # At step 2, inject a surprise event
        "mid_journey_event": "Bus diverted — your chosen bus is not coming. Re-plan now.",
        "max_steps": 4,                 # Agent gets 4 chances (harder task = more steps)
    },
}