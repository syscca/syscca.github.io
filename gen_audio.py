# -*- coding: utf-8 -*-
"""为双语启蒙游戏批量生成真人感神经语音 MP3。
来源：微软 edge-tts（zh-CN-XiaoxiaoNeural / id-ID-GadisNeural）。
含：MP3 头校验、失败重试、并发限制、跳过已存在文件。
"""
import os
import sys
import asyncio
import edge_tts

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
os.makedirs(OUT, exist_ok=True)

VOICE_ZH = "zh-CN-XiaoxiaoNeural"   # 温暖自然的中文女声
VOICE_ID = "id-ID-GadisNeural"      # 印尼语女声
RATE = "-8%"                        # 给小朋友放慢一点点
PITCH = "+8Hz"                      # 亲切活泼

# ---------- 词库（与 index.html 保持一致） ----------
DATA = {
    "animals": {
        "items": [
            ("猫", "kucing"), ("狗", "anjing"), ("奶牛", "sapi"),
            ("鸭子", "bebek"), ("小猪", "babi"), ("小鸟", "burung"),
            ("小鱼", "ikan"), ("狮子", "singa"), ("猴子", "monyet"),
            ("大象", "gajah"), ("兔子", "kelinci"), ("青蛙", "katak"),
        ]
    },
    "family": {
        "items": [
            ("爸爸", "ayah"), ("妈妈", "ibu"), ("爷爷", "kakek"),
            ("奶奶", "nenek"), ("哥哥", "kakak laki-laki"),
            ("姐姐", "kakak perempuan"), ("弟弟", "adik laki-laki"),
            ("妹妹", "adik perempuan"), ("叔叔", "paman"),
            ("阿姨", "bibi"), ("宝宝", "bayi"), ("全家福", "keluarga"),
        ]
    },
    "fruits": {
        "items": [
            ("苹果", "apel"), ("香蕉", "pisang"), ("橙子", "jeruk"),
            ("葡萄", "anggur"), ("西瓜", "semangka"), ("草莓", "stroberi"),
            ("梨", "pir"), ("菠萝", "nanas"), ("樱桃", "ceri"), ("柠檬", "lemon"),
        ]
    },
    "vegetables": {
        "items": [
            ("胡萝卜", "wortel"), ("玉米", "jagung"), ("土豆", "kentang"),
            ("番茄", "tomat"), ("茄子", "terung"), ("辣椒", "cabai"),
            ("黄瓜", "timun"), ("西兰花", "brokoli"),
            ("洋葱", "bawang bombay"), ("蘑菇", "jamur"),
            ("生菜", "selada"), ("大蒜", "bawang putih"),
        ]
    },
    "tastes": {
        "items": [
            ("甜甜的", "manis"), ("酸酸的", "asam"), ("苦苦的", "pahit"),
            ("辣辣的", "pedas"), ("咸咸的", "asin"), ("香香的", "harum"),
            ("凉凉的", "dingin"), ("热热的", "panas"),
            ("软软的", "lembut"), ("脆脆的", "renyah"),
        ]
    },
    "colors": {
        "items": [
            ("红色", "merah"), ("黄色", "kuning"), ("蓝色", "biru"),
            ("绿色", "hijau"), ("紫色", "ungu"), ("橙色", "oranye"),
            ("粉色", "merah muda"), ("黑色", "hitam"),
            ("白色", "putih"), ("棕色", "cokelat"),
        ]
    },
    "numbers": {
        "items": [
            ("一", "satu"), ("二", "dua"), ("三", "tiga"), ("四", "empat"),
            ("五", "lima"), ("六", "enam"), ("七", "tujuh"), ("八", "delapan"),
            ("九", "sembilan"), ("十", "sepuluh"),
        ]
    },
    "vehicles": {
        "items": [
            ("小汽车", "mobil"), ("公交车", "bis"), ("出租车", "taksi"),
            ("消防车", "mobil pemadam kebakaran"), ("救护车", "ambulans"),
            ("火车", "kereta api"), ("飞机", "pesawat terbang"),
            ("直升机", "helikopter"), ("轮船", "kapal"),
            ("自行车", "sepeda"), ("摩托车", "sepeda motor"),
            ("热气球", "balon udara"),
        ]
    },
    "professions": {
        "items": [
            ("医生", "dokter"), ("护士", "perawat"), ("警察", "polisi"),
            ("消防员", "pemadam kebakaran"), ("老师", "guru"), ("厨师", "koki"),
            ("农民", "petani"), ("建筑工人", "pekerja bangunan"),
            ("宇航员", "astronot"), ("飞行员", "pilot"),
            ("画家", "pelukis"), ("科学家", "ilmuwan"),
        ]
    },
    "body": {
        "items": [
            ("头", "kepala"), ("头发", "rambut"), ("脸", "wajah"),
            ("眼睛", "mata"), ("鼻子", "hidung"), ("嘴巴", "mulut"),
            ("耳朵", "telinga"), ("牙齿", "gigi"), ("舌头", "lidah"),
            ("小手", "tangan"), ("小脚", "kaki"), ("腿", "tungkai"),
        ]
    },
    "clothes": {
        "items": [
            ("上衣", "baju"), ("裤子", "celana"), ("裙子", "rok"),
            ("外套", "jaket"), ("毛衣", "sweter"), ("袜子", "kaus kaki"),
            ("鞋子", "sepatu"), ("凉鞋", "sandal"), ("帽子", "topi"),
            ("草帽", "topi jerami"), ("围巾", "syal"),
            ("手套", "sarung tangan"),
        ]
    },
    "actions": {
        "items": [
            ("跑一跑", "berlari"), ("跳一跳", "melompat"),
            ("走一走", "berjalan"), ("爬一爬", "merangkak"),
            ("坐下来", "duduk"), ("站起来", "berdiri"),
            ("睡觉觉", "tidur"), ("吃一口", "makan"),
            ("喝一口", "minum"), ("抱一抱", "memeluk"),
            ("拍拍手", "bertepuk tangan"), ("挥挥手", "melambai"),
        ]
    },
    "household": {
        "items": [
            ("杯子", "cangkir"), ("勺子", "sendok"), ("叉子", "garpu"),
            ("筷子", "sumpit"), ("小床", "tempat tidur"), ("椅子", "kursi"),
            ("台灯", "lampu"), ("雨伞", "payung"), ("肥皂", "sabun"),
            ("牙刷", "sikat gigi"), ("闹钟", "jam weker"), ("电视", "televisi"),
        ]
    },
    "daily": {
        "items": [
            ("我要喝水", "saya mau minum"), ("我要吃饭", "saya mau makan"),
            ("我要尿尿", "saya mau pipis"), ("我困了", "saya mengantuk"),
            ("抱抱我", "minta gendong"), ("我爱你", "aku cinta kamu"),
            ("一起玩", "main bersama yuk"), ("没关系", "tidak apa-apa"),
            ("给你", "ini untukmu"), ("我要这个", "saya mau ini"),
            ("晚安", "selamat tidur"), ("你好棒", "kamu hebat"),
            ("帮我打开", "tolong buka"), ("我要大便", "saya mau pup"),
            ("等一下", "tunggu sebentar"), ("真好吃", "enak sekali"),
        ]
    },
    "weather": {
        "items": [
            ("太阳", "matahari"), ("月亮", "bulan"), ("星星", "bintang"),
            ("白云", "awan"), ("下雨", "hujan"), ("打雷", "guntur"),
            ("彩虹", "pelangi"), ("下雪", "salju"), ("刮风", "berangin"),
            ("晴天", "cerah"), ("闪电", "petir"), ("夜晚", "malam hari"),
        ]
    },
}

