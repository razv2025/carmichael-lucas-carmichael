\\ Decode Stamm-Wilbrandt's carm10e24.bin (PARI writebin vector of all
\\ Carmichael numbers < 10^24) to one decimal integer per line on stdout.
\\ Run:  gp -q --default parisizemax=24000000000 bin2txt.gp < /dev/null > out.txt
default(parisize, 20000000000);
v = read("/Users/razvakil/.claude/jobs/c6e4e4e0/tmp/c24/carm10e24.bin");
n = #v;
for(i = 1, n, print(v[i]));
quit;
