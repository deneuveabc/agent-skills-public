#!/bin/bash
# 降噪 + 响度统一到 -16 LUFS（播客标准）。用法: bash loudness_master.sh 输入 输出
set -e
IN="$1"; OUT="$2"
if [ -z "$IN" ] || [ -z "$OUT" ]; then
  echo "用法: bash loudness_master.sh 输入.m4a 输出.m4a"; exit 1
fi
# 降噪强度：源静音段 mean_volume < -50dB 时把 nr=10 改 nr=6（噪声很干净，别过度处理）
NR=10

echo "=== 响度测量 pass1 ==="
LOG=$(ffmpeg -hide_banner -i "$IN" -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null - 2>&1)
get() { echo "$LOG" | grep -oE "\"$1\" : \"-?[0-9.]+\"" | grep -oE -- '-?[0-9.]+'; }
input_i=$(get input_i); input_tp=$(get input_tp); input_lra=$(get input_lra)
input_thresh=$(get input_thresh); offset=$(get target_offset)
echo "measured: i=$input_i tp=$input_tp lra=$input_lra thresh=$input_thresh offset=$offset"

echo "=== pass2：降噪(afftdn nr=$NR) + 响度(loudnorm linear) ==="
ffmpeg -y -hide_banner -i "$IN" \
  -af "afftdn=nr=${NR}:nf=-50,loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=$input_i:measured_TP=$input_tp:measured_LRA=$input_lra:measured_thresh=$input_thresh:offset=$offset:linear=true" \
  -c:a aac -b:a 192k -ar 32000 "$OUT" 2>&1 | tail -2

echo "=== 校验 ==="
echo -n "时长: "; ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUT"
echo "响度回检 (ebur128):"
ffmpeg -hide_banner -i "$OUT" -af ebur128=framelog=quiet -f null - 2>&1 | grep -E "I:|LRA:|Peak:" || true
ls -lh "$OUT" | awk '{print "大小:", $5}'