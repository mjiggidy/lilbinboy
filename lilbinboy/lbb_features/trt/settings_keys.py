from enum import StrEnum

class TRTSettingsKeys(StrEnum):
	""".ini keys used for Runtime Metrics"""

	SEQ_SELECTION_MODE = "sequence_selection/selection_mode"
	SEQ_SELECTION_COL_NAME = "sequence_selection/sort_column_name"
	SEQ_SELECTION_COL_DIRECTION = "sequence_selection/sort_column_direction"
	SEQ_SELECTION_FILTERS = "sequence_selection/filters"

	LIST_FIELDS_ORDER = "list_view/columns_order"
	LIST_FIELDS_HIDDEN = "list_view/columns_hidden"

	LIST_SORT_FIELD = "list_view/sort_column"
	LIST_SORT_DIRECTION = "list_view/sort_order"

	MARKER_PRESETS_LIST = "marker_presets"

	TRIM_HEAD_MARKER = "trim_settings/trim_head_marker_preset"
	TRIM_HEAD_DURATION = "trim_settings/trim_head"

	
	TRIM_TAIL_MARKER = "trim_settings/trim_tail_marker_preset"
	TRIM_TAIL_DURATION = "trim_settings/trim_tail"
	
	TRIM_TOTAL_DURATION = "trim_settings/trim_total"

	BINS_LIST = "saved_state/bin_paths"
	LAST_BIN = "saved_state/last_bin"
	LAST_RATE = "saved_state/rate"