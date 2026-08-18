/* Slab meet-in-the-middle search for (7,3,4):
 *     a^7 + b^7 + c^7  =  d^7 + e^7 + f^7 + g^7,   1 <= all <= H.
 *
 * Value space [0, 3*H^7] is cut into slabs with ~equal left-side counts.
 * Per slab: generate all 3-term sums (a>=b>=c) in the slab, bucket-sort by
 * the low 64 bits of the true value; then scan all 4-term sums (d>=e>=f>=g)
 * in the slab, filtering through a 2^33-bit bitmap, then binary search.
 * Matches are CANDIDATES (low-64 collisions possible) — exact verification
 * happens in Python (lps/verify.py). Progress JSONL gives provable coverage:
 * every slab logs its z-interval and tuple counts; slabs partition the space.
 *
 * Build: clang -O3 -march=native -pthread -o engine734 engine734.c
 * Run:   ./engine734 H NSLABS progress.jsonl candidates.txt [start_slab]
 */
#include <inttypes.h>
#include <math.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef __uint128_t u128;
typedef uint64_t u64;
typedef uint32_t u32;
typedef uint16_t u16;

static u128 *pow7;   /* pow7[i] = i^7 */
static u64 *pow7lo;  /* low 64 bits  */
static int H;

typedef struct { u64 lo, hi; u16 a, b, c, pad; } Entry;

/* ---------------------------------------------------------------- helpers */

#ifndef POWER
#define POWER 7
#endif

static u128 ipow7(u64 x) {
    u128 v = 1;
    for (int i = 0; i < POWER; i++) v *= x;
    return v;
}

static void u128_hex(u128 v, char *out) {
    sprintf(out, "%016" PRIx64 "%016" PRIx64, (u64)(v >> 64), (u64)v);
}

/* largest i in [1,hi] with pow7[i] <= v, or 0 */
static int p7_floor(u128 v, int hi) {
    int lo = 1, res = 0;
    if (pow7[1] > v) return 0;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (pow7[mid] <= v) { res = mid; lo = mid + 1; } else hi = mid - 1;
    }
    return res;
}

/* ------------------------------------------------------------- left build */

#define NBUCKET 256
typedef struct {
    Entry *buf; size_t len, cap;
} Vec;

static void vec_push(Vec *v, Entry e) {
    if (v->len == v->cap) {
        v->cap = v->cap ? v->cap * 2 : 1 << 16;
        v->buf = realloc(v->buf, v->cap * sizeof(Entry));
        if (!v->buf) { fprintf(stderr, "OOM\n"); exit(1); }
    }
    v->buf[v->len++] = e;
}

static int entry_cmp(const void *x, const void *y) {
    const Entry *ex = (const Entry *)x, *ey = (const Entry *)y;
    if (ex->lo != ey->lo) return ex->lo < ey->lo ? -1 : 1;
    if (ex->hi != ey->hi) return ex->hi < ey->hi ? -1 : 1;
    return 0;
}

typedef struct {
    Vec bucket[NBUCKET];
    pthread_mutex_t lock[NBUCKET];
} LeftBuild;

typedef struct {
    LeftBuild *lb;
    u128 z1, z2;
    _Atomic int *next_a;
} LeftJob;

static void *left_worker(void *arg) {
    LeftJob *J = (LeftJob *)arg;
    Vec local[NBUCKET];
    memset(local, 0, sizeof(local));
    for (;;) {
        int a = atomic_fetch_add(J->next_a, 1);
        if (a > H) break;
        u128 s1 = pow7[a];
        if (s1 >= J->z2) continue;               /* a^7 alone too big */
        if (s1 + 2 * pow7[a] < J->z1) continue;  /* even b=c=a too small */
        for (int b = 1; b <= a; b++) {
            u128 s2 = s1 + pow7[b];
            if (s2 + 1 >= J->z2 && s2 + pow7[1] >= J->z2) break;
            if (s2 + pow7[b] < J->z1) continue;  /* even c=b too small */
            /* c in [c_lo, c_hi] with s2 + c^7 in [z1, z2), c <= b */
            int c_hi = p7_floor(J->z2 - 1 - s2, b);
            if (c_hi == 0) continue;
            int c_lo = 1;
            if (s2 + pow7[1] < J->z1) {
                /* smallest c with pow7[c] >= z1 - s2 */
                u128 need = J->z1 - s2;
                int lo = 1, hi = b; c_lo = b + 1;
                while (lo <= hi) {
                    int mid = (lo + hi) / 2;
                    if (pow7[mid] >= need) { c_lo = mid; hi = mid - 1; }
                    else lo = mid + 1;
                }
            }
            for (int c = c_lo; c <= c_hi; c++) {
                u128 t = s2 + pow7[c];
                Entry e = { (u64)t, (u64)(t >> 64), (u16)a, (u16)b, (u16)c,
                            0 };
                vec_push(&local[e.lo >> 56], e);
            }
        }
    }
    for (int i = 0; i < NBUCKET; i++) {
        if (local[i].len) {
            pthread_mutex_lock(&J->lb->lock[i]);
            Vec *g = &J->lb->bucket[i];
            while (g->len + local[i].len > g->cap) {
                g->cap = g->cap ? g->cap * 2 : 1 << 16;
                g->buf = realloc(g->buf, g->cap * sizeof(Entry));
            }
            memcpy(g->buf + g->len, local[i].buf,
                   local[i].len * sizeof(Entry));
            g->len += local[i].len;
            pthread_mutex_unlock(&J->lb->lock[i]);
        }
        free(local[i].buf);
    }
    return NULL;
}

