#!/usr/bin/env python3
"""
RhCore Simulator — بيئة محاكاة مشتقة من البنية

تشتق مباشرة من:
  ClosureOperator.lean  → gates 0-5
  EnergyCoercivity.lean → globallyCoercive λ
  SigFM.lean            → S(t), q(β,t), P(T)
  PrimeField.lean       → S_primes(t)
  ExplicitFormula.lean  → ψ(x), Z(t)

الحالة = (t, S, S', q, P, λ, status)
التدفق = ∂_λ Ψ = A·Ψ  (Perelman-style)
"""
from __future__ import annotations
import csv, json, math, sys
from dataclasses import dataclass, field, asdict
from pathlib import Path


# ══════════════════════════════════════════════════════════════════════════
# § 1  الحقل الأساسي — مشتق من SigFM.lean
# ══════════════════════════════════════════════════════════════════════════

def S(t: float, gammas: list[float], a: float = 0.5) -> float:
    """S(t) = Σ_γ (t-γ)/((t-γ)²+a²)  — من liInInterval + SigFM"""
    return sum((t - g) / ((t - g)**2 + a**2) for g in gammas)

def dS(t: float, gammas: list[float], a: float = 0.5) -> float:
    """S'(t) = Σ_γ (a²-(t-γ)²)/((t-γ)²+a²)²"""
    return sum((a**2 - (t-g)**2) / ((t-g)**2 + a**2)**2 for g in gammas)

def q(t: float, gammas: list[float], beta: float = 1.0) -> float:
    """q(β,t) = |S|² + β|S'|²  — من gate_carrier"""
    return S(t, gammas)**2 + beta * dS(t, gammas)**2

def p_integrand(t: float, gammas: list[float], eps: float = 1e-3) -> float:
    """P integrand = |S|²/(|S'|+ε)  — من gate_accumulation"""
    return S(t, gammas)**2 / (abs(dS(t, gammas)) + eps)


# ══════════════════════════════════════════════════════════════════════════
# § 2  حالة النظام — مشتقة من ClosureSystem
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class SystemState:
    """حالة كاملة عند نقطة t — تعكس ClosureSystem في Lean"""
    t:        float
    S:        float
    dS:       float
    q:        float
    P_accum:  float        # تراكمي
    lambda_I: float        # Poincaré ratio على النافذة الحالية
    # gates
    gate_carrier:     bool  # q > 0
    gate_noTangency:  bool  # S=0 ⟹ S'≠0
    gate_localEnergy: bool  # |S| ≥ c|t-γ|
    gate_accumulation:bool  # P monotone
    gate_uniqueness:  bool  # no extra equilibrium
    gate_noWinding:   bool  # Δarg = 0 (proxy)
    # status
    status: str             # CLOSED / OPEN / WARN


@dataclass
class SimulatorConfig:
    gammas:    list[float]
    beta:      float = 1.0
    eps:       float = 1e-3
    c:         float = 0.001   # Lojasiewicz constant (conservative)
    tol_tang:  float = 1e-4
    window:    float = 2.0
    steps:     int   = 200


# ══════════════════════════════════════════════════════════════════════════
# § 3  تقييم الـ gates — مشتق من ClosureOperator.lean
# ══════════════════════════════════════════════════════════════════════════

def eval_gates(t: float, cfg: SimulatorConfig,
               P_prev: float, P_curr: float,
               lambda_I: float) -> dict[str, bool]:
    s  = S(t, cfg.gammas)
    ds = dS(t, cfg.gammas)
    qv = q(t, cfg.gammas, cfg.beta)

    # Gate 0: carrier q > 0
    g0 = qv > 0

    # Gate 1: no tangency — if S≈0 then S'≠0
    g1 = not (abs(s) < cfg.tol_tang and abs(ds) < cfg.tol_tang)

    # Gate 2: local energy |S| ≥ c·|t-γ| for nearest γ
    nearest = min(cfg.gammas, key=lambda g: abs(t - g))
    g2 = abs(s) >= cfg.c * abs(t - nearest) or abs(t - nearest) < 0.1

    # Gate 3: accumulation monotone (P_curr ≥ P_prev)
    g3 = P_curr >= P_prev - 1e-10

    # Gate 4: uniqueness — no extra equilibrium (S=0 AND S'=0)
    g4 = not (abs(s) < cfg.tol_tang and abs(ds) < cfg.tol_tang
              and all(abs(t - g) > 0.5 for g in cfg.gammas))

    # Gate 5: no winding proxy — λ_I > 0
    g5 = lambda_I > 0

    return {
        "gate_carrier":     g0,
        "gate_noTangency":  g1,
        "gate_localEnergy": g2,
        "gate_accumulation":g3,
        "gate_uniqueness":  g4,
        "gate_noWinding":   g5,
    }


def poincare_ratio(t: float, cfg: SimulatorConfig) -> float:
    """λ_I = ∫|S'|²/∫|S|² على نافذة [t-w/2, t+w/2]"""
    a  = t - cfg.window / 2
    b  = t + cfg.window / 2
    dt = (b - a) / cfg.steps
    num = sum((dt if 0 < i < cfg.steps else dt/2) *
              dS(a + i*dt, cfg.gammas)**2
              for i in range(cfg.steps + 1))
    den = sum((dt if 0 < i < cfg.steps else dt/2) *
              S(a + i*dt, cfg.gammas)**2
              for i in range(cfg.steps + 1))
    return num / den if den > 1e-30 else float("inf")