# (文件名, 文本, 语言)
tasks = []

# 1) 单词：纯朗读 + 问答整句（整句韵律更自然）
for cat, info in DATA.items():
    for i, (zh, wid) in enumerate(info["items"]):
        tasks.append((f"{cat}-{i}-zh.mp3", zh, "zh"))
        tasks.append((f"{cat}-{i}-id.mp3", wid, "id"))
        tasks.append((f"{cat}-{i}-askzh.mp3", f"{zh}在哪里呀？", "zh"))
        tasks.append((f"{cat}-{i}-askid.mp3", f"Di mana {wid}?", "id"))

# 2) 游戏提示语
ui_clips = [
    ("praise-0-zh", "真棒！", "zh"),
    ("praise-1-zh", "太好啦！", "zh"),
    ("praise-2-zh", "答对了！", "zh"),
    ("praise-3-zh", "好聪明！", "zh"),
    ("praise-0-id", "Hebat!", "id"),
    ("praise-1-id", "Bagus sekali!", "id"),
    ("praise-2-id", "Pintar sekali!", "id"),
    ("praise-3-id", "Mantap!", "id"),
    ("try-0-zh", "再试一次", "zh"),
    ("try-1-zh", "没关系，再试试", "zh"),
    ("try-0-id", "Coba lagi ya", "id"),
    ("try-1-id", "Coba sekali lagi", "id"),
    ("finish-zh", "你太厉害啦！", "zh"),
    ("finish-id", "Luar biasa! Pintar sekali!", "id"),
    ("tap-zh", "点一点，跟我读", "zh"),
    ("tap-id", "Ketuk dan ulangi", "id"),
]
for name, text, lang in ui_clips:
    tasks.append((f"{name}.mp3", text, lang))

