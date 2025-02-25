import uvloop

from .system import logger, system_config, diskcache
from .deus.base.base_instance import Deus
from .deus.athena.athena_instance import Athena
from .deus.base.base_instance import DeusAbstract


uvloop.install()


__all__ = [
    "logger",
    "system_config",
    "diskcache",
    "DeusAbstract",
    "Athena",
    "Deus",
]
