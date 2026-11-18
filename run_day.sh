#!/usr/bin/env bash
# Uso: ./run_day.sh guiones/2026-11-20.json
# Fabrica los vídeos del JSON y los deja en out/ (cada uno < 95 MB).
set -e
R="$(cd "$(dirname "$0")" && pwd)"
export DAY_JSON="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
P="$R/pipeline"; C=/home/claude/canal
cd $C
IDS=$(python3 -c "import json,os;print(' '.join(v['id'] for v in json.load(open(os.environ['DAY_JSON']))['videos']))")
VIDS=$(python3 -c "import json,os;print(' '.join(v['id'] for v in json.load(open(os.environ['DAY_JSON']))['videos'] if v['fmt']=='v'))")
python3 "$P/tts_all.py"
python3 "$P/slides.py" $IDS >/dev/null
python3 "$P/render2.py" $IDS
[ -n "$VIDS" ] && python3 "$P/short_style.py" $VIDS
python3 "$P/music2.py" $IDS
mkdir -p "$R/out"; rm -f "$R/out"/*.mp4
for id in $IDS; do
  src=$C/video2/$id.mp4; echo " $VIDS " | grep -q " $id " && src=$C/video_tiktok/$id.mp4
  out="$R/out/$id.mp4"
  ffmpeg -v error -y -i "$src" -i /tmp/r2_$id/voice.wav -stream_loop -1 -i $C/music/$id.wav \
    -filter_complex "[2:a]volume=0.13[m];[1:a][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest "$out"
  sz=$(stat -c %s "$out")
  if [ "$sz" -gt 95000000 ]; then
    d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out")
    br=$(python3 -c "print(int(88e6*8/$d/1000)-200)")
    ffmpeg -v error -y -i "$out" -c:v libx264 -b:v ${br}k -maxrate ${br}k -bufsize $((br*2))k -preset veryfast -c:a copy "$out.tmp.mp4" && mv "$out.tmp.mp4" "$out"
  fi
  echo "$id $(stat -c %s "$out") bytes"
done
