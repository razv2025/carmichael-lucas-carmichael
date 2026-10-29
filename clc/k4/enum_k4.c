/*
 * enum_k4.c — complete enumeration of Carmichael–Lucas–Carmichael (CLC) numbers
 * with exactly FOUR prime factors up to a bound B.
 *
 * Definition used (kappa = 2 is the CLC problem):
 *   n = p1 p2 p3 p4 (distinct primes, p1<p2<p3<p4), and for every prime p | n
 *        n/p ≡ 1   (mod L_p),   L_p = (p^2 - 1)/kappa          (requires kappa | p^2-1).
 * For kappa = 2 this is exactly "(p-1) | (n-1) and (p+1) | (n+1) for all p | n":
 *   n ≡ 1 (mod p-1), n ≡ -1 (mod p+1)  <=>  n ≡ p (mod lcm(p-1,p+1) = (p^2-1)/2)
 *   <=> (p^2-1)/2 | n - p = p (n/p - 1)  <=>  (p^2-1)/2 | n/p - 1     (gcd(p, p^2-1) = 1).
 * General kappa ("relaxed" problem) exists only so the algorithm can be tested
 * against brute force on an instance that HAS solutions (CLC numbers are not known to exist).
 *
 * Facts used (proved in docs/k4-notes.md; all hold for general kappa with 2 -> kappa):
 *  (F1) [kappa=2 only] every prime factor is ≡ 1 (mod 12).   (--filter)
 *  (F2) Let P = p1 p2, q = p3, r = p4.  The condition at r:  kappa (P q - 1) = d (r^2 - 1), d ≥ 1,
 *       gives q < kappa P,  r < sqrt(kappa P q) < kappa P,  m := q r < kappa^2 P^2.
 *       Hence n = P m < kappa^2 P^3, and n ≤ B forces p1 < B^{1/4}, p2 < (B/p1)^{1/3}, m ≤ B/P.
 *  (F3) Conditions at p1 and p2:  p2 m ≡ 1 (mod L1),  p1 m ≡ 1 (mod L2).
 *       Solvable iff p1 ≡ p2 (mod gcd(L1,L2)); then m lies in ONE class mod Lambda = lcm(L1,L2).
 *  (F4) With e defined by kappa (P r - 1) = e (q^2 - 1) and j = d e:
 *       j m^2 - kappa^2 P^2 m = j (q^2 + r^2 - 1) - kappa^2 P (q + r) + kappa^2,  hence
 *       | j m - kappa^2 P^2 |  ≤  max( 2 j r/q , 2 kappa^2 P/q )  <  max( 2 j sqrt(kappa p1), 2 kappa^2 p1 ).
 *       The set of j satisfying the inequality is an interval containing kappa^2 P^2 / m; so it contains an
       integer iff floor or ceil of kappa^2 P^2 / m satisfies it  (the true j itself need NOT be floor/ceil).
 *  (F5) kappa n = d r^3 - (d - kappa) r,  so r is an integer root of a cubic once d is known.
 *  (F6) [Theorem A, kappa = 2]  Let s be defined by 2(p1 q r - 1) = s (p2^2 - 1) (condition at p2).  Multiplying
 *       2Pq = d r^2 - (d-2),  2Pr = e q^2 - (e-2),  2 p1 q r = s p2^2 - (s-2)  gives  d e s · Π = 8 p1^3 with
 *       Π = (1 - (d-2)/(d r^2))(1 - (e-2)/(e q^2))(1 - (s-2)/(s p2^2)) ∈ [(1-1/p2^2)^3, (1+1/p2^2)^3];
 *       reading the three equations mod p1 shows p1 ∤ d, e, s, so d e s ≠ 8 p1^3.  If Π < 1 this forces
 *       p2^2 ≤ 24 p1^3 + 3; if Π > 1 only the d-factor can exceed 1 (e > d ≥ 1, s > 2 p1), so Π ≤ 1 + 1/r^2 and
 *       r^2 ≤ 8 p1^3 - 1 < 24 p1^3.  The code uses p2^2 ≤ 24 p1^3 + 3 (valid in both cases); the sharp bound is
 *       p2^2 ≤ 24 p1^3 + 1.  Hence for each p1 the whole problem is finite (--p1max mode).
 *
 * Algorithm: for every admissible pair p1 < p2 with p1 p2^3 ≤ B: CRT (F3) -> m0, Lambda;
 * walk m = m0 + t Lambda over (p2^2, min(kappa^2 P^2, B/P)]; window test (F4); survivors:
 * Fermat test 2^(n-1) ≡ 1 (mod n) [kappa=2 only; necessary for Carmichael numbers];
 * then exact reconstruction of r via (F5) over divisors d of j (or trial division when m is small)
 * and a full check of all four conditions and primality. Every SOLUTION line is re-verified in Python.
 *
 * Checkpointing: work is split into blocks of consecutive p1; each finished block appends one JSON
 * line to the log; a rerun with the same log skips finished blocks. Solutions go to a separate file.
 *
 * Build:  cc -O3 -march=native -o enum_k4 enum_k4.c -lpthread -lm
 * Usage:  ./enum_k4 --B 1e30 --kappa 2 --filter --threads 14 --log LOG.jsonl --sol SOL.txt [--bs 128]
 *         ./enum_k4 --B 1e10 --kappa 24 --test --log t.jsonl --sol t.txt     (test mode: no filter, no Fermat)
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <pthread.h>
#include <stdatomic.h>
#include <time.h>
#include <unistd.h>

typedef unsigned __int128 u128;
typedef __int128 i128;
typedef uint64_t u64;
typedef int64_t i64;

/* ---------- parameters ---------- */
static u128 B; static int HAVE_B = 0;
static u64 P1MAX = 0;       /* --p1max X: enumerate ALL n (no bound on n) with smallest prime p1 ≤ X, using Theorem A: p2^2 ≤ 24 p1^3 + 3 */
static u64 KAPPA = 2;
static int FILTER = 0;      /* require p ≡ 1 (mod 12)  (valid theorem for kappa = 2, k = 4) */
static int TESTMODE = 0;    /* no Fermat filter, no residue filter */
static int INTEGERS = 0;
static int HALFTEST = 0;
static u64 SELFTEST = 0;
static int FORCE_CUBIC = 0;
static int DUMPW = 0;
static int OLDWALK = 0;     /* test aid: single-sweep walk over every candidate m (reference for sweep B) */       /* test aid: write every window survivor (p1,p2,m) to the sol file */ /* test aid: force the large-m reconstruction path */    /* --selftest P2MAX: run the self-tests on pairs with p2 ≤ P2MAX and exit */    /* test aid: skip the p1,p2 congruences in full_check (q,r half-problem) */    /* test aid: use all admissible odd integers instead of primes (congruence algebra only) */
static int NTHREADS = 14;
static int BS = 128;
static const char *LOGPATH = NULL, *SOLPATH = NULL;

