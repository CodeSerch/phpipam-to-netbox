from pathlib import Path

import pandas as pd

from analyzer import leer_csv, buscar_archivo

from role_defaults import obtener_roles_default

from converters.manufacturers import convertir_manufacturers
from converters.roles import convertir_roles
from converters.device_types import convertir_device_types
from converters.devices import convertir_devices
from converters.vlans import convertir_vlans
from converters.prefixes import convertir_prefixes
from converters.ip_addresses import convertir_ip_addresses
from converters.vrfs import convertir_vrfs


# ============================================================
# ARCHIVOS PHPIPAM
# ============================================================

ARCHIVOS_ESPERADOS = {
    "Devices": "*_devices_export.csv",
    "Device Types": "*_deviceTypes_export.csv",
    "IP Addresses": "*_ip_address_export.csv",
    "Subnets": "*_subnets_export.csv",
    "VLAN": "*_VLAN_export.csv",
    "VRF": "*_VRF_export.csv",
}


# ============================================================
# PROGRESO
# ============================================================

def actualizar_progreso(
    callback,
    porcentaje: int,
    mensaje: str,
):
    """
    Envía el progreso a la interfaz si existe un callback.
    """

    if callback is not None:

        callback(
            porcentaje,
            mensaje,
        )


# ============================================================
# UTILIDADES
# ============================================================

def normalizar_valor(
    valor,
) -> str:

    if valor is None:
        return ""

    return str(
        valor
    ).strip()


def cargar_archivos(
    carpeta_origen: str | Path,
    progress_callback=None,
) -> dict[str, pd.DataFrame]:
    """
    Carga los CSV de phpIPAM necesarios para la conversión.
    """

    carpeta = Path(
        carpeta_origen
    )

    datos = {}

    total = len(
        ARCHIVOS_ESPERADOS
    )

    for indice, (tipo, patron) in enumerate(
        ARCHIVOS_ESPERADOS.items(),
        start=1,
    ):

        porcentaje = int(
            (indice / total) * 15
        )

        actualizar_progreso(
            progress_callback,
            porcentaje,
            f"Cargando {tipo}...",
        )

        archivo = buscar_archivo(
            carpeta,
            patron,
        )

        if archivo is None:
            continue

        datos[tipo] = leer_csv(
            archivo
        )

    return datos


# ============================================================
# MANUFACTURERS
# ============================================================

def preparar_manufacturers(
    analisis: dict,
) -> list[str]:
    """
    Obtiene los Manufacturers resueltos durante el análisis.

    No vuelve a ejecutar manufacturer_finder.
    """

    resultados = (
        analisis
        .get(
            "manufacturers",
            {},
        )
        .get(
            "resultados",
            [],
        )
    )

    manufacturers = set()

    for resultado in resultados:

        manufacturer = normalizar_valor(
            resultado.get(
                "manufacturer",
                "",
            )
        )

        if manufacturer:

            manufacturers.add(
                manufacturer
            )

    return sorted(
        manufacturers
    )


# ============================================================
# ROLES
# ============================================================

def preparar_roles(
    analisis: dict,
) -> list[dict]:
    """
    Obtiene los Roles recomendados durante el análisis.

    Utiliza los colores definidos en role_defaults.py.
    """

    roles_detectados = (
        analisis
        .get(
            "roles",
            {},
        )
        .get(
            "roles_detectados",
            [],
        )
    )

    roles_default = obtener_roles_default()

    colores = {
        role["name"].lower(): role["color"]
        for role in roles_default
    }

    roles = {}

    for item in roles_detectados:

        role_name = normalizar_valor(
            item.get(
                "role",
                "",
            )
        )

        if not role_name:
            continue

        color = colores.get(
            role_name.lower(),
            "",
        )

        roles[
            role_name.lower()
        ] = {
            "name": role_name,
            "slug": "",
            "color": color,
        }

    return list(
        roles.values()
    )


