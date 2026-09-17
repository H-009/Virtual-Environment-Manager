from enum import Enum
from qfluentwidgets import FluentIconBase, Theme, getIconColor

class MetaverseFluentIcon(FluentIconBase, Enum):
    Web = "Web"
    DownloadList = "DownloadList"
    Link = "Link"
    Installation = "Installation"
    Terminal = "Terminal"
    List = "List"
    PaperClip = "PaperClip"
    Qt = "Qt"

    def path(self, theme=Theme.AUTO):
        return f":/MetaverseFluentIcon/{self.value}_{getIconColor(theme)}.svg"