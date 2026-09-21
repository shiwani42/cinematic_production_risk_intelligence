#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
RAW="$ROOT/raw/walkthrough.webm"
WORK="$ROOT/raw/build"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
OUT="$ROOT/MATRIX_demo_final.mp4"

mkdir -p "$WORK"

# $1=duration $2=out $3=title $4=line2 $5=line3 (optional)
slide() {
  local dur="$1" out="$2" title="$3" l2="$4" l3="${5:-}"
  local vf="drawtext=fontfile=$FONT:text='$title':fontcolor=0xFF6B2C:fontsize=42:x=(w-text_w)/2:y=h*0.26,\
drawtext=fontfile=$FONT_REG:text='$l2':fontcolor=white:fontsize=26:x=(w-text_w)/2:y=h*0.40"
  if [[ -n "$l3" ]]; then
    vf="$vf,drawtext=fontfile=$FONT_REG:text='$l3':fontcolor=white:fontsize=26:x=(w-text_w)/2:y=h*0.50"
  fi
  ffmpeg -y -f lavfi -i "color=c=0x12141a:s=1280x720:d=$dur" \
    -vf "$vf" -c:v libx264 -pix_fmt yuv420p -r 30 -t "$dur" "$out" 2>/dev/null
}

slide 11 "$WORK/01_problem.mp4" "Safety still lives in the spreadsheet" "Storyboard AI ignores what the lot already has" "and what your unit introduces."
slide 10 "$WORK/02_product.mp4" "MATRIX" "Production Risk Intelligence for 1st ADs" "A draft you can take to set — not a chatbot essay."
slide 22 "$WORK/04_stack.mp4" "Built on Google Cloud" "Google ADK + four specialists (named tools)" "IBM Bob: development partner (BOB_USAGE.md)"
slide 14 "$WORK/05_design.mp4" "A complete RA product" "Brief → hazards → assessment → print / JSON" "Fatigue: hours, circadian, altitude, lot × role"
slide 13 "$WORK/06_impact.mp4" "The collision" "Dry-brush pyro under a helicopter on a remote lot" "Fatigued key grip — not fire equals high."
slide 9 "$WORK/07_outro.mp4" "Try it live" "matrix-632958340118.us-central1.run.app/dashboard" ""

ffmpeg -y -i "$RAW" \
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p" \
  -c:v libx264 -pix_fmt yuv420p -r 30 -an "$WORK/03_walk_raw.mp4" 2>/dev/null

ffmpeg -y -i "$WORK/03_walk_raw.mp4" \
  -c:v copy -an "$WORK/03_walk.mp4" 2>/dev/null

printf "file '%s'\n" \
  "$WORK/01_problem.mp4" \
  "$WORK/02_product.mp4" \
  "$WORK/03_walk.mp4" \
  "$WORK/04_stack.mp4" \
  "$WORK/05_design.mp4" \
  "$WORK/06_impact.mp4" \
  "$WORK/07_outro.mp4" > "$WORK/concat.txt"

ffmpeg -y -f concat -safe 0 -i "$WORK/concat.txt" -c copy "$WORK/merged_nosub.mp4" 2>/dev/null

ffmpeg -y -i "$WORK/merged_nosub.mp4" \
  -vf "subtitles=$ROOT/captions.srt:force_style='FontName=DejaVu Sans,FontSize=22,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Shadow=1,MarginV=28'" \
  -c:v libx264 -pix_fmt yuv420p -crf 20 -preset medium -movflags +faststart -an \
  "$OUT" 2>/dev/null

DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUT")
echo "Wrote $OUT (${DUR}s)"