/* ---------- small utils ---------- */
static double now(void){ struct timespec ts; clock_gettime(CLOCK_MONOTONIC,&ts); return ts.tv_sec+ts.tv_nsec*1e-9; }

static u128 parse_u128(const char *s){
    /* decimal, or mantissa e exponent like 1e30 or 25e28 */
    u128 v = 0; const char *p = s;
    while (*p >= '0' && *p <= '9') { v = v*10 + (u128)(*p - '0'); p++; }
    if (*p == 'e' || *p == 'E') { int ex = atoi(p+1); for (int i=0;i<ex;i++) v *= 10; p = ""; }
    if (*p) { fprintf(stderr, "bad number: %s\n", s); exit(2); }
    return v;
}
static void fmt_u128(char *buf, u128 v){
    char t[64]; int i = 0;
    if (v == 0) { strcpy(buf, "0"); return; }
    while (v) { t[i++] = '0' + (int)(v % 10); v /= 10; }
    int k = 0; while (i) buf[k++] = t[--i]; buf[k] = 0;
}
static u64 gcd64(u64 a, u64 b){
    if (!a) return b; if (!b) return a;
    int sh = __builtin_ctzll(a|b); a >>= __builtin_ctzll(a);
    do { b >>= __builtin_ctzll(b); if (a > b) { u64 t=a; a=b; b=t; } b -= a; } while (b);
    return a << sh;
}
/* inverse of a mod m (a < m). Returns 0 if not invertible (and for m == 1). */
static u64 inv64(u64 a, u64 m){
    i128 t = 0, nt = 1; u64 r = m, nr = a;
    while (nr) { u64 q = r / nr; i128 tmp = t - (i128)q*nt; t = nt; nt = tmp; u64 tr = r - q*nr; r = nr; nr = tr; }
    if (r != 1) return 0;
    if (t < 0) t += m;
    return (u64)t;
}
static u64 mulmod64(u64 a, u64 b, u64 m){ return (u64)(((u128)a*b) % m); }
static u64 powmod64(u64 a, u64 e, u64 m){ u64 r = 1; a %= m; while (e) { if (e&1) r = mulmod64(r,a,m); a = mulmod64(a,a,m); e >>= 1; } return r; }
static int is_prime64(u64 n){
    if (n < 2) return 0;
    static const u64 bases[] = {2,3,5,7,11,13,17,19,23,29,31,37};
    for (int i=0;i<12;i++){ if (n == bases[i]) return 1; if (n % bases[i] == 0) return 0; }
    u64 d = n-1; int s = 0; while (!(d&1)) { d >>= 1; s++; }
    for (int i=0;i<12;i++){
        u64 x = powmod64(bases[i], d, n);
        if (x == 1 || x == n-1) continue;
        int ok = 0;
        for (int k=1;k<s;k++){ x = mulmod64(x,x,n); if (x == n-1) { ok = 1; break; } }
        if (!ok) return 0;
    }
    return 1;   /* deterministic for n < 3.3e24 */
}
static u128 isqrt128(u128 n){ if (n < 2) return n; u128 r = (u128)sqrtl((long double)n); while (r*r > n) r--; while ((r+1)*(r+1) <= n) r++; return r; }
static u128 icbrt128(u128 n){ u128 r = (u128)cbrtl((long double)n); if (r) r--; while ((r+1)*(r+1)*(r+1) <= n) r++; while (r*r*r > n) r--; return r; }
/* 128-bit modular arithmetic (n < 2^127) for the Fermat filter */
static u128 mulmod128(u128 a, u128 b, u128 n){
    u128 r = 0; a %= n; b %= n;
    while (b) { if (b & 1) { r += a; if (r >= n) r -= n; } a <<= 1; if (a >= n) a -= n; b >>= 1; }
    return r;
}
static u128 powmod2_128(u128 e, u128 n){ /* 2^e mod n */
    u128 r = 1 % n; int top = 127; while (top >= 0 && !((e >> top) & 1)) top--;
    for (int i = top; i >= 0; i--) { r = mulmod128(r, r, n); if ((e >> i) & 1) { r <<= 1; if (r >= n) r -= n; } }
    return r;
}

