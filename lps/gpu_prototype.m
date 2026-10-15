// Prototype: GPU (Metal) version of the (7,3,4) right-side slab scan.
// Measures enumeration+probe throughput and validates the tuple count
// against the CPU engine's 'right' figure for the same slab.
//
// Parallelisation: 2D grid over (d,e); each thread walks its own f and g
// loops.  128-bit values are emulated with two ulongs.  The bitmap probe
// uses the low 64 bits exactly as the CPU engine does.
//
// build: clang -O2 -fobjc-arc -framework Foundation -framework Metal -o gpuscan gpuscan.m
// run:   ./gpuscan H NSLABS SLAB

#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#include <math.h>

typedef __uint128_t u128;

static NSString *kSrc = @R"MSL(
#include <metal_stdlib>
using namespace metal;

struct U128 { ulong lo; ulong hi; };

inline U128 u128_add(U128 a, U128 b) {
    U128 r; r.lo = a.lo + b.lo; r.hi = a.hi + b.hi + (r.lo < a.lo ? 1 : 0);
    return r;
}
inline bool u128_lt(U128 a, U128 b) {
    return (a.hi < b.hi) || (a.hi == b.hi && a.lo < b.lo);
}
inline bool u128_ge(U128 a, U128 b) { return !u128_lt(a, b); }

struct Params {
    U128 z1, z2;
    uint H;
    uint bitmap_words;   // length of bitmap in 64-bit words
    ulong bitmap_mask;
};

kernel void scan(device const U128   *p7      [[buffer(0)]],
                 device const ulong  *bitmap  [[buffer(1)]],
                 constant Params     &P       [[buffer(2)]],
                 device ulong        *counts  [[buffer(3)]],   // 2 per thread
                 uint2 gid [[thread_position_in_grid]])
{
    uint d = gid.x + 1, e = gid.y + 1;
    if (d > P.H || e > P.H) return;
    uint slot0 = (gid.y * P.H + gid.x) * 2;
    counts[slot0] = 0; counts[slot0 + 1] = 0;
    if (e > d) return;

    U128 s1 = p7[d];
    if (u128_ge(s1, P.z2)) return;

    U128 s2 = u128_add(s1, p7[e]);
    if (u128_ge(s2, P.z2)) return;
    // even with f=g=e the sum must reach z1
    U128 hi2 = u128_add(s2, u128_add(p7[e], p7[e]));
    if (u128_lt(hi2, P.z1)) return;

    ulong tuples = 0, hits = 0;

    for (uint f = 1; f <= e; f++) {
        U128 s3 = u128_add(s2, p7[f]);
        if (u128_ge(s3, P.z2)) break;
        if (u128_lt(u128_add(s3, p7[f]), P.z1)) continue;

        // g range: largest g<=f with s3+g^7 < z2 ; smallest with s3+g^7 >= z1
        uint g_hi = 0;
        {
            uint lo = 1, hi = f;
            while (lo <= hi) {
                uint mid = (lo + hi) >> 1;
                if (u128_lt(u128_add(s3, p7[mid]), P.z2)) { g_hi = mid; lo = mid + 1; }
                else { if (mid == 0) break; hi = mid - 1; }
            }
        }
        if (g_hi == 0) continue;
        uint g_lo = 1;
        if (u128_lt(u128_add(s3, p7[1]), P.z1)) {
            uint lo = 1, hi = f, found = f + 1;
            while (lo <= hi) {
                uint mid = (lo + hi) >> 1;
                if (u128_ge(u128_add(s3, p7[mid]), P.z1)) { found = mid; if (mid == 0) break; hi = mid - 1; }
                else lo = mid + 1;
            }
            g_lo = found;
        }
        if (g_lo > g_hi) continue;

        ulong s3lo = s3.lo;
        for (uint g = g_lo; g <= g_hi; g++) {
            ulong tlo = s3lo + p7[g].lo;
            tuples++;
            ulong idx = tlo & P.bitmap_mask;
            if ((bitmap[idx >> 6] >> (idx & 63)) & 1UL) hits++;
        }
    }
    uint slot = (gid.y * P.H + gid.x) * 2;
    counts[slot] = tuples;
    counts[slot + 1] = hits;
}
)MSL";

