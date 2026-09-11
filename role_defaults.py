# ============================================================
# ROLES DEFAULT
# ============================================================

DEFAULT_ROLES = [
    {
        "name": "Server",
        "slug": "server",
        "color": "2196f3",
    },
    {
        "name": "Storage",
        "slug": "storage",
        "color": "9e9e9e",
    },
    {
        "name": "Router",
        "slug": "router",
        "color": "4caf50",
    },
    {
        "name": "Switch",
        "slug": "switch",
        "color": "00bcd4",
    },
    {
        "name": "Firewall",
        "slug": "firewall",
        "color": "f44336",
    },
    {
        "name": "OLT",
        "slug": "olt",
        "color": "ff9800",
    },
    {
        "name": "Load Balancer",
        "slug": "load-balancer",
        "color": "9c27b0",
    },
    {
        "name": "Access Point",
        "slug": "access-point",
        "color": "795548",
    },
    {
        "name": "Wireless Controller",
        "slug": "wireless-controller",
        "color": "607d8b",
    },
    {
        "name": "Hypervisor",
        "slug": "hypervisor",
        "color": "3f51b5",
    },
    {
        "name": "Database",
        "slug": "database",
        "color": "673ab7",
    },
    {
        "name": "NAS",
        "slug": "nas",
        "color": "8bc34a",
    },
    {
        "name": "Console Server",
        "slug": "console-server",
        "color": "795548",
    },
    {
        "name": "Power",
        "slug": "power",
        "color": "ffc107",
    },
    {
        "name": "Virtual Machine",
        "slug": "virtual-machine",
        "color": "9c27b0",
    },
]


def obtener_roles_default() -> list[dict]:
    """
    Devuelve una copia del catálogo de Roles default.
    """

    return [
        rol.copy()
        for rol in DEFAULT_ROLES
    ]