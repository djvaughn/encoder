from subtitler import Subtitler
from mkv_tools import MkvMerge, MkvInfo, MkvExtract

class MovieConverter():

    def __init__(self, movie, output_path, burn_in_path, sub_path=None) -> None:
        self.__movie = movie
        self.__output_path = output_path
        self.__burn_in_path = burn_in_path
        self.__sub_path = sub_path
        self.__burn_in = False
        self.__movie_dict = {
            "path": self.__movie
        }
        self.__sub_list = []

    def run(self):
        if self.__sub_path:
            self.__sub_list = self.__retrieve_subs_from_sub_dir()
            if len(self.__sub_list) > 1:
                self.__clean_subs()
        elif self.__mkv_check():
            try:
                eng_sub_track_id_list = list(self.__sub_track_gen())
            except:
                eng_sub_track_id_list = None

            if eng_sub_track_id_list:
                mkv_extract = MkvExtract(self.__movie, eng_sub_track_id_list)
                sub_tracks_location = mkv_extract.subtitle_extract()
                self.__sub_list = self.__find_sdh_and_burn_in(sub_tracks_location)
                if len(self.__sub_list) > 1:
                    self.__clean_subs()

        self.__build_movie_dict()
        self.__merge()

    def __mkv_check(self):
        return self.__movie.suffix == ".mkv"
    
    def __sub_track_gen(self):
        mkv_info = MkvInfo(self.__movie)
        movie_track_info = mkv_info.get_info()["tracks"]
        for track in movie_track_info:
            if track["type"] == "subtitles" and track["properties"]["language"] == "eng":
                yield track["id"]

    def __retrieve_subs_from_sub_dir(self):
        list_of_subs = self.__get_movie_sub()
        usable_subs = self.__find_sdh_and_burn_in(list_of_subs)
        return usable_subs

    def __get_movie_sub(self):
        return [sub for sub in self.__sub_finder_gen() if  self.__sub_file_check(sub)]

    def __clean_subs(self):
        subtitler = Subtitler(*self.__sub_list)
        subtitler.clean_subs()
        self.__burn_in = True


    def __sub_finder_gen(self):
        for sub_types in ('*.srt', '*.pgs', '*.vobsub'):
            for sub_type in sub_types:
                yield [self.__sub_path.glob(sub_type)]

    def __sub_file_check(self, sub):
        return sub.is_file() and (("english" in sub.name.lower()) or ("eng" in sub.name.lower()))

    def __find_sdh_and_burn_in(self, list_of_subs):
        sorted_sub_list = sorted(list_of_subs, key = lambda sub: sub.stat().st_size, reverse=True)
        largest_sub = sorted_sub_list.pop(0)
        if sorted_sub_list and sorted_sub_list[-1].stat().st_size < 20000:
            burn_in_sub = sorted_sub_list.pop(-1)
            return [burn_in_sub, largest_sub]
        return [largest_sub]

    def __build_movie_dict(self):
        if self.__burn_in:
            self.__movie_dict["output_path"] = self.__burn_in_path.joinpath(self.__movie.name).with_suffix(".mkv")
        else:
            self.__movie_dict["output_path"] = self.__output_path.joinpath(self.__movie.name).with_suffix(".mkv")
        if self.__sub_list:
            self.__movie_dict["subs"] = self.__sub_list

    def __merge(self):
        mkv_merge = MkvMerge(self.__movie_dict)
        if self.__burn_in:
            mkv_merge.burn_in_convert()
        elif self.__sub_path:
            mkv_merge.convert()
        else:
            mkv_merge.no_sub_convert()
