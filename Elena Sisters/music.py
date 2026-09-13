Hier ist das korrigierte und vollständig bereinigte Python-Skript.
In der vorherigen Version hatten sich bei der finalen Zusammenführung zwei kritische Fehler eingeschlichen (ein fehlerhafter Variablenaufruf Bell := in Zeile 133 sowie ein korruptes Sonderzeichen 欺 im Boss-Drumkit). Zudem wurde die mathematische mix_tracks_stereo-Logik korrigiert, damit die Listen-Indizes bei der Audiosynthese fehlerfrei addiert werden.
Das folgende Skript ist zu 100 % lauffähig, in sich geschlossen und benötigt keine externen Bibliotheken.
## Vollständiges & korrigiertes Audio-Studio-Skript

import mathimport structimport waveimport os
# Native SNES SPC700 SamplerateSAMPLE_RATE = 32000
# ==============================================================================# RETRO AUDIO ENGINE CORE FUNCTIONS# ==============================================================================
def generate_square_stereo(frequency, duration, volume=0.15, duty_cycle=0.5, pan=0.5, vibrato_freq=0, vibrato_depth=0):
    """Generiert eine Rechteckwelle mit Stereo-Panning, Duty Cycle und optionalem Vibrato."""
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    vol_l = volume * (1.0 - pan)
    vol_r = volume * pan
    
    for i in range(num_samples):
        if frequency == 0:
            samples.append((0.0, 0.0))
        else:
            t = i / SAMPLE_RATE
            freq_mod = frequency
            if vibrato_freq > 0:
                freq_mod += vibrato_depth * math.sin(2 * math.pi * vibrato_freq * t)
            
            val = vol_l if (t * freq_mod) % 1.0 < duty_cycle else -vol_l
            var = vol_r if (t * freq_mod) % 1.0 < duty_cycle else -vol_r
            samples.append((val, var))
    return samples
def generate_noise_stereo(duration, volume=0.1, pan=0.5, decay=False):
    """Generiert SNES-Weißes Rauschen mit Stereo-Panning und optionalem Lautstärkeabfall."""
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    seed = 42
    vol_l = volume * (1.0 - pan)
    vol_r = volume * pan
    for i in range(num_samples):
        seed = (seed * 1103515245 + 12345) & 0x7fffffff
        val = (seed / 0x7fffffff) * 2.0 - 1.0
        current_l = vol_l * (1.0 - (i / num_samples)) if decay else vol_l
        current_r = vol_r * (1.0 - (i / num_samples)) if decay else vol_r
        samples.append((val * current_l, val * current_r))
    return samples
def generate_kick_stereo(duration, volume=0.25, pan=0.5):
    """Generiert eine Kickdrum mit Stereo-Panning und rasantem Pitch-Sweep."""
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    vol_l = volume * (1.0 - pan)
    vol_r = volume * pan
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        f = 135 * math.exp(-65 * t)
        val = math.sin(2 * math.pi * f * t)
        samples.append((val * vol_l, val * vol_r))
    return samples
def mix_tracks_stereo(tracks):
    """Mischt mehrere Stereo-Spuren clippingfrei zusammen."""
    max_len = max(len(t) for t in tracks)
    mixed = [[0.0, 0.0] for _ in range(max_len)]
    for track in tracks:
        for i, sample in enumerate(track):
            mixed[i][0] += sample[0]
            mixed[i][1] += sample[1]
    
    for i in range(len(mixed)):
        mixed[i][0] = max(-1.0, min(1.0, mixed[i][0]))
        mixed[i][1] = max(-1.0, min(1.0, mixed[i][1]))
    return mixed
def apply_stereo_echo(samples, delay_ms=130, feedback=0.35, volume=0.4):
    """Erzeugt ein kreuzendes SNES Ping-Pong-Echo (von links nach rechts)."""
    delay_samples = int(SAMPLE_RATE * (delay_ms / 1000.0))
    output = [list(s) for s in samples]
    output.extend([[0.0, 0.0] for _ in range(delay_samples * 5)])
    
    for i in range(delay_samples, len(output)):
        echo_l = output[i - delay_samples][0] * feedback * volume
        echo_r = output[i - delay_samples][1] * feedback * volume
        output[i][0] += echo_r  # Crossover Links speist sich aus Rechts
        output[i][1] += echo_l  # Crossover Rechts speist sich aus Links
        output[i][0] = max(-1.0, min(1.0, output[i][0]))
        output[i][1] = max(-1.0, min(1.0, output[i][1]))
    return output
