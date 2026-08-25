# Experimental Report 001

**Autobiographical Memory Transplantation in an Artificial Agent**  
Leo Ferres

## Automatic evidence

Run from the package root:

```sh
./verify.sh
```

The verifier checks the exact file inventory, validates every SHA-256 digest,
and recomputes the core claims from `evidence/` using
`tools/recompute_core_claims.py` and only Python's standard library.

`report/manuscript/scripts/generate_assets.py` reads `evidence/` and
regenerates the manuscript's numerical values, tables and figures.

## Evidence files

`evidence/` holds the study's frozen materials. Absolute workstation paths in
the coding key and analysis files were rewritten as package-relative paths so
the package is self-contained. No data, coding, adjudication, or analysis value
was changed.

## Build

The canonical PDF is `report/paper.pdf`. To regenerate it:

```sh
make -C report/manuscript
```

The regenerated PDF is written to `report/manuscript/build/paper.pdf`. The
build requires Pandoc, XeLaTeX, Biber, Latexmk, Matplotlib and NumPy. Rerunning
the experimental apparatus additionally requires the packages named in the
report and access to compatible model endpoints.

## Freeze rule

`report/manuscript/paper.md` is content-frozen. Release engineering may
regenerate evidence assets and repair build output. Reopening substantive
prose requires a new author decision.

## Licensing

The report, evidence, and materials are licensed CC BY 4.0; see `LICENSE`.
The code is licensed MIT; see `LICENSE-CODE`. Code means
`evidence/03_apparatus/`, `tools/`, `report/manuscript/scripts/`, and
`verify.sh`.

Cite the package using `CITATION.cff`.
