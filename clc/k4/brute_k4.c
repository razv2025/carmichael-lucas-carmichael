/* brute_k4.c — brute-force reference for the kappa-relaxed 4-prime problem (see enum_k4.c).
 * Enumerates ALL n = p1 p2 p3 p4 ≤ Bt (admissible primes p1<p2<p3<p4, kappa | p^2-1) and tests
 * n/p ≡ 1 (mod (p^2-1)/kappa) for each p.  Prints "n p1 p2 p3 p4" sorted by n.
 * Usage: ./brute_k4 KAPPA Bt   (Bt ≤ ~1e12) */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
typedef uint64_t u64; typedef unsigned __int128 u128;
static u64 KAPPA; static int INTEGERS=0;
static int cmp(const void*a,const void*b){ u64 x=*(u64*)a,y=*(u64*)b; return x<y?-1:x>y; }
int main(int argc,char**argv){
    if(argc<3){fprintf(stderr,"usage: brute_k4 KAPPA Bt\n");return 2;}
    KAPPA=strtoull(argv[1],0,10); if(argc>3 && !strcmp(argv[3],"--integers")) INTEGERS=1; long double Bd=strtold(argv[2],0); u128 Bt=(u128)Bd;
    /* admissible primes up to Bt/(a*b*c) where a<b<c are the three smallest admissible primes */
    u64 N=(u64)(Bt/(5*7*11))+10; char*comp=calloc(N+1,1);
    for(u64 i=2;i*i<=N;i++) if(!comp[i]) for(u64 j=i*i;j<=N;j+=i) comp[j]=1;
    u64 *pr=malloc(8*(N/2+10)); size_t np=0;
    for(u64 p=5;p<=N;p++) if((INTEGERS? (p&1) : !comp[p]) && ((u128)p*p-1)%KAPPA==0) pr[np++]=p;
    if(np<3){printf("# fewer than 3 admissible primes\n");return 0;}
    u64 *L=malloc(8*np); for(size_t i=0;i<np;i++) L[i]=(u64)(((u128)pr[i]*pr[i]-1)/KAPPA);
    u64 *out=NULL; size_t nout=0, cap=0; u64 tuples=0;
    u64 sols[5000][5]; 
    for(size_t i1=0;i1<np;i1++){ u64 p1=pr[i1]; if((u128)p1*p1*p1*p1>Bt) break;
     for(size_t i2=i1+1;i2<np;i2++){ u64 p2=pr[i2]; u128 P=(u128)p1*p2; if(P*p2*p2>Bt) break;
      for(size_t i3=i2+1;i3<np;i3++){ u64 p3=pr[i3]; u128 Q=P*p3; if(Q*p3>Bt) break; u64 Qm1=(u64)Q-1;
       for(size_t i4=i3+1;i4<np;i4++){ u64 p4=pr[i4]; u128 n=Q*p4; if(n>Bt) break; tuples++;
        if(Qm1 % L[i4]) continue;                 /* condition at p4 */
        if((u64)(P*p4-1) % L[i3]) continue;       /* at p3 */
        if((u64)((u128)p1*p3*p4-1) % L[i2]) continue;
        if((u64)((u128)p2*p3*p4-1) % L[i1]) continue;
        if(nout==cap){cap=cap?2*cap:64; out=realloc(out,8*cap);} out[nout]=(u64)n; 
        if(nout<5000){sols[nout][0]=(u64)n;sols[nout][1]=p1;sols[nout][2]=p2;sols[nout][3]=p3;sols[nout][4]=p4;} nout++;
       }}}}
    /* sort by n (sols array parallel) */
    for(size_t a=0;a<nout&&a<5000;a++) for(size_t b=a+1;b<nout&&b<5000;b++) if(sols[b][0]<sols[a][0]){u64 t[5];memcpy(t,sols[a],40);memcpy(sols[a],sols[b],40);memcpy(sols[b],t,40);}
    for(size_t a=0;a<nout&&a<5000;a++) printf("%llu %llu %llu %llu %llu\n",(unsigned long long)sols[a][0],(unsigned long long)sols[a][1],(unsigned long long)sols[a][2],(unsigned long long)sols[a][3],(unsigned long long)sols[a][4]);
    fprintf(stderr,"brute: kappa=%llu Bt=%s admissible_primes=%zu tuples=%llu solutions=%zu\n",(unsigned long long)KAPPA,argv[2],np,(unsigned long long)tuples,nout);
    return 0;
}
