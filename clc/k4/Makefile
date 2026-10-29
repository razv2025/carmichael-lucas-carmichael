CC ?= cc
CFLAGS ?= -O3 -march=native -Wall
all: enum_k4 brute_k4
enum_k4: enum_k4.c
	$(CC) $(CFLAGS) -o $@ $< -lpthread -lm
brute_k4: brute_k4.c
	$(CC) $(CFLAGS) -o $@ $< -lm
# Self-tests: (1) half-problem + CRT brute force in four relaxed variants, (2) end-to-end on the relaxed
# kappa=24 problem (must find exactly 13685, matching brute force), (3) the real problem to 1e24 (must be empty).
test: all
	@rm -f _t_*.jsonl _t_*.txt
	./enum_k4 --B 1e14 --kappa 24  --integers --selftest 90  --log _t_a.jsonl --sol _t_a.txt | tail -1
	./enum_k4 --B 1e14 --kappa 120 --integers --selftest 200 --log _t_b.jsonl --sol _t_b.txt | tail -1
	./enum_k4 --B 1e14 --kappa 24  --selftest 400 --log _t_c.jsonl --sol _t_c.txt | tail -1
	./enum_k4 --B 1e14 --kappa 2   --integers --selftest 130 --log _t_d.jsonl --sol _t_d.txt | tail -1
	./enum_k4 --B 1e11 --kappa 24 --test --threads 4 --log _t_e.jsonl --sol _t_e.txt 2>/dev/null | tail -1
	./brute_k4 24 1e11 2>/dev/null | awk '{print $$1}' | sort > _t_brute.txt
	grep '^SOLUTION' _t_e.txt | sed 's/.* n=\([0-9]*\) .*/\1/' | sort > _t_enum.txt
	cmp _t_brute.txt _t_enum.txt && echo "END-TO-END: enumerator == brute force on kappa=24 to 1e11 ($$(wc -l < _t_enum.txt) solution(s))"
	./enum_k4 --B 1e24 --kappa 2 --filter --threads 8 --log _t_f.jsonl --sol _t_f.txt 2>/dev/null | tail -1
	python3 verify_k4.py _t_f.txt | tail -1
	@rm -f _t_*.jsonl _t_*.txt
clean:
	rm -f enum_k4 brute_k4 _t_*
.PHONY: all test clean
