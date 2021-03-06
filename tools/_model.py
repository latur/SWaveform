# -*- coding: utf-8 -*-
from _functions import *

def models(cursor, type, side, ds):
    matrix = [[0 for j in range(0, 32)] for i in range(0, 64)]
    hmm = [[[0 for k in range(0, 32)] for j in range(0, 32)] for i in range(0, 63)]
    mean_hist = [0 for j in range(0, 600)]

    cursor.execute(f"SELECT signal.chr, signal.coverage FROM signal "
                   f"LEFT JOIN target ON target.id = signal.target_id "
                   f"WHERE signal.type = ? AND signal.side = ? AND target.dataset = ?", (type, side, ds, ))

    total = 0
    for chr, bin in cursor.fetchall():
        if len(bin) == 0:
            continue

        sig = b2sig(bin)
        mean_hist[min(int(sum(sig)/len(sig)), 599)] += 1
        total += 1

        # Normalized
        n64 = normal(sig, 8, 32)
        for i, v in enumerate(n64):
            matrix[i][v] += 1

        # Markov model
        # n64 = normal(sig, 8, 32)
        for i in range(0, len(n64)-1):
            src, dst = (n64[i], n64[i+1])
            hmm[i][src][dst] += 1

    n_hmm = [norm_matrix(matrix) for matrix in hmm]
    n_matrix = norm_matrix(matrix)
    if total > 0:
        mean_hist = [(100 * v/total) for v in mean_hist]

    return (n_matrix, n_hmm, mean_hist, total, )
