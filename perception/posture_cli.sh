#!/usr/bin/env bash
# Live posture readout from the board, one line per change. WHY=1 adds the raw numbers.
LOG="$(cd "$(dirname "$0")/.." && pwd)/interface/live/board.log"
tail -n 0 -F "$LOG" 2>/dev/null | awk -v why="${WHY:-0}" '
  /^trend / {
    p=""; sh=""; ar=""; vis=""; fs="";
    for (i=2;i<=NF;i++) { split($i,kv,"="); if(kv[1]=="posture")p=kv[2]; if(kv[1]=="sh_y")sh=kv[2]; if(kv[1]=="bbox_ar")ar=kv[2]; if(kv[1]=="vis")vis=kv[2]; if(kv[1]=="floor_s")fs=kv[2]; }
    w=p; if(p=="upright")w="standing"; if(p=="bent")w="leaning"; if(p=="absent")w="nobody";
    if (p!=last) { line=w " detected"; if(why=="1") line=line "   (shoulders " sh ", box " ar ", " vis ")"; print line; fflush(); last=p }
    next }
  /^\{/ { print "ALERT: " $0; fflush() }'
