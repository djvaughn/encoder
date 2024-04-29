from pathlib import Path
from movie_converter import MovieConverter
from tv_converter import TvConverter

import re

def _search_for_sub_folders(sub_path):
    # checking if the sub path has a bunch of sub folders.  If so, it's assumed that the media is TV Episode(s)
    for object_path in sub_path.iterdir():
        yield object_path.is_dir()

def _search_for_subs(media_dict):
    sub_path = None
    for folder in ("Subs", "Sub", "subs", "sub"):
        if media_dict.get("input_path").joinpath(folder).exists():
            sub_path = media_dict.get("input_path").joinpath(folder)
            break
    return sub_path


def _find_all_tv_episodes_gen(list_of_videos):
    # checking for episode naming standards SSxEE
    pattern = r"\b(S[0-9]+E[0-9]+)\b"
    episode_regex = re.compile(pattern)
    for video in list_of_videos:
        yield episode_regex.search(str(video))


def _find_files_gen(media_dict):
    file_exstensions = ('*.mp4', '*.mkv')
    for file_exstension in file_exstensions:
        yield media_dict.get('input_path').glob(file_exstension)


def _folder_media_search(media_dict, output_path:Path, burn_in_path:Path):
    list_of_list_videos = list(_find_files_gen(media_dict))
    list_of_videos = []
    for row in list_of_list_videos:
        list_of_videos += row
    try:
        is_tv =  media_dict["is_tv_episodes"] = all(_find_all_tv_episodes_gen(list_of_videos))
    except:
        is_tv = False
    sub_path = _search_for_subs(media_dict)
    if not is_tv and sub_path:
        is_tv = all(_search_for_sub_folders(sub_path))
    
    if is_tv:
        tv = TvConverter(list_of_videos, output_path, burn_in_path, sub_path=sub_path)
        tv.run()
    else:
        movie = MovieConverter(list_of_videos[0], output_path, burn_in_path, sub_path=sub_path)
        movie.run()

def _find_files(input_path: Path, output_path:Path, burn_in_path:Path):
    for media in input_path.iterdir():
        media_dict = {
            "input_path": media
        }
        if media.is_dir():
            _folder_media_search(media_dict, output_path,burn_in_path)

        else:
            pass


def main():
    """the main runner for the x265 converter
    """
    input_path=Path("/input")
    output_path=Path("/output")
    burn_in_path=Path("/burn")
    _find_files(input_path, output_path,burn_in_path)

if __name__ == "__main__":
    main()