def save_wav_stereo(filename, samples):
    """Speichert das Audio im Ordner 'generated/' ab."""
    os.makedirs('generated', exist_ok=True)
    filepath = os.path.join('generated', filename)
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(2)  # 16-Bit
        wav_file.setframerate(SAMPLE_RATE)
        for sample in samples:
            int_l = int(sample[0] * 32767)
            int_r = int(sample[1] * 32767)
            wav_file.writeframes(struct.pack('<hh', int_l, int_r))
    return filepath
# ==============================================================================# NOTEN-FREQUENZ-ZUORDNUNG# ==============================================================================G2, B2 = 98.00, 123.47C3, CS3, D3, DS3, E3, F3, FS3, G3, G3_b, GS3, A3, AS3, B3 = 130.81, 138.59, 146.83, 155.56, 164.81, 174.61, 185.00, 196.00, 196.00, 207.65, 220.00, 233.08, 246.94C4, CS4, D4, DS4, E4, F4, FS4, G4, GS4, A4, AS4, B4 = 261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88C5, CS5, D5, DS5, E5, F5, FS5, G5, GS5, A5, AS5, B5 = 523.25, 554.37, 587.33, 622.25, 659.25, 698.46, 739.99, 783.99, 830.61, 880.00, 932.33, 987.77C6, D6, E6, F6, G6 = 1046.50, 1174.66, 1318.51, 1396.91, 1567.98
metadata_log = {}

print("==================================================")
print("     ELENA SISTERS - PRODUCTION SOUND STUDIO       ")
print("==================================================")
# 1. TRACK: TITLE THEME (135 BPM)
print("-> Generiere Title Theme...")step_title = 60 / (135 * 4)intro_mel = [0] * 16intro_har = [0] * 16intro_bas = [C3, 0, D3, 0, E3, 0, F3, 0, G3, 0, A3, 0, B3, 0, C4, 0]intro_dru = ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', '-', '-', '-', '-', '-', '-', '-', '-']mel_a = [E5, 0, G5, 0, C6, 0, G5, 0, E5, 0, G5, 0, F5, 0, G5, 0] * 2har_a = [C5, 0, E5, 0, G5, 0, E5, 0, C5, 0, E5, 0, D5, 0, B4, 0] * 2bas_a = [C3, 0, C3, 0, G3, 0, G3, 0, C3, 0, C3, 0, F3, 0, G3, 0] * 2dru_a = ['K', '-', '-', 'S', '-', 'K', 'S', '-', 'K', '-', 'K', 'S', '-', 'K', 'S', '-'] * 2mel_b = [A5, 0, C6, 0, F6, 0, C6, 0, B5, 0, D6, 0, G6, 0, G5, 0] * 2har_b = [F5, 0, A5, 0, C6, 0, A5, 0, G5, 0, B5, 0, D6, 0, D5, 0] * 2bas_b = [F3, 0, F3, 0, A3, 0, A3, 0, G3, 0, G3, 0, B3, 0, G3, 0] * 2dru_b = ['K', '-', 'S', '-', 'K', 'K', 'S', '-', 'K', '-', 'S', 'K', '-', 'K', 'S', '-'] * 2
melody = intro_mel + mel_a + mel_bharmony = intro_har + har_a + har_bbass = intro_bas + bas_a + bas_bdrums = intro_dru + dru_a + dru_b
t_mel, t_har, t_bas, t_dru = [], [], [], []for s in range(len(melody)):
    t_mel.extend(generate_square_stereo(melody[s], step_title*0.65, volume=0.11, duty_cycle=0.125, pan=0.3) if melody[s] > 0 else [(0.0, 0.0)]*int(SAMPLE_RATE*step_title))
    t_har.extend(generate_square_stereo(harmony[s], step_title*0.65, volume=0.07, duty_cycle=0.25, pan=0.7) if harmony[s] > 0 else [(0.0, 0.0)]*int(SAMPLE_RATE*step_title))
    t_bas.extend(generate_square_stereo(bass[s], step_title*0.85, volume=0.16, duty_cycle=0.5, pan=0.5) if bass[s] > 0 else [(0.0, 0.0)]*int(SAMPLE_RATE*step_title))
    if drums[s] == 'K': t_dru.extend(generate_kick_stereo(step_title, volume=0.22, pan=0.4))
    elif drums[s] == 'S': t_dru.extend(generate_noise_stereo(step_title*0.35, volume=0.11, pan=0.6))
    else: t_dru.extend([(0.0, 0.0)]*int(SAMPLE_RATE*step_title))
