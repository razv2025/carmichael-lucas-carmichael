/* highend_test.c — exercises do_pair() of enum_k4.c on pairs given on stdin ("p1 p2" per line), in the regime
 * where L2 = (p2^2-1)/2 lies between 2^63 and 2^64 (p1 > 916,000), and prints everything an independent
 * implementation can check:  TRACE p1 p2 m0 Lam  (CRT class),  W p1 p2 m (window survivors),
 * PAIR p1 p2 skip_g skip_inv cand wsurv  (cand = number of class members in (p2^2, 4P^2), single-sweep walk).
 * Compared against pure-Python big-integer arithmetic by highend_test.py.
 * Build: cc -O3 -march=native -DK4_TRACE -o highend_test highend_test.c -lpthread -lm */
#include <stdio.h>
static void k4_trace(unsigned long long p1, unsigned long long p2, unsigned __int128 m0, unsigned __int128 Lam);
#define main enum_main
#include "enum_k4.c"
#undef main
static void k4_trace(unsigned long long p1, unsigned long long p2, u128 m0, u128 Lam){
    char a[64], b[64]; fmt_u128(a, m0); fmt_u128(b, Lam);
    fprintf(solf, "TRACE %llu %llu %s %s\n", p1, p2, a, b);
}
int main(int argc, char **argv){
    KAPPA = 2; FILTER = 1; DUMPW = 1; HAVE_B = 0; solf = stdout;
    OLDWALK = (argc > 1 && !strcmp(argv[1], "--oldwalk"));
    unsigned long long p1, p2;
    while (scanf("%llu %llu", &p1, &p2) == 2) {
        Stats st = {0};
        u64 L1 = (u64)(((u128)p1*p1 - 1) / KAPPA);
        do_pair(p1, L1, p2, &st);
        printf("PAIR %llu %llu %llu %llu %llu %llu\n", p1, p2, (unsigned long long)st.skip_g,
               (unsigned long long)st.skip_inv, (unsigned long long)st.cand, (unsigned long long)st.wsurv);
    }
    return 0;
}
