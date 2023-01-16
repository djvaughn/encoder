import pysrt


class Subtitler:
    """cleans the subtitles
    """

    def __init__(self, burn_in_sub, regular_sub) -> None:
        self._burn_in = pysrt.open(burn_in_sub)
        self._burn_in_length = len(self._burn_in)
        self._regular = pysrt.open(regular_sub)
        self._regular_length = len(self._regular)

    def clean_subs(self):
        """removes the burn_in subs from the regular subs
        """
        for line in self._burn_in:
            print(f"removing: {line.text}")
            try:
                self._regular.remove(line)
            except ValueError:
                target = self._regular.slice(starts_after=line.start-1, ends_before=line.end+1)
                del target
            print(f"removed: {line.text}")
        
        self._regular.save()