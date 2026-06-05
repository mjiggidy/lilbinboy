"""
`QRunnable` enabling threaded bin loading
Logic is implemented via `.binparser`
"""

import logging
from os import PathLike
from PySide6 import QtCore
import avb
from . import binparser

class BSBinViewLoader(QtCore.QRunnable):
	"""Load a given bin in a threadpool"""

	class Signals(QtCore.QObject):
		"""Signals emitted by `BSBinViewLoader`"""

		# Status signals
		sig_begin_loading               = QtCore.Signal(str)
		sig_done_loading                = QtCore.Signal()
		sig_aborted_loading             = QtCore.Signal(object)
		sig_got_exception               = QtCore.Signal(object)

		sig_got_mob_count               = QtCore.Signal(int)

		sig_got_display_mode            = QtCore.Signal(object)
		sig_got_view_settings           = QtCore.Signal(object)
		sig_got_text_column_widths      = QtCore.Signal(object)
		sig_got_frame_mode_scale        = QtCore.Signal(int)
		sig_got_script_mode_scale       = QtCore.Signal(int)
		sig_got_mob                     = QtCore.Signal() # For progress bar
		sig_got_mobs                    = QtCore.Signal(object)
		sig_got_sort_settings           = QtCore.Signal(object)
		sig_got_sift_settings           = QtCore.Signal(object)
		sig_got_bin_display_settings    = QtCore.Signal(object)
		sig_got_bin_appearance_settings = QtCore.Signal(object, object, object, object, object, object, object)

		# Runnable control
		_sig_user_request_stop = QtCore.Signal()

		@QtCore.Slot()
		def requestStop(self):
			self._sig_user_request_stop.emit()

	def __init__(self, bin_path:PathLike, signals:Signals, queue_size:int=500, *args, **kwargs):
		
		super().__init__(*args, **kwargs)
		
		self._bin_path = bin_path
		self._signals  = signals
		self._mob_queue_size = queue_size

		self._stop_requested = False
		self._signals._sig_user_request_stop.connect(self.requestStop)

	def signals(self) -> Signals:
		"""Return the signals instance"""

		return self._signals
	
	def requestStop(self):
		"""Request graceful stop"""

		if not self._stop_requested:
			logging.getLogger(__name__).warning("User requested abort")

		self._stop_requested = True

	def loadDataFromBin(self, bin_handle:avb.file.AVBFile):
		"""Load and emit the data"""

		# NOTE to self:
		# I think I'm going for "very passive" error handling -- ideally so people can see something
		# out of even a corrupt bin.  So, lots of `try`s here but not bailing unless the file can't be
		# opened or understood as an `avb` file or something

		# Load bin properties (view, sorting, etc)
		try:

			# NOTE: Mitigates signal freakouts during early close -- but need to do this better and more thoroughly
			if self._stop_requested:
				#self._signals.sig_aborted_loading.emit(None)
				return

			logging.getLogger(__name__).debug("Begin display flags")
			try:
				opts = binparser.bin_display_flags_from_bin(bin_handle.content)
			except ValueError as e:
				logging.getLogger(__name__).error("Could not parse Bin Display Settings: %s.  Using defaults instead.", e)
				import avbutils
				opts = avbutils.BinDisplayItemTypes.default_items()
			finally:
				self._signals.sig_got_bin_display_settings.emit(opts)
			logging.getLogger(__name__).debug("End display flags")
			
			logging.getLogger(__name__).debug("Begin view settings")

			view_setting = binparser.bin_view_setting_from_bin(bin_handle.content)
			self._signals.sig_got_view_settings     .emit(view_setting)
			self._signals.sig_got_text_column_widths.emit(binparser.bin_column_widths_from_bin(bin_handle.content))
			self._signals.sig_got_frame_mode_scale  .emit(binparser.bin_frame_view_scale_from_bin(bin_handle.content))
			self._signals.sig_got_script_mode_scale .emit(binparser.bin_scipt_view_scale_from_bin(bin_handle.content))

			logging.getLogger(__name__).debug("End view settings")

			logging.getLogger(__name__).debug("Begin display mode")
			self._signals.sig_got_display_mode.emit(binparser.display_mode_from_bin(bin_handle.content))
			logging.getLogger(__name__).debug("End display mode")

			logging.getLogger(__name__).debug("Begin sift settings")
			self._signals.sig_got_sift_settings.emit(binparser.sift_settings_from_bin(bin_handle.content, view_setting=view_setting))
			logging.getLogger(__name__).debug("End sift settings")

			logging.getLogger(__name__).debug("Begin sort settings")
			self._signals.sig_got_sort_settings.emit(binparser.sort_settings_from_bin(bin_handle.content))
			logging.getLogger(__name__).debug("End sort settings")

			logging.getLogger(__name__).debug("Begin appearance settings")
			self._signals.sig_got_bin_appearance_settings.emit(*binparser.appearance_settings_from_bin(bin_handle.content))
			logging.getLogger(__name__).debug("End appearance settings")

		except Exception as e:
			logging.getLogger(__name__).error("Encountered error while loading bin properties: %s", e)
			self._signals.sig_got_exception.emit(e)
			
		# Get mob count for progress
		try:
			logging.getLogger(__name__).debug("Begin bin item count")
			self._signals.sig_got_mob_count.emit(len(bin_handle.content.items))
			logging.getLogger(__name__).debug("End bin item count")
		except Exception as e:
			self._signals.sig_got_exception.emit(e)

		mob_queue = list()
		
		logging.getLogger(__name__).debug("Begin bin item loading with queue size=%s", self._mob_queue_size)
		# Load each mob
		for bin_item in bin_handle.content.items:

			if self._stop_requested:

				self._signals.sig_aborted_loading.emit(None)
				break

			try:
				mob_queue.append(binparser.load_item_from_bin(bin_item))
				#self._signals.sig_got_mob.emit()
			except Exception as e:
				self._signals.sig_got_exception.emit(e)
			
			if len(mob_queue) == self._mob_queue_size:
				self._signals.sig_got_mobs.emit(mob_queue)
				mob_queue = list()
		
		if self._stop_requested:
			return
		
		if len(mob_queue):
			
			logging.getLogger(__name__).debug("Flushing the final %s mobs", len(mob_queue))
			self._signals.sig_got_mobs.emit(mob_queue)
		
		logging.getLogger(__name__).debug("End bin item loading")

	def run(self):
		"""Who will run the runnable?"""

		self._signals.sig_begin_loading.emit(self._bin_path)

		try:

			with avb.open(self._bin_path) as bin_handle:
				self.loadDataFromBin(bin_handle)

		except Exception as e:

			self._signals.sig_got_exception.emit(e)
			self._signals.sig_aborted_loading.emit(str(e))

		self._signals.sig_done_loading.emit()