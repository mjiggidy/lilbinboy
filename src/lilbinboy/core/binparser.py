"""
Functions for creating and returning data model items from a bin
Also used by `.binloader`
"""

import avb, avbutils, timecode
from ..binitems import binitemtypes, timecoderoles
from ..binview  import binviewitemtypes
from ..binfilters.siftfilter import sifters, siftmatchtypes
from ..siftwidget import rangesmodel

def resolve_timecode_component_for_compositiion(mob:avb.trackgroups.Composition, track:avb.trackgroups.Track|None=None, timecode_role:avbutils.timeline.TimecodeTrackRoles=avbutils.timeline.TimecodeTrackRoles.MASTER_TC, offset:int=0):

	if not track:

		track = avbutils.sourcerefs.primary_track_for_composition(mob)

	try:
	
		# Look for track in mob
		timecode_track = next(avbutils.timeline.get_tracks_from_composition(mob, type=avbutils.timeline.TrackTypes.TIMECODE, index=int(timecode_role)))
		return avbutils.sourcerefs.resolve_base_component_from_component(timecode_track.component, offset=offset)
	
	except StopIteration:

		# Resolve the track component and look in thurr
		source_component, next_offset = avbutils.sourcerefs.resolve_base_component_from_component(track.component, offset)

		if not isinstance(source_component, avb.components.SourceClip):

			print("Got down to ", source_component)
			return None, next_offset
		
		return resolve_timecode_component_for_compositiion(mob=source_component.mob, track=source_component.track, timecode_role=timecode_role, offset=next_offset)
	
def get_timecode_start(timecodes:dict[avbutils.timeline.TimecodeTrackRoles, timecode.TimecodeRange], role:avbutils.timeline.TimecodeTrackRoles) -> timecode.Timecode | str:

	if role in timecodes:
		return timecodes[role].start
	return ""

def bin_display_flags_from_bin(bin_content:avb.bin.Bin) -> avbutils.BinDisplayItemTypes:
	return avbutils.BinDisplayItemTypes.get_options_from_bin(bin_content)
	
def bin_view_setting_from_bin(bin_content:avb.bin.Bin) -> binviewitemtypes.BSBinViewInfo:
		
	return binviewitemtypes.BSBinViewInfo.from_binview(bin_content.view_setting)

def bin_frame_view_scale_from_bin(bin_content:avb.bin.Bin) -> int:
	"""Get the Frame view mode scale"""

	return bin_content.mac_image_scale

def bin_scipt_view_scale_from_bin(bin_content:avb.bin.Bin) -> int:
	"""Get the Script view mode scale"""

	return bin_content.ql_image_scale

def bin_column_widths_from_bin(bin_content:avb.bin.Bin) -> dict[str, int]:
	"""Decode bin column widths"""

	try:
		import json
		bin_column_widths = json.loads(bin_content.attributes.get("BIN_COLUMNS_WIDTHS",{}).decode("utf-8"))
	except Exception as e:
		#print(e)
		bin_column_widths = {}
	
	return bin_column_widths
	
def sift_settings_from_bin(bin_content:avb.bin.Bin, view_setting:binviewitemtypes.BSBinViewInfo) -> list[list[sifters.BSAbstractSifter]]:
	return sifters.BSAbstractSifter.sift_settings_from_bin(bin_content, view_setting)
	
def sort_settings_from_bin(bin_content:avb.bin.Bin) -> list[list[int, str]]:
	return bin_content.sort_columns

def display_mode_from_bin(bin_content:avb.bin.Bin) -> avbutils.BinDisplayModes:
	"""Load the display mode"""

	return avbutils.BinDisplayModes.get_mode_from_bin(bin_content)

def appearance_settings_from_bin(bin_content:avb.bin.Bin) -> tuple:
	"""General and misc appearance settings stored around the bin"""

	# Sus out that font name
	# Try for Bin Font Name (strongly preferred), or fall back on mac font index (not likely to work)
	if "attributes" in bin_content.property_data and "ATTR__BIN_FONT_NAME" in bin_content.attributes:
		bin_font = bin_content.attributes["ATTR__BIN_FONT_NAME"]
	else:
		bin_font = bin_content.mac_font

	# SKIP: This is now handled via binview.  Need to update the signal here
	bin_column_widths = {}

	return (
		bin_font,
		bin_content.mac_font_size,
		bin_content.forground_color,
		bin_content.background_color,
		bin_column_widths,
		bin_content.home_rect,
		bin_content.was_iconic,
	)