/* ---------- primes ---------- */
static u64 *pr = NULL; static size_t np = 0;   /* admissible primes, increasing */
static size_t n_p1 = 0;                        /* number of them usable as p1 (≤ B^{1/4}) */

static int admissible(u64 p){
    if (p < 5) return 0;
    if (FILTER && p % 12 != 1) return 0;
    u128 t = (u128)p*p - 1;
    return t % KAPPA == 0;
}
static void build_primes(u64 N){
    /* odd-only bit sieve up to N */
    u64 half = N/2 + 1; u64 words = (half + 63)/64;
    u64 *bits = calloc(words, 8); if (!bits) { perror("calloc"); exit(1); }
    u64 lim = (u64)sqrtl((long double)N) + 1;
    for (u64 i = 1; 2*i+1 <= lim; i++) {
        if (bits[i>>6] & (1ULL << (i&63))) continue;
        u64 p = 2*i+1; for (u64 j = (p*p)/2; j < half; j += p) bits[j>>6] |= 1ULL << (j&63);
    }
    size_t cap = 1<<20; pr = malloc(cap*8); np = 0;
    for (u64 i = 1; 2*i+1 <= N; i++) {
        if (!INTEGERS && (bits[i>>6] & (1ULL << (i&63)))) continue;
        u64 p = 2*i+1; if (!admissible(p)) continue;
        if (np == cap) { cap *= 2; pr = realloc(pr, cap*8); if (!pr) { perror("realloc"); exit(1); } }
        pr[np++] = p;
    }
    free(bits);
}
static size_t upper_index(u64 x){ /* number of admissible primes ≤ x */
    size_t lo = 0, hi = np; while (lo < hi) { size_t mid = (lo+hi)/2; if (pr[mid] <= x) lo = mid+1; else hi = mid; } return lo;
}

/* ---------- stats / logging ---------- */
typedef struct { u64 pairs, skip_g, skip_inv, cand, wsurv, fsurv, sol; } Stats;
static pthread_mutex_t logmx = PTHREAD_MUTEX_INITIALIZER;
static FILE *g_log = NULL, *solf = NULL;

static int full_check(u64 p1, u64 p2, u64 q, u64 r, u128 *n_out){
    u64 ps[4] = {p1, p2, q, r};
    if (!(p1 < p2 && p2 < q && q < r)) return 0;
    for (int i=0;i<4;i++) if (!admissible(ps[i])) return 0;
    if (!INTEGERS && (!is_prime64(q) || !is_prime64(r))) return 0;
    u128 n = (u128)p1*p2; n *= q; n *= r;
    for (int i = HALFTEST ? 2 : 0; i<4; i++){
        u128 L = ((u128)ps[i]*ps[i] - 1) / KAPPA;
        u128 m = n / ps[i];
        if ((m - 1) % L) return 0;
    }
    *n_out = n; return 1;
}
static void report_solution(u64 p1, u64 p2, u64 q, u64 r, u128 n, u128 m, u128 jj, Stats *st){
    char nb[64], mb[64], jb[64]; fmt_u128(nb,n); fmt_u128(mb,m); fmt_u128(jb,jj);
    pthread_mutex_lock(&logmx);
    fprintf(solf, "SOLUTION kappa=%llu n=%s p1=%llu p2=%llu q=%llu r=%llu m=%s j=%s\n",
            (unsigned long long)KAPPA, nb, (unsigned long long)p1, (unsigned long long)p2,
            (unsigned long long)q, (unsigned long long)r, mb, jb);
    fflush(solf);
    if (!HALFTEST) fprintf(stderr, "*** SOLUTION n=%s = %llu * %llu * %llu * %llu\n", nb,
            (unsigned long long)p1,(unsigned long long)p2,(unsigned long long)q,(unsigned long long)r);
    pthread_mutex_unlock(&logmx);
    st->sol++;
}

