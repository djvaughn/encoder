from subtitler import Subtitler
from mkv_tools import MkvMerge, MkvInfo, MkvExtract
from itertools import chain

class TvConverter():

    def __init__(self, episodes, output_path, burn_in_path, sub_path=None) -> None:
        self.__episodes = episodes
        self.__output_path = output_path
        self.__burn_in_path = burn_in_path
        self.__sub_path = sub_path
        self.__episodes_dict_list = []

    def run(self):
        for episode in self.__episodes:
            sub_list = None
            burn_in = False
            sub_path = False
            output = self.__output_path
            if self.__sub_path:
                sub_path = True
                sub_list = self.__retrieve_subs_from_sub_dir(episode.stem)
                if len(sub_list) > 1:
                    self.__clean_subs(sub_list)
                    output = self.__burn_in_path
                    burn_in = True
            elif self.__mkv_check(episode):
                eng_sub_track_id_list = list(self.__sub_track_gen(episode))
                if eng_sub_track_id_list:
                    mkv_extract = MkvExtract(episode, eng_sub_track_id_list)
                    sub_tracks_location = mkv_extract.subtitle_extract(episode.stem)
                    sub_list = self.__find_sdh_and_burn_in(sub_tracks_location)
                    sub_path = True
                    if len(sub_list) > 1:
                        self.__clean_subs(sub_list)
                        output = self.__burn_in_path
                        burn_in = True
            self.__episodes_dict_list.append(self.__build_episode_dict(episode, output, sub_list, burn_in, sub_path))
        self.__merge()

    def __mkv_check(self, episode):
        return episode.suffix == ".mkv"
    
    def __sub_track_gen(self, episode):
        mkv_info = MkvInfo(episode)
        movie_track_info = mkv_info.get_info()["tracks"]
        for track in movie_track_info:
            if track["type"] == "subtitles" and track["properties"]["language"] == "eng":
                yield track["id"]

    def __retrieve_subs_from_sub_dir(self, name):
        list_of_subs = self.__get_tv_sub(name)
        usable_subs = self.__find_sdh_and_burn_in(list_of_subs)
        return usable_subs

    def __get_tv_sub(self, name):
        return [sub for sub in self.__sub_finder_gen(name) if  self.__sub_file_check(sub)]

    def __clean_subs(self, sub_list):
        subtitler = Subtitler(*sub_list)
        subtitler.clean_subs()

    def __sub_finder_gen(self, name):
        return chain(
            self.__sub_path.joinpath(name).glob('*.srt'),
            self.__sub_path.joinpath(name).glob('*.pgs'),
            self.__sub_path.joinpath(name).glob('*.vobsub')
        )

    def __sub_file_check(self, sub):
        return sub.is_file() and (("english" in sub.name.lower()) or ("eng" in sub.name.lower()))

    def __find_sdh_and_burn_in(self, list_of_subs):
        sorted_sub_list = sorted(list_of_subs, key = lambda sub: sub.stat().st_size, reverse=True)
        largest_sub = sorted_sub_list.pop(0)
        if sorted_sub_list and sorted_sub_list[-1].stat().st_size < 30000:
            burn_in_sub = sorted_sub_list.pop(-1)
            return [burn_in_sub, largest_sub]
        return [largest_sub]

    def __build_episode_dict(self, episode, output_path, subs, burn_in, sub_path):
        return {
            "path": episode,
            "output_path": output_path.joinpath(episode.name).with_suffix(".mkv"),
            "subs": subs,
            "burn_in": burn_in,
            "sub_path": sub_path
        }

    def __merge(self):
        for episode_dict in self.__episodes_dict_list:
            sub_path = episode_dict.pop("sub_path", False)
            burn_in = episode_dict.pop("burn_in", False)
            mkv_merge = MkvMerge(episode_dict)
            if burn_in:
                mkv_merge.burn_in_convert()
            elif sub_path:
                mkv_merge.convert()
            else:
                mkv_merge.no_sub_convert()
