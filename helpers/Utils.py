import re


class Utils:
    @staticmethod
    def match_text(pattern: str, text: str) -> str:
        return re.search(pattern, text).group()