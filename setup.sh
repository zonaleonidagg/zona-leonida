#!/usr/bin/env bash
# Prepara una sesión nueva para fabricar vídeos de Zona Leonida.
set -e
R="$(cd "$(dirname "$0")" && pwd)"
H=/home/claude
pip install -q --break-system-packages kokoro-onnx soundfile numpy pillow 2>&1 | grep -v -i warn || true
mkdir -p "$R/work/tts" "$R/work/canal"/{brand,thumbs,slides,audio,video,video2,video_tiktok,mascot,music}
[ -e $H/tts ] || ln -s "$R/work/tts" $H/tts
[ -e $H/canal ] || ln -s "$R/work/canal" $H/canal
[ -e $H/clips ] || ln -s "$R/assets/clips" $H/clips
cd $H/tts
[ -s kokoro-v1.0.onnx ] || curl -sSLo kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -s voices-v1.0.bin ] || curl -sSLo voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd $H/canal
[ -s brand/avatar.png ] || python3 "$R/pipeline/brand.py"
ls mascot/neutral_c_0.png >/dev/null 2>&1 || python3 "$R/pipeline/mascot.py"
[ -s audio/music_loop.wav ] || python3 -c "import numpy as np, soundfile as sf; sf.write('audio/music_loop.wav', np.zeros((44100,2)), 44100)"
echo "setup ok"
