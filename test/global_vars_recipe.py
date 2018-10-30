from hpccm.common import container_type

if hpccm.config.g_ctype != container_type.SINGULARITY:
    raise Exception("Global variable g_ctype not set correctly!")
