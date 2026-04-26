# Mumbai Last-Mile Crisis Response

## Training an AI Agent to Navigate Mumbai Commute Chaos with Reinforcement Learning

Mumbai has more than **120 lakh daily commuters**. Every day, people depend on trains, buses, autos, metro lines, and walking routes to reach offices, hospitals, colleges, and homes.

But anyone who has travelled knows the truth.

It is tough to make the perfect decision to choose which mode of transport to take given the budget and time one has. Especially since environment is not completely observable - we don't know how much delayed is the next bus, or which road is blocked, or how long is the queue in the metro.

We humans solve this using instinct.

We asked a different question:

**Can an AI agent learn to survive Mumbai commute chaos the same way humans do?**

That is the idea behind our project.

---

# The Problem We Chose

Most AI benchmarks test language, memory, or coding.

Real life is different.

Real life needs:

* making decisions with incomplete information
* balancing time vs cost
* reacting to disruptions
* planning multiple steps ahead
* adapting when the first plan fails

Mumbai commuting is a perfect real-world RL problem.

---


# What We Built

We created a custom reinforcement learning environment where an agent must complete trips across Mumbai using available transport options.

Example routes include:

* Andheri East → Kurla Station
* Andheri East → Ghatkopar → Kurla Station
* Ghatkopar → Kurla Station
* Multi-leg transfer journeys with intermediate hubs

At every step, the agent receives:

* Current location
* Final destination
* Time remaining
* Budget remaining
* Weather condition
* Available travel modes
* Estimated time and price
* Known disruptions

Then it must choose one action:

* Train
* Metro
* Bus
* Auto
* Walk

---

# Why This Is Hard

The best answer changes every episode.

Examples:

* During rain, autos become unreliable
* During train delays, metro may be better
* Low budget may force bus or walk
* Expensive first choice can ruin final leg

So the model cannot memorize one answer.

It must learn patterns.

---

# How We Trained the Agent

We used a **3-phase GRPO training pipeline**.

### Phase 1 — Easy Tasks

Simple routes with clear best choices.

### Phase 2 — Medium Tasks

More trade-offs between time and budget.

### Phase 3 — Hard Tasks

Disruptions, tight constraints, and multi-step planning.

The model repeatedly:

1. Reads scenario
2. Chooses transport
3. Receives reward
4. Improves future decisions

---

# Reward Design

The agent is rewarded for:

* reaching destination
* saving time
* staying inside budget
* selecting reliable transport
* making route progress

The agent is penalized for:

* wasting time
* overspending
* poor route choices
* failing trip completion

This creates realistic learning pressure.

---

# Results

## Success Rate Improvement

* Easy: **15% → 60%**
* Medium: **25% → 30%**
* Hard: **10% → 0%**
* Bonus: **60% → 85%**

## Mean Reward Improvement

* Easy: **-0.404 → 0.575**
* Medium: **-0.066 → 0.040**
* Hard: **0.263 → -0.016**
* Bonus: **0.525 → 0.980**

These results show strong gains in easier and moderate scenarios, with hard tasks remaining an open challenge.

---

# Training Visualization

![Training Results](training_results.png)

---

# Example Live Scenario

Trip:

**Andheri East → Kurla Station**

Starting Conditions:

* 45 minutes remaining
* ₹55 budget
* Light rain
* Train disruption warning

Trained agent selected:

1. Metro to Ghatkopar
2. Train to Kurla Station

Reached destination successfully with time left.

---

# Why This Matters Beyond Mumbai

This same framework can train agents for:

* delivery routing
* ambulance dispatch
* field workforce mobility
* disaster logistics
* smart city transport planning

---

# What We Learned

Bigger models are not always enough.

Sometimes the real improvement comes from:

* better environments
* better feedback loops
* better reward systems

That is the power of reinforcement learning.

---

# Honest Reflection

Our hard-mode tasks remain difficult.

That is expected.

Real-world planning under uncertainty is genuinely hard, and solving it fully is future work.

We chose realism over fake perfection.

---

# Final Thought

Mumbai commuters solve optimization problems every day without calling them optimization problems.

We simply built an environment where AI has to learn the same skill.

---

# Links

* Hugging Face Space: https://huggingface.co/spaces/eagle25/mumbai-lastmile-env
* API Docs: https://eagle25-mumbai-lastmile-env.hf.space/docs
* Live Environment: https://eagle25-mumbai-lastmile-env.hf.space
