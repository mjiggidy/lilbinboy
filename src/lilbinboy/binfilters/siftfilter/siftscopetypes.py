import enum

class BSSiftScopeType(enum.Enum):
	"""None? Any? A column? A range? YOU TELL ME, FRIENDOOOOO"""

	NoColumn     = enum.auto()
	"""Sift no column"""

	SingleColumn = enum.auto()
	"""Sift a specified column for a given string"""

	Range        = enum.auto()
	"""Sift a specified property for the inclusion of a given value"""

	AnyColumn    = enum.auto()
	"""Sift any column in the current view for a given string"""