def load_item_from_bin(bin_item:avb.bin.BinItem) -> binitemtypes.BSBinItemInfo:
		"""Parse a mob and its bin item properties"""

		
		comp:avb.trackgroups.Composition = bin_item.mob

		# Get frame scale to normalize frame coords below

		# NOTE BOUD DIS:
		
		# The bin seems to store x,y coords of the THUMBNAIL specifically
		# (not the whole "item" with padding, margins, outline, label, etc)
		# These coordinates are stored PREMULTIPLEID by the zoom factor

		# I'm preferring to normalize these coordinates to zoom=1.0 and top-left
		# coordinates refer to the top-left of the item proper

		# This is still very TODO

		frame_scale_x = bin_frame_view_scale_from_bin(bin_item.root.content)
		frame_scale_y = 74 + ((frame_scale_x - avbutils.bins.THUMB_FRAME_MODE_RANGE.start) * 10)
		mob_coords= ((bin_item.x-16) / frame_scale_x, (bin_item.y-16) / frame_scale_y * 14) 	# Y Unit * 14 height?
		
		# Initial data model info
		mob_id    = comp.mob_id
		mob_types = avbutils.BinDisplayItemTypes.from_bin_item(bin_item)
		mob_tracks= avbutils.timeline.get_tracks_from_composition(comp)
		mob_name  = comp.name
		mob_color = avbutils.compositions.composition_clip_color(comp)
		mob_frame = bin_item.keyframe

		# Prep defaults
		# TODO: Should be at least, like, some sort of struct
		tape_name = None
		source_file_name = None

		timecode_ranges = {}

#		timecode_range = None #TAKE THIS OUT
		
		
		user_attributes = dict()
		source_drive = None

		mark_in    = None
		mark_out   = None
		mark_range = None

		if avbutils.BinDisplayItemTypes.SEQUENCE in mob_types:
			master_timecode_range = avbutils.get_timecode_range_for_composition(comp)

			if master_timecode_range:
				timecode_ranges[timecoderoles.BSTimecodeTrackRoles.MASTER_TC] = master_timecode_range

			user_attributes = comp.attributes.get("_USER",{})

		else:

			if avbutils.sourcerefs.composition_has_physical_source(comp):
			
				if avbutils.sourcerefs.physical_source_type_for_composition(comp) == avbutils.SourceMobRole.SOURCE_FILE:
					source_file_name = avbutils.sourcerefs.physical_source_name_for_composition(comp)
				else:
					tape_name = avbutils.sourcerefs.physical_source_name_for_composition(comp)
			
			# Drive info
			if "descriptor" in comp.property_data and isinstance(comp.descriptor, avb.essence.MediaDescriptor) and isinstance(comp.descriptor.locator, avb.misc.MSMLocator):
				source_drive = comp.descriptor.locator.last_known_volume
			else:
				try:
				# TODO: Do if comp itself is file source first, otherwise...
					file_source_clip, offset = next(avbutils.file_references_for_component(avbutils.primary_track_for_composition(comp).component))
				except StopIteration as e:
					#print("No file soruce:",comp)
					pass
				else:
					if isinstance(file_source_clip.mob.descriptor.locator, avb.misc.MSMLocator):
						source_drive = file_source_clip.mob.descriptor.locator.last_known_volume
						#print(source_drive)
			
			# Timecode
			# NOTE: This is all pretty sloppy here.
			try:
				master_timecode_range = avbutils.get_timecode_range_for_composition(comp)
				if master_timecode_range:
					timecode_ranges[timecoderoles.BSTimecodeTrackRoles.MASTER_TC] = master_timecode_range
			except Exception as e:
				pass

			# NOTE: UNRELIABLE
			if timecoderoles.BSTimecodeTrackRoles.MASTER_TC in timecode_ranges and "attributes" in comp.property_data:

				master_timecode_range = timecode_ranges[timecoderoles.BSTimecodeTrackRoles.MASTER_TC]
				mark_in = master_timecode_range.start + timecode.Timecode(comp.attributes.get("_IN"), rate=master_timecode_range.rate)   if "_IN"  in comp.attributes else None