/* exact resolution of a window survivor (p1,p2,m,jj) */
static void handle(u64 p1, u64 p2, u64 P, u128 m, u128 jj, Stats *st){
    if (!TESTMODE && (u128)P > ((u128)1 << 40)) {
        /* n = P m may exceed 128 bits: hand the window survivor to verify_k4.py (Fermat + factoring in Python) */
        char mb[64], jb[64]; fmt_u128(mb,m); fmt_u128(jb,jj);
        pthread_mutex_lock(&logmx);
        fprintf(solf, "WSURV p1=%llu p2=%llu m=%s j=%s\n", (unsigned long long)p1,(unsigned long long)p2, mb, jb);
        fflush(solf);
        pthread_mutex_unlock(&logmx);
        return;
    }
    u128 n = (u128)P * m;
    if (!TESTMODE) {
        if (powmod2_128(n - 1, n) != 1) return;   /* not even a base-2 Fermat pseudoprime */
        st->fsurv++;
        char nb[64], mb[64], jb[64]; fmt_u128(nb,n); fmt_u128(mb,m); fmt_u128(jb,jj);
        pthread_mutex_lock(&logmx);
        fprintf(solf, "FSURV p1=%llu p2=%llu m=%s j=%s n=%s\n", (unsigned long long)p1,(unsigned long long)p2, mb, jb, nb);
        fflush(solf);
        pthread_mutex_unlock(&logmx);
    }
    u128 nn;
    if (!FORCE_CUBIC && m < ((u128)1 << 54)) {
        /* small m: trial-divide m for every split m = q r with p2 < q < r */
        u64 mm = (u64)m; u64 lim = (u64)isqrt128(m);
        for (u64 q = p2 + 1; q <= lim; q++) {
            if (mm % q) continue; u64 r = mm / q; if (r <= q) break;
            if (full_check(p1, p2, q, r, &nn)) report_solution(p1,p2,q,r,nn,m,jj,st);
        }
        return;
    }
    /* large m: r is a root of d x^3 - (d - kappa) x - kappa n  (F5) for the integer d = kappa(Pq-1)/(r^2-1),
       and d < kappa P q/(r^2-1) < kappa P/q < kappa p1.  (Independent of jj: the true j = de can be any
       integer in the window interval, not only floor/ceil of T/m — see the self-test history in README.) */
    u128 kn = (u128)KAPPA * n;
    for (u128 d = 1; d <= (u128)KAPPA * p1; d++) {
        u128 x = icbrt128(kn / d);
        for (int dx = -1; dx <= 1; dx++) {
            u128 r = x + dx; if (r < 3) continue;
            i128 val = (i128)(d*r*r*r) - (i128)(d*r) + (i128)((u128)KAPPA*r);
            if (val != (i128)kn) continue;
            if (m % r) continue; u128 q = m / r;
            if (q <= p2 || q >= r || (r >> 64)) continue;
            if (full_check(p1, p2, (u64)q, (u64)r, &nn)) report_solution(p1,p2,(u64)q,(u64)r,nn,m,jj,st);
        }
    }
}

static inline int window_ok(u128 T, u128 m, u128 jj, u64 S, u128 bound2){
    u128 jm = jj * m; u128 lhs = jm >= T ? jm - T : T - jm;
    u128 rhs = (u128)2 * jj * S; if (rhs < bound2) rhs = bound2;
    return lhs <= rhs;
}
static int selftest(u64 p2max_t);

