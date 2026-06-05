"""
These sifters sift.  Maybe they're "rules."  "Strategies."
I dunno, I'm just one man.
Each is responsible for one sift criteria.
"""

from .abstractsifter     import BSAbstractSifter

from .anycolumnsifter    import BSAnyColumnSifter
from .rangesifter        import BSRangeSifter
from .singlecolumnsifter import BSSingleColumnSifter
from .nocolumnsifter     import BSNoColumnSifter