"""Versão pocket da V4 (~44 s) COM a demo inteira, para comparar trilhas. Timeline de 2:17 (com a demo estendida).

Trechos (tempo de filme da V4 2:17), sempre em fronteira de frase da locução:
  0,00–3,10    "Todo talento começa em algum lugar."
  10,75–15,55  "O iSCOUT existe para mudar isso, democratizar o caminho desde cedo."
  40,85–46,65  "São cinco dimensões…" (radar)
  70,96–86,52  demo "iScout Ao Vivo" em tela cheia, inteira ("Cada registro ajuda a mostrar técnica…")
  122,22–128,52 "Mais visibilidade… mais informação… mais transparência…"
  128,52–137,42 assinatura
A música toca contínua (sem emendas) de START até o fim do pocket. O START é escolhido para o final natural da faixa
cair na assinatura. Ganho casado em -18,2 LUFS antes do duck, sidechain sob a voz e loudnorm -14,3 LUFS.

Uso: python3 pocket_v4.py <video V4 2:17 sem áudio> <voz 2:17 (wav)> <musica> <inicio_s> <saida.mp4> [cresc_s]
     cresc_s: crescendo da música na abertura (curva exponencial); padrão 0,3 s
"""
import subprocess, sys

VID, VOZ, MUS, START, OUT = sys.argv[1:6]
START = float(START); CRESC = float(sys.argv[6]) if len(sys.argv) > 6 else .3
SEGS = [(0.0, 3.1), (10.75, 15.55), (40.85, 46.65), (70.96, 86.52), (122.22, 128.52), (128.52, 137.4167)]
dur = sum(b - a for a, b in SEGS)

lu = subprocess.run(["ffmpeg", "-hide_banner", "-i", MUS, "-af", f"atrim=start={START}:end={START + dur},ebur128", "-f", "null", "-"],
                    capture_output=True, text=True).stderr
I = float([ln for ln in lu.splitlines() if ln.strip().startswith("I:")][-1].split()[1])
gain = -18.2 - I

k = len(SEGS)
fc = "".join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];" for i, (a, b) in enumerate(SEGS))
fc += f"[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume=2dB,asplit={k}" + "".join(f"[n{i}]" for i in range(k)) + ";"
fc += "".join(f"[n{i}]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={b-a-0.015}:d=0.015[a{i}];" for i, (a, b) in enumerate(SEGS))
fc += "".join(f"[v{i}]" for i in range(k)) + f"concat=n={k}:v=1:a=0[v];"
fc += "".join(f"[a{i}]" for i in range(k)) + f"concat=n={k}:v=0:a=1[nar];"
fc += (f"[2:a]aresample=48000,atrim=start={START}:end={START + dur},asetpts=PTS-STARTPTS,volume={gain:.2f}dB,"
       f"afade=t=in:d={CRESC}:curve=exp,afade=t=out:st={dur-1.2}:d=1.2[m];"
       "[nar]asplit=2[n][sc];[m][sc]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=450:makeup=1[md];"
       "[md][n]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14.3:TP=-2:LRA=11,aresample=48000,alimiter=limit=0.8:level=false[o]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VID, "-i", VOZ, "-i", MUS, "-filter_complex", fc, "-map", "[v]", "-map", "[o]",
                "-c:v", "libx264", "-crf", "19", "-maxrate", "20M", "-bufsize", "40M", "-preset", "medium", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", OUT], check=True)
print(OUT, round(dur, 2), f"trilha {I:.1f} LUFS -> {gain:+.1f} dB")
