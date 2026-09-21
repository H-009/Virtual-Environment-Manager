from enum import Enum

# 贡献者
class ContributorKey(Enum):
    H009 = "H-009"

    def __str__(self):
        return self.value

# 仓库
class RepoKey(Enum):
    VEM = "Virtual-Environment-Manager"

    def __str__(self):
        return self.value