#				print("***", comp.name, mark_in)
				mark_out = master_timecode_range.start + timecode.Timecode(comp.attributes.get("_OUT"), rate=master_timecode_range.rate) if "_OUT" in comp.attributes else None
#				print("***", mark_out)
				if mark_in and mark_out and mark_in < mark_out:
					mark_range = timecode.TimecodeRange(start=mark_in, end=mark_out)




			attributes_reverse = []
			for source, offset in avbutils.source_references_for_component(avbutils.sourcerefs.primary_track_for_composition(comp).component):
				
				if "attributes" in source.mob.property_data:
					attributes_reverse.append(source.mob.attributes.get("_USER",{}))
				
				# Timecode

				for tc_role in avbutils.timeline.TimecodeTrackRoles:

					tc_component, offset = resolve_timecode_component_for_compositiion(comp, timecode_role=tc_role, offset=offset + source.start_time)
					
					if not isinstance(tc_component, avb.components.Timecode):
						import logging
						logging.getLogger(__name__).error("Got weird TC component for %s: %s", mob_name,tc_component)
						continue
					
					# NOTE: Maybe need to adjust offset.frame_number * tc_component.fps/offset.fps?
					master_timecode_range = timecode.TimecodeRange(
						start = timecode.Timecode(tc_component.start + offset.frame_number, rate=tc_component.fps),
						duration=comp.length
					)

					timecode_ranges[tc_role] = master_timecode_range

			for a in reversed(attributes_reverse):
				user_attributes.update(a)
			if "attributes" in comp.property_data:
				user_attributes.update(comp.attributes.get("_USER",{}))

		try:
			marker = next(avbutils.get_markers_from_timeline(comp))
		except StopIteration:
			marker = None

		master_timecode_range = timecode_ranges.get(avbutils.timeline.TimecodeTrackRoles.MASTER_TC, None)

		item = {
			avbutils.bins.BinColumnFieldIDs.Name:         binitemtypes.BSStringViewItem(mob_name),
			avbutils.bins.BinColumnFieldIDs.Color:        binitemtypes.BSClipColorViewItem(mob_color),
			avbutils.bins.BinColumnFieldIDs.Start:        binitemtypes.get_viewitem_for_item(get_timecode_start(timecode_ranges, avbutils.timeline.TimecodeTrackRoles.MASTER_TC)),
			avbutils.bins.BinColumnFieldIDs.AuxiliaryTC1: binitemtypes.get_viewitem_for_item(get_timecode_start(timecode_ranges, avbutils.timeline.TimecodeTrackRoles.AUX_TC_1)),
			avbutils.bins.BinColumnFieldIDs.AuxiliaryTC2: binitemtypes.get_viewitem_for_item(get_timecode_start(timecode_ranges, avbutils.timeline.TimecodeTrackRoles.AUX_TC_2)),
			avbutils.bins.BinColumnFieldIDs.AuxiliaryTC3: binitemtypes.get_viewitem_for_item(get_timecode_start(timecode_ranges, avbutils.timeline.TimecodeTrackRoles.AUX_TC_3)),
			avbutils.bins.BinColumnFieldIDs.AuxiliaryTC4: binitemtypes.get_viewitem_for_item(get_timecode_start(timecode_ranges, avbutils.timeline.TimecodeTrackRoles.AUX_TC_4)),
			avbutils.bins.BinColumnFieldIDs.AuxiliaryTC5: binitemtypes.get_viewitem_for_item(get_timecode_start(timecode_ranges, avbutils.timeline.TimecodeTrackRoles.AUX_TC_5)),
			avbutils.bins.BinColumnFieldIDs.TC24:         binitemtypes.get_viewitem_for_item(get_timecode_start(timecode_ranges, avbutils.timeline.TimecodeTrackRoles.TC_24)),
			avbutils.bins.BinColumnFieldIDs.TC25:         binitemtypes.get_viewitem_for_item(get_timecode_start(timecode_ranges, avbutils.timeline.TimecodeTrackRoles.TC_25)),
			avbutils.bins.BinColumnFieldIDs.AuxTC24:      binitemtypes.get_viewitem_for_item(get_timecode_start(timecode_ranges, avbutils.timeline.TimecodeTrackRoles.AUX_TC_2)),
			avbutils.bins.BinColumnFieldIDs.TC30NP:       binitemtypes.get_viewitem_for_item(get_timecode_start(timecode_ranges, avbutils.timeline.TimecodeTrackRoles.TC_30NP,)),
			avbutils.bins.BinColumnFieldIDs.End:          binitemtypes.get_viewitem_for_item(master_timecode_range.end if master_timecode_range else ""),
			avbutils.bins.BinColumnFieldIDs.Duration:     binitemtypes.BSDurationViewItem(master_timecode_range.duration) if master_timecode_range else binitemtypes.BSStringViewItem(""),
			avbutils.bins.BinColumnFieldIDs.ModifiedDate: binitemtypes.get_viewitem_for_item(comp.last_modified),
			avbutils.bins.BinColumnFieldIDs.CreationDate: binitemtypes.get_viewitem_for_item(comp.creation_time),
			avbutils.bins.BinColumnFieldIDs.BinItemIcon:  binitemtypes.get_viewitem_for_item(mob_types),
			avbutils.bins.BinColumnFieldIDs.Marker:       binitemtypes.BSMarkerViewItem(marker),
			avbutils.bins.BinColumnFieldIDs.Tracks:       binitemtypes.BSStringViewItem(avbutils.timeline.format_track_labels(mob_tracks) or None),
			avbutils.bins.BinColumnFieldIDs.Tape:         binitemtypes.get_viewitem_for_item(tape_name or ""),
			avbutils.bins.BinColumnFieldIDs.Drive:        binitemtypes.get_viewitem_for_item(source_drive or ""),
			avbutils.bins.BinColumnFieldIDs.SourceFile:   binitemtypes.get_viewitem_for_item(source_file_name or ""),
			avbutils.bins.BinColumnFieldIDs.SourcePath:   binitemtypes.get_viewitem_for_item(user_attributes.get("Scene") or ""),
			avbutils.bins.BinColumnFieldIDs.Take:         binitemtypes.get_viewitem_for_item(user_attributes.get("Take") or ""),
			avbutils.bins.BinColumnFieldIDs.Labroll:      binitemtypes.get_viewitem_for_item(user_attributes.get("Labroll") or ""),
			avbutils.bins.BinColumnFieldIDs.Soundroll:    binitemtypes.get_viewitem_for_item(user_attributes.get("Soundroll") or ""),
			avbutils.bins.BinColumnFieldIDs.Camroll:      binitemtypes.get_viewitem_for_item(user_attributes.get("Camroll") or ""),
			avbutils.bins.BinColumnFieldIDs.FPS:          binitemtypes.get_viewitem_for_item(user_attributes.get("FPS") or ""),
			avbutils.bins.BinColumnFieldIDs.SoundTC:      binitemtypes.get_viewitem_for_item(user_attributes.get("Sound TC") or ""),
			avbutils.bins.BinColumnFieldIDs.ShootDate:    binitemtypes.get_viewitem_for_item(user_attributes.get("Shoot Date") or ""),
			avbutils.bins.BinColumnFieldIDs.AudioSR:      binitemtypes.get_viewitem_for_item(user_attributes.get("Audio SR") or ""),
			avbutils.bins.BinColumnFieldIDs.MarkIn:       binitemtypes.get_viewitem_for_item(mark_in or ""),
			avbutils.bins.BinColumnFieldIDs.MarkOut:      binitemtypes.get_viewitem_for_item(mark_out or ""),
			avbutils.bins.BinColumnFieldIDs.InOut:        binitemtypes.BSDurationViewItem(mark_range.duration) if mark_range else binitemtypes.BSStringViewItem(""),
		}

		for k,v in user_attributes.items():
			user_attributes[k] = binitemtypes.BSStringViewItem(v)

		# New
		item.update({40: user_attributes})

		# Package timecodes

		print(timecode_ranges)
		
		return binitemtypes.BSBinItemInfo(
			name = mob_name,
			item_type = mob_types,
			view_items = item,
			frame_coordinates = mob_coords,
			keyframe_offset   = mob_frame,
			mob_id = mob_id,
			tracks=mob_tracks,
			clip_color=mob_color,
			timecodes=timecode_ranges
		)
