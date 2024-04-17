from os import listdir
from os.path import isfile, join
import mido
from mido import Message
from collections import defaultdict
import json

PATH = "./"

def main(path: str) -> None:
    files = [f for f in listdir(path) if isfile(join(path, f)) and "mid" in f]
    for i, file in enumerate(files):
        mid = mido.MidiFile(file)
        new_file = file.lower().replace(" ","_").replace("(","_").replace(")","_").replace("-","_").replace(".","_").replace("'","_").replace("__","_").replace("__","_").replace("_mid","")
        print(new_file)
        tracks = mid.tracks
        json_rep = defaultdict(list)
        all_atomic_messages = list()
        all_complex_messages = list()
        for track in tracks:
            _t_ = 0
            for msg in track:
                if isinstance(msg, Message):
                    _t_ += msg.time
                    _ch_ = msg.channel
                    _b_ = msg.bytes()
                    _b_[0] = _b_[0] & 0xF0
                    if len(_b_) < 3:
                        _b_.append(0)
                    full = [_ch_] + _b_
                    if _b_ not in all_atomic_messages:
                        all_atomic_messages.append(_b_)
                    if full not in all_complex_messages:
                        all_complex_messages.append(full)
                    json_rep[_t_] += [full]
        for _t_ in json_rep.keys():
            json_rep[_t_] = sorted(json_rep[_t_])
        json_object = json.dumps(json_rep, indent=2, sort_keys=True)
        with open(f"{new_file}.json", "w") as outfile:
            outfile.write(json_object)
    print(len(all_atomic_messages))
    with open(f"all_atomic.json", "w") as outfile:
        outfile.write(json.dumps(all_atomic_messages, indent=2, sort_keys=True))
    print(len(all_complex_messages))
    with open(f"all_complex.json", "w") as outfile:
        outfile.write(json.dumps(all_complex_messages, indent=2, sort_keys=True))




main(path=PATH)

