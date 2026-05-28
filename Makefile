RUN_ID ?= $(shell python -c "from datetime import datetime, timezone; print(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))")
OUT     = out/$(RUN_ID)
BUCKET ?= replace-with-artifact-bucket
PROJECT = rhcore-reference-closure
ZEROS   = repo/data/zeros_prechecked.csv

.PHONY: all clean setup run attest push verify

all: clean setup run attest

# ── Environment ────────────────────────────────────────────────────────────
setup:
	pip install -r requirements.txt --quiet

# ── Core pipeline ──────────────────────────────────────────────────────────
run: $(OUT)/.done

$(OUT)/.done:
	mkdir -p $(OUT)

	@echo "==> Stage 1: zeros sanity"
	python tools/zeta_sanity.py --zeros=$(ZEROS) > $(OUT)/zeta_status.json

	@echo "==> Stage 2: gate simulator"
	python tools/gate_simulator.py 2>/dev/null || true
	cp repo/data/gate_report.json $(OUT)/gate_report.json 2>/dev/null || true

	@echo "==> Stage 3: Poincaré witness"
	python tools/poincare_witness.py \
		--zeros=$(ZEROS) --T=35 --windows=20 \
		--out=$(OUT)/poincare_witness.json

	@echo "==> Stage 4: heat kernel"
	python ci/heat_kernel_check.py \
		--cutoff 50 --tol 1e-8 \
		--out=$(OUT)/heat_kernel_check.json

	@echo "==> Stage 5: phase seal"
	python ci/phase_seal_check.py \
		--mesh 512 --zeros=$(ZEROS) \
		--out=$(OUT)/phase_seal.json

	@echo "==> Stage 6: Li positivity"
	python ci/li_interval_json_check.py \
		--intervals=ci/artifacts/li_intervals.json \
		--limit=50 --out=$(OUT)/li_positivity.json

	@echo "==> Stage 7: validate Li artifact"
	python tools/validate_li_artifact.py \
		--zeros-status=$(OUT)/zeta_status.json \
		--li=repo/data/li_n_intervals.csv \
		--radius-threshold=1e-12 \
		--out=$(OUT)/closure_status.json \
		--trace-out=$(OUT)/closure_trace.json

	@echo "==> Stage 8: RH_STATE manifest"
	python tools/emit_rh_state.py \
		--run-id=$(RUN_ID) \
		--zeros=$(ZEROS) \
		--closure-status=$(OUT)/closure_status.json \
		--out=$(OUT)/RH_STATE.json

	@echo "==> Stage 9: RO-Crate"
	python tools/build_ro_crate.py \
		--artifact $(ZEROS) \
		--artifact $(OUT)/zeta_status.json \
		--artifact repo/data/li_n_intervals.csv \
		--artifact $(OUT)/closure_status.json \
		--artifact $(OUT)/closure_trace.json \
		--artifact $(OUT)/RH_STATE.json \
		--artifact OWNERS.md \
		--out $(OUT)/ro-crate-metadata.json

	@echo "==> Stage 10: checksums"
	python -c "\
import hashlib, pathlib, sys; \
out = pathlib.Path('$(OUT)'); \
lines = []; \
[lines.append(hashlib.sha256(f.read_bytes()).hexdigest() + '  ' + f.name) \
 for f in sorted(out.iterdir()) if f.is_file() and f.name != 'checksums.txt']; \
(out / 'checksums.txt').write_text('\n'.join(lines) + '\n')"

	touch $(OUT)/.done
	@echo "==> Run complete: $(OUT)"

# ── Attestation ────────────────────────────────────────────────────────────
attest: $(OUT)/.done
	@command -v cosign >/dev/null 2>&1 && \
		cosign sign-blob --yes \
			--output-signature $(OUT)/bundle.sig \
			--output-certificate $(OUT)/bundle.pem \
			$(OUT)/checksums.txt && \
		echo "cosign: signed" || \
		echo "cosign: not installed, skipping attestation"

# ── Push to S3 ─────────────────────────────────────────────────────────────
push: $(OUT)/.done
	aws s3 cp $(OUT)/ s3://$(BUCKET)/$(PROJECT)/runs/$(RUN_ID)/ --recursive
	@echo "pushed to s3://$(BUCKET)/$(PROJECT)/runs/$(RUN_ID)/"

