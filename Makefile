# Stolen directly from the latexrun README
.PHONY: FORCE
paper.pdf: FORCE
	@latexrun thesis.tex

.PHONY: check
check:
	@checkwriting chapters/*.tex

.PHONY: clean
clean:
	@latexrun --clean-all

# Run "make" whenever a LaTeX source file changes
# http://stackoverflow.com/questions/25689589
.PHONY: watch
watch:
	@fswatch -0 **.tex | xargs -0 -n1 -I"{}" make
