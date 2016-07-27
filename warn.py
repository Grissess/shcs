from warnings import warn

class SecurityWarning(Warning):
    pass

def bad_sec_practice(details=''):
    warnings.warn("Bad security practice" + (": " + details if details else ""), SecurityWarning, 2)
