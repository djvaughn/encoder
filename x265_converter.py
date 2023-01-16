from click import command, option, Path as click_path
from pathlib import Path
from mkv_converter import MkvMerge
from subtitler import Subtitler

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
    if sorted_sub_list[-1].stat().st_size < 20000:
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
    if sorted_sub_list[-1].stat().st_size < 20000:
        burn_in_sub_list = sorted_sub_list.pop(-1)
    else:
        burn_in_sub_list = None
    if burn_in_sub_list:
        return [largest_sub, burn_in_sub_list]
    return [largest_sub]



def _convert_episode(episode, sub_path, output_path):
    episode_dict = {
        "path": episode,
        "output_path": output_path.joinpath(episode.name).with_suffix(".mkv"),
        "subs": _get_episode_sub(episode.stem, sub_path)
    }
    
    if len(episode_dict["subs"])>1:
        subtitler = Subtitler(episode_dict["subs"][1], episode_dict["subs"][0])
        subtitler.clean_subs()
        mkv_merge = MkvMerge(episode_dict)
        mkv_merge.burn_in_convert()
    else:
        mkv_merge = MkvMerge(episode_dict)
        mkv_merge.convert()


def _folder_media_search(media_dict, output_path:Path):
    sub_path = media_dict.get("input_path").joinpath("Subs")
    media_dict["is_subs"] = sub_path.exists()
    media_dict["is_tv"] = all([object_path.is_dir() for object_path in sub_path.iterdir()])

    if media_dict["is_tv"]:
        for episode in media_dict.get("input_path").iterdir(): 
            if episode != sub_path and episode.suffix == ".mp4":
                _convert_episode(episode, sub_path, output_path) 

    else:
        movie = media_dict.get("input_path").glob("*.mp4")
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
                mkv_merge = MkvMerge(movies_dict)
                mkv_merge.burn_in_convert()
                mkv_merge.burn_in_convert()
            else:
                mkv_merge = MkvMerge(movies_dict)
                mkv_merge.convert()
        else:
            mkv_merge = MkvMerge(movies_dict)
            mkv_merge.no_sub_convert()


def _find_files(input_path: Path, output_path:Path):
    for media in input_path.iterdir():
        media_dict = {
            "input_path": media
        }
        if media.is_dir():
            _folder_media_search(media_dict, output_path)

        else:
            pass

@command()
@option("-i", "--input-path", "input_path", type=click_path(exists=True, dir_okay=True), required=True)
@option("-o", "--output-path", "output_path", type=click_path(exists=True, dir_okay=True), required=True)
def main(input_path, output_path):
    """the main runner for the x265 converter
    """
    _find_files(input_path, output_path)

if __name__ == "__main__":
   main()