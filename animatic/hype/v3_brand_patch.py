"""Re-renderiza só a assinatura final da V3 e emenda no vídeo já renderizado (evita refazer 2 min de render).

Uso: FMT=.. (envs da V3) python3 v3_brand_patch.py <v3_FMT_video.mp4> <saida.mp4>
"""
import subprocess, sys
import numpy as np
import filme_v3 as m
from filme import brand
from fx import W, H, FPS

src, dst = sys.argv[1], sys.argv[2]
start = int(round(m.SHOTS[-1][0] * FPS))           # primeiro frame da assinatura
frames = brand(m.TOTAL - start, "Transformando o futuro", "do futebol de base.", "Visite iscout.tech", l2y=.735)
rng = np.random.default_rng(3)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-filter_complex", f"[0:v]trim=end_frame={start},setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1[v]",
                      "-map", "[v]", "-c:v", "libx264", "-crf", "20", "-maxrate", "20M", "-bufsize", "40M", "-preset", "medium", "-pix_fmt", "yuv420p", dst],
                     stdin=subprocess.PIPE)
for im in frames:
    a = np.asarray(im.convert("RGB")).astype(np.float32) + rng.normal(0, 3, (H, W, 1)).astype(np.float32)
    p.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
print(start, len(frames))
