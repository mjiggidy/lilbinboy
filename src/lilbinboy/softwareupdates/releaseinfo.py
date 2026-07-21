from PySide6 import QtCore
import dataclasses

@dataclasses.dataclass(frozen=True)
class ReleaseInfo:
	"""Release information for a... software... release.. thing"""

	name:str
	"""Release Name"""

	release_notes:str
	"""Release notes (Markdown)"""

	date:QtCore.QDateTime
	"""Release datetime (UTC)"""

	version:QtCore.QVersionNumber
	"""Version number"""

	release_url:QtCore.QUrl
	"""Github Release Page"""