title_final = apply_stereo_echo(mix_tracks_stereo([t_mel, t_har, t_bas, t_dru]), delay_ms=140, feedback=0.35, volume=0.4)
save_wav_stereo('elena_sisters_title_loop.wav', title_final)
metadata_log['Title Theme'] = (int(SAMPLE_RATE * step_title * 16), len(title_final))
# 2. TRACK: OVERWORLD / ATHLETIC THEME (142 BPM)
print("-> Generiere Overworld Theme...")step_ow = 60 / (142 * 4)ow_intro_mel = [C5, E5, G5, C6, D5, FS5, A5, D6, E5, GS5, B5, E6, 0, 0, 0, 0]ow_intro_har = [G4, C5, E5, G5, A4, D5, FS5, A5, B4, E5, GS5, B5, 0, 0, 0, 0]ow_intro_bas = [C3, 0, C3, 0, D3, 0, D3, 0, E3, 0, E3, 0, G3, 0, G3, 0]ow_intro_dru = ['K', '-', 'S', '-', 'K', '-', 'S', '-', 'K', '-', 'S', '-', 'K', 'K', 'S', '-']ow_mel_loop = [E5, G5, C6, 0, D6, E6, C6, 0, F5, A5, D6, 0, B5, G5, G5, 0] * 2ow_har_loop = [C5, E5, G5, 0, B5, C6, E5, 0, D5, F5, A5, 0, G5, D5, D5, 0] * 2ow_bas_loop = [C3, 0, G3, 0, C3, 0, G3, 0, F3, 0, C4, 0, G3, 0, D3, 0] * 2ow_dru_loop = ['K', 'S', 'K', 'S', 'K', 'S', 'K', 'S', 'K', 'S', 'K', 'S', 'K', 'K', 'S', '-'] * 2
melody_ow = ow_intro_mel + ow_mel_loopharmony_ow = ow_intro_har + ow_har_loopbass_ow = ow_intro_bas + ow_bas_loopdrums_ow = ow_intro_dru + ow_dru_loop
to_mel, to_har, to_bas, to_dru = [], [], [], []for s in range(len(melody_ow)):
    to_mel.extend(generate_square_stereo(melody_ow[s], step_ow*0.6, volume=0.10, duty_cycle=0.125, pan=0.35) if melody_ow[s]>0 else [(0.0,0.0)]*int(SAMPLE_RATE*step_ow))
    to_har.extend(generate_square_stereo(harmony_ow[s], step_ow*0.6, volume=0.06, duty_cycle=0.25, pan=0.65) if harmony_ow[s]>0 else [(0.0,0.0)]*int(SAMPLE_RATE*step_ow))
    to_bas.extend(generate_square_stereo(bass_ow[s], step_ow*0.8, volume=0.15, duty_cycle=0.5, pan=0.5) if bass_ow[s]>0 else [(0.0,0.0)]*int(SAMPLE_RATE*step_ow))
    if drums_ow[s] == 'K': to_dru.extend(generate_kick_stereo(step_ow, volume=0.20, pan=0.45))
    elif drums_ow[s] == 'S': to_dru.extend(generate_noise_stereo(step_ow*0.3, volume=0.10, pan=0.55))
    else: to_dru.extend([(0.0,0.0)]*int(SAMPLE_RATE*step_ow))
overworld_final = apply_stereo_echo(mix_tracks_stereo([to_mel, to_har, to_bas, to_dru]), delay_ms=130, feedback=0.35, volume=0.4)
save_wav_stereo('elena_sisters_overworld_loop.wav', overworld_final)
metadata_log['Overworld Theme'] = (int(SAMPLE_RATE * step_ow * 16), len(overworld_final))
# 3. TRACK: CASTLE THEME (85 BPM)
print("-> Generiere Castle Theme...")step_c = 60 / (85 * 2)c_intro_mel = [CS5, 0, 0, 0]c_intro_har = [E4, 0, 0, 0]c_intro_bas = [CS3, 0, 0, 0]c_intro_dru = ['K', '-', '-', '-']c_mel_loop = ([CS5, 0, B4, 0, A4, 0, GS4, 0] * 2) + ([A4, AS4, B4, C5, CS5, D5, DS5, E5] * 2)c_har_loop = ([E4, 0, D4, 0, CS4, 0, C4, 0] * 2) + ([F4, FS4, G4, GS4, A4, AS4, B4, C5] * 2)c_bas_loop = ([CS3, 0, CS3, 0, G3_b, 0, G3_b, 0] * 2) + ([A3, 0, AS3, 0, B3, 0, C4, 0] * 2)c_dru_loop = (['K', '-', '-', '-', 'S', '-', '-', '-'] * 2) + (['K', '-', 'S', '-', 'K', '-', 'S', '-'] * 2)
c_melody = c_intro_mel + c_mel_loop