static void do_pair(u64 p1, u64 L1, u64 p2, Stats *st){
    st->pairs++;
    u128 p2sq = (u128)p2*p2;
    u128 L2w = (p2sq - 1) / KAPPA;
    if (L2w >> 64) { fprintf(stderr, "L2 does not fit in 64 bits (p2=%llu); lower B\n", (unsigned long long)p2); exit(3); }
    u64 L2 = (u64)L2w;
    u64 g = gcd64(L1, L2);
    if ((p2 - p1) % g) { st->skip_g++; return; }            /* (F3) consistency */
    u64 a1 = 0, a2 = 0;
    if (L1 > 1) { a1 = inv64(p2 % L1, L1); if (!a1) { st->skip_inv++; return; } }
    if (L2 > 1) { a2 = inv64(p1 % L2, L2); if (!a2) { st->skip_inv++; return; } }
    u64 L2g = L2 / g, L1g = L1 / g;
    u64 k0 = 0;
    if (L2g > 1) {
        i128 diff = (i128)a2 - (i128)a1; diff %= (i128)L2; if (diff < 0) diff += L2;
        u64 dg = (u64)(diff / g);                            /* g | diff guaranteed by consistency */
        u64 iv = inv64(L1g % L2g, L2g);                      /* gcd(L1g, L2g) = 1 */
        k0 = mulmod64(dg % L2g, iv, L2g);
    }
    u128 Lam = (u128)L1 * L2g;
    u128 m0 = (u128)a1 + (u128)L1 * k0;                      /* 0 ≤ m0 < Lam */
    u64 P = p1 * p2;
    u128 T = (u128)KAPPA * KAPPA * P; T *= P;                /* kappa^2 P^2 */
    u128 mmax = T - 1; if (HAVE_B) { u128 bp = B / P; if (bp < mmax) mmax = bp; }
    u128 mmin = p2sq + 1;
    if (mmax < mmin) return;
    u128 m = m0;
    if (m < mmin) { u128 t = (mmin - m0 + Lam - 1) / Lam; m = m0 + t*Lam; }
    u64 S = (u64)isqrt128((u128)KAPPA * p1); if ((u128)S*S < (u128)KAPPA*p1) S++;   /* ceil sqrt(kappa p1) */
    u128 bound2 = (u128)2 * KAPPA * KAPPA * p1;
    /* Candidates m ≡ m0 (mod Lam) in [m, mmax].  A candidate passes iff some integer j has |j m - T| ≤ R_j,
       R_j = max(2 j S, bound2).  Two sweeps:
         A: m ≤ Mstar — walk m, test j = floor(T/m) and j+1 (sufficient: the admissible j form an interval containing T/m);
         B: m > Mstar — walk j, intersect the exact m-window [ceil((T-R_j)/j), floor((T+R_j)/j)] with the progression.
       Mstar ≈ sqrt(T Lam) balances the two; total work ≈ 2 sqrt(T/Lam) per pair instead of T/Lam. */
    u128 Mstar = (u128)(sqrt((double)T) * sqrt((double)Lam));
    if (Mstar > mmax || OLDWALK) Mstar = mmax;
    if (Mstar < m) Mstar = m - 1 < m ? m - 1 : 0;     /* then sweep A is empty */
    double Tf = (double)T;
    for (; m <= Mstar; m += Lam) {
        st->cand++;
        u128 j = (u128)(Tf / (double)m);
        while (j > 0 && j*m > T) j--;
        while ((j+1)*m <= T) j++;
        if (j == 0) j = 1;
        for (int c = 0; c < 2; c++) {
            u128 jj = j + c;
            if (window_ok(T, m, jj, S, bound2)) { st->wsurv++;
                if (DUMPW) { char mb[64]; fmt_u128(mb,m); pthread_mutex_lock(&logmx); fprintf(solf,"W %llu %llu %s\n",(unsigned long long)p1,(unsigned long long)p2,mb); pthread_mutex_unlock(&logmx); }
                handle(p1, p2, P, m, jj, st); break; }
        }
    }
    if (m > mmax) return;
    /* sweep B over j; m ranges over (Mstar, mmax] ∩ [m, ...) */
    u128 mlo_B = m;                                           /* first progression element > Mstar */
    u128 twoS = (u128)2*S;
    u128 jlo = 1; if (T > bound2) { jlo = (T - bound2) / (mmax + twoS); if (jlo > 1) jlo -= 1; else jlo = 1; }
    if (Mstar <= twoS) { fprintf(stderr, "Mstar too small\n"); exit(5); }
    u128 jhi = (T + bound2) / (Mstar - twoS) + 1;
    for (u128 j = jlo; j <= jhi; j++) {
        st->cand++;
        u128 Rj = (u128)2*j*S; if (Rj < bound2) Rj = bound2;
        u128 lo = T > Rj ? (T - Rj + j - 1) / j : 0;
        u128 hi = (T + Rj) / j;
        if (lo < mlo_B) lo = mlo_B;
        if (hi > mmax) hi = mmax;
        if (lo > hi) continue;
        /* first progression element ≥ lo:  m0 + t Lam ≥ lo */
        u128 mm = lo <= m0 ? m0 : m0 + ((lo - m0 + Lam - 1) / Lam) * Lam;
        for (; mm <= hi; mm += Lam) {
            if (!window_ok(T, mm, j, S, bound2)) continue;     /* exact test (defensive; the window is exact) */
            /* the admissible j for a fixed m form an interval: report m only under the smallest one */
            if (j > 1 && window_ok(T, mm, j - 1, S, bound2)) continue;
            st->wsurv++;
            if (DUMPW) { char mb[64]; fmt_u128(mb,mm); pthread_mutex_lock(&logmx); fprintf(solf,"W %llu %llu %s\n",(unsigned long long)p1,(unsigned long long)p2,mb); pthread_mutex_unlock(&logmx); }
            handle(p1, p2, P, mm, j, st);
        }
    }
}

/* ---------- self-tests (see test.sh) ---------- */
/* T1: brute-force the (q,r) half-problem for small admissible pairs and check (F2),(F4),(F5) + reconstruction.
   T2: brute-force the CRT class of (F3) for small pairs and compare with m0, Lambda. */
