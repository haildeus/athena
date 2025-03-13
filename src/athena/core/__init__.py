import uvloop

from .deus.athena.athena_instance import Athena
from .deus.base.base_instance import Deus, DeusAbstract
from .system import diskcache, logger, system_config

uvloop.install()


__all__ = [
    "logger",
    "system_config",
    "diskcache",
    "DeusAbstract",
    "Athena",
    "Deus",
]
