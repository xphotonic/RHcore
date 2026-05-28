# Perovskite Device CSV Schema

Use `perovskite_devices_template.csv` to track JV, MPP, EQE, stability, and
provenance fields for perovskite devices.

Required schema:

```text
device_id,wafer_id,cell_xy,active_area_cm2,stack_description,substrate,batch_date,encapsulation,precondition_protocol,temperature_C,humidity_RH_pct,atm,scan_speed_Vs,scan_dir,illumination_spectrum,illumination_intensity_sun,Voc_V,Jsc_mAcm2,FF_pct,PCE_MPP_pct,PCE_JV_fwd_pct,PCE_JV_rev_pct,hysteresis_index,series_R_ohmcm2,shunt_R_kohmcm2,stabilization_time_s,stability_protocol,MPPT_window_s,EQE_file,JV_fwd_file,JV_rev_file,MPP_trace_file,IV_raw_file,notes,operator,analysis_script,analysis_version,doi_or_repo
```

Key units:

- `active_area_cm2`: cm^2
- `temperature_C`: deg C
- `humidity_RH_pct`: percent RH
- `scan_speed_Vs`: V/s
- `illumination_intensity_sun`: suns
- `Voc_V`: V
- `Jsc_mAcm2`: mA/cm^2
- `FF_pct`, `PCE_*_pct`: percent
- `series_R_ohmcm2`: ohm cm^2
- `shunt_R_kohmcm2`: kohm cm^2

Hysteresis:

```text
hysteresis_index = abs(PCE_JV_fwd_pct - PCE_JV_rev_pct) / max(PCE_JV_fwd_pct, PCE_JV_rev_pct)
```

Validation/enrichment:

```bash
python tools/validate_perovskite_csv.py \
  --csv data/perovskite/perovskite_devices_template.csv \
  --out outputs/perovskite_devices_enriched.csv \
  --checksums outputs/perovskite_checksums.txt \
  --report outputs/perovskite_validation.json
```

The checksum file records SHA256 hashes for source files referenced by
`EQE_file`, `JV_fwd_file`, `JV_rev_file`, `MPP_trace_file`, and `IV_raw_file`
when those files exist relative to the CSV directory.

Use `--strict-files` when the raw files must already be present and the run
should fail on any missing EQE/JV/MPP/IV reference.