static int selftest(u64 p2max_t){
    HALFTEST = 1;
    u64 half = 0, viol = 0, crt_pairs = 0, crt_viol = 0, far = 0;
    size_t ihi = upper_index(p2max_t);
    for (size_t i = 0; i < ihi; i++) for (size_t k = i+1; k < ihi; k++) {
        u64 p1 = pr[i], p2 = pr[k]; u64 P = p1*p2;
        u64 L1 = (u64)(((u128)p1*p1-1)/KAPPA), L2 = (u64)(((u128)p2*p2-1)/KAPPA);
        u128 T = (u128)KAPPA*KAPPA*P; T *= P;
        u64 S = (u64)isqrt128((u128)KAPPA*p1); if ((u128)S*S < (u128)KAPPA*p1) S++;
        u128 bound2 = (u128)2*KAPPA*KAPPA*p1;
        /* --- T1 --- */
        for (u64 q = p2+1; q < KAPPA*P; q++) {
            if (!admissible(q)) continue;
            u128 Nq = (u128)KAPPA*((u128)P*q - 1);
            u128 dmax = Nq / ((u128)q*q - 1);                 /* r > q  <=>  d < Nq/(q^2-1) */
            for (u128 d = 1; d <= dmax; d++) {
                if (Nq % d) continue;
                u128 r2 = 1 + Nq/d; u128 r = isqrt128(r2); if (r*r != r2 || r <= q) continue;
                if (!admissible((u64)r)) continue;
                if (!INTEGERS && (!is_prime64(q) || !is_prime64((u64)r))) continue;
                u128 Lq = ((u128)q*q-1)/KAPPA;
                if (((u128)P*r - 1) % Lq) continue;           /* condition at q */
                /* half-solution (P,q,r): check the invariants the enumerator relies on */
                half++;
                u128 m = (u128)q*r; u128 e = (u128)KAPPA*((u128)P*r-1)/((u128)q*q-1); u128 jj = d*e;
                u128 jf = T/m; int ok = 1;
                if (!(q < (u128)KAPPA*P) || !(m < T)) ok = 0;                         /* (F2) */
                if (!window_ok(T, m, jj, S, bound2)) ok = 0;                            /* (F4) inequality for the true j */
                if (!window_ok(T, m, jf, S, bound2) && !window_ok(T, m, jf+1, S, bound2)) ok = 0;  /* the production filter passes */
                if (jj != jf && jj != jf+1) far++;                                      /* informative: true j not floor/ceil */
                { u128 kn = (u128)KAPPA*P*m; i128 val = (i128)(d*r*r*r) - (i128)(d*r) + (i128)((u128)KAPPA*r); if (val != (i128)kn) ok = 0; } /* (F5) */
                /* reconstruction through the production path */
                Stats st = {0}; long pos = ftell(solf);
                FORCE_CUBIC = 0; handle(p1, p2, P, m, jj, &st); if (st.sol != 1) ok = 0;
                FORCE_CUBIC = 1; handle(p1, p2, P, m, jj, &st); if (st.sol != 2) ok = 0; FORCE_CUBIC = 0;
                fseek(solf, pos, SEEK_SET); ftruncate(fileno(solf), pos);              /* discard test solution lines */
                if (!ok) { viol++; char mb[64]; fmt_u128(mb,m); fprintf(stderr, "T1 VIOLATION p1=%llu p2=%llu q=%llu r=%llu m=%s d=%llu e=%llu sol=%llu\n",
                    (unsigned long long)p1,(unsigned long long)p2,(unsigned long long)q,(unsigned long long)r, mb,(unsigned long long)d,(unsigned long long)e,(unsigned long long)st.sol); }
            }
        }
        /* --- T2 --- */
        u64 g = gcd64(L1, L2);
        u128 mmax = T - 1; if (mmax > 20000000) mmax = 20000000;
        u64 nb = 0; u128 first = 0, second = 0;
        for (u128 m = (u128)p2*p2+1; m <= mmax; m++) {
            if (L1 > 1 && ((u128)p2*m) % L1 != 1) continue;
            if (L2 > 1 && ((u128)p1*m) % L2 != 1) continue;
            if (nb == 0) first = m; else if (nb == 1) second = m; nb++;
        }
        int consistent = ((p2-p1) % g == 0) && (L1 <= 1 || inv64(p2%L1,L1)) && (L2 <= 1 || inv64(p1%L2,L2));
        crt_pairs++;
        if (!consistent) { if (nb) { crt_viol++; fprintf(stderr, "T2 VIOLATION: pair (%llu,%llu) declared inconsistent but has %llu solutions\n",(unsigned long long)p1,(unsigned long long)p2,(unsigned long long)nb); } continue; }
        u64 a1 = L1>1 ? inv64(p2%L1,L1) : 0, a2 = L2>1 ? inv64(p1%L2,L2) : 0;
        u64 L2g = L2/g, L1g = L1/g, k0 = 0;
        if (L2g > 1) { i128 diff = (i128)a2-(i128)a1; diff %= (i128)L2; if (diff<0) diff += L2; u64 dg=(u64)(diff/g); k0 = mulmod64(dg%L2g, inv64(L1g%L2g,L2g), L2g); }
        u128 Lam = (u128)L1*L2g, m0 = (u128)a1 + (u128)L1*k0;
        u128 mmin = (u128)p2*p2+1, mm = m0; if (mm < mmin) { u128 t=(mmin-m0+Lam-1)/Lam; mm = m0+t*Lam; }
        u64 nb2 = 0; for (u128 m = mm; m <= mmax; m += Lam) nb2++;
        if (nb != nb2 || (nb && first != mm) || (nb > 1 && second != mm+Lam)) { crt_viol++; fprintf(stderr, "T2 VIOLATION pair (%llu,%llu): brute %llu (first %llu) vs formula %llu (first %llu, Lam %llu)\n",
            (unsigned long long)p1,(unsigned long long)p2,(unsigned long long)nb,(unsigned long long)first,(unsigned long long)nb2,(unsigned long long)mm,(unsigned long long)Lam); }
    }
    printf("SELFTEST kappa=%llu integers=%d pairs(p2<=%llu): T1 half-solutions=%llu (true j not floor/ceil in %llu) violations=%llu | T2 pairs=%llu violations=%llu\n",
           (unsigned long long)KAPPA, INTEGERS, (unsigned long long)p2max_t, (unsigned long long)half,(unsigned long long)far,(unsigned long long)viol,(unsigned long long)crt_pairs,(unsigned long long)crt_viol);
    HALFTEST = 0;
    return (viol || crt_viol) ? 1 : 0;
}