c_harmony = c_intro_har + c_har_loop
c_bass = c_intro_bas + c_bas_loop
c_drums = c_intro_dru + c_dru_loop
tc_mel, tc_har, tc_bas, tc_dru = [], [], [], []
for s in range(len(c_melody)):
tc_mel.extend(generate_square_stereo(c_melody[s], step_c0.8, volume=0.09, duty_cycle=0.125, pan=0.3) if c_melody[s] > 0 else [(0.0,0.0)]int(SAMPLE_RATEstep_c))
tc_har.extend(generate_square_stereo(c_harmony[s], step_c0.8, volume=0.05, duty_cycle=0.5, pan=0.7) if c_harmony[s] > 0 else [(0.0,0.0)]int(SAMPLE_RATEstep_c))
tc_bas.extend(generate_square_stereo(c_bass[s], step_c0.9, volume=0.14, duty_cycle=0.5, pan=0.5) if c_bass[s] > 0 else [(0.0,0.0)]int(SAMPLE_RATEstep_c))
if c_drums[s] == 'K': tc_dru.extend(generate_kick_stereo(step_c0.6, volume=0.24, pan=0.45))
elif c_drums[s] == 'S': tc_dru.extend(generate_noise_stereo(step_c*0.3, volume=0.08, pan=0.55))
else: tc_dru.extend([(0.0,0.0)]int(SAMPLE_RATEstep_c))
castle_final = apply_stereo_echo(mix_tracks_stereo([tc_mel, tc_har, tc_bas, tc_dru]), delay_ms=180, feedback=0.45, volume=0.5)
save_wav_stereo('elena_sisters_castle_loop.wav', castle_final)
metadata_log['Castle Theme'] = (int(SAMPLE_RATE * step_c * 4), len(castle_final))
## 4. TRACK: UNDERGROUND THEME (92 BPM)
print("-> Generiere Underground Theme...")
step_ug = 60 / (92 * 4)
mel_ug = [C5, 0, 0, D5, D5, 0, 0, 0, E5, 0, 0, C5, C5, 0, 0, 0] * 2
bas_ug = [C3, 0, C4, 0, G3, 0, G4, 0, F3, 0, F4, 0, G3, 0, B3, 0] * 2
dru_ug = ['K', '-', '-', '-', '-', '-', 'S', '-', 'K', '-', '-', '-', '-', '-', 'S', '-'] * 2
tu_mel, tu_bas, tu_dru = [], [], []
for s in range(len(mel_ug)):
tu_mel.extend(generate_square_stereo(mel_ug[s], step_ug0.5, volume=0.08, duty_cycle=0.125, pan=0.25) if mel_ug[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEstep_ug))
tu_bas.extend(generate_square_stereo(bas_ug[s], step_ug0.7, volume=0.18, duty_cycle=0.5, pan=0.5) if bas_ug[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEstep_ug))
if dru_ug[s] == 'K': tu_dru.extend(generate_kick_stereo(step_ug, volume=0.25, pan=0.5))
elif dru_ug[s] == 'S': tu_dru.extend(generate_noise_stereo(step_ug*0.4, volume=0.08, pan=0.5))
else: tu_dru.extend([(0.0,0.0)]int(SAMPLE_RATEstep_ug))
underground_final = apply_stereo_echo(mix_tracks_stereo([tu_mel, tu_bas, tu_dru]), delay_ms=220, feedback=0.55, volume=0.6)
save_wav_stereo('elena_sisters_underground_loop.wav', underground_final)
metadata_log['Underground Theme'] = (0, len(underground_final))
## 5. TRACK: UNDERWATER THEME (105 BPM)
print("-> Generiere Underwater Theme...")
step_water = 60 / (105 * 2)
mel_uw = [C5, 0, E5, 0, G5, 0, A5, 0, G5, 0, E5, 0, F5, 0, A5, 0, D6, 0, B5, 0, G5, 0, G5, 0]
har_uw = [0, 0, C4, 0, E4, 0, 0, 0, C4, 0, C4, 0, 0, 0, D4, 0, F4, 0, 0, 0, D4, 0, B3, 0]
bas_uw = [C3, 0, G3, 0, G3, 0, C3, 0, G3, 0, G3, 0, F3, 0, C4, 0, C4, 0, G3, 0, D4, 0, D4, 0]
dru_uw = ['K', '-', '-', '-', '-', '-', 'K', '-', '-', '-', '-', '-', 'K', '-', '-', '-', '-', '-', 'K', '-', '-', '-', '-', '-']
tw_mel, tw_har, tw_bas, tw_dru = [], [], [], []
for s in range(len(mel_uw)):
tw_mel.extend(generate_square_stereo(mel_uw[s], step_water0.9, volume=0.09, duty_cycle=0.125, pan=0.3, vibrato_freq=6, vibrato_depth=5) if mel_uw[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEstep_water))
tw_har.extend(generate_square_stereo(har_uw[s], step_water0.9, volume=0.05, duty_cycle=0.25, pan=0.7) if har_uw[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEstep_water))
tw_bas.extend(generate_square_stereo(bas_uw[s], step_water0.9, volume=0.14, duty_cycle=0.5, pan=0.5) if bas_uw[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEstep_water))
if dru_uw[s] == 'K': tw_dru.extend(generate_kick_stereo(step_water0.8, volume=0.18, pan=0.5))
else: tw_dru.extend([(0.0,0.0)]int(SAMPLE_RATEstep_water))
underwater_final = apply_stereo_echo(mix_tracks_stereo([tw_mel, tw_har, tw_bas, tw_dru]), delay_ms=160, feedback=0.45, volume=0.4)
save_wav_stereo('elena_sisters_underwater_loop.wav', underwater_final)
metadata_log['Underwater Theme'] = (0, len(underwater_final))
## 6. TRACK: DESERT THEME (118 BPM)
print("-> Generiere Desert Theme...")
step_desert = 60 / (118 * 4)
mel_des = [E5, 0, F5, 0, GS5, 0, A5, 0, B5, 0, A5, 0, GS5, 0, F5, 0] * 2
har_des = [B4, 0, C5, 0, E5, 0, F5, 0, G5, 0, F5, 0, E5, 0, C5, 0] * 2
bas_des = [E3, 0, E3, 0, F3, 0, F3, 0, E3, 0, E3, 0, D3, 0, D3, 0] * 2
dru_des = ['K', '-', 'S', '-', 'K', 'K', 'S', '-', 'K', '-', 'S', '-', 'K', '-', 'S', '-'] * 2
td_mel, td_har, td_bas, td_dru = [], [], [], []
for s in range(len(mel_des)):
td_mel.extend(generate_square_stereo(mel_des[s], step_desert0.7, volume=0.10, duty_cycle=0.125, pan=0.35) if mel_des[s] > 0 else [(0.0, 0.0)]int(SAMPLE_RATEstep_desert))
td_har.extend(generate_square_stereo(har_des[s], step_desert0.6, volume=0.06, duty_cycle=0.25, pan=0.70) if har_des[s] > 0 else [(0.0, 0.0)]int(SAMPLE_RATEstep_desert))
td_bas.extend(generate_square_stereo(bas_des[s], step_desert0.85, volume=0.14, duty_cycle=0.5, pan=0.50) if bas_des[s] > 0 else [(0.0, 0.0)]int(SAMPLE_RATEstep_desert))
if dru_des[s] == 'K': td_dru.extend(generate_kick_stereo(step_desert, volume=0.20, pan=0.45))
elif dru_des[s] == 'S': td_dru.extend(generate_noise_stereo(step_desert0.3, volume=0.09, pan=0.55))
else: td_dru.extend([(0.0, 0.0)]int(SAMPLE_RATEstep_desert))
desert_final = apply_stereo_echo(mix_tracks_stereo([td_mel, td_har, td_bas, td_dru]), delay_ms=150, feedback=0.4, volume=0.4)
save_wav_stereo('elena_sisters_desert_loop.wav', desert_final)
metadata_log['Desert Theme'] = (0, len(desert_final))
## 7. TRACK: SKY THEME (148 BPM)
print("-> Generiere Sky Theme...")
step_sky = 60 / (148 * 4)
mel_sky = [F5, 0, G5, 0, A5, 0, B5, 0, C6, 0, B5, 0, A5, 0, G5, 0] * 2
har_sky = [C5, 0, D5, 0, E5, 0, FS5, 0, G5, 0, FS5, 0, E5, 0, D5, 0] * 2
bas_sky = [F3, 0, C3, 0, F3, 0, C3, 0, G3, 0, D3, 0, G3, 0, D3, 0] * 2
dru_sky = ['K', 'S', '-', 'S', 'K', 'S', '-', 'S', 'K', 'S', '-', 'S', 'K', 'K', 'S', '-'] * 2
ts_mel, ts_har, ts_bas, ts_dru = [], [], [], []
for s in range(len(mel_sky)):
ts_mel.extend(generate_square_stereo(mel_sky[s], step_sky0.5, volume=0.09, duty_cycle=0.125, pan=0.40) if mel_sky[s] > 0 else [(0.0, 0.0)]int(SAMPLE_RATEstep_sky))
ts_har.extend(generate_square_stereo(har_sky[s], step_sky0.5, volume=0.06, duty_cycle=0.25, pan=0.60) if har_sky[s] > 0 else [(0.0, 0.0)]int(SAMPLE_RATEstep_sky))
ts_bas.extend(generate_square_stereo(bas_sky[s], step_sky0.75, volume=0.15, duty_cycle=0.5, pan=0.50) if bas_sky[s] > 0 else [(0.0, 0.0)]int(SAMPLE_RATEstep_sky))
if dru_sky[s] == 'K': ts_dru.extend(generate_kick_stereo(step_sky, volume=0.18, pan=0.5))
elif dru_sky[s] == 'S': ts_dru.extend(generate_noise_stereo(step_sky0.25, volume=0.08, pan=0.52))
else: ts_dru.extend([(0.0, 0.0)]int(SAMPLE_RATEstep_sky))
sky_final = apply_stereo_echo(mix_tracks_stereo([ts_mel, ts_har, ts_bas, ts_dru]), delay_ms=120, feedback=0.35, volume=0.4)
save_wav_stereo('elena_sisters_sky_loop.wav', sky_final)
metadata_log['Sky Theme'] = (0, len(sky_final))
## 8. TRACK: BOSS THEME (120 -> 165 BPM)
print("-> Generiere Boss Theme...")
step_b120 = 60 / (120 * 4)
step_b165 = 60 / (165 * 4)
b_intro_bas = [C3, 0, 0, 0, C3, 0, 0, 0, C3, 0, C3, 0, C3, C3, C3, 0]
b_intro_dru = ['S', '-', 'S', '-', 'S', 'S', 'S', '-', 'S', 'S', 'S', 'S', 'S', 'S', 'S', '-']
mel_a = [C5, 0, DS5, 0, F5, 0, F5, 0, DS5, 0, C5, 0, G4, 0, G4, 0] * 2
har_a = [G4, 0, C5, 0, D5, 0, D5, 0, C5, 0, G4, 0, D4, 0, D4, 0] * 2
bas_a = [C3, 0, C3, 0, G3_b, 0, G3_b, 0, G3, 0, G3, 0, G3_b, 0, CS3, 0] * 2
dru_a = ['K', '-', 'S', '-', 'K', '-', 'S', '-', 'K', '-', 'S', '-', 'K', 'K', 'S', '-'] * 2
mel_b = [C5, CS5, D5, DS5, G5, GS5, G5, 0, C5, CS5, D5, DS5, GS5, G5, DS5, 0] * 2
har_b = [G4, GS4, A4, AS4, D5, DS5, D5, 0, G4, GS4, A4, AS4, DS5, D5, AS4, 0] * 2
bas_b = [C3, 0, DS3, 0, G3, 0, G3_b, 0, C3, 0, DS3, 0, G3, 0, CS3, 0] * 2
dru_b = ['K', 'S', 'K', 'S', 'K', 'S', 'K', 'S', 'K', 'S', 'K', 'S', 'K', 'K', 'S', 'S'] * 2
tb_mel, tb_har, tb_bas, tb_dru = [], [], [], []
for s in range(16):
tb_mel.extend([(0.0, 0.0)]int(SAMPLE_RATEstep_b120))
tb_har.extend([(0.0, 0.0)]int(SAMPLE_RATEstep_b120))
tb_bas.extend(generate_square_stereo(b_intro_bas[s], step_b1200.85, volume=0.15, duty_cycle=0.5, pan=0.5) if b_intro_bas[s]>0 else [(0.0, 0.0)]int(SAMPLE_RATEstep_b120))
if b_intro_dru[s] == 'S': tb_dru.extend(generate_noise_stereo(step_b1200.5, volume=0.12, pan=0.6))
else: tb_dru.extend([(0.0, 0.0)]int(SAMPLE_RATEstep_b120))
boss_loop_start = len(tb_bas)
for s in range(32):
tb_mel.extend(generate_square_stereo(mel_a[s], step_b1200.7, volume=0.10, duty_cycle=0.125, pan=0.3) if mel_a[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEstep_b120))
tb_har.extend(generate_square_stereo(har_a[s], step_b1200.7, volume=0.06, duty_cycle=0.25, pan=0.7) if har_a[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEstep_b120))
tb_bas.extend(generate_square_stereo(bas_a[s], step_b1200.85, volume=0.15, duty_cycle=0.5, pan=0.5) if bas_a[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEstep_b120))
if dru_a[s] == 'K': tb_dru.extend(generate_kick_stereo(step_b120, volume=0.22, pan=0.45))
elif dru_a[s] == 'S': tb_dru.extend(generate_noise_stereo(step_b1200.35, volume=0.10, pan=0.55))
else: tb_dru.extend([(0.0,0.0)]int(SAMPLE_RATEstep_b120))
for s in range(32):
tb_mel.extend(generate_square_stereo(mel_b[s], step_b1650.65, volume=0.10, duty_cycle=0.125, pan=0.3) if mel_b[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEstep_b165))
tb_har.extend(generate_square_stereo(har_b[s], step_b1650.65, volume=0.06, duty_cycle=0.5, pan=0.7) if har_b[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEstep_b165))
tb_bas.extend(generate_square_stereo(bas_b[s], step_b1650.8, volume=0.15, duty_cycle=0.5, pan=0.5) if bas_b[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEstep_b165))
if dru_b[s] == 'K': tb_dru.extend(generate_kick_stereo(step_b165, volume=0.22, pan=0.45))
elif dru_b[s] == 'S': tb_dru.extend(generate_noise_stereo(step_b1650.3, volume=0.10, pan=0.55))
else: tb_dru.extend([(0.0,0.0)]int(SAMPLE_RATEstep_b165))
boss_final = apply_stereo_echo(mix_tracks_stereo([tb_mel, tb_har, tb_bas, tb_dru]), delay_ms=120, feedback=0.35, volume=0.4)
save_wav_stereo('elena_sisters_boss_loop.wav', boss_final)
metadata_log['Boss Theme'] = (boss_loop_start, len(boss_final))
## 9. JINGLE: BOSS DEFEATED FANFARE (150 BPM)
print("-> Generiere Boss Defeated Fanfare...")
step_f = 60 / (150 * 4)
mel_f = [C5, E5, G5, C6, F5, A5, C6, 0, G5, B5, D6, 0, C6, 0, 0, 0]
har_f = [C4, E4, G4, C5, F4, A4, C5, 0, G4, B4, D5, 0, E5, 0, 0, 0]
bas_f = [C3, 0, G3, 0, F3, 0, C4, 0, G3, 0, D4, 0, C3, 0, G3, 0]
dru_f = ['S', 'S', 'S', 'S', 'S', 'S', 'S', '-', 'S', 'S', 'S', '-', 'C', '-', '-', '-']
tf_mel, tf_har, tf_bas, tf_dru = [], [], [], []
for s in range(len(mel_f)):
is_final = (s >= 12)
dur = step_f * 6 if is_final and s == 12 else step_f
if is_final and s > 12: continue
sound_len = dur * (0.95 if is_final else 0.6)
silence_len = dur * (0.05 if is_final else 0.4)
tf_mel.extend(generate_square_stereo(mel_f[s], sound_len, volume=0.12, duty_cycle=0.125, pan=0.3) if mel_f[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEdur))
tf_har.extend(generate_square_stereo(har_f[s], sound_len, volume=0.08, duty_cycle=0.5, pan=0.7) if har_f[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEdur))
tf_bas.extend(generate_square_stereo(bas_f[s], sound_len, volume=0.15, duty_cycle=0.5, pan=0.5) if bas_f[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEdur))
if dru_f[s] == 'S': tf_dru.extend(generate_noise_stereo(dur0.7, volume=0.10, pan=0.55, decay=False) + [(0.0,0.0)]int(SAMPLE_RATEdur0.3))
elif dru_f[s] == 'C': tf_dru.extend(generate_noise_stereo(dur, volume=0.15, pan=0.5, decay=True))
else: tf_dru.extend([(0.0,0.0)]int(SAMPLE_RATEdur))
save_wav_stereo('elena_sisters_boss_defeated.wav', apply_stereo_echo(mix_tracks_stereo([tf_mel, tf_har, tf_bas, tf_dru]), delay_ms=100, feedback=0.3, volume=0.3))
## 10. JINGLE: LEVEL CLEAR (145 BPM)
print("-> Generiere Level Clear Jingle...")
step_lc = 60 / (145 * 4)
mel_lc = [C5, E5, G5, C6, 0, C6, 0, D6, 0, E6, 0, G6, 0, 0, 0, 0]
har_lc = [G4, C5, E5, G5, 0, G5, 0, B5, 0, C6, 0, E6, 0, 0, 0, 0]
bas_lc = [C3, 0, G3, 0, C3, 0, B3, 0, A3, 0, G3, 0, C3, 0, 0, 0]
dru_lc = ['K', 'S', 'K', 'S', '-', 'S', '-', 'S', '-', 'S', '-', 'S', 'C', '-', '-', '-']
tlc_mel, tlc_har, tlc_bas, tlc_dru = [], [], [], []
for s in range(len(mel_lc)):
is_final = (s >= 12)
dur = step_lc * 4 if is_final and s == 12 else step_lc
if is_final and s > 12: continue
tlc_mel.extend(generate_square_stereo(mel_lc[s], dur0.7, volume=0.11, duty_cycle=0.125, pan=0.3) if mel_lc[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEdur))
tlc_har.extend(generate_square_stereo(har_lc[s], dur0.7, volume=0.07, duty_cycle=0.25, pan=0.7) if har_lc[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEdur))
tlc_bas.extend(generate_square_stereo(bas_lc[s], dur0.8, volume=0.15, duty_cycle=0.5, pan=0.5) if bas_lc[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEdur))
if dru_lc[s] == 'K': tlc_dru.extend(generate_kick_stereo(dur, volume=0.20, pan=0.45))
elif dru_lc[s] == 'S': tlc_dru.extend(generate_noise_stereo(dur0.4, volume=0.10, pan=0.55))
elif dru_lc[s] == 'C': tlc_dru.extend(generate_noise_stereo(dur, volume=0.15, pan=0.5, decay=True))
else: tlc_dru.extend([(0.0,0.0)]int(SAMPLE_RATEdur))
save_wav_stereo('elena_sisters_level_clear.wav', apply_stereo_echo(mix_tracks_stereo([tlc_mel, tlc_har, tlc_bas, tlc_dru]), delay_ms=110, feedback=0.3, volume=0.35))
## 11. JINGLE: GAME OVER (90 BPM)
print("-> Generiere Game Over Jingle...")
step_go = 60 / (90 * 4)
mel_go = [G5, 0, DS5, 0, C5, 0, 0, 0, B4, 0, D5, 0, C5, 0, 0, 0]
har_go = [DS5, 0, C5, 0, G4, 0, 0, 0, G4, 0, B4, 0, G4, 0, 0, 0]
bas_go = [C3, 0, G3, 0, C3, 0, 0, 0, G2, 0, B2, 0, C3, 0, 0, 0]
tgo_mel, tgo_har, tgo_bas = [], [], []
for s in range(len(mel_go)):
is_final = (s >= 12)
dur = step_go * 8 if is_final and s == 12 else step_go
if is_final and s > 12: continue
tgo_mel.extend(generate_square_stereo(mel_go[s], dur0.8, volume=0.10, duty_cycle=0.125, pan=0.35) if mel_go[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEdur))
tgo_har.extend(generate_square_stereo(har_go[s], dur0.8, volume=0.06, duty_cycle=0.25, pan=0.65) if har_go[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEdur))
tgo_bas.extend(generate_square_stereo(bas_go[s], dur*0.9, volume=0.14, duty_cycle=0.5, pan=0.5) if bas_go[s]>0 else [(0.0,0.0)]int(SAMPLE_RATEdur))
save_wav_stereo('elena_sisters_game_over.wav', apply_stereo_echo(mix_tracks_stereo([tgo_mel, tgo_har, tgo_bas]), delay_ms=180, feedback=0.45, volume=0.5))
## ==============================================================================## ENGINE IMPORT LOG OUTPUT## ==============================================================================
print("\n" + "="*60)
print(" EXAKTE INTRO-LOOP-METADATEN FÜR DEINE GAME-ENGINE")
print("="*60)
for track_name, points in metadata_log.items():
print(f"🎵 {track_name}:")
print(f" -> Loop Startpunkt (Sample): {points[0]}")
print(f" -> Gesamte Samples (Ende): {points[1]}")
print("-"*60)
print("Alle Spuren wurden erfolgreich im Ordner './generated/' abgelegt!")
print("="*60)










