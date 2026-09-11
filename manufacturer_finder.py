from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from urllib.parse import (
    quote_plus,
    urlparse,
    parse_qs,
    unquote,
)

import requests


# ============================================================
# RESULTADO
# ============================================================

@dataclass
class ManufacturerResult:
    model: str
    manufacturer: str
    source: str
    confidence: str
    match_type: str
    matched_model: str = ""
    url: str = ""


# ============================================================
# MAPPING LOCAL
# ============================================================

LOCAL_MANUFACTURERS = {
    "Router-HW": "Huawei",
    "Switch-HW": "Huawei",
    "OLT-HW": "Huawei",

    "Router-MK": "MikroTik",
    "Firewall-MK": "MikroTik",

    "DELL-DL380": "HPE",
    "DELL-DL385p": "HPE",

    "DELL-R730": "Dell",
    "DELL-R740": "Dell",
    "DELL-7920": "Dell",
    "DELL-ME5024": "Dell",

    "QNAP": "QNAP",
}


# ============================================================
# FABRICANTES CONOCIDOS
# ============================================================

MANUFACTURER_DOMAINS = {
    "Dell": {
        "dell.com",
        "delltechnologies.com",
    },

    "HPE": {
        "hpe.com",
        "hp.com",
    },

    "Cisco": {
        "cisco.com",
    },

    "Huawei": {
        "huawei.com",
    },

    "MikroTik": {
        "mikrotik.com",
    },

    "QNAP": {
        "qnap.com",
    },

    "Arista": {
        "arista.com",
    },

    "Juniper": {
        "juniper.net",
    },

    "Lenovo": {
        "lenovo.com",
    },

    "Supermicro": {
        "supermicro.com",
    },
}


# ============================================================
# SESIÓN HTTP
# ============================================================

SESSION = requests.Session()

SESSION.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/140.0 Safari/537.36"
        )
    }
)


# ============================================================
# NORMALIZAR TEXTO
# ============================================================

def normalizar_texto(valor: str) -> str:

    return " ".join(
        str(valor)
        .strip()
        .split()
    )


# ============================================================
# NORMALIZAR PARA COMPARACIÓN
# ============================================================

def normalizar_comparacion(valor: str) -> str:

    valor = normalizar_texto(
        valor
    )

    valor = valor.lower()

    valor = re.sub(
        r"[-_/]+",
        " ",
        valor
    )

    valor = re.sub(
        r"\s+",
        " ",
        valor
    )

    return valor.strip()


# ============================================================
# BUSCAR LOCALMENTE
# ============================================================

def buscar_manufacturer_local(
    modelo: str,
) -> ManufacturerResult:

    modelo = normalizar_texto(
        modelo
    )

    manufacturer = LOCAL_MANUFACTURERS.get(
        modelo,
        ""
    )

    if manufacturer:

        return ManufacturerResult(
            model=modelo,
            manufacturer=manufacturer,
            source="local",
            confidence="high",
            match_type="exact",
            matched_model=modelo,
        )

    return ManufacturerResult(
        model=modelo,
        manufacturer="",
        source="local",
        confidence="unknown",
        match_type="unknown",
    )


# ============================================================
# EXTRAER DOMINIO
# ============================================================

def obtener_dominio(url: str) -> str:

    try:

        url = unescape(
            url
        ).strip()

        if url.startswith("//"):

            url = "https:" + url

        parsed = urlparse(
            url
        )

        # ----------------------------------------------------
        # DuckDuckGo redirect
        # ----------------------------------------------------

        if "duckduckgo.com" in parsed.netloc.lower():

            parametros = parse_qs(
                parsed.query
            )

            if "uddg" in parametros:

                url_real = unquote(
                    parametros["uddg"][0]
                )

                parsed = urlparse(
                    url_real
                )

        dominio = parsed.netloc.lower()

        if dominio.startswith("www."):

            dominio = dominio[4:]

        return dominio

    except Exception:

        return ""


