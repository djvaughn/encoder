from pathlib import Path
from sh import mkvmerge

input = Path("/input")
output = Path("/output")

def print_out(line):
    print(line)
    
def rm_tree(pth):
    for child in pth.glob('*'):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    pth.rmdir()
    
def get_file_paths(media_dir):
    input_file_list = [media_files for media_files in media_dir.iterdir() if media_files.suffix in [".mp4", ".mkv"]]
    output_file_list = [output.joinpath(input_file.name).with_suffix(".mkv") for input_file in input_file_list]
    return sorted(input_file_list), sorted(output_file_list)

def get_subs_path(media_dir):
    subs_dir = media_dir.joinpath("Subs")
    if not subs_dir.exists():
        sub_file_list = [sub for sub in media_dir.iterdir() if sub.is_file() and sub.suffix in [".srt", ".psg"]]
    else:
        
        sub_file_list = [sub for sub in sorted(subs_dir.glob('**/*.srt'))]
        sub_file_list.extend([sub for sub in sorted(subs_dir.glob('**/*.psg'))])
        
    sub_list = list(filter(lambda x: x.is_file() and (("english" in x.name.lower()) or ("eng" in x.name.lower())), sub_file_list))
    sub_dict = {}
    for sub in sub_list:
        # print(sub)
        if str(sub.parent) in sub_dict:
            dir_sub_list = sub_dict[str(sub.parent)]
            dir_sub_list.append(sub)
            sorted_list = sorted(dir_sub_list, key = lambda sub: sub.stat().st_size, reverse=True)
            sub_dict[str(sub.parent)] = sorted_list
        else:
            sub_dict[str(sub.parent)] = [sub]
    
    # for key, value in sub_dict.items():
    #     value_str_list = [str(sub) for sub in sub_dict[key]]
    #     value_str = ", ".join(value_str_list)
    #     print(f"\n\n{key}: {value_str}")
    final_sub_list = [sub_lists[0] for sub_lists in sub_dict.values()]
    return sorted(final_sub_list)
    
def mkv_merge(encode_list, subs):
    if subs:
        print(encode_list)
        for input_path, output_path, sub_path in encode_list:
            # print(f"Input: {input_path}\nOutput: {output_path}\nSubPath: {sub_path}")
            mkvmerge(
            "--ui-language", "en_US",
            "--output", output_path.resolve(),
            "--language", "0:en",
            input_path.resolve(),
            "--sub-charset", "0:UTF-8",
            "--language", "0:en",
            sub_path.resolve(),
            "--track-order", "0:0,0:1,1:0"
            , _out=print_out
            )
            print(f"Completed {output_path.name}")
        return True
    else:
        return False
    
if not input.exists():
    raise OSError("Inputs is missing")
    
for media_dir in input.iterdir():
    input_file_list, output_file_list = get_file_paths(media_dir)
    # print(input_file_list)
    # print(output_file_list)
    sub_list = get_subs_path(media_dir)
    if sub_list:
        encode_list = list(zip(input_file_list, output_file_list, sub_list))
        subs = True
    else:
        encode_list = list(zip(input_file_list, output_file_list))
        subs = False
    # print(encode_list)
        
    finished = mkv_merge(encode_list, subs)
    if finished:
        rm_tree(media_dir)
    print("All encoding complete")
    
[
  "--ui-language",
  "en_US",
  "--output",
  "/storage/Downloads/completed/Missing.Link.2019.1080p.BluRay.x265-RARBG/Missing.Link.2019.1080p.BluRay.x265-RARBG.mkv",
  "--language",
  "0:mul",
  "--language",
  "1:en",
  "(",
  "/storage/Downloads/completed/Missing.Link.2019.1080p.BluRay.x265-RARBG/Missing.Link.2019.1080p.BluRay.x265-RARBG.mp4",
  ")",
  "--sub-charset",
  "0:UTF-8",
  "--language",
  "0:en",
  "--forced-display-flag",
  "0:yes",
  "(",
  "/storage/Downloads/completed/Missing.Link.2019.1080p.BluRay.x265-RARBG/Subs/6_English.srt",
  ")",
  "--sub-charset",
  "0:UTF-8",
  "--language",
  "0:en",
  "(",
  "/storage/Downloads/completed/Missing.Link.2019.1080p.BluRay.x265-RARBG/Subs/7_English.srt",
  ")",
  "--track-order",
  "0:0,0:1,1:0,2:0"
]

[
  "--ui-language",
  "en_US",
  "--output",
  "/storage/Downloads/completed/Ford.v.Ferrari.2019.1080p.BluRay.x265-RARBG/Ford.v.Ferrari.2019.1080p.BluRay.x265-RARBG.mkv",
  "--language",
  "0:mul",
  "--language",
  "1:en",
  "(",
  "/storage/Downloads/completed/Ford.v.Ferrari.2019.1080p.BluRay.x265-RARBG/Ford.v.Ferrari.2019.1080p.BluRay.x265-RARBG.mp4",
  ")",
  "--sub-charset",
  "0:UTF-8",
  "--language",
  "0:en",
  "(",
  "/storage/Downloads/completed/Ford.v.Ferrari.2019.1080p.BluRay.x265-RARBG/Subs/3_English.srt",
  ")",
  "--sub-charset",
  "0:UTF-8",
  "--language",
  "0:en",
  "--forced-display-flag",
  "0:yes",
  "(",
  "/storage/Downloads/completed/Ford.v.Ferrari.2019.1080p.BluRay.x265-RARBG/Subs/2_English.srt",
  ")",
  "--track-order",
  "0:0,0:1,1:0,2:0"
]
    
    
    
    
    
 # /usr/bin/mkvmerge --ui-language en_US --output /storage/Downloads/completed/Missing.Link.2019.1080p.BluRay.x265-RARBG/Missing.Link.2019.1080p.BluRay.x265-RARBG.mkv --language 0:mul --language 1:en '(' /storage/Downloads/completed/Missing.Link.2019.1080p.BluRay.x265-RARBG/Missing.Link.2019.1080p.BluRay.x265-RARBG.mp4 ')' --sub-charset 0:UTF-8 --language 0:en --forced-display-flag 0:yes '(' /storage/Downloads/completed/Missing.Link.2019.1080p.BluRay.x265-RARBG/Subs/6_English.srt ')' --sub-charset 0:UTF-8 --language 0:en '(' /storage/Downloads/completed/Missing.Link.2019.1080p.BluRay.x265-RARBG/Subs/7_English.srt ')' --track-order 0:0,0:1,1:0,2:0