# ============================================================
# DEVICE TYPES
# ============================================================

def preparar_device_types(
    analisis: dict,
    datos: dict[str, pd.DataFrame],
) -> list[dict]:
    """
    Convierte Device Types de phpIPAM.

    El Manufacturer se obtiene del análisis previo.
    """

    df = datos.get(
        "Device Types"
    )

    if df is None:
        return []

    manufacturer_index = {}

    resultados_manufacturers = (
        analisis
        .get(
            "manufacturers",
            {},
        )
        .get(
            "resultados",
            [],
        )
    )

    for resultado in resultados_manufacturers:

        tipo = normalizar_valor(
            resultado.get(
                "original",
                "",
            )
        )

        manufacturer = normalizar_valor(
            resultado.get(
                "manufacturer",
                "",
            )
        )

        if tipo:

            manufacturer_index[
                tipo.lower()
            ] = manufacturer

    registros = []

    for _, fila in df.iterrows():

        model = normalizar_valor(
            fila.get(
                "Name",
                "",
            )
        )

        description = normalizar_valor(
            fila.get(
                "Description",
                "",
            )
        )

        if not model:
            continue

        manufacturer = manufacturer_index.get(
            model.lower(),
            "",
        )

        registros.append(
            {
                "manufacturer": manufacturer,
                "model": model,
                "slug": "",
                "part_number": "",
                "u_height": "0",
                "is_full_depth": "",
                "airflow": "",
                "weight": "",
                "weight_unit": "",
                "comments": description,
                "tags": "",
            }
        )

    return registros


# ============================================================
# DEVICES
# ============================================================

def preparar_devices(
    datos: dict[str, pd.DataFrame],
) -> list[dict]:
    """
    Convierte Devices de phpIPAM.
    """

    df = datos.get(
        "Devices"
    )

    if df is None:
        return []

    registros = []

    for _, fila in df.iterrows():

        hostname = normalizar_valor(
            fila.get(
                "hostname",
                "",
            )
        )

        device_type = normalizar_valor(
            fila.get(
                "type",
                "",
            )
        )

        description = normalizar_valor(
            fila.get(
                "description",
                "",
            )
        )

        rack = normalizar_valor(
            fila.get(
                "rack",
                "",
            )
        )

        registros.append(
            {
                "name": hostname,
                "device_type": device_type,
                "status": "active",
                "location": "",
                "rack": rack,
                "position": "",
                "face": "",
                "serial": "",
                "asset_tag": "",
                "description": description,
                "comments": "",
                "platform": "",
                "tags": "",
            }
        )

    return registros


# ============================================================
# VLANS
# ============================================================

def preparar_vlans(
    datos: dict[str, pd.DataFrame],
) -> list[dict]:

    df = datos.get(
        "VLAN"
    )

    if df is None:
        return []

    registros = []

    for _, fila in df.iterrows():

        registros.append(
            {
                "vid": normalizar_valor(
                    fila.get(
                        "Number",
                        "",
                    )
                ),
                "name": normalizar_valor(
                    fila.get(
                        "Name",
                        "",
                    )
                ),
                "status": "active",
                "group": "",
                "site": "",
                "tenant": "",
                "role": "",
                "description": normalizar_valor(
                    fila.get(
                        "Description",
                        "",
                    )
                ),
                "comments": "",
                "tags": "",
            }
        )

    return registros


# ============================================================
# PREFIXES
# ============================================================

def preparar_prefixes(
    datos: dict[str, pd.DataFrame],
) -> list[dict]:

    df = datos.get(
        "Subnets"
    )

    if df is None:
        return []

    registros = []

    for _, fila in df.iterrows():

        registros.append(
            {
                "prefix": normalizar_valor(
                    fila.get(
                        "Subnet",
                        "",
                    )
                ),
                "status": "active",
                "vrf": normalizar_valor(
                    fila.get(
                        "VRF",
                        "",
                    )
                ),
                "tenant": "",
                "vlan": "",
                "role": "",
                "site": "",
                "description": normalizar_valor(
                    fila.get(
                        "Description",
                        "",
                    )
                ),
                "comments": "",
                "tags": "",
            }
        )

    return registros


