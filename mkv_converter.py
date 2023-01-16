from sh import mkvmerge

class MkvMerge:
    """converts mp4 to mkv
    """

    def __init__(self, media_dict):
        self.__input_path = media_dict["path"]
        self.__output_path = media_dict["output_path"]
        self.__subs = media_dict["subs"]

    def _print_out(self, line):
        """used as an output for mkvmerge

        Args:
            line (str): the output
        """
        print(line)

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
            self.__subs[1].resolve(),
            "--sub-charset", "0:UTF-8",
            "--language", "0:en",
            self.__subs[0].resolve(),
            "--track-order", "0:0,0:1,1:0,2:0"
            , _out=self._print_out
            )
        print(f"Completed {self.__output_path.name}")