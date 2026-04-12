.PHONY: help paper clean check

help:
    @echo "Available targets:"
    @echo "  make paper   - build position paper PDF"
    @echo "  make clean   - remove build artifacts"
    @echo "  make check   - run LaTeX checks"

paper:
    ./scripts/build-paper.sh

clean:
    rm -rf papers/position-paper/build

check:
    ./scripts/check-latex.sh
