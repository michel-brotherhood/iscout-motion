#!/bin/sh
# Mixagem final: trilha B + SFX sintetizados (tempos em ms, alinhados ao storyboard).
cd "$(dirname "$0")/out"
ev() { echo "[$1]adelay=$2|$2,volume=$3[$4]"; }
ffmpeg -v error -y -i gen/trilha_b.mp3 \
  -i sfx/kick.wav -i sfx/kick.wav -i sfx/kick.wav -i sfx/whoosh.wav -i sfx/whoosh.wav \
  -i sfx/click.wav -i sfx/click.wav -i sfx/click.wav -i sfx/click.wav -i sfx/sweep.wav -i sfx/sweep.wav \
  -i sfx/amb.wav -i sfx/whistle.wav -filter_complex "
[0]volume=0.85,afade=t=out:st=29.2:d=0.8[m];
$(ev 1 250 0.9 k1);$(ev 2 1000 0.8 k2);$(ev 3 1750 0.9 k3);
$(ev 4 3450 0.7 w1);$(ev 5 7700 0.6 w2);
$(ev 6 9150 0.5 c1);$(ev 7 9500 0.5 c2);$(ev 8 9850 0.5 c3);$(ev 9 10200 0.5 c4);
$(ev 10 10750 0.6 s1);$(ev 11 16300 0.6 s2);
$(ev 12 18300 0.9 a1);$(ev 13 22100 0.8 wh);
[m][k1][k2][k3][w1][w2][c1][c2][c3][c4][s1][s2][a1][wh]amix=inputs=14:normalize=0:duration=first,alimiter=limit=0.89,atrim=0:30[out]" \
  -map "[out]" -c:a pcm_s16le -ar 48000 mix_final.wav
