import sys, json
import avb
from lilbinboy.binview import jsonadapter, binviewitemtypes, binviewmodel

# GO ON, HACK ME
FIRST_OUTPUT  = "/Users/mjordan/Desktop/01_bin_to_json.json"
SECOND_OUTPUT = "/Users/mjordan/Desktop/02_json_to_json.json"
THIRD_OUTPUT  = "/Users/mjordan/Desktop/03_json_binmodel_roundtrip.json"

if __name__ == "__main__":

	if len(sys.argv) < 2:
	
		import pathlib
		sys.exit(f"Usage: {pathlib.Path(__file__).name} path/to/bin.avb")
	
	with avb.open(sys.argv[1]) as bin_handle:

		bin_view = binviewitemtypes.BSBinViewInfo.from_binview(bin_handle.content.view_setting)

	with open(FIRST_OUTPUT, "w") as json_handle:

		print(jsonadapter.BSBinViewJsonAdapter.from_binview(bin_view), file=json_handle)

	with open(FIRST_OUTPUT) as json_handle:

		bin_view = jsonadapter.BSBinViewJsonAdapter.to_binview(json_handle.read())

	with open(SECOND_OUTPUT,"w") as json_handle:

		print(jsonadapter.BSBinViewJsonAdapter.from_binview(bin_view), file=json_handle)

	with open(SECOND_OUTPUT) as json_handle:

		bin_view_model = binviewmodel.BSBinViewModel()
		bin_view_model.setBinViewInfo(jsonadapter.BSBinViewJsonAdapter.to_binview(json_handle.read()))
	
	with open(THIRD_OUTPUT, "w") as json_handle:

		print(jsonadapter.BSBinViewJsonAdapter.from_binview(bin_view_model.binViewInfo()), file=json_handle)