typedef struct { LeftBuild *lb; _Atomic int *next_b; } SortJob;

static void *sort_worker(void *arg) {
    SortJob *J = (SortJob *)arg;
    for (;;) {
        int i = atomic_fetch_add(J->next_b, 1);
        if (i >= NBUCKET) break;
        qsort(J->lb->bucket[i].buf, J->lb->bucket[i].len, sizeof(Entry),
              entry_cmp);
    }
    return NULL;
}

/* ------------------------------------------------------------ right scan */

#define BITMAP_BITS 33
static u64 *bitmap; /* 2^33 bits = 1 GiB */

static inline int bitmap_test(u64 key) {
    u64 idx = key & ((1ULL << BITMAP_BITS) - 1);
    return (bitmap[idx >> 6] >> (idx & 63)) & 1;
}
static inline void bitmap_set(u64 key) {
    u64 idx = key & ((1ULL << BITMAP_BITS) - 1);
    bitmap[idx >> 6] |= 1ULL << (idx & 63);
}

typedef struct {
    LeftBuild *lb;
    u128 z1, z2;
    _Atomic int *next_d;
    _Atomic long long *right_count;
    _Atomic long long *cand_count;
    FILE *cand_file;
    pthread_mutex_t *cand_lock;
} ScanJob;

static void report_match(ScanJob *J, const Entry *e, int d, int dd, int f,
                         int g) {
    pthread_mutex_lock(J->cand_lock);
    fprintf(J->cand_file, "%d %d %d %d %d %d %d\n", e->a, e->b, e->c, d, dd,
            f, g);
    fflush(J->cand_file);
    pthread_mutex_unlock(J->cand_lock);
    atomic_fetch_add(J->cand_count, 1);
}

static void *scan_worker(void *arg) {
    ScanJob *J = (ScanJob *)arg;
    long long rc = 0;
    for (;;) {
        int d = atomic_fetch_add(J->next_d, 1);
        if (d > H) break;
        u128 s1 = pow7[d];
        if (s1 >= J->z2) continue;
        if (s1 + 3 * pow7[d] < J->z1) continue;
        for (int e = 1; e <= d; e++) {
            u128 s2 = s1 + pow7[e];
            if (s2 + 2 >= J->z2) break;
            if (s2 + 2 * pow7[e] < J->z1) continue;
            for (int f = 1; f <= e; f++) {
                u128 s3 = s2 + pow7[f];
                if (s3 + 1 >= J->z2) break;
                if (s3 + pow7[f] < J->z1) continue;
                int g_hi = p7_floor(J->z2 - 1 - s3, f);
                if (g_hi == 0) continue;
                int g_lo = 1;
                if (s3 + pow7[1] < J->z1) {
                    u128 need = J->z1 - s3;
                    int lo = 1, hi = f; g_lo = f + 1;
                    while (lo <= hi) {
                        int mid = (lo + hi) / 2;
                        if (pow7[mid] >= need) { g_lo = mid; hi = mid - 1; }
                        else lo = mid + 1;
                    }
                }
                for (int g = g_lo; g <= g_hi; g++) {
                    u128 t = s3 + pow7[g];
                    u64 tlo = (u64)t, thi = (u64)(t >> 64);
                    rc++;
                    if (!bitmap_test(tlo)) continue;
                    /* binary search in bucket, order (lo, hi) */
                    Vec *B = &J->lb->bucket[tlo >> 56];
                    size_t lo = 0, hi = B->len;
                    while (lo < hi) {
                        size_t mid = (lo + hi) / 2;
                        const Entry *m = &B->buf[mid];
                        if (m->lo < tlo || (m->lo == tlo && m->hi < thi))
                            lo = mid + 1;
                        else hi = mid;
                    }
                    for (size_t i = lo;
                         i < B->len && B->buf[i].lo == tlo &&
                         B->buf[i].hi == thi;
                         i++)
                        report_match(J, &B->buf[i], d, e, f, g);
                }
            }
        }
    }
    atomic_fetch_add(J->right_count, rc);
    return NULL;
}

