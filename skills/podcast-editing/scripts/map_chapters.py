#!/usr/bin/env python3
"""
章节时间戳映射：原音频时间 -> 成片时间。
读 build_cuts.py 的 --segments-out 保留段文件（每行 "start end"，原音频秒），
把章节的原音频秒数换算成成片的 mm:ss（听众可点击跳转）。

用法:
  python3 map_chapters.py segments.txt "226|章节A" "710|章节B" ...
每个位置参数形如 "原音频秒|章节标题"，用 | 分隔。
"""
import sys


def load_segs(path):
    segs = []
    for line in open(path):
        a, b = line.split()
        segs.append((float(a), float(b)))
    return segs


def o2v(segs, t):
    acc = 0.0
    for s, e in segs:
        if t <= s:
            return acc
        if t < e:
            return acc + (t - s)
        acc += e - s
    return acc


def main():
    if len(sys.argv) < 3:
        print("用法: python3 map_chapters.py segments.txt \"秒|标题\" ...", file=sys.stderr)
        sys.exit(1)
    segs = load_segs(sys.argv[1])
    for arg in sys.argv[2:]:
        t, _, name = arg.partition('|')
        v = o2v(segs, float(t))
        mm, ss = int(v // 60), int(v % 60)
        print(f"{mm:02d}:{ss:02d}  {name}")  # 播客时间轴通常 mm:ss


if __name__ == '__main__':
    main()