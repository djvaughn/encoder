from sh import mkvmerge, mkvextract
from json import loads
from pathlib import Path

class MkvMerge:
    """converts mp4 to mkv
    """

    def __init__(self, media_dict):
        self.__input_path = media_dict["path"]
        self.__output_path = media_dict["output_path"]
        self.__subs = media_dict["subs"]

    def convert(self):
        """converts a mp4 to mkv with one sub
        """
        mkvmerge(
            "--ui-language", "en_US",
            "--output", self.__output_path.resolve(),
            "--language", "0:en",
            self.__input_path.resolve(),
            "--sub-charset", "0:UTF-8",
            "--language", "0:en",
            self.__subs[0].resolve(),
            "--track-order", "0:0,0:1,1:0"
            , _out=self._print_out
            )
        print(f"Completed {self.__output_path.name}")

    def no_sub_convert(self):
        """converts a mp4 to mkv with no subs
        """
        mkvmerge(
            "--ui-language", "en_US",
            "--output", self.__output_path.resolve(),
            "--language", "0:en",
            self.__input_path.resolve(),
            "--track-order", "0:0,0:1"
            , _out=self._print_out
            )
        print(f"Completed {self.__output_path.name}")

    
    def burn_in_convert(self):
        """converts a mp4 to mkv with burn in subs
        """
        mkvmerge(
            "--ui-language", "en_US",
            "--output", self.__output_path.resolve(),
            "--language", "0:en",
            "--language", "1:en",
            self.__input_path.resolve(),
            "--sub-charset", "0:UTF-8",
            "--language", "0:en",
            self.__subs[0].resolve(),
            "--sub-charset", "0:UTF-8",
            "--language", "0:en",
            self.__subs[1].resolve(),
            "--track-order", "0:0,0:1,1:0,2:0"
            , _out=self._print_out
            )
        print(f"Completed {self.__output_path.name}")

    
    def _print_out(self, line):
        """used as an output for mkvmerge

        Args:
            line (str): the output
        """
        print(line)

class MkvInfo:
    """Info on media file
    """

    def __init__(self, media):
        self.__media = media

    def get_info(self):
        return loads(
            str(
                mkvmerge(
                    "-J", 
                    self.__media.resolve()
                    )
                )
            )

class MkvExtract:

    def __init__(self, media, track_list):
        self.__media = media
        self.__track_list = track_list

    def subtitle_extract(self, episode_name=None):
        sub_tracks_location = []
        for track in self.__track_list:
            if episode_name:
                sub_track_location = f"{self.__media.resolve().parent}/{episode_name}_{track}_eng.srt"
            else:
                sub_track_location = f"{self.__media.resolve().parent}/{track}_eng.srt"
            mkvextract(
                "tracks",
                self.__media.resolve(),
                f"{track}:{sub_track_location}"
            )
            sub_tracks_location.append(Path(sub_track_location))
        
        return sub_tracks_location