import sys
import avb, avbutils, timecode

import enum

class TimecodeTrackRoles(enum.Enum):
	
	MASTER = 1

	AUX_TC_1 = 3
	AUX_TC_2 = 4
	AUX_TC_3 = 5
	AUX_TC_4 = 6
	AUX_TC_5 = 7
	AUX_TC_6 = 8

	AUX_TC_24 = 12


def inspect_timecode_component(timecode_component:avb.components.Timecode):

	rate  = timecode_component.fps
	frame = timecode_component.start
	lenth = timecode_component.length
	
	return timecode.TimecodeRange(
		start=timecode.Timecode(frame, rate=rate),
		duration=lenth
	)



if __name__ == "__main__":

	if not len(sys.argv) > 1:

		import pathlib
		
		sys.exit(f"Usage: {pathlib.Path(__file__).name} binfile.avb")
	
	for bin_path in sys.argv[1:]:

		print(bin_path)

		with avb.open(bin_path) as bin_handle:

			bin_contents = bin_handle.content

			for item in bin_contents.items:
				
				print(item.mob)

				for track in item.mob.tracks:

	#				if not track.media_kind == "timecode":
	#					continue

					

					tc_component = track.component

					if track.media_kind == "timecode" and isinstance(tc_component, avb.components.Timecode):

						print("STD TC:", TimecodeTrackRoles(track.index), inspect_timecode_component(tc_component))
					
					elif track.media_kind == "timecode" and isinstance(tc_component, avb.components.Sequence):

						#print(tc_component.property_data)

						
						if len(tc_component.components) == 1:

							print("AUX TC:", TimecodeTrackRoles(track.index), "EMPTY")
							continue
						
						elif not len(tc_component.components) == 3:

							print("WEIRD", tc_component.components)
							continue

						print("AUX TC:", TimecodeTrackRoles(track.index),inspect_timecode_component(tc_component.components[1]))

					else:
						print("OTHER :", track.index)

