"""
generate_video.py

Gera um vídeo MP4 estilo "Matrix" (queda de código) com os nomes das ferramentas orbitando
o personagem, a partir de uma imagem base.

Uso:
python generate_video.py --input assets/SEU_ARQUIVO.png --output output.mp4 --duration 30

Dependências:
pip install moviepy imageio imageio-ffmpeg numpy

Observação: é recomendado ter ffmpeg instalado no sistema.
"""
import argparse
import os
import math
import random
from moviepy.editor import (ImageClip, TextClip, CompositeVideoClip, ColorClip, VideoFileClip)
import numpy as np

def falling_code_clips(w, h, duration, fps=24, n_streams=60):
    """Cria várias pequenas faixas de texto que caem do topo ao longo do tempo, simulando 'Matrix'."""
    clips = []
    chars = "01ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()-_=+[]{};:,.<>/?\\|"
    for i in range(n_streams):
        x = random.randint(0, w)
        start_t = random.uniform(0, duration*0.8)
        stream_len = random.randint(10, 35)
        speed = random.uniform(h/ (duration*0.5), h / (duration*0.2))
        txt = "".join(random.choice(chars) for _ in range(stream_len))
        fontsize = random.randint(10, 20)
        txtclip = (TextClip(txt, font="Arial-Bold", fontsize=fontsize, color=(0,255,0))
                   .set_start(start_t)
                   .set_pos(lambda t, x=x, speed=speed, start_t=start_t: (x, (t - start_t) * speed if t>=start_t else -100))
                   .set_duration(duration - start_t + 0.1)
                   .crossfadein(0.1)
                   .set_opacity(0.6))
        clips.append(txtclip)
    return clips

def orbiting_text_clips(center, radius, tool_names, duration, w, h, fps=24):
    """Cria clipes de texto que orbitam ao redor de um centro."""
    clips = []
    cx, cy = center
    per = duration / len(tool_names)  # time between each starting 'lock' motion
    for idx, name in enumerate(tool_names):
        ang_offset = random.uniform(0, 2*math.pi)
        txt = TextClip(name, fontsize=40, font="Arial-Bold", color="white").set_duration(duration)
        # define a position function that orbits slowly and then eases to a fixed spot
        def make_pos(ang_offset=ang_offset, idx=idx):
            def pos(t):
                # slow angular motion
                omega = 0.7  # radians per second
                angle = ang_offset + omega * t + idx * 0.7
                x = cx + radius * math.cos(angle)
                y = cy + radius * math.sin(angle) * 0.7
                return (x - txt.w/2, y - txt.h/2)
            return pos
        txt = txt.set_pos(make_pos()).set_opacity(0.95)
        clips.append(txt)
    return clips

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Imagem base (assets/...)")
    parser.add_argument("--output", default="output.mp4", help="Arquivo de saída MP4")
    parser.add_argument("--duration", type=float, default=30.0, help="Duração em segundos")
    parser.add_argument("--fps", type=int, default=24, help="FPS de saída")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Imagem não encontrada: {args.input}")

    # Carrega imagem base
    bg = ImageClip(args.input).set_duration(args.duration)

    w, h = bg.size
    # Create falling code clips
    code_clips = falling_code_clips(w, h, args.duration, fps=args.fps, n_streams=70)

    # Orbiting tool names (positions around character)
    # User should adjust center/radius as needed. We'll guess center near middle-left.
    center = (w * 0.58, h * 0.48)
    radius = min(w, h) * 0.28
    tool_names = ["ChatGPT", "Copilot", "Midjourney", "Leonardo AI", "Eventlabs", "Canva"]
    orbit_clips = orbiting_text_clips(center, radius, tool_names, args.duration, w, h, fps=args.fps)

    # Title clips: appear at start and end
    title_start = (TextClip("Alquimistas da Informação", fontsize=70, font="Arial-Bold", color="#b7f58a")
                   .set_duration(4)
                   .set_pos("center")
                   .crossfadein(0.5)
                   .set_opacity(0.95))
    title_end = (TextClip("Alquimistas da Informação", fontsize=70, font="Arial-Bold", color="#b7f58a")
                 .set_duration(4)
                 .set_start(args.duration - 4)
                 .set_pos("center")
                 .crossfadein(0.5)
                 .set_opacity(1.0))

    # Composite all clips
    all_clips = [bg] + code_clips + orbit_clips + [title_start, title_end]
    comp = CompositeVideoClip(all_clips, size=(w, h)).set_duration(args.duration)
    # Slight color enhancement: overlay a transparent teal color to match Matrix tone
    overlay = ColorClip(size=(w,h), color=(0,30,0)).set_opacity(0.08).set_duration(args.duration)
    final = CompositeVideoClip([comp, overlay]).set_duration(args.duration)

    # Write output
    print("Renderizando vídeo... isso pode demorar dependendo do seu hardware.")
    final.write_videofile(args.output, fps=args.fps, codec="libx264", threads=4, preset="medium")
    print("Pronto:", args.output)

if __name__ == "__main__":
    main()
