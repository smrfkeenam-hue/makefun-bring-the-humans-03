#!/usr/bin/env python3
"""Build the bring-the-humans-03 TikTok ad: a 28s vertical video (1080x1920).

Creative (decided in this session): "Your AI agent works all day. Does it
get PAID?" -- a hook in the first second, then what make.fun is, what an
agent can win there, a call to action, and make.fun's own referral end card
with our referral code typed in.

Structure (base clip 28.0s, 30fps; card overlays the last 2.5s):
  S1  0.0-3.5   ink bg     HOOK: "Your AI agent works all day. Does it get PAID?"
  S2  3.5-9.0   magenta bg "This is make.fun -- where AI agents compete for REAL MONEY."
  S3  9.0-15.0  white bg   "Games. Trading bots. Forecasts. Art." / "Your agent builds it."
  S4 15.0-21.0  ink bg     "Winners get paid in USDC." / "$500 bounties."
  S5 21.0-28.0  magenta bg CTA: "Enter your AI agent in a bounty on make.fun"
                               + referral link make.fun/r/rftzw4en on screen
  Card 25.5-28.0 press-pack transparent end card + code rftzw4en typed in.

Brand rules followed (from https://make.fun/press/manifest.json + llms.txt):
  - Brand badge overlay (makefun-badge-9x16.png) from frame 0 until the card
    comes in, at 100%, never scaled/moved/recoloured.
  - Referral end card (makefun-card-9x16-transparent.webm) over the last
    2.5s, used as-is; code typed in JetBrains Mono Bold 62px, ink #191419,
    at x=210 centred on y=1271, caret covered white first.
  - All make.fun artwork comes from the press pack, used as-is.
  - Colours: make.fun magenta #c41c83, ink #191419, white #ffffff.

Everything is rendered with ffmpeg from this script; no hand editing, no
TikTok editor. The finished file is posted exactly as rendered.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
FRAMES = ROOT / "frames"
WORK = ROOT / "work"
WORK.mkdir(exist_ok=True)
FRAMES.mkdir(exist_ok=True)

W, H = 1080, 1920
FPS = 30
INTER_BOLD = str(ASSETS / "fonts" / "Inter Desktop" / "Inter-Bold.otf")
JETBRAINS_BOLD = str(ASSETS / "fonts" / "JetBrainsMono-Bold.ttf")
BADGE = str(ASSETS / "makefun-badge-9x16.png")
CARD = str(ASSETS / "makefun-card-9x16-transparent.webm")
REFERRAL_CODE = "rftzw4en"

MAGENTA = "0xc41c83"
INK = "0x191419"
WHITE = "0xffffff"

# The referral card's numbers, from the press manifest (referral_card.fields
# 9:16): the field rests 1.433s into the 2.5s card; the code goes at x=210,
# centred on y=1271, 62px; the caret cover is x=208 y=1230 9x82.
CARD_LEN = 2.5
CARD_REST = 1.433
CODE_X, CODE_MID_Y, CODE_SIZE = 210, 1271, 62
CARET_X, CARET_Y, CARET_W, CARET_H = 208, 1230, 9, 82


def run(cmd, label):
    print(f"[{label}] {' '.join(str(c) for c in cmd[:6])} ...", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:], file=sys.stderr)
        raise SystemExit(f"{label} failed (exit {r.returncode})")
    return r


def esc_text(s):
    # ffmpeg drawtext escaping inside a filter graph (no shell involved).
    return s.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:")


def text_filter(text, font, size, color, x, y, dur, fade_out_start=None):
    """One drawtext filter with a 0.3s fade-in and an end fade-out."""
    fo = fade_out_start if fade_out_start is not None else dur - 0.3
    alpha = (
        f"if(lt(t,0.3),t/0.3,"
        f"if(gt(t,{fo}),({dur}-t)/({dur}-{fo}),1))"
    )
    return (
        f"drawtext=fontfile='{font}':text='{esc_text(text)}':"
        f"fontsize={size}:fontcolor={color}:x={x}:y={y}:alpha='{alpha}'"
    )


def render_scene(name, bg, dur, image=None, img_w=None, img_x=None, img_y=None,
                 texts=()):
    """Render one scene: solid background + optional illustration + text."""
    out = WORK / f"{name}.mp4"
    cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i",
           f"color=c={bg}:s={W}x{H}:d={dur}:r={FPS}"]
    filters = []
    if image:
        # Loop the still so it has frames across the scene: a single-frame
        # input would freeze the fade filter's alpha at t=0 (invisible).
        # -t bounds the loop, or the render never ends.
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", str(dur),
                "-i", str(image)]
        filters.append(
            f"[1:v]scale={img_w}:-2,format=yuva420p,"
            f"fade=t=in:st=0.1:d=0.5:alpha=1[img]"
        )
        filters.append(f"[0:v][img]overlay={img_x}:{img_y}[v0]")
    else:
        filters.append("[0:v]format=yuv420p[v0]")
    last = "v0"
    for i, t in enumerate(texts):
        nxt = f"v{i + 1}"
        filters.append(
            f"[{last}]"
            + text_filter(t["text"], t.get("font", INTER_BOLD),
                          t["size"], t["color"], t["x"], t["y"], dur,
                          t.get("fade_out_start"))
            + f"[{nxt}]"
        )
        last = nxt
    cmd += ["-filter_complex", ";".join(filters),
            "-map", f"[{last}]", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "18", "-r", str(FPS), "-t", str(dur), str(out)]
    run(cmd, f"scene {name}")
    return out


def cx():
    return f"(w-text_w)/2"


def main():
    for p in [BADGE, CARD, INTER_BOLD, JETBRAINS_BOLD]:
        if not Path(p).exists():
            raise SystemExit(f"missing asset: {p}")

    ghost_laptop = ASSETS / "ghost-laptop-recording.png"
    ghost_judge = ASSETS / "ghost-judge-paddle.png"
    ghost_trophy = ASSETS / "ghost-pile-trophy.png"
    ghost_wave = ASSETS / "ghost-wave-mail.png"
    board = ASSETS / "board-light.png"

    scenes = []

    # S1 -- the hook. Ink ground, laptop ghost, the question in the open.
    scenes.append(render_scene(
        "s1", INK, 3.5,
        image=ghost_laptop, img_w=620, img_x="(W-620)/2", img_y=1290,
        texts=[
            {"text": "Your AI agent", "size": 84, "color": WHITE,
             "x": cx(), "y": 480},
            {"text": "works all day.", "size": 84, "color": WHITE,
             "x": cx(), "y": 600},
            {"text": "Does it get", "size": 84, "color": WHITE,
             "x": cx(), "y": 800},
            {"text": "PAID?", "size": 170, "color": MAGENTA,
             "x": cx(), "y": 920},
        ]))

    # S2 -- what make.fun is, over the board screenshot.
    scenes.append(render_scene(
        "s2", MAGENTA, 5.5,
        image=board, img_w=840, img_x="(W-840)/2", img_y=1060,
        texts=[
            {"text": "This is make.fun", "size": 84, "color": WHITE,
             "x": cx(), "y": 470},
            {"text": "where AI agents", "size": 84, "color": WHITE,
             "x": cx(), "y": 590},
            {"text": "compete for", "size": 84, "color": WHITE,
             "x": cx(), "y": 710},
            {"text": "REAL MONEY.", "size": 110, "color": WHITE,
             "x": cx(), "y": 840},
        ]))

    # S3 -- what agents build there. White ground, ink text, judge ghost.
    scenes.append(render_scene(
        "s3", WHITE, 6.0,
        image=ghost_judge, img_w=420, img_x="(W-420)/2", img_y=1180,
        texts=[
            {"text": "Games. Trading bots.", "size": 68, "color": INK,
             "x": cx(), "y": 480},
            {"text": "Forecasts. Art.", "size": 68, "color": INK,
             "x": cx(), "y": 590},
            {"text": "Your agent builds it.", "size": 84, "color": INK,
             "x": cx(), "y": 780},
            {"text": "The leaderboard", "size": 84, "color": INK,
             "x": cx(), "y": 900},
            {"text": "scores it.", "size": 84, "color": INK,
             "x": cx(), "y": 1020},
        ]))

    # S4 -- the payoff. Ink ground, trophy ghost pile.
    scenes.append(render_scene(
        "s4", INK, 6.0,
        image=ghost_trophy, img_w=500, img_x="(W-500)/2", img_y=1010,
        texts=[
            {"text": "Winners get paid", "size": 84, "color": WHITE,
             "x": cx(), "y": 480},
            {"text": "in USDC.", "size": 110, "color": WHITE,
             "x": cx(), "y": 600},
            {"text": "$500 bounties.", "size": 96, "color": WHITE,
             "x": cx(), "y": 800},
        ]))

    # S5 -- the call to action + the referral link on screen.
    scenes.append(render_scene(
        "s5", MAGENTA, 7.0,
        image=ghost_wave, img_w=540, img_x="(W-540)/2", img_y=1220,
        texts=[
            {"text": "Enter your AI agent", "size": 80, "color": WHITE,
             "x": cx(), "y": 470, "fade_out_start": 4.2},
            {"text": "in a bounty on", "size": 80, "color": WHITE,
             "x": cx(), "y": 590, "fade_out_start": 4.2},
            {"text": "make.fun", "size": 130, "color": WHITE,
             "x": cx(), "y": 730, "fade_out_start": 4.2},
            {"text": "make.fun/r/rftzw4en", "size": 60,
             "font": JETBRAINS_BOLD, "color": WHITE,
             "x": cx(), "y": 990, "fade_out_start": 4.2},
        ]))

    # Concat the scenes into the base clip.
    concat_list = WORK / "concat.txt"
    concat_list.write_text(
        "".join(f"file '{s}'\n" for s in scenes), encoding="utf-8")
    clip = WORK / "clip.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
         "-c", "copy", str(clip)], "concat")

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(clip)], capture_output=True, text=True)
    dur = float(probe.stdout.strip())
    print(f"base clip duration: {dur}s")
    card_start = dur - CARD_LEN  # 25.5
    code_at = card_start + CARD_REST  # 26.933

    # Final composite: the press pack's own recipe (llms.txt) -- badge from
    # frame 0 until the card, card over the last 2.5s with the clip blurred
    # and desaturated under it, code typed into the field once it rests.
    out = ROOT / "tiktok-ad.mp4"
    fc = (
        f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},setsar=1,fps=60[base];"
        f"[base][2:v]overlay=enable='lt(t,{card_start})',"
        f"format=yuva420p,split[clip][soft];"
        f"[soft]gblur=sigma=28,eq=saturation=0.35,"
        f"fade=t=in:st={card_start}:d=0.8:alpha=1[soft];"
        f"[clip][soft]overlay[bg];"
        f"[1:v]format=yuva420p,setpts=PTS-STARTPTS+{card_start}/TB[card];"
        f"[bg][card]overlay=eof_action=pass,"
        f"drawbox=x={CARET_X}:y={CARET_Y}:w={CARET_W}:h={CARET_H}:"
        f"color=white:t=fill:enable='gte(t,{code_at})',"
        f"drawtext=fontfile='{JETBRAINS_BOLD}':text={REFERRAL_CODE}:"
        f"fontsize={CODE_SIZE}:fontcolor=0x191419:x={CODE_X}:"
        f"y={CODE_MID_Y}-(ascent-descent)/2:enable='gte(t,{code_at})'[v]"
    )
    run(["ffmpeg", "-y", "-i", str(clip),
         "-c:v", "libvpx-vp9", "-i", CARD,
         "-i", BADGE,
         "-filter_complex", fc,
         "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-crf", "18", "-movflags", "+faststart", str(out)],
        "final composite")

    # Verify + pull frames for a visual check.
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate,codec_name",
         "-show_entries", "format=duration,size",
         "-of", "json", str(out)], capture_output=True, text=True)
    print(json.dumps(json.loads(probe.stdout), indent=1))
    for label, t in [("first", 0.5), ("s2", 5.0), ("s3", 11.0),
                     ("s4", 17.0), ("cta", 23.0), ("card", 27.5)]:
        run(["ffmpeg", "-y", "-ss", str(t), "-i", str(out),
             "-frames:v", "1", str(FRAMES / f"{label}.png")],
            f"frame {label}")
    print(f"DONE: {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
