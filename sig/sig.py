from .jsinterp import JSInterpreter
import re
import os
import requests

requests.packages.urllib3.disable_warnings()

NO_DEFAULT = object()

class Sig:
    def __init__(self):
        pass
    def _parse_sig_js(self, jscode):
            funcname = self._search_regex(
                (r'\b[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*encodeURIComponent\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                r'\b[a-zA-Z0-9]+\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*encodeURIComponent\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                r'(?P<sig>[a-zA-Z0-9$]+)\s*=\s*function\(\s*a\s*\)\s*{\s*a\s*=\s*a\.split\(\s*""\s*\)',
                # Obsolete patterns
                r'(["\'])signature\1\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                r'\.sig\|\|(?P<sig>[a-zA-Z0-9$]+)\(',
                r'yt\.akamaized\.net/\)\s*\|\|\s*.*?\s*[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*(?:encodeURIComponent\s*\()?\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                r'\b[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                r'\b[a-zA-Z0-9]+\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                r'\bc\s*&&\s*a\.set\([^,]+\s*,\s*\([^)]*\)\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                r'\bc\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*\([^)]*\)\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                r'\bc\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*\([^)]*\)\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\('),
                jscode, 'Initial JS player signature function name', group='sig')

            jsi = JSInterpreter(jscode)
            initial_function = jsi.extract_function(funcname)
            return lambda s: initial_function([s])

    def _extract_signature_function(self, video_id, player_url, example_sig):
        code = requests.get(player_url, verify=False)
        res = self._parse_sig_js(code.text)
        return res

    def _search_regex(self, pattern, string, name, default=NO_DEFAULT, fatal=True, flags=0, group=None):
        if isinstance(pattern, (str, str, type(re.compile('')))):
            mobj = re.search(pattern, string, flags)
        else:
            for p in pattern:
                mobj = re.search(p, string, flags)
                if mobj:
                    break
        if mobj:
            if group is None:
                return next(g for g in mobj.groups() if g is not None)
            else:
                return mobj.group(group)
        elif default is not NO_DEFAULT:
            return default
        elif fatal:
            pass
        else:
            return None

    def getSig(self, v, player_url, s):
        sf = self._extract_signature_function(v, player_url, s)
        return sf(s)
