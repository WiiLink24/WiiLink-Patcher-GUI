import enum


class Regions(enum.Enum):
    USA = 0
    PAL = 1
    Japan = 2


class Languages(enum.Enum):
    Japan = 0
    English = 1
    Spanish = 2
    French = 3
    German = 4
    Italian = 5
    Dutch = 6
    Portuguese = 7
    Russian = 8


class DemaeConfigs(enum.Enum):
    Standard = 0
    Dominos = 1


class Platforms(enum.Enum):
    Wii = 0
    vWii = 1
    Dolphin = 2


class SetupTypes(enum.Enum):
    Express = 0
    Custom = 1
    Extras = 2


class WFCNetworks(enum.Enum):
    Wiimmfi = 0
    WWFC = 1


class ChannelTypes(enum.Enum):
    WiiConnect24 = 0
    Regional = 1
    WFC = 2
