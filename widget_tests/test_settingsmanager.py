from PySide6 import QtWidgets
from lilbinboy import Config
from lilbinboy.lbb_common.settings_manager import LBSettingsManager

app = QtWidgets.QApplication()
app.setOrganizationName(Config.ORG_NAME)
app.setOrganizationDomain(Config.ORG_DOMAIN)
app.setApplicationName(Config.APP_NAME)
app.setApplicationVersion(Config.APP_VERSION)

settings_manager = LBSettingsManager()

print(f"Settings manager created at {settings_manager.basePath().toLocalFile()} as {settings_manager.format()}")

settings = settings_manager.settings("testy")
print(f"Created {settings} at {settings.fileName()}")