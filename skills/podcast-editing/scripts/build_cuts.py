#!/usr/bin/env python3
"""
播客剪辑主脚本：结构剪 → 长停顿压缩 → 去口癖（可选，需 SenseVoice 词级 jsonl）。

用法：
  python3 build_cuts.py --audio 原音频.m4a --output 精剪v3.m4a \
      --cut "0,11.5" --cut "1797.4,1873.9" --cut "4216.7,END" \
      [--sensevoice 词级转写.jsonl] [--segments-out segments.txt] \
      [--min-gap 2.0] [--keep-gap 0.7] [--no-filler]

  --cut "start,end"：删除的原音频区间；end 用 END 表示音频末尾。
  省略 --sensevoice 则只做结构剪 + 停顿压缩。
"""
import argparse, json, re, subprocess, tempfile, os, sys

# -------- 去口癖词表（可调） --------
SINGLE = set('嗯呃额唉哦埃')                                  # 纯语气词
PHRASES = sorted(['就是说', '然后就是', '就是就是', '然后', '就是', '对吧', '反正'],
                 key=len, reverse=True)                      # 口头禅
STUT = set('我你他她它这那就对')                              # 结巴重复字（安全集合）
BACK = set('嗯对是哦')                                        # 单独应答（前后空 0.4s+）
PUNCT = set('，。？！、；：·…—“”‘’（） \t\n')


def probe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def detect_silences(audio, noise="-40dB", d=0.12):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", audio,
                        "-af", f"silencedetect=noise={noise}:d={d}", "-f", "null", "-"],
                       capture_output=True, text=True)
    pairs, cur = [], None
    for line in r.stderr.splitlines():
        m = re.search(r"silence_start: ([0-9.]+)", line)
        if m:
            cur = float(m.group(1)); continue
        m = re.search(r"silence_end: ([0-9.]+)", line)
        if m and cur is not None:
            pairs.append((cur, float(m.group(1)))); cur = None
    return pairs


def parse_cuts(cut_strs, dur):
    cuts = []
    for c in cut_strs:
        a, b = c.split(",")
        a = float(a)
        b = dur if b.strip().upper() == "END" else float(b)
        cuts.append((a, b))
    return cuts


def subtract(base, cuts):
    """从 base 区间列表里减去 cuts 区间（都按 start 排序）。"""
    cuts = sorted(cuts)
    out = []
    for a, b in base:
        c = a
        for s, e in cuts:
            if e <= c:
                continue
            if s >= b:
                break
            if s > c:
                out.append((c, s))
            c = max(c, e)
        if c < b:
            out.append((c, b))
    return out


def load_chars(jsonl):
    chars = []
    for line in open(jsonl):
        seg = json.loads(line)
        toks = seg.get('tokens', [])
        ts = seg.get('timestamps', [])
        n = len(toks)
        for i, tok in enumerate(toks):
            if tok in PUNCT:
                continue
            t0 = ts[i] if i < len(ts) else 0.0
            t1 = ts[i + 1] if i + 1 < n else seg['end']
            chars.append((tok, t0, t1))
    return chars


def filler_removals(chars):
    N = len(chars)
    mark = [False] * N
    counts = {'语气词': 0, '口头禅': 0, '重复字': 0, '单独应答': 0}

    def span(i, j, key):
        for k in range(i, j):
            if not mark[k]:
                mark[k] = True
                counts[key] += 1

    for i, (ch, t0, t1) in enumerate(chars):
        if ch in SINGLE:
            span(i, i + 1, '语气词')

    i = 0
    while i < N:
        hit = False
        for ph in PHRASES:
            L = len(ph)
            if i + L <= N and not any(mark[i:i + L]) \
                    and ''.join(c[0] for c in chars[i:i + L]) == ph:
                span(i, i + L, '口头禅'); i += L; hit = True; break
        if not hit:
            i += 1

    i = 0
    while i < N:
        if mark[i]:
            i += 1; continue
        j = i
        while j < N and chars[j][0] == chars[i][0]:
            j += 1
        if j - i >= 2 and chars[i][0] in STUT:
            span(i + 1, j, '重复字')
        i = j

    for i in range(N):
        if mark[i] or chars[i][0] not in BACK:
            continue
        gb = chars[i][1] - chars[i - 1][2] if i > 0 else 9e9
        ga = chars[i + 1][1] - chars[i][2] if i + 1 < N else 9e9
        if gb > 0.4 and ga > 0.4:
            span(i, i + 1, '单独应答')

    rem = []
    i = 0
    while i < N:
        if mark[i]:
            j = i
            while j < N and mark[j]:
                j += 1
            rem.append((chars[i][1], chars[j - 1][2])); i = j
        else:
            i += 1
    print("去口癖:", counts, "删除区间", len(rem), "个")
    return rem


def render(audio, segments, output):
    parts, labels = [], []
    for i, (s, e) in enumerate(segments):
        parts.append(f"[0:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS[a{i}]")
        labels.append(f"[a{i}]")
    fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(segments)}:v=0:a=1[out]"
    fscript = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False)
    fscript.write(fc); fscript.close()
    r = subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", audio,
                        "-filter_complex_script", fscript.name, "-map", "[out]",
                        "-c:a", "aac", "-b:a", "128k", "-ar", "32000", output],
                       capture_output=True, text=True)
    os.unlink(fscript.name)
    if r.returncode != 0:
        print("FFMPEG 出错:", r.stderr[-2000:], file=sys.stderr)
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--audio', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--cut', action='append', default=[], help='"start,end"，end 可用 END')
    ap.add_argument('--sensevoice', help='SenseVoice 词级 jsonl，提供则去口癖')
    ap.add_argument('--min-gap', type=float, default=2.0)
    ap.add_argument('--keep-gap', type=float, default=0.7)
    ap.add_argument('--segments-out', help='把最终保留段写进该文件（供 map_chapters）')
    ap.add_argument('--no-filler', action='store_true')
    args = ap.parse_args()

    dur = probe_duration(args.audio)
    keeps = subtract([(0, dur)], parse_cuts(args.cut, dur))

    silences = detect_silences(args.audio)
    final = []
    for A, B in keeps:
        c = A
        for s, e in silences:
            if e - s <= args.min_gap or s < c or e > B:
                continue
            if s > c:
                final.append((c, s))
            final.append((s, s + args.keep_gap)); c = e
        if c < B:
            final.append((c, B))

    if args.sensevoice and not args.no_filler:
        final = subtract(final, filler_removals(load_chars(args.sensevoice)))

    if args.segments_out:
        with open(args.segments_out, 'w') as f:
            for s, e in final:
                f.write(f"{s:.3f} {e:.3f}\n")
        print("保留段已写:", args.segments_out)

    total = sum(e - s for s, e in final)
    print(f"保留 {len(final)} 段，预计 {total:.1f}s = {int(total // 60)}:{total % 60:04.1f}")
    render(args.audio, final, args.output)
    print("完成:", args.output)


if __name__ == '__main__':
    main()