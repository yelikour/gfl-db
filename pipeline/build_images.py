# -*- coding: utf-8 -*-
"""Convert extracted portraits to site-ready webp images.

Reads site/data/image_jobs.json (from build_data.py), writes site/public/images/.
  thumb:    from normal.png  width 360  q80  (grid card)
  normal:   width 1280 q82   (detail view)
  damaged:  width 1280 q82   (detail view)

Supports --sample N (process first N jobs for size estimation), --limit N, resume by default
(skips existing outputs with newer mtime than source).
"""
import json
import os
import sys
import time

from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
JOBS = os.path.join(ROOT, 'site', 'data', 'image_jobs.json')
OUTDIR = os.path.join(ROOT, 'site', 'public', 'images')

THUMB_W, FULL_W = 360, 1280
THUMB_Q, FULL_Q = 80, 82

Image.MAX_IMAGE_PIXELS = None


def convert(src, dst, width, quality):
    im = Image.open(src)
    if im.mode not in ('RGBA', 'RGB'):
        im = im.convert('RGBA')
    if im.width > width:
        h = round(im.height * width / im.width)
        im = im.resize((width, h), Image.LANCZOS)
    im.save(dst, 'WEBP', quality=quality, method=4)


def main():
    sample = 0
    limit = 0
    for a in sys.argv[1:]:
        if a.startswith('--sample='):
            sample = int(a.split('=')[1])
        elif a.startswith('--limit='):
            limit = int(a.split('=')[1])
    jobs = json.load(open(JOBS, encoding='utf-8'))
    if sample:
        jobs = jobs[:sample]
    if limit:
        jobs = jobs[:limit]
    os.makedirs(OUTDIR, exist_ok=True)
    t0 = time.time()
    done = skipped = missing = failed = 0
    total_bytes = 0
    for i, job in enumerate(jobs):
        for kind, dst_rel in job['out'].items():
            src = job['src'].get('normal' if kind == 'thumb' else kind)
            if not src:
                continue
            srcp = os.path.join(ROOT, src)
            dstp = os.path.join(OUTDIR, os.path.basename(dst_rel))
            if not os.path.exists(srcp):
                missing += 1
                continue
            if os.path.exists(dstp) and os.path.getmtime(dstp) >= os.path.getmtime(srcp):
                skipped += 1
                continue
            try:
                convert(srcp, dstp, THUMB_W if kind == 'thumb' else FULL_W,
                        THUMB_Q if kind == 'thumb' else FULL_Q)
                done += 1
                total_bytes += os.path.getsize(dstp)
            except Exception as e:
                failed += 1
                print(f'FAIL {srcp}: {e}', flush=True)
        if (i + 1) % 200 == 0:
            print(f'[{i+1}/{len(jobs)}] done={done} skip={skipped} {time.time()-t0:.0f}s', flush=True)
    dt = time.time() - t0
    print(f'COMPLETE jobs={len(jobs)} done={done} skipped={skipped} missing={missing} failed={failed} '
          f'{dt:.0f}s out_bytes={total_bytes}')


if __name__ == '__main__':
    main()
