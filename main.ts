// Entry point for the bring-the-humans-03 TikTok ad entry.
//
// The entry is a video posted on TikTok; this program's only job is to hand
// its address to the grader. It copies VIDEO.json from the repository root
// to the output directory, byte for byte. The house reads the video itself
// from TikTok -- nothing this program writes about the video counts.
//
// Before copying, it checks the file is valid JSON with a url string, so a
// malformed VIDEO.json fails loudly here instead of at the gate.
import { copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "out";
const source = join(here, "VIDEO.json");

if (!existsSync(source)) {
  throw new Error(`VIDEO.json not found at ${source}`);
}
const parsed = JSON.parse(readFileSync(source, "utf-8")) as unknown;
if (typeof parsed !== "object" || parsed === null || !("url" in parsed) ||
    typeof (parsed as { url: unknown }).url !== "string") {
  throw new Error("VIDEO.json must be an object with a string 'url'");
}

mkdirSync(outDir, { recursive: true });
copyFileSync(source, join(outDir, "VIDEO.json"));
console.log(`VIDEO.json -> ${join(outDir, "VIDEO.json")}`);
