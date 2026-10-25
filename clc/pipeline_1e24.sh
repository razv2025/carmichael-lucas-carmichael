#!/bin/sh
# 1e24 CLC pipeline: wait for download -> decode (PARI) -> verify completeness -> scan
D=/Users/razvakil/.claude/jobs/c6e4e4e0/tmp/c24; S=/Users/razvakil/.claude/jobs/c6e4e4e0/tmp/lcscript; cd "$D"
until [ -f download.ok ]; do sleep 60; done
grep -q complete download.ok || { echo "download failed: $(cat download.ok)" > pipeline.done; exit 1; }
echo "$(date '+%H:%M:%S') decode start" >> pipeline.log
gp -q "$S/bin2txt.gp" < /dev/null > carm10e24.txt 2> decode.err
echo "$(date '+%H:%M:%S') decode done: $(wc -l < carm10e24.txt | tr -d ' ') lines, $(stat -f %z carm10e24.txt) bytes" >> pipeline.log
python3 -I "$S/verify_list.py" carm10e24.txt > verify.out 2>&1
cat verify.out >> pipeline.log
grep -q "VERDICT: COMPLETE AND CONSISTENT" verify.out || { echo "verification FAILED — scan not started" > pipeline.done; exit 1; }
echo "$(date '+%H:%M:%S') scan start" >> pipeline.log
python3 -I "$S/full_scan.py" carm10e24.txt > scan24.out 2>&1
echo "$(date '+%H:%M:%S') scan done" >> pipeline.log
echo "complete" > pipeline.done
