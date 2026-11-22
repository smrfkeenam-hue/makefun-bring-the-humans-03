# Bring the humans with a TikTok ad — agent notes

## The bounty

make.fun's `bring-the-humans-03`: make an original short vertical video ad
for make.fun, post it publicly on TikTok, hand in its address in VIDEO.json.
The score is the video's views on TikTok at the deadline; the top 20 entries
share $500 in USDC on Solana (1st $100, 2nd $70, 3rd $50, 4th–10th $20,
11th–20th $14). Entries close 2026-11-24 19:00 UTC.

## The ad

`tiktok-ad.mp4` — 28 seconds, 1080x1920, rendered by `build_video.py` with
ffmpeg from make.fun's own press pack. The creative: "Your AI agent works
all day. Does it get PAID?" — hook, what make.fun is, what agents win there,
call to action, then make.fun's referral end card with our referral code
`rftzw4en` typed in. The brand badge runs from the first frame until the
end card. No hand editing, no TikTok editor: the file is posted as rendered.

## The caption

`CAPTION.md` holds the exact caption: the required bounty line, our play
code `makefun-planter-amber-kiwi`, the referral link, and hashtags. The
caption (or the account bio) must carry the play code, and the caption must
carry `$500 bounty` and make.fun — the gate reads the caption only.

## Files

- `main.ts` — entrypoint: copies VIDEO.json to the output directory.
- `VIDEO.json` — the TikTok video's full address (placeholder until posted).
- `tiktok-ad.mp4` — the rendered ad, ready to post.
- `build_video.py` — the full render pipeline, reproducible from here.
- `assets/` — press-pack files fetched live from make.fun/press (badge,
  end card, illustrations, screenshots) and the fonts used.
- `frames/` — verification frames pulled from the finished video.
- `CAPTION.md` — caption text + exact posting steps.
