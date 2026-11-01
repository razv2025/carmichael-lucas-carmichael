#!/bin/sh
# Regenerate the archived outputs of the polynomial-family searches cited in the paper's appendix (single-core each).
cd "$(dirname "$0")/../.."
{ echo "# $(date)  python3 -m agrawal.family --mode pm1 --m 5 --amax 20000";  nice -n 10 python3 -m agrawal.family --mode pm1 --m 5  --amax 20000; } > agrawal/results/pm1_m5_a20000.txt 2>&1
{ echo "# $(date)  --mode pm1 --m 7 --amax 5000";  nice -n 10 python3 -m agrawal.family --mode pm1 --m 7  --amax 5000;  } > agrawal/results/pm1_m7_a5000.txt 2>&1
{ echo "# $(date)  --mode pm1 --m 9 --amax 3000";  nice -n 10 python3 -m agrawal.family --mode pm1 --m 9  --amax 3000;  } > agrawal/results/pm1_m9_a3000.txt 2>&1
{ echo "# $(date)  --mode pm1 --m 11 --amax 1500"; nice -n 10 python3 -m agrawal.family --mode pm1 --m 11 --amax 1500; } > agrawal/results/pm1_m11_a1500.txt 2>&1
{ echo "# $(date)  --mode m4 --amax 500";          nice -n 10 python3 -m agrawal.family --mode m4 --amax 500;           } > agrawal/results/m4_a500.txt 2>&1
{ echo "# $(date)  --mode gen --m 5 --amax 150";   nice -n 10 python3 -m agrawal.family --mode gen --m 5 --amax 150;    } > agrawal/results/m5_a150.txt 2>&1
echo "# finished $(date)" >> agrawal/results/m5_a150.txt
