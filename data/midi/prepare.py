import json
from collections import defaultdict
from os import listdir
from os.path import isfile, join

import mido

from mappings import GM_CAT

PATH = "./"


def main(path: str) -> None:
    files = [f for f in listdir(path) if isfile(join(path, f)) and "mid" in f]
    all_atomic_messages = list()
    all_complex_messages = list()
    for i, file in enumerate(files):
        mid = mido.MidiFile(file)
        new_file = (
            file.lower()
            .replace(" ", "_")
            .replace("(", "_")
            .replace(")", "_")
            .replace("-", "_")
            .replace(".", "_")
            .replace("'", "_")
            .replace("__", "_")
            .replace("__", "_")
            .replace("_mid", "")
        )
        print(new_file)
        tracks = mid.tracks
        # first pass
        midi_ch_instr_data = defaultdict(lambda: defaultdict(list))
        ch_prg = dict()
        time_signature = list()
        tempos = list()
        other_time = list()
        other_no_time = list()
        # tempo -> number of quarter notes (beats) per minute
        # 1/32 notes in quarter
        ticks_per_beat = mid.ticks_per_beat
        notated_32nd_notes_per_beat = 0
        tempo = 0.0
        single_measure = 0.0
        for track in tracks:
            time_command_count = 0
            for j, msg in enumerate(track):
                if msg.type == "program_change":
                    ch_prg[msg.channel] = msg.program
                elif msg.type == "time_signature":
                    time_signature.append(msg)
                    single_measure = round(msg.numerator / msg.denominator, 4)
                    notated_32nd_notes_per_beat = msg.notated_32nd_notes_per_beat
                elif msg.type == "set_tempo":
                    tempo = round(60000000 / msg.tempo)
                    tempos.append(msg)
                elif hasattr(msg, "time") and hasattr(msg, "channel"):
                    _b_ = msg.bytes()
                    _b_[0] = _b_[0] & 0xF0
                    _ch_ = msg.channel
                    _t_ = msg.time
                    if _b_[0] == 144 or _b_[0] == 128:
                        _instr_ = ch_prg[_ch_]
                        midi_ch_instr_data[_ch_][ch_prg[_ch_]].append(
                            _b_ + [_t_] + [_instr_] + [time_command_count]
                        )
                        time_command_count += 1
                    elif _t_ > 0:
                        _instr_ = ch_prg[_ch_]
                        midi_ch_instr_data[_ch_][ch_prg[_ch_]].append(
                            _b_ + [_t_] + [_instr_] + [time_command_count]
                        )
                        time_command_count += 1
                    else:
                        other_time.append(msg)
                else:
                    other_no_time.append(msg)
        midi_ch_instr_time = defaultdict(lambda: defaultdict(list))
        for _ch_ in midi_ch_instr_data.keys():
            for _instr_ in midi_ch_instr_data[_ch_].keys():
                current_time = 0.0
                n_current_time = 0.0
                current_ticks = 0
                for msg in midi_ch_instr_data[_ch_][_instr_]:
                    ticks = msg[3]
                    current_ticks += ticks
                    time_command_count = msg[5]
                    midi_ch_instr_time[_ch_][_instr_].append(
                        [time_command_count, current_ticks, ticks]
                    )
        max_ticks = 0.0
        for _ch_ in midi_ch_instr_time.keys():
            if len(midi_ch_instr_time[_ch_]) > 1:
                chunks = sorted(midi_ch_instr_time[_ch_].values())
                for j in range(1, len(chunks)):
                    prev_last_current_ticks = chunks[j - 1][-1][1]
                    for k in range(len(chunks[j])):
                        chunks[j][k][1] += prev_last_current_ticks
            for _instr_ in midi_ch_instr_time[_ch_].keys():
                for _time_ in midi_ch_instr_time[_ch_][_instr_]:
                    if _time_[1] > max_ticks:
                        max_ticks = _time_[1]
        song_duration_s_1 = (
            max_ticks / ticks_per_beat / tempo
        ) * 60  # from midi units (ticks)
        midi_ch_instr_notes = defaultdict(lambda: defaultdict(list))
        for _ch_ in midi_ch_instr_data.keys():
            for _instr_ in midi_ch_instr_data[_ch_].keys():
                notes_d = defaultdict(list)
                notes_t = defaultdict(list)
                for j in range(len(midi_ch_instr_data[_ch_][_instr_])):
                    _data_ = midi_ch_instr_data[_ch_][_instr_][j]
                    _time_ = midi_ch_instr_time[_ch_][_instr_][j]
                    midi_ch_instr_notes[_ch_][_instr_].append([])
                    if _data_[0] == 144 or _data_[0] == 128:
                        notes_d[_data_[1]] += [_data_ + [j]]
                        notes_t[_data_[1]] += [_time_ + [j]]
                for note in notes_d.keys():
                    events_d = notes_d[note]
                    events_t = notes_t[note]
                    j = 0
                    while j < len(events_d):
                        k = 1
                        while j + k < len(events_d):
                            if (
                                events_d[j + k][0] == 144
                                and events_d[j + k][2] > 0
                                and events_t[j + k][1] - events_t[j + 0][1] > 0
                            ):
                                break
                            else:
                                k += 1
                        single_note_d_event = events_d[j : (j + k)]
                        single_note_t_event = events_t[j : (j + k)]
                        if k == 1:
                            pass
                        elif k == 2:
                            pass
                        else:
                            pass
                        j += k
                pass
                pass

        midi_time_instr_notes_rep = defaultdict(
            lambda: defaultdict(lambda: defaultdict(list))
        )
        for _ch_ in midi_ch_instr_time.keys():
            for _instr_ in midi_ch_instr_time[_ch_].keys():
                _instr_type_ = GM_CAT[_instr_]
                for j in range(len(midi_ch_instr_time[_ch_][_instr_])):
                    _time_ = midi_ch_instr_time[_ch_][_instr_][j]
                    _note_ = midi_ch_instr_notes[_ch_][_instr_][j]
                    _t_ = round(_time_[1] / ticks_per_beat, 3)
                    midi_time_instr_notes_rep[_t_][_instr_type_][_instr_].append(_note_)

                    pass

        json_object = json.dumps(midi_time_instr_notes_rep, indent=2, sort_keys=True)
        with open(f"{new_file}.json", "w") as outfile:
            outfile.write(json_object)
    print(len(all_atomic_messages))
    with open(f"all_atomic.json", "w") as outfile:
        outfile.write(json.dumps(all_atomic_messages, indent=2, sort_keys=True))
    print(len(all_complex_messages))
    with open(f"all_complex.json", "w") as outfile:
        outfile.write(json.dumps(all_complex_messages, indent=2, sort_keys=True))


main(path=PATH)
