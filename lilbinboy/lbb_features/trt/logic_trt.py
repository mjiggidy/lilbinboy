import avb, avbutils
import pathlib, concurrent.futures, datetime, dataclasses
from collections import namedtuple
from timecode import Timecode

# START CONFIG

# Durations of head/tail slates, will be factored out of TRT per reel
SLATE_HEAD_DURATION = Timecode("8:00")
"""The specified duration will be removed from reel durations and TRT calculations"""

SLATE_TAIL_DURATION = Timecode("3:23")
"""The specified duration will be removed from reel durations and TRT calculations"""

TRT_ADJUST_DURATION = Timecode("0:00")
"""Add or subtract a final duration from the total runtime (useful for adjusting for end credits, etc)"""

# How to sort sequences to find the "most current"
BIN_SORTING_METHOD = avbutils.BinSorting.DATE_MODIFIED
"""How to sort sequences in a bin to determine the most current one"""

REEL_NUMBER_BIN_COLUMN_NAME = "Reel #"
"""The name of the Avid bin column from which to extract the Reel Number"""

# Results list setup
COLUMN_SPACING = "     "
HEADERS = {
	"Reel Name"     : 0,
	"Reel TRT"      : 11,
	"LFOA"          : 7,
	"Date Modified" : 19,
	"Bin Locked"    : 10
}

# END CONFIG

USAGE = f"Usage: {__file__} path/to/avbs [--head {SLATE_HEAD_DURATION}] [--tail {SLATE_TAIL_DURATION}] [--trt-adjust {TRT_ADJUST_DURATION}]"

BinInfo = namedtuple("BinInfo","reel path lock")

@dataclasses.dataclass(frozen=True)
class AVBLocator:
	"Avid locator"

	locator_name:str
	locator_author:str
	locator_position:Timecode

@dataclasses.dataclass(frozen=True)
class ReelInfo:
	"""Representation of a Sequence from an Avid bin"""

	sequence_name:str = str()
	"""The name of the sequence"""

	duration_total:Timecode = Timecode(0)
	"""The total duration of the sequence"""

	date_modified:datetime.datetime = datetime.datetime.now()
	"""The date the sequence was last modified in the bin"""

	reel_number:int|None = None
	"""The number of the reel in the feature"""

	locators:list[AVBLocator]|None = None
	"""Locators found in this reel"""

def get_reel_number_from_timeline_attributes(attrs:avb.components.core.AVBPropertyData) -> str|None:
	"""Extract the 'Reel #' bin column data from a sequence's attributes.  Returns None if not set."""

	# Raise an exception if we weren't given property data.  Otherwise we'll treat failures as "that data just wasn't set"
	if not isinstance(attrs, avb.components.core.AVBPropertyData):
		raise ValueError(f"Expected AVBPropertyData, but got {type(attrs)} instead.")

	try:
		return attrs["_USER"][REEL_NUMBER_BIN_COLUMN_NAME]
	except KeyError:
		return None

def get_locators_from_sequence(sequence=avb.trackgroups.Composition):
	"""TODO: Return a list of `AVBLocator`s"""

	return list()

def get_reel_info(
	sequence:avb.trackgroups.Composition,
	head_duration:Timecode=SLATE_HEAD_DURATION,
	tail_duration:Timecode=SLATE_TAIL_DURATION) -> ReelInfo:
	"""Get the properties of a given sequence"""
	
	return ReelInfo(
		sequence_name=sequence.name,
		date_modified=sequence.last_modified,
		reel_number=get_reel_number_from_timeline_attributes(sequence.attributes),
		duration_total=Timecode(sequence.length, rate=round(sequence.edit_rate)),
		locators=get_locators_from_sequence(sequence)
	)

def get_reel_info_from_path(
	bin_path:pathlib.Path,
	head_duration:Timecode=SLATE_HEAD_DURATION,
	tail_duration:Timecode=SLATE_TAIL_DURATION,
	sort_by:avbutils.BinSorting=avbutils.BinSorting.NAME)-> ReelInfo:
	"""Given a Avid bin's file path, parse the bin and get the latest sequence info"""

	#print("Using",str(tail_duration))

	with avb.open(bin_path) as bin_handle:

		# avb.file.AVBFile -> avb.bin.Bin
		bin_contents = bin_handle.content
		
		# Get all sequences in bin
		sequences = avbutils.get_timelines_from_bin(bin_contents)

		# Sorting by sequence name with human sorting for version numbers
		try:
			latest_sequence = sorted(sequences, key=avbutils.BinSorting.get_sort_lambda(sort_by), reverse=True)[0]
		except IndexError:
			raise Exception(f"No sequences found in bin")
		
		# Get info from latest reel
		try:
			sequence_info = get_reel_info(latest_sequence, head_duration=head_duration, tail_duration=tail_duration)
		except Exception as e:
			raise Exception(f"Error parsing sequence: {e}")
	
	return sequence_info



def get_latest_stats_from_bins(bin_paths:list[pathlib.Path]) -> list[BinInfo]:
	"""Get stats for a list of bins"""

	parsed_info = []
	
	# Parse Bins Concurrently
	with concurrent.futures.ProcessPoolExecutor() as ex:

		# Create a dict associating a subprocess with the path of the bin it's working on
		future_info = {
			ex.submit(get_reel_info_from_path,
				bin_path=bin_path,
				head_duration=SLATE_HEAD_DURATION,
				tail_duration=SLATE_TAIL_DURATION,
				sort_by = BIN_SORTING_METHOD): bin_path for bin_path in bin_paths
		}

		# Process each result as it becomes available
		for future_result in concurrent.futures.as_completed(future_info):
			bin_path = future_info[future_result]

			try:
				info = future_result.result()
			except Exception as e:
				print(f"Skipping {bin_path.name}: {e}")
				continue

			lock = avbutils.get_lockfile_for_bin(bin_path)

			# Combine all the info
			parsed_info.append(BinInfo(
				reel = info,
				path = bin_path,
				lock = lock
			))
			
			# While we're here: Figure out the padding for the Reel Name column
			HEADERS["Reel Name"] = max(HEADERS.get("Reel Name",0), len(info.sequence_name))
	
	return parsed_info
	

def print_trts(parsed_info:list[BinInfo]):
	"""Print the results"""

	# List the results
	# This is terrible code but you get the idea
	print("")

	print(COLUMN_SPACING.join(colname.ljust(pad) for colname, pad in HEADERS.items()))
	print(COLUMN_SPACING.join('=' * pad for _, pad in HEADERS.items()))

	for info in sorted(parsed_info, key=lambda x: avbutils.human_sort(x.reel.sequence_name)):
		print(COLUMN_SPACING.join(x for x in [
			info.reel.sequence_name.ljust(HEADERS.get("Reel Name")),
			str(info.reel.duration_adjusted).rjust(HEADERS.get("Reel TRT")),
			info.reel.lfoa.rjust(HEADERS.get("LFOA")),
			str(info.reel.date_modified).rjust(HEADERS.get("Date Modified")),
			info.lock.ljust(HEADERS.get("Bin Locked")) if info.lock else '-',
		]))
	
	if TRT_ADJUST_DURATION.frame_number != 0:
		print("")
		print(f"+ Additional adjustment: {TRT_ADJUST_DURATION}")
	
	print("")
	print(f"* Total Runtime: {max(sum(info.reel.duration_adjusted for info in parsed_info) + TRT_ADJUST_DURATION, 0)}")
	print("")