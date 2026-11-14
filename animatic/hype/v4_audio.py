"""Áudio da V4 com a demo estendida: mix da V3 até logo antes de "Com o tempo," + EXT s só de trilha + resto do mix.

O trecho inserido repete os 5 compassos da trilha que acabaram de tocar (a trilha está alinhada ao filme: offset
medido de 0,01 s), então as duas emendas caem na mesma fase do compasso. Ganho casado com o nível da trilha no mix
(~0,66 da trilha pura logo antes da emenda, ~0,8 sem voz), com rampas e crossfade de 60 ms nas emendas.

Uso: python3 v4_audio.py <mix V3 (wav/mp4)> <music.mp3> <saida.wav>
"""
import subprocess, sys
import numpy as np

SR = 48000
EXT = 9.92                  # igual a filme_v4.EXT
T_IN = 76.45                # tempo de filme da emenda (a voz volta em 76,6 + EXT)
G_EDGE, G_MID = .66, .80

def read(path, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path] + (["-af", af] if af else []) + ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()

def main(mix, music, out):
    a = read(mix); mu = read(music, "atempo=0.9681")
    i0, n = int(T_IN * SR), int(EXT * SR)
    mid = mu[i0 - n:i0].copy()
    t = np.arange(n) / SR
    g = np.full(n, G_MID, np.float32)
    up, dn = t < 1.0, t > EXT - .8
    g[up] = G_EDGE + (G_MID - G_EDGE) * (t[up] / 1.0)
    g[dn] = G_EDGE + (G_MID - G_EDGE) * ((EXT - t[dn]) / .8)
    mid *= g[:, None]
    xf = int(.06 * SR); w = np.linspace(0, 1, xf, dtype=np.float32)[:, None]
    head, tail = a[:i0].copy(), a[i0:].copy()
    mid[:xf] = head[-xf:] * (1 - w) + mid[:xf] * w          # emenda 1: mix -> trilha
    tail[:xf] = mid[-xf:] * (1 - w) + tail[:xf] * w          # emenda 2: trilha -> mix
    y = np.concatenate([head[:-xf], mid, tail])
    pk = np.abs(y).max()
    if pk > .89: y *= .89 / pk
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s16le", out],
                   input=y.astype(np.float32).tobytes(), check=True)
    print(len(y) / SR, "s, pico", round(float(np.abs(y).max()), 3))

if __name__ == "__main__":
    main(*sys.argv[1:4])
