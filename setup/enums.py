import enum


class Regions(enum.Enum):
    USA = 1
    PAL = 2
    Japan = 3


class Languages(enum.Enum):
    Japan = 1
    English = 2
    Spanish = 3
    French = 4
    German = 5
    Italian = 6
    Dutch = 7
    Portuguese = 8
    Russian = 9


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
