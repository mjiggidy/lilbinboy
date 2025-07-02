import re
from PySide6 import QtCore, QtGui, QtWidgets
from timecode import Timecode

class LBSpinBoxTC(QtWidgets.QSpinBox):

	sig_timecode_changed = QtCore.Signal(Timecode)

	MAX_TC_STRING = "100:00:00:00"
	"""Timecode string for max range calculations"""

	PAT_TC_VALID = re.compile(r"^[-+]?([0-9]{1,2}:){0,3}[0-9]{1,2}$")
	"""Valid timecode pattern for validation"""

	PAT_TC_INTER = re.compile(r"^[+-]?([0-9]{1,2}:){0,3}$")
	"""Intermediate pattern"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._rate = 24
		self._resample_on_rate_change = True

		self._allow_negative = False
		self._allow_positive = True

		self.valueChanged.connect(lambda: self.sig_timecode_changed.emit(self.timecode()))
		
		self.setKeyboardTracking(False)
		self.lineEdit().setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		self._update_range()

	def _update_range(self):
		"""Update timecode range"""
		# TODO: Might want to make this user-facing
		self.setRange(
			Timecode(self.MAX_TC_STRING, rate=self.rate()).frame_number * -1 if self.allowNegative() else 0,
			Timecode(self.MAX_TC_STRING, rate=self.rate()).frame_number      if self.allowPositive() else 0,
		)

	@QtCore.Slot(bool)
	def setResampleOnRateChange(self, resample:bool):
		"""Resample Timecode to closest neighbor when rate changes.  If false, will maintain frame number."""
		self._resample_on_rate_change = bool(resample)
	
	def resampleOnRateChange(self) -> bool:
		"""If Timecode will be resampled when the rate changes.  If false, will maintain frame number."""
		return self._resample_on_rate_change
			
	@QtCore.Slot(bool)
	def setAllowNegative(self, allow:bool):
		"""Allow negative (<0) frame ranges"""
		self._allow_negative = bool(allow)
		self._update_range()
		self.setValue(self.value())

	def allowNegative(self) -> bool:
		"""Are negative frames (<0) allowed"""
		return self._allow_negative

	@QtCore.Slot(bool)	
	def setAllowPositive(self, allow:bool):
		"""Allow positive (>0) frame ranges"""
		self._allow_positive = bool(allow)
		self._update_range()
		self.setValue(self.value())
	
	def allowPositive(self) -> bool:
		"""Are positive frames (>0) allowed"""
		return self._allow_positive
	
	@QtCore.Slot(int)
	def setFrameNumber(self, frame_number:int):
		"""Set based on frame number"""
		self.setValue(int(frame_number))
	
	def frameNumber(self) -> int:
		"""The frame number as an integer"""
		return self.value()
	
	@QtCore.Slot(int)
	def setRate(self, rate:int):
		"""Set the timecode rate"""
		old_tc = self.timecode()

		if rate == self.rate():
			return
		elif rate < 0:
			raise ValueError(f"Invalid timecode rate ({rate})")
		
		self._rate = int(rate)
		self._update_range()

		if self.resampleOnRateChange():
			self.setValue(old_tc.resample(rate=self.rate()).frame_number)
		else:
			self.setValue(self.value())
	
	def rate(self) -> int:
		"""Timecode rate"""
		return self._rate
	
	@QtCore.Slot(Timecode)
	def setTimecode(self, timecode:Timecode):
		"""Set frame and rate from a given timecode"""
		self.setRate(timecode.rate)
		self.setValue(timecode.frame_number)
	
	def timecode(self) -> Timecode:
		"""Get the current timecode"""
		return Timecode(self.frameNumber(), rate=self.rate())
	
	def textFromValue(self, val:int) -> str:
		"""Format frame number to Timecode string"""
		# Add a '+' for positive values for differentiation
		prefix = "+" if self.allowNegative() and self.value() > 0 else ""
		return prefix + str(Timecode(val, rate=self.rate()))
	
	def valueFromText(self, text:str) -> int:
		"""Derive timecode frame number from user input text"""
		
		# Pass through valid timecode patterns
		if self.PAT_TC_VALID.match(text):
			return Timecode(text, rate=self.rate()).frame_number
		
		# Otherwise, validate() will only allow for integers hopefully lol
		# So format integer with colons (001234 -> 00:12:34)

		if not text.lstrip("+-").isnumeric():
			return 0
		
		is_negative = text.startswith("-")

		text_raw_reversed = text.lstrip("+-")[::-1]
		text_formatted = ("-" if is_negative else "") + (":".join([text_raw_reversed[idx:idx+2] for idx in range(0, len(text_raw_reversed),2)]))[::-1]
		return Timecode(text_formatted, rate=self.rate()).frame_number

	def validate(self, input:str, pos:int) -> QtGui.QValidator.State:
		
		# Match simple frame counts
		if not input:
			state = QtGui.QValidator.State.Intermediate
		elif input == "+" or input == "-":
			state = QtGui.QValidator.State.Intermediate
		elif len(input.lstrip("+-")) <= 8 and input.lstrip("+-").isnumeric():
			state = QtGui.QValidator.State.Acceptable
		
		# Match timecode
		elif self.PAT_TC_INTER.match(input):
			state = QtGui.QValidator.State.Intermediate
		elif self.PAT_TC_VALID.match(input):
			state = QtGui.QValidator.State.Acceptable
		
		# Nah
		else:
			state = QtGui.QValidator.State.Invalid

		return state
	
	def toolTip(self):
		return f"{self.timecode()} @ {self.rate()} fps"