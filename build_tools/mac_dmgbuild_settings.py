format = "UDBZ" # TODO: Investigate UDZO
files = ["build/Lil' Bin Boy.app"]
symlinks = { "Applications": "/Applications" }

badge_icon = "build_tools/icons/macos_lilbinboy.icns"
icon_locations = {
	"Lil' Bin Boy.app": (135, 160),
	"Applications": (500, 160)
}

background = "build_tools/bkgs/macos_dmg_bkg.tiff"
widow_rect = (800, 800, 800, 400)

show_status_bar = False
show_tab_view   = False
show_toolbar    = False
show_pathbar    = False
show_sidebar    = False

default_view = "icon-view"
icon_size = 128

license = {
	"default-language": "en_US",
	"licenses": {
		"en_US": "EULA"
	}
}