/* ---------- blocks / threads ---------- */
static atomic_int next_blk; static int nblk; static unsigned char *done;
static double t_start;

static void *worker(void *arg){
    (void)arg;
    for (;;) {
        int b = atomic_fetch_add(&next_blk, 1); if (b >= nblk) break;
        if (done[b]) continue;
        Stats st = {0}; double t0 = now();
        size_t lo = (size_t)b * BS, hi = lo + BS; if (hi > n_p1) hi = n_p1;
        for (size_t i = lo; i < hi; i++) {
            u64 p1 = pr[i];
            u64 L1 = (u64)(((u128)p1*p1 - 1) / KAPPA);
            u64 p2max = UINT64_MAX;
            if (HAVE_B) { u128 c = icbrt128(B / p1); if (c < (u128)p2max) p2max = (u64)c; }
            if (KAPPA == 2 && FILTER) { u128 t = isqrt128((u128)24*p1*p1*p1 + 3); if (t < (u128)p2max) p2max = (u64)t; }   /* Theorem A */
            size_t ihi = upper_index(p2max);
            for (size_t k = i + 1; k < ihi; k++) do_pair(p1, L1, pr[k], &st);
        }
        pthread_mutex_lock(&logmx);
        fprintf(g_log, "{\"blk\":%d,\"p1lo\":%llu,\"p1hi\":%llu,\"pairs\":%llu,\"skip_g\":%llu,\"skip_inv\":%llu,\"cand\":%llu,\"wsurv\":%llu,\"fsurv\":%llu,\"sol\":%llu,\"sec\":%.2f,\"t\":%.0f}\n",
                b, (unsigned long long)pr[lo], (unsigned long long)pr[hi-1],
                (unsigned long long)st.pairs,(unsigned long long)st.skip_g,(unsigned long long)st.skip_inv,
                (unsigned long long)st.cand,(unsigned long long)st.wsurv,(unsigned long long)st.fsurv,(unsigned long long)st.sol,
                now()-t0, now()-t_start);
        fflush(g_log);
        pthread_mutex_unlock(&logmx);
    }
    return NULL;
}