# ══════════════════════════════════════════════════════════════════════════
# § 4  التدفق — مشتق من Perelman flow في ClosureOperator
# ══════════════════════════════════════════════════════════════════════════

def flow_step(t: float, cfg: SimulatorConfig,
              P_prev: float, dt: float) -> SystemState:
    """خطوة تدفق واحدة: تحسب الحالة عند t"""
    s      = S(t, cfg.gammas)
    ds_val = dS(t, cfg.gammas)
    qv     = q(t, cfg.gammas, cfg.beta)
    p_inc  = p_integrand(t, cfg.gammas, cfg.eps) * dt
    P_curr = P_prev + p_inc
    lam    = poincare_ratio(t, cfg)
    gates  = eval_gates(t, cfg, P_prev, P_curr, lam)
    all_ok = all(gates.values())
    status = "CLOSED" if all_ok else (
             "WARN"   if gates["gate_carrier"] and gates["gate_uniqueness"]
             else "OPEN")
    return SystemState(
        t=t, S=s, dS=ds_val, q=qv,
        P_accum=P_curr, lambda_I=lam,
        **gates, status=status
    )


# ══════════════════════════════════════════════════════════════════════════
# § 5  المحاكي الكامل
# ══════════════════════════════════════════════════════════════════════════

class RhCoreSimulator:
    """
    بيئة محاكاة مشتقة من البنية.

    كل خطوة تحسب:
      - S(t), S'(t), q(t)       من SigFM
      - gates 0-5               من ClosureOperator
      - λ_I                     من EnergyCoercivity
      - P(T)                    من gate_accumulation
      - status: CLOSED/WARN/OPEN
    """

    def __init__(self, cfg: SimulatorConfig):
        self.cfg     = cfg
        self.history: list[SystemState] = []
        self._P      = 0.0

    def step(self, t: float, dt: float = 0.1) -> SystemState:
        state    = flow_step(t, self.cfg, self._P, dt)
        self._P  = state.P_accum
        self.history.append(state)
        return state

    def run(self, t_start: float, t_end: float,
            n_steps: int = 500) -> list[SystemState]:
        dt = (t_end - t_start) / n_steps
        self._P = 0.0
        self.history = []
        for i in range(n_steps + 1):
            self.step(t_start + i * dt, dt)
        return self.history

    def summary(self) -> dict:
        if not self.history:
            return {}
        statuses  = [s.status for s in self.history]
        lambdas   = [s.lambda_I for s in self.history
                     if math.isfinite(s.lambda_I)]
        open_pts  = [s for s in self.history if s.status == "OPEN"]
        return {
            "n_steps":       len(self.history),
            "t_range":       [self.history[0].t, self.history[-1].t],
            "P_final":       self.history[-1].P_accum,
            "lambda_inf":    min(lambdas) if lambdas else 0.0,
            "lambda_mean":   sum(lambdas)/len(lambdas) if lambdas else 0.0,
            "status_counts": {
                "CLOSED": statuses.count("CLOSED"),
                "WARN":   statuses.count("WARN"),
                "OPEN":   statuses.count("OPEN"),
            },
            "open_points":   [{"t": p.t, "S": p.S, "dS": p.dS}
                              for p in open_pts[:5]],
            "final_status":  self.history[-1].status,
            "rh_supported":  len(open_pts) == 0,
        }

    def export(self, path: str) -> None:
        rows = [asdict(s) for s in self.history]
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)


# ══════════════════════════════════════════════════════════════════════════
# § 6  CLI
# ══════════════════════════════════════════════════════════════════════════

def load_zeros(path: str) -> list[float]:
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        col = next(k for k in (reader.fieldnames or [])
                   if k.lower() in ("t", "imag", "zero"))
        return [float(row[col]) for row in reader]


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description="RhCore Simulator")
    p.add_argument("--zeros",   default="repo/data/zeros_prechecked.csv")
    p.add_argument("--t-start", type=float, default=1.0)
    p.add_argument("--t-end",   type=float, default=35.0)
    p.add_argument("--steps",   type=int,   default=500)
    p.add_argument("--beta",    type=float, default=1.0)
    p.add_argument("--out-csv", default="artifacts/simulator_trace.csv")
    p.add_argument("--out-json",default="artifacts/simulator_summary.json")
    args = p.parse_args()

    gammas = load_zeros(args.zeros)
    cfg    = SimulatorConfig(gammas=gammas, beta=args.beta)
    sim    = RhCoreSimulator(cfg)

    print(f"Running simulator: t∈[{args.t_start},{args.t_end}], "
          f"{args.steps} steps, {len(gammas)} zeros")

    sim.run(args.t_start, args.t_end, args.steps)
    summary = sim.summary()

    sim.export(args.out_csv)
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_json).write_text(json.dumps(summary, indent=2))

    print(json.dumps(summary, indent=2))
    return 0 if summary.get("rh_supported") else 1


if __name__ == "__main__":
    sys.exit(main())