int main(int argc, char **argv) { @autoreleasepool {
    int H = argc > 1 ? atoi(argv[1]) : 1500;
    int NSLABS = argc > 2 ? atoi(argv[2]) : 7600;
    int SLAB = argc > 3 ? atoi(argv[3]) : 4000;
    int NSLAB_RUN = argc > 4 ? atoi(argv[4]) : 1;

    u128 *p7 = malloc((size_t)(H + 1) * sizeof(u128));
    for (int i = 0; i <= H; i++) { u128 v = 1; for (int k = 0; k < 7; k++) v *= (u128)i; p7[i] = v; }
    u128 zmax = 3 * p7[H] + 1;

    id<MTLDevice> dev = MTLCreateSystemDefaultDevice();
    NSError *err = nil;
    id<MTLLibrary> lib = [dev newLibraryWithSource:kSrc options:nil error:&err];
    if (!lib) { printf("shader compile failed: %s\n", [[err localizedDescription] UTF8String]); return 1; }
    id<MTLComputePipelineState> ps = [dev newComputePipelineStateWithFunction:[lib newFunctionWithName:@"scan"] error:&err];
    id<MTLCommandQueue> q = [dev newCommandQueue];
    id<MTLBuffer> bp7 = [dev newBufferWithBytes:p7 length:(H + 1) * sizeof(u128) options:MTLResourceStorageModeShared];
    size_t nthreads = (size_t)H * H;
    id<MTLBuffer> bct = [dev newBufferWithLength:2 * nthreads * sizeof(uint64_t) options:MTLResourceStorageModeShared];

    double t_left = 0, t_gpu = 0;
    unsigned long long tot = 0;
    size_t cap = 1 << 20;
    uint64_t *lo = malloc(cap * sizeof(uint64_t));

    for (int slab = SLAB; slab < SLAB + NSLAB_RUN; slab++) {
        double f1 = pow((double)slab / NSLABS, 7.0 / 3.0), f2 = pow((double)(slab + 1) / NSLABS, 7.0 / 3.0);
        u128 z1 = (u128)(f1 * (double)zmax), z2 = (u128)(f2 * (double)zmax);
        if (z2 <= z1) z2 = z1 + 1;

        NSDate *tl = [NSDate date];
        size_t left = 0;
        for (int a = 1; a <= H; a++) {
            if (p7[a] >= z2) break;
            for (int b = 1; b <= a; b++) {
                u128 s2 = p7[a] + p7[b];
                if (s2 + 1 >= z2) break;
                for (int c = 1; c <= b; c++) {
                    u128 t = s2 + p7[c];
                    if (t >= z2) break;
                    if (t < z1) continue;
                    if (left == cap) { cap *= 2; lo = realloc(lo, cap * sizeof(uint64_t)); }
                    lo[left++] = (uint64_t)t;
                }
            }
        }
        int bits = 20; while ((1LL << bits) < 32 * (long long)left && bits < 33) bits++;
        size_t words = (size_t)1 << (bits - 6);
        uint64_t *bm = calloc(words, sizeof(uint64_t));
        uint64_t mask = ((uint64_t)1 << bits) - 1;
        for (size_t i = 0; i < left; i++) { uint64_t ix = lo[i] & mask; bm[ix >> 6] |= 1ULL << (ix & 63); }
        t_left += -[tl timeIntervalSinceNow];

        id<MTLBuffer> bbm = [dev newBufferWithBytes:bm length:words * 8 options:MTLResourceStorageModeShared];
        struct { uint64_t z1lo, z1hi, z2lo, z2hi; uint32_t H, bw; uint64_t mask; } P;
        P.z1lo = (uint64_t)z1; P.z1hi = (uint64_t)(z1 >> 64);
        P.z2lo = (uint64_t)z2; P.z2hi = (uint64_t)(z2 >> 64);
        P.H = H; P.bw = (uint32_t)words; P.mask = mask;
        id<MTLBuffer> bP = [dev newBufferWithBytes:&P length:sizeof(P) options:MTLResourceStorageModeShared];

        NSDate *tg = [NSDate date];
        id<MTLCommandBuffer> cb = [q commandBuffer];
        id<MTLComputeCommandEncoder> enc = [cb computeCommandEncoder];
        [enc setComputePipelineState:ps];
        [enc setBuffer:bp7 offset:0 atIndex:0];
        [enc setBuffer:bbm offset:0 atIndex:1];
        [enc setBuffer:bP  offset:0 atIndex:2];
        [enc setBuffer:bct offset:0 atIndex:3];
        [enc dispatchThreads:MTLSizeMake(H, H, 1) threadsPerThreadgroup:MTLSizeMake(32, 8, 1)];
        [enc endEncoding]; [cb commit]; [cb waitUntilCompleted];
        t_gpu += -[tg timeIntervalSinceNow];

        uint64_t *c = [bct contents];
        for (size_t i = 0; i < nthreads; i++) tot += c[2*i];
        free(bm);
    }
    printf("slabs %d..%d  tuples=%llu\n  host left-build %.2fs | GPU scan %.2fs | total %.2fs\n",
           SLAB, SLAB + NSLAB_RUN - 1, tot, t_left, t_gpu, t_left + t_gpu);
    printf("  GPU-scan-only rate %.3e/s | hybrid (left+scan) rate %.3e/s\n",
           tot / t_gpu, tot / (t_left + t_gpu));
    return 0;
} }