# 3) 情景对话游戏：角色台词 + 应答短语 + 通关祝贺
chat_lines = [
    ("你好呀！", "Halo teman!"),
    ("早上好，宝贝！", "Selamat pagi, sayang!"),
    ("这个送给你！", "Ini untukmu!"),
    ("哎哟！", "Aduh!"),
    ("明天见！", "Sampai jumpa besok!"),
]
for i, (zh, wid) in enumerate(chat_lines):
    tasks.append((f"chat-c{i}-zh.mp3", zh, "zh"))
    tasks.append((f"chat-c{i}-id.mp3", wid, "id"))

chat_responses = [
    ("hello", "你好！", "Halo!"),
    ("bye", "再见！", "Dadah!"),
    ("morning", "早上好！", "Selamat pagi!"),
    ("thanks", "谢谢！", "Terima kasih!"),
    ("sorry", "对不起！", "Maaf!"),
]
for key, zh, wid in chat_responses:
    tasks.append((f"chat-r-{key}-zh.mp3", zh, "zh"))
    tasks.append((f"chat-r-{key}-id.mp3", wid, "id"))

tasks.append(("chatfinish-zh.mp3", "你会打招呼啦，真棒！", "zh"))
tasks.append(("chatfinish-id.mp3", "Kamu sudah bisa menyapa, hebat!", "id"))

# 4) 第二组情景对话「我会说日常」
chat2_lines = [
    ("一起玩好不好？", "Main bersama, yuk?"),
    ("肚子饿了吗？", "Kamu sudah lapar?"),
    ("口渴了吧？", "Haus ya?"),
    ("该睡觉啦！", "Saatnya tidur!"),
    ("来，抱抱！", "Ayo, minta gendong!"),
]
for i, (zh, wid) in enumerate(chat2_lines):
    tasks.append((f"chat2-c{i}-zh.mp3", zh, "zh"))
    tasks.append((f"chat2-c{i}-id.mp3", wid, "id"))

chat2_responses = [
    ("ok", "好呀好呀！", "Boleh, yuk!"),
    ("eat", "我要吃饭！", "Saya mau makan!"),
    ("drink", "我要喝水！", "Saya mau minum!"),
    ("night", "晚安！", "Selamat tidur!"),
    ("hug", "抱抱！", "Minta gendong!"),
]
for key, zh, wid in chat2_responses:
    tasks.append((f"chat2-r-{key}-zh.mp3", zh, "zh"))
    tasks.append((f"chat2-r-{key}-id.mp3", wid, "id"))

tasks.append(("chat2finish-zh.mp3", "日常用语我会说，真棒！", "zh"))
tasks.append(("chat2finish-id.mp3", "Sudah bisa bahasa sehari-hari, hebat!", "id"))


def valid_mp3(path):
    """校验：文件存在、够大、以 ID3 或 MPEG 帧同步字开头。"""
    try:
        if os.path.getsize(path) < 2400:
            return False
        with open(path, "rb") as f:
            head = f.read(3)
        return head[:3] == b"ID3" or head[0] == 0xFF and (head[1] & 0xE0) == 0xE0
    except OSError:
        return False


async def synth_one(fname, text, lang, sem, retries=3):
    path = os.path.join(OUT, fname)
    if os.path.exists(path) and valid_mp3(path):
        return fname, "skip"
    voice = VOICE_ZH if lang == "zh" else VOICE_ID
    async with sem:
        for attempt in range(1, retries + 1):
            try:
                communicate = edge_tts.Communicate(
                    text, voice=voice, rate=RATE, pitch=PITCH
                )
                await communicate.save(path)
                if valid_mp3(path):
                    return fname, "ok"
            except Exception as e:  # noqa: BLE001
                last = repr(e)
                await asyncio.sleep(0.8 * attempt)
    return fname, f"FAIL (last={last})"


async def main():
    sem = asyncio.Semaphore(4)
    results = await asyncio.gather(*[synth_one(*t, sem) for t in tasks])
    ok = sum(1 for _, s in results if s in ("ok", "skip"))
    fails = [(n, s) for n, s in results if s not in ("ok", "skip")]
    for n, s in results:
        if s not in ("ok", "skip"):
            print("FAILED:", n, s)
    print(f"TOTAL={len(tasks)} OK={ok} FAIL={len(fails)}")
    if fails:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
