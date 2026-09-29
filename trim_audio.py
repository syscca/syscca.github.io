# -*- coding: utf-8 -*-
"""裁剪 audio/ 下全部 MP3 的首尾静音，词内停顿保留。"""
import os
import glob
import subprocess
import concurrent.futures

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(HERE, "audio")
TMP_DIR = os.path.join(HERE, "audio_trim_tmp")
os.makedirs(TMP_DIR, exist_ok=True)

FILTER = (
    "silenceremove=start_periods=1:start_silence=0.06:start_threshold=-40dB,"
    "areverse,"
    "silenceremove=start_periods=1:start_silence=0.14:start_threshold=-40dB,"
    "areverse"
)

def trim_one(path):
    name = os.path.basename(path)
    tmp = os.path.join(TMP_DIR, name)
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", path, "-af", FILTER,
        "-codec:a", "libmp3lame", "-q:a", "4", tmp,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(tmp) or os.path.getsize(tmp) < 1500:
        return name, "FAIL", r.stderr[-200:]
    os.replace(tmp, path)
    return name, "ok", os.path.getsize(path)

def main():
    files = sorted(glob.glob(os.path.join(AUDIO_DIR, "*.mp3")))
    fails = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for name, status, info in ex.map(trim_one, files):
            if status != "ok":
                fails += 1
                print("FAILED:", name, info)
    try:
        os.rmdir(TMP_DIR)
    except OSError:
        pass
    print(f"TRIMMED={len(files)} FAIL={fails}")

if __name__ == "__main__":
    main()
