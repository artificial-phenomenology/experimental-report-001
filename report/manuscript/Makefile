SHELL := /bin/bash

PAPER ?= paper.md
PANDOC ?= pandoc
LATEXMK ?= latexmk
PYTHON ?= python3
BUILD_DIR ?= build
LOCAL_PRACTICE ?= ../../../ai-native-practice

STEM := $(basename $(notdir $(PAPER)))
NOTE_CACHE := .cache/ai-native-practice-note.md
NOTE_REVISION := .cache/ai-native-practice-note.revision
NOTE_MD := $(BUILD_DIR)/ai-native-practice-note.md
NOTE_TEX := $(BUILD_DIR)/ai-native-practice-note.tex
VALUES := generated/values.json
EXPANDED_MD := $(BUILD_DIR)/$(STEM)-expanded.md
COMPLETE_MD := $(BUILD_DIR)/$(STEM)-complete.md
OUTPUT_TEX := $(BUILD_DIR)/$(STEM).tex
OUTPUT_PDF := $(BUILD_DIR)/$(STEM).pdf

PANDOC_COMMON := \
	--from=markdown \
	--standalone \
	--template=template.tex \
	--resource-path=.:$(dir $(PAPER)) \
	--biblatex \
	--include-after-body=$(NOTE_TEX)

.DEFAULT_GOAL := all

.PHONY: all pdf tex markdown prepare assets refresh-note check clean distclean help

all: pdf

pdf: tex
	$(LATEXMK) -xelatex -bibtex -interaction=nonstopmode -halt-on-error \
		-outdir=$(BUILD_DIR) $(OUTPUT_TEX)
	@echo "Built $(OUTPUT_PDF)"

tex: prepare
	$(PANDOC) $(EXPANDED_MD) $(PANDOC_COMMON) --to=latex --output=$(OUTPUT_TEX)
	@echo "Built $(OUTPUT_TEX)"

markdown: prepare
	@echo "Built $(COMPLETE_MD)"

prepare: check assets refresh-note
	@mkdir -p $(BUILD_DIR)
	@$(PYTHON) scripts/expand_manuscript.py $(PAPER) $(VALUES) $(EXPANDED_MD)
	@./scripts/prepare-note.sh $(NOTE_CACHE) $(NOTE_REVISION) $(NOTE_MD)
	@./scripts/assemble-paper.sh $(EXPANDED_MD) $(NOTE_MD) $(COMPLETE_MD)
	@$(PANDOC) $(NOTE_MD) --from=markdown --to=latex --output=$(NOTE_TEX)

assets:
	@mkdir -p .cache/matplotlib
	@MPLCONFIGDIR="$(abspath .cache/matplotlib)" $(PYTHON) scripts/generate_assets.py

refresh-note:
	@if test -f "$(LOCAL_PRACTICE)/ai-native-practice-note.md"; then \
		AI_NATIVE_PRACTICE_SOURCE="$(LOCAL_PRACTICE)" \
			./scripts/update-practice-note.sh $(NOTE_CACHE) $(NOTE_REVISION); \
	else \
		./scripts/update-practice-note.sh $(NOTE_CACHE) $(NOTE_REVISION); \
	fi

check:
	@command -v $(PANDOC) >/dev/null || { echo "Missing dependency: pandoc" >&2; exit 1; }
	@command -v xelatex >/dev/null || { echo "Missing dependency: xelatex" >&2; exit 1; }
	@command -v biber >/dev/null || { echo "Missing dependency: biber" >&2; exit 1; }
	@command -v $(LATEXMK) >/dev/null || { echo "Missing dependency: latexmk" >&2; exit 1; }
	@mkdir -p .cache/matplotlib
	@MPLCONFIGDIR="$(abspath .cache/matplotlib)" $(PYTHON) -c 'import matplotlib, numpy' || { echo "Missing Python plotting dependencies" >&2; exit 1; }
	@test -f $(PAPER) || { echo "Paper not found: $(PAPER)" >&2; exit 1; }

clean:
	@rm -rf $(BUILD_DIR)
	@rm -f $(STEM).4ct $(STEM).4tc $(STEM).aux $(STEM).bcf $(STEM).css \
		$(STEM).html $(STEM).idv $(STEM).lg $(STEM).log $(STEM).run.xml \
		$(STEM).tmp $(STEM).xdv $(STEM).xref

distclean: clean
	@rm -rf .cache generated images/generated

help:
	@echo "make                  Regenerate evidence assets and build the PDF"
	@echo "make assets           Regenerate values, tables, and plots"
	@echo "make tex              Build generated LaTeX"
	@echo "make markdown         Build expanded Markdown with the practice note"
	@echo "make clean            Remove generated document output"
	@echo "make distclean        Also remove generated assets and local caches"
