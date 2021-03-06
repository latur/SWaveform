# -*- coding: utf-8 -*-

import sys, os, re
import sqlite3, gzip
from _functions import *

# --------------------------------------------------------------------------- #
if len(sys.argv) < 3:
    echo('Usage:   python3 %s [DB sqlite file] [coverage path] [dataset]\n' % sys.argv[0])
    echo('Example: python3 %s ./signal.db HG002/coverage HGDP\n\n' % sys.argv[0])
    sys.exit(1)

# --------------------------------------------------------------------------- #
db_file, coverage_path = sys.argv[1:3]
con = sqlite3.connect(db_file)
cur = con.cursor()

# --------------------------------------------------------------------------- #
if len(sys.argv) >= 4:
    ds = sys.argv[3]
    cur.execute(f"SELECT id, name, file FROM target WHERE dataset = '{ds}'")
else:
    cur.execute("SELECT id, name, file FROM target")

notfound = {}
total = 0
no_coverage = 0
for t_id, name, file in cur.fetchall():
    total += 1
    echo('Target: %s -> %s [%d]%s\r' % (name, file, total, " " * 60))

    cur.execute(f"SELECT id, chr, start, end FROM signal WHERE target_id = {t_id:d}")
    for id, chr, start, end in cur.fetchall():
        if start < 0: continue
        if chr[0:3] == 'chr': chr = chr[3:]
        cov_file = "%s/%s/%s.bcov" % (coverage_path, file, chr)
        if not os.path.isfile(cov_file):
            cov_file = "%s/%s/chr%s.bcov" % (coverage_path, file, chr)
        if not os.path.isfile(cov_file):
            notfound[cov_file] = True
            continue
        bytes = 2 * (end - start + 1)
        with open(cov_file, 'rb') as f:
            f.seek(start * 2)
            bin_data = f.read(bytes)
        if bin_data == bytearray([0 for i in range(bytes)]):
            cur.execute(f"DELETE FROM signal WHERE id = ?", (id,))
            no_coverage += 1
            continue
        cur.execute(f"UPDATE signal set coverage = ? WHERE id = ?", (bin_data, id,))

con.commit()
echo('Done%s\n' % (" " * 60))

skp = " ".join([f for f in notfound])
if skp != "": echo('Chromosome coverage files not found:\n%s\n' % skp)
echo('No coverage: %d\n' % no_coverage)
