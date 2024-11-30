import pathlib, datetime, dataclasses
import avb, avbutils
from timecode import TimecodeRange

@dataclasses.dataclass(frozen=True)
class TimelineInfo:
	"""Representation of a Timeline (well, Sequence) from an Avid bin"""

	timeline_name:str
	"""The name of the sequence"""

	timeline_tc_range:TimecodeRange
	"""Start TC of sequence"""

	timeline_color:tuple[int,int,int]|None
	"""16-bit RGB triad chosen for the sequence color label"""

	date_created:datetime.datetime
	"""The date the sequence was last modified in the bin"""

	date_modified:datetime.datetime
	"""The date the sequence was last modified in the bin"""

	markers:list[avbutils.MarkerInfo]
	"""markers found in this reel"""

	bin_path:str
	"""Bin path"""

	bin_lock:avbutils.LockInfo|None
	"""Bin lock info if available"""

def get_timelines_from_bin(bin_path:str) -> list[TimelineInfo]:
	"""Given a Avid bin's file path, parse the bin and get sequence info"""

	timeline_info = []

	# Check for  lock first, why not
	bin_lock = avbutils.LockInfo(pathlib.Path(bin_path).with_suffix(".lck")) if pathlib.Path(bin_path).with_suffix(".lck").is_file() else None

	with avb.open(bin_path) as bin_handle:


		# avb.file.AVBFile -> avb.bin.Bin
		bin_contents = bin_handle.content
		
		# Get all sequences in bin
		timeline_compositions = avbutils.get_timelines_from_bin(bin_contents)

		# Sorting by sequence name with human sorting for version numbers
		for timeline in timeline_compositions:
			timeline_info.append(
				TimelineInfo(
					timeline_name     = timeline.name,
					timeline_color    = avbutils.composition_clip_color(timeline),
					date_created      = timeline.creation_time,
					date_modified     = timeline.last_modified,
					timeline_tc_range =	avbutils.get_timecode_range_for_composition(timeline),
					markers           = avbutils.get_markers_from_timeline(timeline),
					bin_path          = bin_path,
					bin_lock          = bin_lock
				)
			)
	
	return timeline_info