"""Teste de trilhas (geração Z): o corte de 30 s da V4 com outra música, mesma locução e mesma mixagem.

Mesmos trechos, locução e duck do cortes_v3.py; só a trilha muda. O trecho da música é escolhido para o pico cair
num momento-chave do corte, e o ganho é casado com o loudness da trilha atual no corte (-18,2 LUFS antes do duck),
para a comparação entre as músicas ser justa.

Uso: python3 teste_musica.py <video sem áudio (timeline 2:07)> <narr3.wav> <musica> <inicio_s> <ganho_dB> <saida.mp4>
"""
import subprocess, sys

VID, NARR, MUS, START, GAIN, OUT = sys.argv[1:7]
START, GAIN = float(START), float(GAIN)
NARR_IN = 0.8
SEGS = [(0.0, 3.1), (10.75, 15.55), (40.85, 46.65), (112.3, 118.6), (118.6, 127.5)]   # corte de 30 s (cortes_v3.py)
dur = sum(b - a for a, b in SEGS)

vf = "".join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];" for i, (a, b) in enumerate(SEGS))
af = f"[1:a]adelay={int(NARR_IN*1000)}|{int(NARR_IN*1000)},apad=whole_dur=128,aresample=48000,pan=stereo|c0=c0|c1=c0,volume=2dB,asplit={len(SEGS)}" + \
     "".join(f"[n{i}]" for i in range(len(SEGS))) + ";" + \
     "".join(f"[n{i}]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={b-a-0.015}:d=0.015[a{i}];" for i, (a, b) in enumerate(SEGS))
fc = vf + af + "".join(f"[v{i}]" for i in range(len(SEGS))) + f"concat=n={len(SEGS)}:v=1:a=0[v];" + \
     "".join(f"[a{i}]" for i in range(len(SEGS))) + f"concat=n={len(SEGS)}:v=0:a=1[nar];" + \
     f"[2:a]aresample=48000,atrim=start={START}:end={START + dur},asetpts=PTS-STARTPTS,volume={GAIN}dB,afade=t=in:d=0.4,afade=t=out:st={dur-1.5}:d=1.5[m];" + \
     "[nar]asplit=2[n][sc];[m][sc]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=450:makeup=1[md];" + \
     "[md][n]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14.3:TP=-2:LRA=11,aresample=48000,alimiter=limit=0.8:level=false[o]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VID, "-i", NARR, "-i", MUS, "-filter_complex", fc, "-map", "[v]", "-map", "[o]",
                "-c:v", "libx264", "-crf", "21", "-maxrate", "20M", "-bufsize", "40M", "-preset", "medium", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", OUT], check=True)
print(OUT, round(dur, 2))
