from __future__ import annotations
import enum, typing

class BSSiftMatchTypes(enum.IntEnum):
	"""How to match text for sifting"""

	# NOTE: SiftItems are listed in reverse order
	# NOTE: This corresponds to the sift values returned by pyavb
	# NOTE: i kissy u

	Contains       = 1
	"""Column contains a given string"""

	BeginsWith     = 2
	"""Column begins with a given string"""
 
	MatchesExactly = 3
	"""Column matches exactly a given string"""