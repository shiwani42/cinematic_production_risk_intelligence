#!/usr/bin/env bash
# Assemble MATRIX demo: short intro, long live UI, crossfaded Dev UI, short outro.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
WALK_RAW="$ROOT/raw/walkthrough.webm"
DEV_RAW="$ROOT/raw/devui.webm"
WORK="$ROOT/raw/build"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
OUT="$ROOT/MATRIX_demo_final.mp4"

mkdir -p "$WORK"

slide() {
  local dur="$1" out="$2" title="$3" l2="$4" l3="${5:-}"
  local vf="drawtext=fontfile=$FONT:text='$title':fontcolor=0xFF6B2C:fontsize=42:x=(w-text_w)/2:y=h*0.26,\
drawtext=fontfile=$FONT_REG:text='$l2':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=h*0.40"
  if [[ -n "$l3" ]]; then
    vf="$vf,drawtext=fontfile=$FONT_REG:text='$l3':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=h*0.50"
  fi
  ffmpeg -y -f lavfi -i "color=c=0x12141a:s=1280x720:d=$dur" \
    -vf "$vf" -c:v libx264 -pix_fmt yuv420p -r 30 -t "$dur" "$out" 2>/dev/null
}

# Cold open ≤12s (single card)
slide 10 "$WORK/01_intro.mp4" "MATRIX" "Lot hazards × unit hazards × collision on the shot list" "Production Risk Intelligence for 1st ADs"

normalize() {
  local in="$1" out="$2" trim_start="${3:-0}"
  ffmpeg -y -ss "$trim_start" -i "$in" \
    -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p" \
    -c:v libx264 -pix_fmt yuv420p -r 30 -an "$out" 2>/dev/null
}

normalize "$WALK_RAW" "$WORK/walk.mp4" 0
# Trim Dev UI to agent-structure view (skip empty Events shell + modal dismiss)
normalize "$DEV_RAW" "$WORK/devui.mp4" 7.8

WALK_D=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$WORK/walk.mp4")
XF=0.45
OFF=$(python3 -c "print(max(0, float('$WALK_D') - $XF))")

ffmpeg -y -i "$WORK/walk.mp4" -i "$WORK/devui.mp4" \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=${XF}:offset=${OFF}[v]" \
  -map "[v]" -c:v libx264 -pix_fmt yuv420p -r 30 -an "$WORK/live.mp4" 2>/dev/null

# Closing cards ≤30s total
slide 11 "$WORK/04_stack.mp4" "Google ADK on Cloud Run" "Four specialists · deterministic tools · Gemini narrates" "IBM Bob dev partner — BOB_USAGE.md"
slide 9 "$WORK/05_impact.mp4" "The collision" "Pyro under a helicopter · fatigued key grip" "Not fire equals high."
slide 6 "$WORK/06_outro.mp4" "Try it live" "matrix-632958340118.us-central1.run.app/dashboard" ""

printf "file '%s'\n" \
  "$WORK/01_intro.mp4" \
  "$WORK/live.mp4" \
  "$WORK/04_stack.mp4" \
  "$WORK/05_impact.mp4" \
  "$WORK/06_outro.mp4" > "$WORK/concat.txt"

ffmpeg -y -f concat -safe 0 -i "$WORK/concat.txt" -c copy "$WORK/merged_nosub.mp4" 2>/dev/null

ffmpeg -y -i "$WORK/merged_nosub.mp4" \
  -vf "subtitles=$ROOT/captions.srt:force_style='FontName=DejaVu Sans,FontSize=22,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Shadow=1,MarginV=28'" \
  -c:v libx264 -pix_fmt yuv420p -crf 20 -preset medium -movflags +faststart -an \
  "$OUT" 2>/dev/null

DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUT")
echo "Wrote $OUT (${DUR}s)"
LIVE_D=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$WORK/live.mp4")
echo "Live UI segment (walk + devui xfade): ${LIVE_D}s"
