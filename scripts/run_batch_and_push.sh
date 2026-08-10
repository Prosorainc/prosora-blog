#!/usr/bin/env bash
set -euo pipefail
cd /home/ubuntu/affiliate-blog/scripts
echo "[run] starting batch_books.py --max 20"
python3 batch_books.py --max 20
echo "[run] batch done, running push_blog.py"
python3 push_blog.py
echo "[run] all done"
