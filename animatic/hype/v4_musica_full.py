"""Trilha alternativa no filme V4 inteiro (2:17): estende a música até a duração do filme e remixa com a locução.

Extensão: a música toca de 0 até J, volta L segundos e segue até o fim (o final natural cai na assinatura).
L é procurado perto de N compassos por correlação da forma de onda em volta de J (emenda na mesma fase), com
crossfade de 80 ms. Opcionalmente atrasa o início (pad) para casar o fim da música com o fim do filme.
Locução: narr3.wav (entra em 0,8 s) com a pausa de EXT s da demo inserida em 76,45 s (como v4_audio.py).
Mix igual aos cortes: trilha a -18,2 LUFS antes do duck, sidechain sob a voz, loudnorm -14,3 LUFS.

Uso: python3 v4_musica_full.py <musica.wav> <narr3.wav> <J_s> <L_alvo_s> <pad_s> <saida.wav> [skip_s] [cresc_s]
     skip_s: ponto da faixa em que a música entra no filme
     cresc_s: crescendo da abertura (volume sobe de -24 dB a 0 dB, linear em dB, nesse tempo; padrão 0,3 s)
     FRASE_EXTRA=arquivo:tempo_filme:ganho_dB  insere uma frase na locução (ex.: a linha sobre a demo)
"""
import subprocess, sys
import numpy as np

SR = 48000; FILM = 137.4167; EXT = 9.92; T_IN = 76.45; NARR_IN = 0.8

def read(path, af=None, ac=2):
    cmd = ["ffmpeg", "-v", "error", "-i", path] + (["-af", af] if af else []) + ["-ac", str(ac), "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, ac).copy()

def find_loop(m, J, L0, span=.25, win=3.0):
    """L em [L0-span, L0+span] que maximiza a correlação entre m[J-L-win : J-L] e m[J-win : J] (mono, 8 kHz)."""
    x = m.mean(1)[::6]; sr = SR / 6
    a = x[int((J - win) * sr):int(J * sr)]
    best = None
    for Ls in np.arange(L0 - span, L0 + span, 1 / sr):
        i = int((J - Ls - win) * sr); b = x[i:i + len(a)]
        c = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
        if best is None or c > best[0]: best = (c, Ls)
    return best

def main(mus, narr, J, L0, pad, out, skip=0, cresc=.3):
    J, L0, pad, skip, cresc = float(J), float(L0), float(pad), float(skip), float(cresc)
    m = read(mus)
    c, L = find_loop(m, J, L0)
    print(f"loop: J={J:.2f}s L={L:.4f}s corr={c:.3f}")
    j, l, xf = int(J * SR), int(L * SR), int(.08 * SR)
    w = np.linspace(0, 1, xf, dtype=np.float32)[:, None]
    head, tail = m[int(skip * SR):j].copy(), m[j - l:].copy()
    tail[:xf] = head[-xf:] * (1 - w) + tail[:xf] * w
    bed = np.concatenate([np.zeros((int(pad * SR), 2), np.float32), head[:-xf], tail])
    n = int(FILM * SR)
    bed = bed[:n] if len(bed) >= n else np.concatenate([bed, np.zeros((n - len(bed), 2), np.float32)])
    fo = int(1.2 * SR); bed[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None]
    fi = int(cresc * SR); x = np.linspace(0, 1, fi, dtype=np.float32)
    bed[:fi] *= (10 ** ((-24 + 24 * x) / 20) * np.minimum(1, x / .02))[:, None]          # crescendo da abertura
    # locução na timeline de 2:17 (pausa da demo inserida)
    v = read(narr, ac=1)[:, 0]
    v = np.concatenate([np.zeros(int(NARR_IN * SR), np.float32), v])
    i0 = int(T_IN * SR)
    v = np.concatenate([v[:i0], np.zeros(int(EXT * SR), np.float32), v[i0:]])
    v = v[:n] if len(v) >= n else np.concatenate([v, np.zeros(n - len(v), np.float32)])
    import os
    if os.environ.get("FRASE_EXTRA"):
        fp, ft, fg = os.environ["FRASE_EXTRA"].rsplit(":", 2)
        e = read(fp, ac=1)[:, 0] * 10 ** (float(fg) / 20); i = int(float(ft) * SR)
        v[i:i + len(e)] += e[:max(0, n - i)]
    tmp = out + ".parts"
    import os; os.makedirs(tmp, exist_ok=True)
    for name, arr, ch in (("bed", bed, 2), ("voz", v[:, None], 1)):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", str(ch), "-i", "-", "-c:a", "pcm_f32le",
                        f"{tmp}/{name}.wav"], input=arr.astype(np.float32).tobytes(), check=True)
    lu = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{tmp}/bed.wav", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float([ln for ln in lu.splitlines() if ln.strip().startswith("I:")][-1].split()[1])
    gain = -18.2 - I
    fc = (f"[0:a]volume={gain:.2f}dB[m];[1:a]pan=stereo|c0=c0|c1=c0,volume=2dB,asplit=2[n][sc];"
          "[m][sc]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=450:makeup=1[md];"
          "[md][n]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14.3:TP=-2:LRA=11,aresample=48000,alimiter=limit=0.8:level=false[o]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{tmp}/bed.wav", "-i", f"{tmp}/voz.wav", "-filter_complex", fc,
                    "-map", "[o]", "-c:a", "pcm_s24le", out], check=True)
    print(f"trilha {I:.1f} LUFS -> ganho {gain:+.1f} dB; saída {out}")

if __name__ == "__main__":
    main(*sys.argv[1:9])
