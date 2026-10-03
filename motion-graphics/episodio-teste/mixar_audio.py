"""Mixagem do episódio de teste: voz limpa + trilha com rebaixamento sob a fala + sons de papel nas dobras.
Uso: importar mixar(eventos, saida_wav, dur). eventos = [(segundos, 'abre' | 'fecha')]"""
import os, subprocess, shutil, wave
import numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__))
SR = 44100
FF = shutil.which('ffmpeg') or os.path.expanduser('~/bin/ffmpeg')
UP = '/root/.claude/uploads/b9350d26-e0dc-581a-9039-0887dbd4547a/'
ARQ_MUSICA = os.path.join(AQUI, 'audio', 'trilha.mp3'); ARQ_PAPEL = os.path.join(AQUI, 'audio', 'papel.mp3')

def _ler(path, canais=2, ss=0.0, t=None):
    cmd = [FF, '-nostdin', '-loglevel', 'error', '-ss', str(ss)] + (['-t', str(t)] if t else []) + ['-i', path, '-ac', str(canais), '-ar', str(SR), '-f', 'f32le', '-']
    x = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
    return x.reshape(-1, canais) if canais > 1 else x

def db(x): return 20 * np.log10(np.maximum(x, 1e-9))

def _segmento(x, a, b, pico_db=-16.0, fade=0.01, fade_fim=0.06):
    """trecho do som de papel, normalizado, com entrada seca (já começa no estalo) e saída curta"""
    y = x[int(a * SR):int(b * SR)].copy(); y *= 10 ** (pico_db / 20) / max(1e-6, np.abs(y).max())
    f0, f1 = int(fade * SR), int(fade_fim * SR); y[:f0] *= np.linspace(0, 1, f0)[:, None]; y[-f1:] *= np.linspace(1, 0, f1)[:, None]
    return y

def mixar(eventos, saida, dur=76.0, musica_db=-30.0, rebaixa_db=6.0):
    n = int(dur * SR)
    voz = np.zeros(n, np.float32); v = _ler(os.path.join(AQUI, 'audio_limpo.wav'), 1); voz[:min(n, len(v))] = v[:n]
    # trilha: começa do início, mesma duração, entrada suave e saída longa
    m = _ler(ARQ_MUSICA, 2, 0.0, dur); mus = np.zeros((n, 2), np.float32); mus[:min(n, len(m))] = m[:n]
    mus *= 10 ** ((musica_db - db(np.sqrt((mus ** 2).mean()))) / 20)
    fi, fo = int(1.0 * SR), int(3.0 * SR); mus[:fi] *= np.linspace(0, 1, fi)[:, None]; mus[-fo:] *= np.linspace(1, 0, fo)[:, None]
    # rebaixamento: envelope da voz (ataque 60 ms, solta 400 ms)
    k = int(0.02 * SR); env = np.sqrt((voz[:n // k * k].reshape(-1, k) ** 2).mean(1)); ativa = (db(env) > -42).astype(np.float32)
    g = np.zeros_like(ativa); atq, sol = 1 - np.exp(-0.02 / 0.06), 1 - np.exp(-0.02 / 0.40)
    for i in range(1, len(ativa)): g[i] = g[i - 1] + ((atq if ativa[i] > g[i - 1] else sol) * (ativa[i] - g[i - 1]))
    ganho = np.repeat(10 ** (-rebaixa_db * g / 20), k); ganho = np.concatenate([ganho, np.full(n - len(ganho), ganho[-1])]); mus *= ganho[:, None]
    # sons de papel
    p = _ler(ARQ_PAPEL, 2); abre = _segmento(p, 0.56, 1.16); fecha = _segmento(p, 1.20, 1.75)
    sfx = np.zeros((n, 2), np.float32); rng = np.random.RandomState(5)
    for t, tipo in eventos:
        y = (abre if tipo == 'abre' else fecha) * 10 ** (rng.uniform(-1.5, 1.0) / 20); i = int(t * SR)
        if 0 <= i < n: j = min(n, i + len(y)); sfx[i:j] += y[:j - i]
    mix = mus + sfx + voz[:, None] * np.float32(1.0)
    pico = np.abs(mix).max(); mix *= min(1.0, 0.95 / pico)
    w = wave.open(saida, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    return dict(pico_antes=float(db(pico)), eventos=len(eventos))
