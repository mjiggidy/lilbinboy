import logging
from PySide6 import QtCore, QtNetwork

from .releaseinfo import ReleaseInfo

TIMEOUT_DURATION_MSEC = 5_000
"""Network timeout duration"""

TIMER_COOLDOWN_MSEC   = 10_000
"""Cooldown before manual check is enabled again (for API rate limiting)"""

TIMER_AUTOCHECK_MSEC  = 60_000
"""Default autocheck interval"""

class BSUpdatesManager(QtCore.QObject):
	"""Controller for checking for version updates via Github releases"""

	sig_autoCheckChanged     = QtCore.Signal(bool)

	sig_networkCheckStarted  = QtCore.Signal()
	sig_networkCheckFinished = QtCore.Signal()
	sig_networkCheckError    = QtCore.Signal(QtNetwork.QNetworkReply.NetworkError)
	sig_cooldownExpired      = QtCore.Signal()
	sig_enabled_changed      = QtCore.Signal(bool)

	sig_newReleaseAvailable  = QtCore.Signal(object)
	sig_releaseIsCurrent     = QtCore.Signal(object)

	def __init__(self,
		url_releases:QtCore.QUrl|str,
		current_version:QtCore.QVersionNumber|str=QtCore.QVersionNumber(0,0,0),
		start_enabled:bool=True,
		autocheck_enabled:bool=True,
		*args,
		**kwargs
	):

		super().__init__(*args, **kwargs)

		self._current_version   = QtCore.QVersionNumber.fromString(current_version) if isinstance(current_version, str) else current_version

		self._url_releases      = QtCore.QUrl(url_releases)
		self._is_enabled        = start_enabled
		self._autocheck_enabled = autocheck_enabled

		self._netman = QtNetwork.QNetworkAccessManager()
		self._netman.setTransferTimeout(TIMEOUT_DURATION_MSEC)
		self._current_request = None
		self._latest_release_info = None
		"""The last latest release found"""

		self._cooldown_timer  = QtCore.QTimer(interval=TIMER_COOLDOWN_MSEC, singleShot=True)
		self._autocheck_timer = QtCore.QTimer(interval=TIMER_AUTOCHECK_MSEC, singleShot=True)

		# Signals
		self._cooldown_timer.timeout.connect(self.sig_cooldownExpired)
		self._autocheck_timer.timeout.connect(self.checkForUpdates)

		self._netman.finished.connect(self._cooldown_timer.start)
		self._netman.finished.connect(self.processNetworkReply)
		self._netman.finished.connect(self.sig_networkCheckFinished)

		if self._autocheck_enabled:
			self.checkForUpdates()
	
	# ---
	# Releases URL
	# ---
	
	def releasesUrl(self) -> QtCore.QUrl:
		"""URL for Release Info JSON"""

		return self._url_releases
	
	def setReleasesUrl(self, url_releases:QtCore.QUrl):
		"""Set the URL for Release Info JSON"""

		self._url_releases = url_releases

	# ---
	# Cooldown timer for API rate limiting
	# ---

	def setCooldownInterval(self, milliseconds:int):
		"""Set cooldown interval (in milliseconds) for API rate limiting"""
		if milliseconds > self.autoCheckInterval():
			raise ValueError(self.tr("Cooldown interval must be less than autocheck interval"))
		self._cooldown_timer.setInterval(milliseconds)
	
	def cooldownInterval(self) -> int:
		"""Cooldown interval (in milliseconds) for API rate limiting"""
		return self._cooldown_timer.interval()
	
	def cooldownInProgress(self) -> bool:
		"""Whether we coolin it"""
		return self._cooldown_timer.isActive()
	
	# ---
	# Enable/disable
	# ---
	@QtCore.Slot()
	@QtCore.Slot(bool)
	def setEnabled(self, is_enabled:bool=True):
		
		if not self._is_enabled == is_enabled:
			
			self._is_enabled = is_enabled
			self.sig_enabled_changed.emit(is_enabled)
			
			logging.getLogger(__name__).debug("Update manager enabled=%s", is_enabled)

			if self._is_enabled and self._autocheck_enabled:
				self._autocheck_timer.start()
	
	@QtCore.Slot()
	@QtCore.Slot(bool)
	def setDisabled(self, is_disabled:bool=True):

		self.setEnabled(not is_disabled)
	
	# ---
	# Autocheck
	# ---

	@QtCore.Slot(bool)
	def setAutoCheckEnabled(self, autocheck:bool):
		"""Set automatically check for updates"""

		if autocheck != self._autocheck_enabled:
			self.sig_autoCheckChanged.emit(autocheck)

		self._autocheck_enabled = autocheck

		# Start autocheck if a new release hasn't already been found
		if self.autoCheckEnabled() and self.latestReleaseInfo() is None:
			
			if self._cooldown_timer.isActive():
				# Schedule autocheck
				self._autocheck_timer.start()
			
			else:
				# or just do it
				self.checkForUpdates()

		else:
			self._autocheck_timer.stop()

	def autoCheckEnabled(self) -> bool:
		"""Is automatically checl for updates enabled"""
		
		return self._autocheck_enabled
	
	def setAutoCheckInterval(self, milliseconds:int):
		"""Set how often (in milliseconds) to check for updates if autocheck is enabled"""

		if milliseconds < self.cooldownInterval():
			raise ValueError(self.tr("Autocheck interval must be greater than cooldown interval"))
		
		self._autocheck_timer.setInterval(milliseconds)

	def autoCheckInterval(self) -> int:
		"""How often (in milliseconds) to check for updates if autocheck is enabled"""

		return self._autocheck_timer.interval()
	
	# ---
	# Version/Release info
	# ---

	def currentVersion(self) -> QtCore.QVersionNumber:
		"""Get Lil' Bin Boy current version"""

		return self._current_version
	
	def latestReleaseInfo(self) -> ReleaseInfo|None:

		"""The latest release info gathered from the last time network check succeeded"""
		return self._latest_release_info

	# ---
	# Network Check
	# ---

	def checkInProgress(self) -> bool:
		"""Indicates a current check is in progress"""
		# Useful for setting window initial state
		return self._current_request is not None
	
	@QtCore.Slot()
	def checkForUpdates(self):
		"""Initiate check for updates via network"""

		if not self._is_enabled:
			logging.getLogger(__name__).debug("Skipping network update check: currently disabled")
			return
		
		# Skip if we have an active QNetworkRequest or in cooldown period
		if self.checkInProgress() or self._cooldown_timer.isActive():
			logging.getLogger(__name__).debug(
				"Skipping network update check (checkInProgress=%s; cooldowntimerIsActive=%s)",
				self.checkInProgress(), self._cooldown_timer.isActive()
			)
			return
		
		logging.getLogger(__name__).debug("Network update check start")

		self.sig_networkCheckStarted.emit()
		self._current_request = self._netman.get(QtNetwork.QNetworkRequest(self.releasesUrl()))

	@QtCore.Slot(QtNetwork.QNetworkReply)
	def processNetworkReply(self, reply:QtNetwork.QNetworkReply):
		"""Read the ReleaseInfo JSON and determine if a new version is available"""

		# Unset current
		self._current_request = None

		if reply.error() != QtNetwork.QNetworkReply.NetworkError.NoError:

			self.sig_networkCheckError.emit(reply.error())
			logging.getLogger(__name__).error("Cannot check for updates: %s", reply.errorString())

			if self.autoCheckEnabled():
				self._autocheck_timer.start()

			return

		# Parse JSON for latest version
		try:
		
			response = QtCore.QJsonDocument.fromJson(reply.readAll())
			latest_release:dict = response.array().first().toObject()
		
		except Exception as e:
		
			logging.getLogger(__name__).error("Problem with network update check response: %s", e)
		
			return

		# Latest version to `ReleaseInfo` struct
		try:
			latest_release_info = ReleaseInfo(
				name          = latest_release["name"],
				version       = QtCore.QVersionNumber.fromString(latest_release["tag_name"][1:]), # Strip 'v'
				release_notes = latest_release["body"],
				release_url   = QtCore.QUrl(latest_release["html_url"]),
				date          = QtCore.QDateTime.fromString(latest_release["published_at"], QtCore.Qt.DateFormat.ISODate)
			)
		
		except KeyError as e:	# Maybe do this
			
			logging.getLogger(__name__).error("Missing info from network update check response: %s", e)
			
			self.sig_networkCheckError.emit(QtNetwork.QNetworkReply.NetworkError.UnknownContentError)
			
			if self.autoCheckEnabled():
				self._autocheck_timer.start()
			
			return
		
		if self.currentVersion() < latest_release_info.version:
			# Store and emit new release info
			self._latest_release_info = latest_release_info
			logging.getLogger(__name__).info("Network update check found new version (currentVersion=%s; newVersion=%s)", self.currentVersion(), latest_release_info.version)

			self.sig_newReleaseAvailable.emit(latest_release_info)
		
		else:
			# Restart autocheck
			logging.getLogger(__name__).debug("Current version appears to be the latest (currentVersion=%s; newVersion=%s)", self.currentVersion(), latest_release_info.version)
			self.sig_releaseIsCurrent.emit(latest_release_info)
			if self.autoCheckEnabled():
				self._autocheck_timer.start()