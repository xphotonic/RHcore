import FormalField.Applications.ApplicationCore

namespace FormalField
namespace Applications

inductive PhysicsObligation where
  | carrier
  | metric
  | dimension
  | field
  | passage
  | flow
  | effect
  | readout
  | empiricalCalibration
deriving DecidableEq, Repr

structure PhysicsApplication where
  obligationReady : PhysicsObligation → Prop

def PhysicsStructuralReady (P : PhysicsApplication) : Prop :=
  P.obligationReady PhysicsObligation.carrier ∧
    P.obligationReady PhysicsObligation.metric ∧
    P.obligationReady PhysicsObligation.dimension ∧
    P.obligationReady PhysicsObligation.field ∧
    P.obligationReady PhysicsObligation.passage ∧
    P.obligationReady PhysicsObligation.flow ∧
    P.obligationReady PhysicsObligation.effect ∧
    P.obligationReady PhysicsObligation.readout

def PhysicsEmpiricalPending (P : PhysicsApplication) : Prop :=
  ¬ P.obligationReady PhysicsObligation.empiricalCalibration

theorem physics_structural_ready_carrier (P : PhysicsApplication) :
    PhysicsStructuralReady P → P.obligationReady PhysicsObligation.carrier := by
  intro h
  exact h.1

theorem physics_structural_ready_metric (P : PhysicsApplication) :
    PhysicsStructuralReady P → P.obligationReady PhysicsObligation.metric := by
  intro h
  exact h.2.1

theorem physics_structural_ready_dimension (P : PhysicsApplication) :
    PhysicsStructuralReady P → P.obligationReady PhysicsObligation.dimension := by
  intro h
  exact h.2.2.1

theorem physics_structural_ready_field (P : PhysicsApplication) :
    PhysicsStructuralReady P → P.obligationReady PhysicsObligation.field := by
  intro h
  exact h.2.2.2.1

theorem physics_structural_ready_passage (P : PhysicsApplication) :
    PhysicsStructuralReady P → P.obligationReady PhysicsObligation.passage := by
  intro h
  exact h.2.2.2.2.1

theorem physics_structural_ready_flow (P : PhysicsApplication) :
    PhysicsStructuralReady P → P.obligationReady PhysicsObligation.flow := by
  intro h
  exact h.2.2.2.2.2.1

theorem physics_structural_ready_effect (P : PhysicsApplication) :
    PhysicsStructuralReady P → P.obligationReady PhysicsObligation.effect := by
  intro h
  exact h.2.2.2.2.2.2.1

theorem physics_structural_ready_readout (P : PhysicsApplication) :
    PhysicsStructuralReady P → P.obligationReady PhysicsObligation.readout := by
  intro h
  exact h.2.2.2.2.2.2.2

-- Physics applications remain interpretive/empirical until calibration and
-- independent measurement are supplied.

end Applications
end FormalField