# ============================================================
# IDENTIFICAR FABRICANTE POR DOMINIO
# ============================================================

def manufacturer_por_dominio(
    dominio: str,
) -> str:

    dominio = dominio.lower()

    for manufacturer, dominios in MANUFACTURER_DOMAINS.items():

        for dominio_oficial in dominios:

            if (
                dominio == dominio_oficial
                or dominio.endswith(
                    "." + dominio_oficial
                )
            ):

                return manufacturer

    return ""


# ============================================================
# LIMPIAR HTML
# ============================================================

def limpiar_html(
    texto: str,
) -> str:

    texto = unescape(
        texto
    )

    texto = re.sub(
        r"<[^>]+>",
        " ",
        texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


# ============================================================
# GENERAR CONSULTAS
# ============================================================

def generar_consultas(
    modelo: str,
) -> list[str]:
    """
    Genera varias consultas para intentar encontrar
    coincidencias exactas o aproximadas.

    Ejemplo:

        OLT 5800 X7

    genera búsquedas como:

        "OLT 5800 X7" manufacturer
        "OLT 5800 X7" hardware
        5800 X7 manufacturer
        5800 X7 server
        5800 X7 hardware
    """

    modelo = normalizar_texto(
        modelo
    )

    consultas = []

    # --------------------------------------------------------
    # Búsqueda exacta
    # --------------------------------------------------------

    consultas.append(
        f'"{modelo}" manufacturer'
    )

    consultas.append(
        f'"{modelo}" hardware'
    )

    consultas.append(
        f'"{modelo}" model'
    )

    # --------------------------------------------------------
    # Quitar términos genéricos
    # --------------------------------------------------------

    palabras_genericas = {
        "olt",
        "switch",
        "router",
        "firewall",
        "server",
        "storage",
        "device",
        "hw",
        "hardware",
        "network",
        "appliance",
    }

    partes = modelo.split()

    partes_utiles = [
        parte
        for parte in partes
        if parte.lower() not in palabras_genericas
    ]

    if partes_utiles:

        modelo_reducido = " ".join(
            partes_utiles
        )

        if (
            modelo_reducido.lower()
            != modelo.lower()
        ):

            consultas.append(
                f'"{modelo_reducido}" manufacturer'
            )

            consultas.append(
                f'"{modelo_reducido}" hardware'
            )

    # --------------------------------------------------------
    # Búsqueda por tokens principales
    # --------------------------------------------------------

    if len(partes_utiles) >= 2:

        consultas.append(
            f'"{" ".join(partes_utiles)}" server'
        )

    # --------------------------------------------------------
    # Quitar duplicados
    # --------------------------------------------------------

    resultado = []

    for consulta in consultas:

        if consulta not in resultado:

            resultado.append(
                consulta
            )

    return resultado


# ============================================================
# EXTRAER MODELO CANDIDATO DEL TÍTULO
# ============================================================

def extraer_modelo_candidato(
    titulo: str,
    modelo_original: str,
) -> str:

    titulo = limpiar_html(
        titulo
    )

    modelo_original = normalizar_texto(
        modelo_original
    )

    if not titulo:

        return ""

    # --------------------------------------------------------
    # Si el modelo original aparece en el título
    # --------------------------------------------------------

    if (
        normalizar_comparacion(
            modelo_original
        )
        in
        normalizar_comparacion(
            titulo
        )
    ):

        return modelo_original

    # --------------------------------------------------------
    # Intentar detectar nombres comerciales
    # --------------------------------------------------------

    patrones = [

        # Ejemplo:
        # HPE ProLiant DL380 Gen10
        r"\b(?:HPE|HP)\s+ProLiant\s+[A-Za-z0-9\-]+"
        r"(?:\s+Gen\d+)?",

        # Ejemplo:
        # Huawei MA5800-X7
        r"\b(?:Huawei\s+)?MA\d{4}"
        r"(?:[-\s]?[A-Z0-9]+)*",

        # Ejemplo:
        # Dell PowerEdge R730
        r"\b(?:Dell\s+)?PowerEdge\s+[A-Za-z0-9\-]+",

        # Modelo genérico con números
        r"\b[A-Z]{1,8}\d{2,}[A-Z0-9\-]*",
    ]

    for patron in patrones:

        coincidencia = re.search(
            patron,
            titulo,
            flags=re.IGNORECASE
        )

        if coincidencia:

            return normalizar_texto(
                coincidencia.group(0)
            )

    return titulo


# ============================================================
# BUSCAR EN WEB
# ============================================================

def buscar_manufacturer_web(
    modelo: str,
    max_resultados: int = 10,
) -> list[ManufacturerResult]:

    modelo = normalizar_texto(
        modelo
    )

    if not modelo:

        return []

    consultas = generar_consultas(
        modelo
    )

    candidatos = {}

    # ========================================================
    # EJECUTAR CONSULTAS
    # ========================================================

    for consulta in consultas:

        print(
            f"\nBUSQUEDA WEB -> {consulta}"
        )

        url = (
            "https://html.duckduckgo.com/html/?q="
            + quote_plus(consulta)
        )

        try:

            response = SESSION.get(
                url,
                timeout=10,
            )

            response.raise_for_status()

        except requests.RequestException as error:

            print(
                f"Error de búsqueda web: {error}"
            )

            continue

        html = response.text

        bloques = re.findall(
            r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )

        print(
            f"Resultados encontrados: {len(bloques)}"
        )

        # ====================================================
        # ANALIZAR RESULTADOS
        # ====================================================

        for enlace, titulo_html in bloques[
            :max_resultados
        ]:

            destino = unescape(
                enlace
            )

            dominio = obtener_dominio(
                destino
            )

            manufacturer = (
                manufacturer_por_dominio(
                    dominio
                )
            )

            if not manufacturer:

                continue

            titulo = limpiar_html(
                titulo_html
            )

            modelo_encontrado = (
                extraer_modelo_candidato(
                    titulo,
                    modelo
                )
            )

            clave = (
                manufacturer,
                modelo_encontrado,
            )

            if clave not in candidatos:

                candidatos[clave] = {
                    "manufacturer": manufacturer,
                    "matched_model": modelo_encontrado,
                    "url": destino,
                    "score": 0,
                    "official_results": 0,
                }

            candidato = candidatos[clave]

            # ------------------------------------------------
            # Puntuación por dominio oficial
            # ------------------------------------------------

            if dominio in {
                "hpe.com",
                "hp.com",
                "dell.com",
                "delltechnologies.com",
                "cisco.com",
                "huawei.com",
                "mikrotik.com",
                "qnap.com",
                "arista.com",
                "juniper.net",
                "lenovo.com",
                "supermicro.com",
            }:

                candidato["score"] += 5

                candidato["official_results"] += 1

            else:

                candidato["score"] += 2

            # ------------------------------------------------
            # Coincidencia del modelo
            # ------------------------------------------------

            modelo_normalizado = (
                normalizar_comparacion(
                    modelo
                )
            )

            encontrado_normalizado = (
                normalizar_comparacion(
                    modelo_encontrado
                )
            )

            if (
                modelo_normalizado
                and
                modelo_normalizado
                in
                encontrado_normalizado
            ):

                candidato["score"] += 5

            elif (
                encontrado_normalizado
                and
                any(
                    token in encontrado_normalizado
                    for token in modelo_normalizado.split()
                    if len(token) >= 3
                )
            ):

                candidato["score"] += 2

    # ========================================================
    # CONVERTIR CANDIDATOS EN RESULTADOS
    # ========================================================

    candidatos_ordenados = sorted(
        candidatos.values(),
        key=lambda item: item["score"],
        reverse=True,
    )

    resultados = []

    for candidato in candidatos_ordenados:

        score = candidato["score"]

        official_results = (
            candidato["official_results"]
        )

        # ----------------------------------------------------
        # CONFIANZA
        # ----------------------------------------------------

        if (
            official_results >= 2
            and score >= 10
        ):

            confidence = "high"

        elif (
            official_results >= 1
            and score >= 7
        ):

            confidence = "medium"

        else:

            confidence = "low"

        resultados.append(
            ManufacturerResult(
                model=modelo,
                manufacturer=candidato["manufacturer"],
                source="web",
                confidence=confidence,
                match_type="approximate",
                matched_model=candidato["matched_model"],
                url=candidato["url"],
            )
        )

    return resultados


# ============================================================
# BUSCAR MANUFACTURER
# ============================================================

def buscar_manufacturer(
    modelo: str,
    usar_web: bool = True,
) -> ManufacturerResult:

    modelo = normalizar_texto(
        modelo
    )

    # --------------------------------------------------------
    # 1. LOCAL
    # --------------------------------------------------------

    local = buscar_manufacturer_local(
        modelo
    )

    if local.manufacturer:

        return local

    # --------------------------------------------------------
    # 2. WEB
    # --------------------------------------------------------

    if usar_web:

        resultados_web = (
            buscar_manufacturer_web(
                modelo
            )
        )

        if not resultados_web:

            return ManufacturerResult(
                model=modelo,
                manufacturer="",
                source="none",
                confidence="unknown",
                match_type="unknown",
            )

        # ----------------------------------------------------
        # UN SOLO CANDIDATO
        # ----------------------------------------------------

        if len(resultados_web) == 1:

            resultado = resultados_web[0]

            # Si hay buena evidencia oficial,
            # lo consideramos una sugerencia fuerte.
            if resultado.confidence == "high":

                resultado.match_type = "approximate"

            return resultado

        # ----------------------------------------------------
        # VARIOS CANDIDATOS
        # ----------------------------------------------------

        mejor = resultados_web[0]

        segundo = resultados_web[1]

        # Si están muy cerca, no decidimos automáticamente.
        # El usuario deberá confirmar.
        #
        # Ejemplo:
        #
        # HPE   score alto
        # Dell  score apenas menor
        #

        # Actualmente no exponemos score en el dataclass,
        # por lo que cualquier múltiples resultados
        # se consideran revisión manual.

        return ManufacturerResult(
            model=modelo,
            manufacturer=mejor.manufacturer,
            source="web",
            confidence=mejor.confidence,
            match_type="approximate",
            matched_model=mejor.matched_model,
            url=mejor.url,
        )

    # --------------------------------------------------------
    # 3. UNKNOWN
    # --------------------------------------------------------

    return ManufacturerResult(
        model=modelo,
        manufacturer="",
        source="none",
        confidence="unknown",
        match_type="unknown",
    )


# ============================================================
# MOSTRAR RESULTADO
# ============================================================

def imprimir_resultado(
    resultado: ManufacturerResult,
) -> None:

    print(
        f"\nModelo original: "
        f"{resultado.model}"
    )

    print(
        f"Manufacturer sugerido: "
        f"{resultado.manufacturer or '?'}"
    )

    print(
        f"Fuente: "
        f"{resultado.source}"
    )

    print(
        f"Confianza: "
        f"{resultado.confidence}"
    )

    print(
        f"Tipo de coincidencia: "
        f"{resultado.match_type}"
    )

    if resultado.matched_model:

        print(
            f"Modelo encontrado: "
            f"{resultado.matched_model}"
        )

    if resultado.url:

        print(
            f"URL: "
            f"{resultado.url}"
        )


# ============================================================
# PRUEBA DIRECTA
# ============================================================

if __name__ == "__main__":

    print(
        "=" * 60
    )

    print(
        "MANUFACTURER FINDER"
    )

    print(
        "=" * 60
    )

    modelo = input(
        "\nModelo/type de phpIPAM: "
    ).strip()

    if not modelo:

        print(
            "\nNo se ingresó ningún modelo."
        )

    else:

        resultado = buscar_manufacturer(
            modelo
        )

        imprimir_resultado(
            resultado
        )