/* ------------------------------------------------------------------ main */

int main(int argc, char **argv) {
    if (argc < 5) {
        fprintf(stderr,
                "usage: %s H NSLABS progress.jsonl candidates.txt [start]\n",
                argv[0]);
        return 2;
    }
    H = atoi(argv[1]);
    int nslabs = atoi(argv[2]);
    const char *prog_path = argv[3], *cand_path = argv[4];
    int start_slab = argc > 5 ? atoi(argv[5]) : 0;
    int nthreads = 14;

    pow7 = malloc((H + 1) * sizeof(u128));
    pow7lo = malloc((H + 1) * sizeof(u64));
    for (int i = 0; i <= H; i++) {
        pow7[i] = ipow7(i);
        pow7lo[i] = (u64)pow7[i];
    }
    bitmap = calloc(1ULL << (BITMAP_BITS - 6), sizeof(u64));
    if (!bitmap) { fprintf(stderr, "bitmap OOM\n"); return 1; }

    u128 zmax = 3 * pow7[H] + 1;
    FILE *prog = fopen(prog_path, "a");
    FILE *cand = fopen(cand_path, "a");
    pthread_mutex_t cand_lock = PTHREAD_MUTEX_INITIALIZER;

    for (int slab = start_slab; slab < nslabs; slab++) {
        /* equal-left-count slab boundaries: z_i = zmax * (i/n)^(7/3) */
        double f1 = pow((double)slab / nslabs, 7.0 / 3.0);
        double f2 = pow((double)(slab + 1) / nslabs, 7.0 / 3.0);
        u128 z1 = (u128)(f1 * (double)zmax);
        u128 z2 = slab + 1 == nslabs ? zmax : (u128)(f2 * (double)zmax);
        if (z2 <= z1) z2 = z1 + 1;
        time_t t0 = time(NULL);

        LeftBuild lb;
        memset(&lb, 0, sizeof(lb));
        for (int i = 0; i < NBUCKET; i++)
            pthread_mutex_init(&lb.lock[i], NULL);
        _Atomic int next_a = 1;
        LeftJob lj = { &lb, z1, z2, &next_a };
        pthread_t th[64];
        for (int i = 0; i < nthreads; i++)
            pthread_create(&th[i], NULL, left_worker, &lj);
        for (int i = 0; i < nthreads; i++) pthread_join(th[i], NULL);

        _Atomic int next_b = 0;
        SortJob sj = { &lb, &next_b };
        for (int i = 0; i < nthreads; i++)
            pthread_create(&th[i], NULL, sort_worker, &sj);
        for (int i = 0; i < nthreads; i++) pthread_join(th[i], NULL);

        memset(bitmap, 0, 1ULL << (BITMAP_BITS - 3));
        long long left_count = 0;
        for (int i = 0; i < NBUCKET; i++) {
            left_count += (long long)lb.bucket[i].len;
            for (size_t j = 0; j < lb.bucket[i].len; j++)
                bitmap_set(lb.bucket[i].buf[j].lo);
        }

        _Atomic int next_d = 1;
        _Atomic long long right_count = 0, cand_count = 0;
        ScanJob sc = { &lb, z1, z2, &next_d, &right_count, &cand_count,
                       cand, &cand_lock };
        for (int i = 0; i < nthreads; i++)
            pthread_create(&th[i], NULL, scan_worker, &sc);
        for (int i = 0; i < nthreads; i++) pthread_join(th[i], NULL);

        char h1[40], h2[40];
        u128_hex(z1, h1); u128_hex(z2, h2);
        fprintf(prog,
                "{\"slab\": %d, \"H\": %d, \"nslabs\": %d, \"z1\": \"%s\", "
                "\"z2\": \"%s\", \"left\": %lld, \"right\": %lld, "
                "\"cands\": %lld, \"secs\": %ld}\n",
                slab, H, nslabs, h1, h2, left_count,
                (long long)right_count, (long long)cand_count,
                (long)(time(NULL) - t0));
        fflush(prog);
        fprintf(stderr, "slab %d/%d done: left %lld right %lld cands %lld "
                "(%lds)\n", slab + 1, nslabs, left_count,
                (long long)right_count, (long long)cand_count,
                (long)(time(NULL) - t0));
        for (int i = 0; i < NBUCKET; i++) free(lb.bucket[i].buf);
    }
    fclose(prog);
    fclose(cand);
    return 0;
}
