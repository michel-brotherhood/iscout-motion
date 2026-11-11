"""Cortes de 30 s e 15 s da V3 a partir do render completo (mesmos quadros, legendas e locução).

Cada trecho começa e termina em fronteira de frase da locução (tempos da transcrição palavra a palavra),
então a narração nunca é cortada no meio. A trilha é o final da trilha da V3 (pega o drop e o fecho na
assinatura), com duck sob a voz.

Uso: python3 cortes_v3.py <out/v3> <out/v3/narr3.wav>   (narr3 = locução com o CTA "Visite nosso site…")
"""
import os, subprocess, sys

V3, NARR = sys.argv[1], sys.argv[2]
NARR_IN = 0.8
# trechos em tempo de FILME (s): (início, fim)
CUTS = {
    "30": [(0.0, 3.1),        # Todo talento começa em algum lugar.
           (10.75, 15.55),     # O iSCOUT existe para mudar isso, democratizar o caminho desde cedo.
           (40.85, 46.65),    # São cinco dimensões: técnica, tática, física, resiliência e potencial. (radar)
           (112.3, 118.6),    # Mais visibilidade… mais informação… mais transparência…
           (118.6, 127.5)],   # assinatura: iSCOUT, transformando o futuro do futebol de base. Explore nosso app!
    "15": [(0.0, 3.1),
           (13.2, 15.55),      # democratizar o caminho desde cedo.
           (118.6, 127.5)],
}

def run(*a): subprocess.run(a, check=True)

for cut, segs in CUTS.items():
    dur = sum(b - a for a, b in segs)
    for fmt, tag in (("239", "239"), ("169", "16x9")):
        src = os.path.join(V3, f"v3_{fmt}_video.mp4")
        vf = "".join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];" for i, (a, b) in enumerate(segs))
        # locução no tempo do filme (entra em NARR_IN), cortada nos mesmos trechos, com 15 ms de fade nas emendas
        af = f"[1:a]adelay={int(NARR_IN*1000)}|{int(NARR_IN*1000)},apad=whole_dur=128,aresample=48000,pan=stereo|c0=c0|c1=c0,volume=2dB,asplit={len(segs)}" + \
             "".join(f"[n{i}]" for i in range(len(segs))) + ";" + \
             "".join(f"[n{i}]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={b-a-0.015}:d=0.015[a{i}];" for i, (a, b) in enumerate(segs))
        fc = vf + af + "".join(f"[v{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=0[v];" + \
             "".join(f"[a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1[nar];" + \
             f"[2:a]atempo=0.9681,aresample=48000,atrim=start={127.5-dur}:end=127.5,asetpts=PTS-STARTPTS,volume=-6dB,afade=t=in:d=0.6,afade=t=out:st={dur-1.5}:d=1.5[m];" + \
             "[nar]asplit=2[n][sc];[m][sc]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=450:makeup=1[md];" + \
             "[md][n]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14.3:TP=-2:LRA=11,aresample=48000,alimiter=limit=0.8:level=false[o]"
        out = os.path.join(V3, "entregas", f"iSCOUT_V3_{cut}s_{tag}.mp4")
        run("ffmpeg", "-v", "error", "-y", "-i", src, "-i", NARR, "-i", os.path.join(V3, "music.mp3"), "-filter_complex", fc,
            "-map", "[v]", "-map", "[o]", "-c:v", "libx264", "-crf", "21", "-maxrate", "20M", "-bufsize", "40M", "-preset", "medium",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out)
        run("ffmpeg", "-v", "error", "-y", "-i", out, "-vf", "scale=1280:-2", "-c:v", "libx264", "-crf", "26", "-maxrate", "3M", "-bufsize", "6M",
            "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out.replace(".mp4", "_whatsapp.mp4"))
        print(out, round(dur, 2))