# ============================================================
# IP ADDRESSES
# ============================================================

def preparar_ip_addresses(
    datos: dict[str, pd.DataFrame],
) -> list[dict]:

    df = datos.get(
        "IP Addresses"
    )

    if df is None:
        return []

    registros = []

    for _, fila in df.iterrows():

        registros.append(
            {
                "address": normalizar_valor(
                    fila.get(
                        "IP Address",
                        "",
                    )
                ),
                "status": "active",
                "vrf": normalizar_valor(
                    fila.get(
                        "VRF",
                        "",
                    )
                ),
                "dns_name": normalizar_valor(
                    fila.get(
                        "Hostname",
                        "",
                    )
                ),
                "description": normalizar_valor(
                    fila.get(
                        "Description",
                        "",
                    )
                ),
                "comments": "",
                "role": "",
                "tenant": "",
                "tags": "",
            }
        )

    return registros


# ============================================================
# VRFS
# ============================================================

def preparar_vrfs(
    datos: dict[str, pd.DataFrame],
) -> list[dict]:

    df = datos.get(
        "VRF"
    )

    if df is None:
        return []

    registros = []

    for _, fila in df.iterrows():

        registros.append(
            {
                "name": normalizar_valor(
                    fila.get(
                        "Name",
                        "",
                    )
                ),
                "rd": normalizar_valor(
                    fila.get(
                        "RD",
                        "",
                    )
                ),
                "enforce_unique": "",
                "description": normalizar_valor(
                    fila.get(
                        "Description",
                        "",
                    )
                ),
                "comments": "",
                "tags": "",
            }
        )

    return registros


# ============================================================
# CONVERSIÓN PRINCIPAL
# ============================================================