int main(int argc, char **argv){
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--B") && i+1 < argc) { B = parse_u128(argv[++i]); HAVE_B = 1; }
        else if (!strcmp(argv[i], "--p1max") && i+1 < argc) P1MAX = strtoull(argv[++i], 0, 10);
        else if (!strcmp(argv[i], "--kappa") && i+1 < argc) KAPPA = strtoull(argv[++i], 0, 10);
        else if (!strcmp(argv[i], "--threads") && i+1 < argc) NTHREADS = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--bs") && i+1 < argc) BS = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--log") && i+1 < argc) LOGPATH = argv[++i];
        else if (!strcmp(argv[i], "--sol") && i+1 < argc) SOLPATH = argv[++i];
        else if (!strcmp(argv[i], "--filter")) FILTER = 1;
        else if (!strcmp(argv[i], "--dumpw")) DUMPW = 1;
        else if (!strcmp(argv[i], "--oldwalk")) OLDWALK = 1;
        else if (!strcmp(argv[i], "--fermat-check")) {   /* test aid: read decimal n (< 2^126) per line, print 2^(n-1) mod n */
            char line[256];
            while (fgets(line, sizeof line, stdin)) { size_t L = strlen(line); while (L && (line[L-1]=='\n'||line[L-1]=='\r')) line[--L]=0; if (!L) continue;
                u128 n = parse_u128(line); char a[64], b[64]; fmt_u128(a, n); fmt_u128(b, powmod2_128(n - 1, n)); printf("%s %s\n", a, b); }
            return 0; }
        else if (!strcmp(argv[i], "--test")) { TESTMODE = 1; FILTER = 0; }
        else if (!strcmp(argv[i], "--integers")) { INTEGERS = 1; TESTMODE = 1; FILTER = 0; }
        else if (!strcmp(argv[i], "--selftest") && i+1 < argc) { SELFTEST = strtoull(argv[++i], 0, 10); TESTMODE = 1; FILTER = 0; }
        else { fprintf(stderr, "unknown arg %s\n", argv[i]); return 2; }
    }
    if ((!HAVE_B && !P1MAX) || !LOGPATH || !SOLPATH) { fprintf(stderr, "need --B and/or --p1max, --log, --sol\n"); return 2; }
    if (P1MAX && !(KAPPA == 2 && FILTER)) { fprintf(stderr, "--p1max needs kappa=2 --filter (Theorem A)\n"); return 2; }
    if (!HAVE_B) { B = 0; B = ~B; B >>= 2; }   /* no bound on n */
    if (FILTER && KAPPA != 2) { fprintf(stderr, "--filter is a theorem only for kappa=2\n"); return 2; }
    if (B >> 126) { fprintf(stderr, "B too large\n"); return 2; }
    char bb[64]; if (HAVE_B) fmt_u128(bb, B); else strcpy(bb, "none");

    /* smallest admissible prime -> p2 range */
    u64 p1min = 5; while (!admissible(p1min)) p1min++;   /* 5,7,11,13 are all prime; loop stops at a prime for sane kappa */
    if (!INTEGERS) { u64 t = p1min; int isp = 1; for (u64 d = 2; d*d <= t; d++) if (t % d == 0) { isp = 0; break; } if (!isp) { fprintf(stderr,"bug p1min\n"); return 2; } }
    u128 p1max = isqrt128(isqrt128(B));
    if (P1MAX && (u128)P1MAX < p1max) p1max = P1MAX;
    u128 p2max = HAVE_B ? icbrt128(B / p1min) : 0;
    if (KAPPA == 2 && FILTER) { u128 t = isqrt128((u128)24*p1max*p1max*p1max + 3); if (!HAVE_B || t < p2max) p2max = t; }
    if (p2max >> 40) { fprintf(stderr, "p2 range too large for in-memory sieve\n"); return 2; }
    fprintf(stderr, "B=%s kappa=%llu filter=%d test=%d  p1min=%llu p1max=%llu p2max=%llu threads=%d bs=%d\n",
            bb, (unsigned long long)KAPPA, FILTER, TESTMODE, (unsigned long long)p1min,
            (unsigned long long)p1max, (unsigned long long)p2max, NTHREADS, BS);
    double t0 = now();
    build_primes((u64)p2max);
    n_p1 = upper_index((u64)p1max);
    nblk = (int)((n_p1 + BS - 1) / BS);
    fprintf(stderr, "sieve: %zu admissible primes ≤ p2max, %zu usable as p1, %d blocks (%.1fs)\n", np, n_p1, nblk, now()-t0);

    /* resume */
    done = calloc(nblk ? nblk : 1, 1);
    int ndone = 0;
    { FILE *f = fopen(LOGPATH, "r"); if (f) { char line[1024]; while (fgets(line, sizeof line, f)) { int b; if (sscanf(line, "{\"blk\":%d,", &b) == 1 && b >= 0 && b < nblk && !done[b]) { done[b] = 1; ndone++; } } fclose(f); } }
    if (ndone) fprintf(stderr, "resume: %d/%d blocks already done\n", ndone, nblk);
    g_log = fopen(LOGPATH, "a"); solf = fopen(SOLPATH, "a+");
    if (!g_log || !solf) { perror("open log/sol"); return 1; }
    if (SELFTEST) return selftest(SELFTEST);
    if (!ndone) { fprintf(g_log, "{\"header\":1,\"B\":\"%s\",\"p1max\":%llu,\"kappa\":%llu,\"filter\":%d,\"test\":%d,\"bs\":%d,\"nblk\":%d,\"n_p1\":%zu,\"np\":%zu}\n",
                          bb, (unsigned long long)P1MAX, (unsigned long long)KAPPA, FILTER, TESTMODE, BS, nblk, n_p1, np); fflush(g_log); }

    t_start = now(); atomic_store(&next_blk, 0);
    pthread_t th[256]; if (NTHREADS > 256) NTHREADS = 256;
    for (int i = 0; i < NTHREADS; i++) pthread_create(&th[i], NULL, worker, NULL);
    for (int i = 0; i < NTHREADS; i++) pthread_join(th[i], NULL);
    fclose(g_log); fclose(solf);

    /* aggregate from the log */
    Stats tot = {0}; int cnt = 0; unsigned char *seen = calloc(nblk ? nblk : 1, 1);
    FILE *f = fopen(LOGPATH, "r"); char line[1024];
    while (fgets(line, sizeof line, f)) {
        int b; unsigned long long v[9];
        if (sscanf(line, "{\"blk\":%d,\"p1lo\":%llu,\"p1hi\":%llu,\"pairs\":%llu,\"skip_g\":%llu,\"skip_inv\":%llu,\"cand\":%llu,\"wsurv\":%llu,\"fsurv\":%llu,\"sol\":%llu",
                   &b, &v[0], &v[1], &v[2], &v[3], &v[4], &v[5], &v[6], &v[7], &v[8]) == 10) {
            if (b < 0 || b >= nblk || seen[b]) continue; seen[b] = 1; cnt++;
            tot.pairs += v[2]; tot.skip_g += v[3]; tot.skip_inv += v[4]; tot.cand += v[5]; tot.wsurv += v[6]; tot.fsurv += v[7]; tot.sol += v[8];
        }
    }
    fclose(f);
    printf("%s blocks=%d/%d pairs=%llu skip_gcd=%llu skip_inv=%llu cand=%llu window_survivors=%llu fermat_survivors=%llu solutions=%llu wall=%.1fs\n",
           cnt == nblk ? "COMPLETE" : "PARTIAL", cnt, nblk,
           (unsigned long long)tot.pairs,(unsigned long long)tot.skip_g,(unsigned long long)tot.skip_inv,(unsigned long long)tot.cand,
           (unsigned long long)tot.wsurv,(unsigned long long)tot.fsurv,(unsigned long long)tot.sol, now()-t0);
    return cnt == nblk ? 0 : 4;
}
