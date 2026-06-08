import Mathlib

noncomputable section

open scoped Matrix

namespace FormalField.Core

abbrev TriadicSpace := EuclideanSpace ℝ (Fin 3)

def v : TriadicSpace := ![(1 : ℝ), (2 : ℝ), (3 : ℝ)]

def k (R : TriadicSpace) : ℝ :=
  inner R v / inner v v

def projTriadic (R : TriadicSpace) : TriadicSpace :=
  k R • v

theorem one_sq_add_two_sq_add_three_sq : (1 : ℝ) ^ 2 + 2 ^ 2 + 3 ^ 2 = 14 := by
  norm_num

theorem inner_v_v : inner v v = (14 : ℝ) := by
  simp [v, PiLp.inner_apply, Fin.sum_univ_three]
  norm_num

theorem v_ne_zero : v ≠ 0 := by
  intro hv
  have h0 := congrArg (fun x : TriadicSpace => x 0) hv
  norm_num [v] at h0

theorem k_eq_inner_div_fourteen (R : TriadicSpace) :
    k R = inner R v / 14 := by
  rw [k, inner_v_v]

theorem projTriadic_mem_span (R : TriadicSpace) :
    projTriadic R ∈ Submodule.span ℝ ({v} : Set TriadicSpace) := by
  refine Submodule.mem_span_singleton.mpr ?_
  exact ⟨k R, rfl⟩

theorem projTriadic_coord0 (R : TriadicSpace) :
    projTriadic R 0 = k R := by
  simp [projTriadic, v]

theorem projTriadic_coord1 (R : TriadicSpace) :
    projTriadic R 1 = 2 * k R := by
  simp [projTriadic, v, mul_comm]

theorem projTriadic_coord2 (R : TriadicSpace) :
    projTriadic R 2 = 3 * k R := by
  simp [projTriadic, v, mul_comm]

theorem projTriadic_coords (R : TriadicSpace) :
    projTriadic R = ![k R, 2 * k R, 3 * k R] := by
  ext i
  fin_cases i
  · simp [projTriadic_coord0]
  · simp [projTriadic_coord1]
  · simp [projTriadic_coord2]

theorem projTriadic_ratio_AB (R : TriadicSpace) (hk : k R ≠ 0) :
    projTriadic R 0 / projTriadic R 1 = (1 : ℝ) / 2 := by
  rw [projTriadic_coord0, projTriadic_coord1]
  field_simp [hk]
  ring

theorem projTriadic_ratio_AC (R : TriadicSpace) (hk : k R ≠ 0) :
    projTriadic R 0 / projTriadic R 2 = (1 : ℝ) / 3 := by
  rw [projTriadic_coord0, projTriadic_coord2]
  field_simp [hk]
  ring

theorem projTriadic_ratio_BC (R : TriadicSpace) (hk : k R ≠ 0) :
    projTriadic R 1 / projTriadic R 2 = (2 : ℝ) / 3 := by
  rw [projTriadic_coord1, projTriadic_coord2]
  field_simp [hk]
  ring

theorem inner_sub_projTriadic_v_eq_zero (R : TriadicSpace) :
    inner (R - projTriadic R) v = (0 : ℝ) := by
  rw [inner_sub_left, projTriadic, real_inner_smul_left, inner_v_v, k_eq_inner_div_fourteen]
  ring

theorem sub_smul_eq_sub_proj_add (R : TriadicSpace) (t : ℝ) :
    R - t • v = (R - projTriadic R) + (k R - t) • v := by
  ext i
  fin_cases i
  · simp [projTriadic, projTriadic_coord0, v, sub_eq_add_neg]
    ring
  · simp [projTriadic, projTriadic_coord1, v, sub_eq_add_neg]
    ring
  · simp [projTriadic, projTriadic_coord2, v, sub_eq_add_neg]
    ring

theorem norm_sq_sub_smul_v (R : TriadicSpace) (t : ℝ) :
    ‖R - t • v‖ ^ 2 = ‖R - projTriadic R‖ ^ 2 + ‖(k R - t) • v‖ ^ 2 := by
  rw [sub_smul_eq_sub_proj_add R t]
  have horth : inner (R - projTriadic R) ((k R - t) • v) = (0 : ℝ) := by
    calc
      inner (R - projTriadic R) ((k R - t) • v)
          = (k R - t) * inner (R - projTriadic R) v := by
              rw [real_inner_smul_right]
      _ = 0 := by rw [inner_sub_projTriadic_v_eq_zero, mul_zero]
  simpa [sq] using norm_add_sq_eq_norm_sq_add_norm_sq_real horth

theorem projTriadic_minimizes (R : TriadicSpace) (t : ℝ) :
    ‖R - projTriadic R‖ ^ 2 ≤ ‖R - t • v‖ ^ 2 := by
  have h := norm_sq_sub_smul_v R t
  nlinarith [sq_nonneg ‖(k R - t) • v‖]

theorem eq_projTriadic_of_norm_sq_eq (R : TriadicSpace) {t : ℝ}
    (h : ‖R - t • v‖ ^ 2 = ‖R - projTriadic R‖ ^ 2) :
    t • v = projTriadic R := by
  have hdecomp := norm_sq_sub_smul_v R t
  have hzero : ‖(k R - t) • v‖ ^ 2 = 0 := by
    linarith
  have hnorm : ‖(k R - t) • v‖ = 0 := by
    nlinarith
  have hsmul : (k R - t) • v = 0 := by
    exact norm_eq_zero.mp hnorm
  rcases smul_eq_zero.mp hsmul with hkt | hv
  · have ht : t = k R := by linarith
    simp [projTriadic, ht]
  · exact (v_ne_zero hv).elim

theorem projTriadic_unique_on_span (R S : TriadicSpace)
    (hS : S ∈ Submodule.span ℝ ({v} : Set TriadicSpace))
    (hmin : ‖R - S‖ ^ 2 = ‖R - projTriadic R‖ ^ 2) :
    S = projTriadic R := by
  rcases Submodule.mem_span_singleton.mp hS with ⟨t, rfl⟩
  exact eq_projTriadic_of_norm_sq_eq R hmin

end FormalField.Core
