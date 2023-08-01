from pathlib import Path
from mkv_converter import MkvMerge
from subtitler import Subtitler
import re

# def _rm_tree(pth):
#     """removes the media folder

#     Args:
#         pth (Path): media folder path
#     """
#     for child in pth.glob('*'):
#         if child.is_file():
#             child.unlink()
#         else:
#             rm_tree(child)
#     pth.rmdir()


def _sub_file_check(sub):
    return sub.is_file() and (("english" in sub.name.lower()) or ("eng" in sub.name.lower()))


def _get_episode_sub(name, sub_path):
    episode_sub_folder = sub_path.joinpath(name)
    sub_file_list = [sub for sub in episode_sub_folder.glob('*.srt') if _sub_file_check(sub)]
    sorted_sub_list = sorted(sub_file_list, key = lambda sub: sub.stat().st_size, reverse=True)
    largest_sub = sorted_sub_list.pop(0)
    if sorted_sub_list and sorted_sub_list[-1].stat().st_size < 20000:
        burn_in_sub_list = sorted_sub_list.pop(-1)
    else:
        burn_in_sub_list = None
    if burn_in_sub_list:
        return [largest_sub, burn_in_sub_list]
    return [largest_sub]


def _get_movie_sub(sub_path):
    sub_file_list = [sub for sub in sub_path.glob('*.srt') if _sub_file_check(sub)]
    sorted_sub_list = sorted(sub_file_list, key = lambda sub: sub.stat().st_size, reverse=True)
    largest_sub = sorted_sub_list.pop(0)
    if sorted_sub_list and sorted_sub_list[-1].stat().st_size < 20000:
        burn_in_sub_list = sorted_sub_list.pop(-1)
    else:
        burn_in_sub_list = None
    if burn_in_sub_list:
        return [largest_sub, burn_in_sub_list]
    return [largest_sub]



def _convert_episode(episode, burn_in_path, episode_dict):
    if episode_dict["subs"] and len(episode_dict["subs"])>1:
        subtitler = Subtitler(episode_dict["subs"][1], episode_dict["subs"][0])
        episode_dict["output_path"] = burn_in_path.joinpath(episode.name).with_suffix(".mkv")
        subtitler.clean_subs()
        mkv_merge = MkvMerge(episode_dict)
        mkv_merge.burn_in_convert()
    elif episode_dict["subs"]:
        mkv_merge = MkvMerge(episode_dict)
        mkv_merge.convert()
    else:
        mkv_merge = MkvMerge(episode_dict)
        mkv_merge.no_sub_convert()


def _folder_media_search(media_dict, output_path:Path, burn_in_path:Path):
    sub_path = media_dict.get("input_path").joinpath("Subs")
    media_dict["is_subs"] = sub_path.exists()
    list_of_mp4s = list(media_dict.get("input_path").glob('*.mp4'))
    pattern = r"\b(S[0-9]+E[0-9]+)\b"
    media_dict["is_tv_episodes"] = all([True if re.search(pattern, str(video)) else False for video in list_of_mp4s])
    if media_dict["is_subs"]:
        media_dict["is_tv"] = all([object_path.is_dir() for object_path in sub_path.iterdir()])
    elif media_dict["is_tv_episodes"]:
       media_dict["is_tv"] =  media_dict["is_tv_episodes"]
    else:
        media_dict["is_tv"] = False
    

    if media_dict["is_tv"]:
        for episode in list_of_mp4s: 
            if media_dict["is_subs"]:
                subs = _get_episode_sub(episode.stem, sub_path)
            else: 
                subs = None
            
            episode_dict = {
                "path": episode,
                "output_path": output_path.joinpath(episode.name).with_suffix(".mkv"),
                "subs": subs
            }

            _convert_episode(episode, burn_in_path, episode_dict)

    else:
        movie = list(media_dict.get("input_path").glob("*.mp4"))[0]
        if media_dict["is_subs"]:
            subs = _get_movie_sub(sub_path)
        else:
            subs = None
        
        movies_dict = {
            "path": movie,
            "output_path": output_path.joinpath(movie.name).with_suffix(".mkv"),
            "subs": subs
        }

        if subs:
            if len(movies_dict["subs"])>1:
                subtitler = Subtitler(movies_dict["subs"][1], movies_dict["subs"][0])
                subtitler.clean_subs()
                movies_dict["output_path"] = burn_in_path.joinpath(movie.name).with_suffix(".mkv")
                mkv_merge = MkvMerge(movies_dict)
                mkv_merge.burn_in_convert()
            else:
                mkv_merge = MkvMerge(movies_dict)
                mkv_merge.convert()
        else:
            mkv_merge = MkvMerge(movies_dict)
            mkv_merge.no_sub_convert()


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
