
from __future__ import annotations
import json, abc, typing
from . import binviewitemtypes

CURRENT_VERSION = "1.0"

class BSBinViewAbstractAdapter(abc.ABC):

	@abc.abstractmethod
	def from_binview(self, binview_info:binviewitemtypes.BSBinViewInfo) -> typing.Any:
		"""Export a binview to this format"""

	@abc.abstractmethod
	def to_binview(self, from_source:typing.Any):
		"""Import from source to a binview"""

class BSBinViewJsonAdapter(BSBinViewAbstractAdapter):
	"""JSON Importer/Exporter for a binview"""

	DEFAULT_FILE_EXTENSION = ".json"

	def from_binview(self, binview_info:binviewitemtypes.BSBinViewInfo) -> str:
		"""Return a JSON-formatted string  representing a given `BSBinViewInfo`"""

		return json.dumps({
			"name": binview_info.name,
			"version": CURRENT_VERSION,
			"columns": [h.to_json_dict() for h in binview_info.columns]
		}, indent="\t")
	
	def to_binview(self, json_string:str) -> binviewitemtypes.BSBinViewInfo:
		"""Return a `BSBinViewInfo` object from a given binview JSON string"""

		binview_parsed = json.loads(json_string)

		if binview_parsed.get("version") != CURRENT_VERSION:
			raise ValueError("Unsupported binview json version")
		
		return binviewitemtypes.BSBinViewInfo(
			name    = binview_parsed.get("name", "NoName"),
			columns = [self._column_from_json(col) for col in binview_parsed.get("columns",[])]
		)
	
	def _column_from_json(self, column_json:str) -> binviewitemtypes.BSBinViewColumnInfo:
		"""Column info from JSON string"""

		import avbutils

		return binviewitemtypes.BSBinViewColumnInfo(
			field_id     = avbutils.bins.BinColumnFieldIDs[column_json["field_id"]],
			format_id    = avbutils.bins.BinColumnFormat[column_json["format_id"]],
			display_name = column_json["display_name"],
			is_hidden    = bool(column_json["is_hidden"])
		)