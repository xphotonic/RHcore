FROM leanprover/lean4:v4.14.0

WORKDIR /workspace

COPY lean-toolchain lakefile.lean lake-manifest.json ./
COPY RhCore ./RhCore
COPY data ./data
COPY tools ./tools

RUN lake build RhCore.Final

CMD ["lake", "build", "RhCore.Final"]

