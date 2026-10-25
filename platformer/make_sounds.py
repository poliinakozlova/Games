# генерація звуків через pydub
import math
import os
import warnings

warnings.filterwarnings("ignore", message="Couldn't find ffmpeg")  # для wav ffmpeg не потрібен
from pydub import AudioSegment
from pydub.generators import Sine, Triangle, WhiteNoise, SignalGenerator

from settings import SND_DIR
from sounds import SOUND_FILES, MUSIC_FILE

RATE = 22050


class Sweep(SignalGenerator):
    # тон з плавною зміною частоти
    def __init__(self, f_start, f_end, duration_ms, wave="sine"):
        super().__init__(sample_rate=RATE)
        self.f_start, self.f_end = f_start, f_end
        self.length = int(RATE * duration_ms / 1000)
        self.wave = wave

    def generate(self):
        phase, i = 0.0, 0
        while True:
            t = min(i / self.length, 1.0)
            phase += (self.f_start + (self.f_end - self.f_start) * t) / self.sample_rate
            p = phase % 1.0
            if self.wave == "triangle":
                yield 4 * abs(p - 0.5) - 1
            elif self.wave == "square":
                yield 1.0 if p < 0.5 else -1.0
            else:
                yield math.sin(2 * math.pi * p)
            i += 1


def note(midi):
    # номер ноти midi -> частота в гц
    return 440 * 2 ** ((midi - 69) / 12)


def silence():
    return AudioSegment.silent(duration=0, frame_rate=RATE)


def tone(freq, ms, wave=Sine, volume=-12):
    return wave(freq, sample_rate=RATE).to_audio_segment(duration=ms, volume=volume)


def sweep(f_start, f_end, ms, wave="sine", volume=-12):
    return Sweep(f_start, f_end, ms, wave).to_audio_segment(duration=ms, volume=volume)


def pluck(freq, ms, volume=-12):
    # нота музичної скриньки
    seg = tone(freq, ms, Sine, volume).overlay(tone(freq * 2, ms, Sine, volume - 10))
    return seg.fade_in(4).fade_out(int(ms * 0.9))


def make_jump():
    return sweep(420, 880, 140, "sine", -10).fade_out(90)


def make_coin():
    return pluck(note(83), 80, -10) + pluck(note(88), 260, -10)


def make_stomp():
    boing = sweep(620, 160, 140, "triangle", -8).fade_out(100)
    puff = WhiteNoise(sample_rate=RATE).to_audio_segment(duration=90, volume=-24)
    return boing.overlay(puff.low_pass_filter(1500).fade_out(80))


def make_hurt():
    return sweep(520, 180, 320, "square", -12).low_pass_filter(1800).fade_out(220)


def make_level_complete():
    seg = silence()
    for m in (84, 88, 91):
        seg += pluck(note(m), 110, -10)
    return seg + pluck(note(96), 500, -10)


def make_game_over():
    seg = silence()
    for m in (67, 64, 60):
        seg += tone(note(m), 220, Triangle, -10).fade_out(150)
    return seg + sweep(note(55), note(48), 700, "triangle", -10).fade_out(500)


def make_click():
    return tone(1200, 35, Sine, -14).fade_out(25)


# колискова: (нота, к-сть восьмих)
MELODY = [
    (76, 2), (79, 2), (84, 2), (79, 2),   (81, 2), (79, 2), (76, 4),
    (77, 2), (76, 2), (74, 2), (72, 2),   (74, 6), (79, 2),
    (76, 2), (79, 2), (84, 2), (86, 2),   (84, 2), (81, 2), (79, 4),
    (77, 2), (76, 2), (74, 2), (71, 2),   (72, 8),
]
BASS = (48, 45, 41, 43, 48, 45, 41, 48)   # тоніка кожного такту


def make_music():
    eighth = 60000 / 92 / 2               # темп 92 bpm
    lead = silence()
    for m, length in MELODY:
        lead += pluck(note(m), length * eighth, -16)
    bass = silence()
    for root in BASS:
        for m in (root, root + 7):        # тоніка і квінта
            bass += tone(note(m), 4 * eighth, Triangle, -20).fade_in(10).fade_out(int(3 * eighth))
    return lead.overlay(bass)


GENERATORS = {
    "jump": make_jump,
    "coin": make_coin,
    "stomp": make_stomp,
    "hurt": make_hurt,
    "level_complete": make_level_complete,
    "game_over": make_game_over,
    "click": make_click,
}


def generate_all():
    os.makedirs(SND_DIR, exist_ok=True)
    print("генерую звуки через pydub...")
    for name, make in GENERATORS.items():
        make().export(os.path.join(SND_DIR, SOUND_FILES[name]), format="wav")
    make_music().export(os.path.join(SND_DIR, MUSIC_FILE), format="wav")
    print("готово:", SND_DIR)


if __name__ == "__main__":
    generate_all()