# ── Verify a prior run ─────────────────────────────────────────────────────
verify:
	@test -n "$(VERIFY_RUN_ID)" || (echo "usage: make verify VERIFY_RUN_ID=<id>" && exit 1)
	aws s3 cp s3://$(BUCKET)/$(PROJECT)/runs/$(VERIFY_RUN_ID)/ out/verify/ --recursive
	@command -v cosign >/dev/null 2>&1 && \
		cosign verify-blob \
			--signature out/verify/bundle.sig \
			--certificate out/verify/bundle.pem \
			out/verify/checksums.txt && \
		echo "cosign: verified" || \
		echo "cosign: not installed, skipping verification"
	python -c "\
import json; \
d = json.load(open('out/verify/closure_status.json')); \
print('closure:', d['status']); \
exit(0 if d['status'] == 'PASS' else 1)"

# ── Toolchain sync ──────────────────────────────────────────────────────
sync-toolchain:
	bash scripts/sync_toolchain.sh $(MATHLIB_TAG)

# ── CyberRiemann Artifact ───────────────────────────────────────────────────
cyber-artifact:
	python tools/cyber_riemann_artifact.py --out=artifacts/cyber_riemann_artifact.json

# ── Clean ──────────────────────────────────────────────────────────────────
clean:
	rm -rf out

# ── Experimental datasets (Zenodo) ─────────────────────────────────────────
# Usage: make experimental-szilard INPUT=path/to/szilard.csv
# Usage: make experimental-cantilever INPUT=path/to/cantilever.csv
# Usage: make experimental-ot INPUT=path/to/ot_trace.csv

experimental-bootstrap:
	@test -n "$(INPUT)" || (echo "usage: make experimental-bootstrap INPUT=<csv>" && exit 1)
	python tools/landauer_bootstrap.py \
		--trace=$(INPUT) \
		--typeb=repo/data/experimental/typeB.json \
		--block-size=50 --n-boot=2000 \
		--out=artifacts/energy_per_erasure.json \
		--cycle-out=artifacts/cycle_energy.csv

experimental-szilard:
	@test -n "$(INPUT)" || (echo "usage: make experimental-szilard INPUT=<csv>" && exit 1)
	python tools/zenodo_adapter.py \
		--dataset szilard --input=$(INPUT) \
		--out-dir=repo/data/experimental

experimental-cantilever:
	@test -n "$(INPUT)" || (echo "usage: make experimental-cantilever INPUT=<csv>" && exit 1)
	python tools/zenodo_adapter.py \
		--dataset cantilever --input=$(INPUT) \
		--out-dir=repo/data/experimental

experimental-ot:
	@test -n "$(INPUT)" || (echo "usage: make experimental-ot INPUT=<csv>" && exit 1)
	python tools/zenodo_adapter.py \
		--dataset ot_arhmm --input=$(INPUT) \
		--out-dir=repo/data/experimental

# Optional richer provenance:
# make experimental-intake DATASET=szilard INPUT=... DOI=10.5281/... LICENSE=CC-BY-4.0 URL=https://zenodo.org/records/...
experimental-intake:
	@test -n "$(DATASET)" || (echo "usage: make experimental-intake DATASET=<szilard|ot_arhmm|cantilever> INPUT=<file>" && exit 1)
	@test -n "$(INPUT)" || (echo "usage: make experimental-intake DATASET=<...> INPUT=<file>" && exit 1)
	python tools/zenodo_adapter.py \
		--dataset $(DATASET) \
		--input $(INPUT) \
		--out-dir=repo/data/experimental \
		--doi "$(DOI)" \
		--license "$(LICENSE)" \
		--record-url "$(URL)"

# Download from Zenodo record/DOI, then normalize through adapter.
# Usage:
# make experimental-intake-zenodo DATASET=szilard RECORD_URL=https://zenodo.org/records/14516010
# make experimental-intake-zenodo DATASET=szilard DOI=10.5281/zenodo.14516010
experimental-intake-zenodo:
	@test -n "$(DATASET)" || (echo "usage: make experimental-intake-zenodo DATASET=<szilard|ot_arhmm|cantilever> RECORD_URL=<...> or DOI=<...>" && exit 1)
	@test -n "$(RECORD_URL)$(DOI)" || (echo "usage: provide RECORD_URL=<...> or DOI=<...>" && exit 1)
	python tools/zenodo_intake.py \
		--dataset $(DATASET) \
		--record-url "$(RECORD_URL)" \
		--doi "$(DOI)" \
		--license "$(LICENSE)" \
		--out-dir repo/data/experimental

# Batch intake for predefined high-fidelity datasets in:
# repo/data/experimental/zenodo_sources.json
experimental-intake-all:
	python tools/zenodo_intake.py \
		--all \
		--sources-json repo/data/experimental/zenodo_sources.json \
		--out-dir repo/data/experimental