def convertir_exportacion(
    carpeta_origen: str | Path,
    carpeta_destino: str | Path,
    site: str,
    roles_por_tipo: dict[str, str],
    analisis: dict,
    progress_callback=None,
) -> dict:
    """
    Convierte una exportación phpIPAM utilizando
    el resultado del análisis previamente ejecutado.

    El análisis NO se vuelve a ejecutar.

    progress_callback:
        función(porcentaje, mensaje)
    """

    origen = Path(
        carpeta_origen
    )

    destino = Path(
        carpeta_destino
    )

    # --------------------------------------------------------
    # VALIDAR ORIGEN
    # --------------------------------------------------------

    if not origen.exists():

        raise FileNotFoundError(
            f"La carpeta de origen no existe: {origen}"
        )

    if not origen.is_dir():

        raise NotADirectoryError(
            f"La ruta de origen no es una carpeta: {origen}"
        )

    # --------------------------------------------------------
    # VALIDAR SITE
    # --------------------------------------------------------

    site = normalizar_valor(
        site
    )

    if not site:

        raise ValueError(
            "El Site de destino es obligatorio."
        )

    # --------------------------------------------------------
    # VALIDAR ANÁLISIS
    # --------------------------------------------------------

    if not analisis:

        raise ValueError(
            "No existe un análisis válido. "
            "Ejecutá primero el análisis."
        )

    # --------------------------------------------------------
    # CREAR DESTINO
    # --------------------------------------------------------

    destino.mkdir(
        parents=True,
        exist_ok=True,
    )

    actualizar_progreso(
        progress_callback,
        2,
        "Preparando conversión...",
    )

    # --------------------------------------------------------
    # CARGAR DATOS
    # --------------------------------------------------------

    datos = cargar_archivos(
        origen,
        progress_callback,
    )

    # ========================================================
    # MANUFACTURERS
    # ========================================================

    actualizar_progreso(
        progress_callback,
        20,
        "Generando manufacturers.csv...",
    )

    manufacturers = preparar_manufacturers(
        analisis
    )

    if manufacturers:

        resultados_manufacturers = (
            convertir_manufacturers(
                manufacturers,
                destino,
            )
        )

    else:

        resultados_manufacturers = None

    # ========================================================
    # ROLES
    # ========================================================

    actualizar_progreso(
        progress_callback,
        30,
        "Generando roles.csv...",
    )

    roles = preparar_roles(
        analisis
    )

    if roles:

        resultados_roles = (
            convertir_roles(
                roles,
                destino,
            )
        )

    else:

        resultados_roles = None

    # ========================================================
    # DEVICE TYPES
    # ========================================================

    actualizar_progreso(
        progress_callback,
        40,
        "Generando device_types.csv...",
    )

    device_types = preparar_device_types(
        analisis,
        datos,
    )

    if device_types:

        resultados_device_types = (
            convertir_device_types(
                device_types,
                destino,
            )
        )

    else:

        resultados_device_types = None

    # ========================================================
    # DEVICES
    # ========================================================

    actualizar_progreso(
        progress_callback,
        50,
        "Generando devices.csv...",
    )

    devices = preparar_devices(
        datos
    )

    if devices:

        resultados_devices = (
            convertir_devices(
                devices,
                destino,
                site,
                roles_por_tipo,
            )
        )

    else:

        resultados_devices = None

    # ========================================================
    # VLANS
    # ========================================================

    actualizar_progreso(
        progress_callback,
        62,
        "Generando vlans.csv...",
    )

    vlans = preparar_vlans(
        datos
    )

    if vlans:

        resultados_vlans = (
            convertir_vlans(
                vlans,
                destino,
            )
        )

    else:

        resultados_vlans = None

    # ========================================================
    # PREFIXES
    # ========================================================

    actualizar_progreso(
        progress_callback,
        72,
        "Generando prefixes.csv...",
    )

    prefixes = preparar_prefixes(
        datos
    )

    if prefixes:

        resultados_prefixes = (
            convertir_prefixes(
                prefixes,
                destino,
            )
        )

    else:

        resultados_prefixes = None

    # ========================================================
    # IP ADDRESSES
    # ========================================================

    actualizar_progreso(
        progress_callback,
        84,
        "Generando ip_addresses.csv...",
    )

    ip_addresses = preparar_ip_addresses(
        datos
    )

    if ip_addresses:

        resultados_ip_addresses = (
            convertir_ip_addresses(
                ip_addresses,
                destino,
            )
        )

    else:

        resultados_ip_addresses = None

    # ========================================================
    # VRFS
    # ========================================================

    actualizar_progreso(
        progress_callback,
        94,
        "Generando vrfs.csv...",
    )

    vrfs = preparar_vrfs(
        datos
    )

    if vrfs:

        resultados_vrfs = (
            convertir_vrfs(
                vrfs,
                destino,
            )
        )

    else:

        resultados_vrfs = None

    # ========================================================
    # RESULTADOS
    # ========================================================

    resultados = {}

    if resultados_manufacturers is not None:

        resultados[
            "manufacturers"
        ] = resultados_manufacturers

    if resultados_roles is not None:

        resultados[
            "roles"
        ] = resultados_roles

    if resultados_device_types is not None:

        resultados[
            "device_types"
        ] = resultados_device_types

    if resultados_devices is not None:

        resultados[
            "devices"
        ] = resultados_devices

    if resultados_vlans is not None:

        resultados[
            "vlans"
        ] = resultados_vlans

    if resultados_prefixes is not None:

        resultados[
            "prefixes"
        ] = resultados_prefixes

    if resultados_ip_addresses is not None:

        resultados[
            "ip_addresses"
        ] = resultados_ip_addresses

    if resultados_vrfs is not None:

        resultados[
            "vrfs"
        ] = resultados_vrfs

    actualizar_progreso(
        progress_callback,
        100,
        "Conversión terminada.",
    )

    return resultados