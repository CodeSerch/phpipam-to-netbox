# phpIPAM → NetBox

Herramienta en Python para convertir exportaciones CSV de **phpIPAM** en archivos CSV compatibles con **NetBox**.

Python tool to convert **phpIPAM CSV exports** into **NetBox-compatible CSV files**.

## Características / Features

* Analiza exportaciones CSV de phpIPAM.
* Detecta tipos, fabricantes y roles.
* Valida datos básicos.
* Genera CSV para NetBox.
* Barra de progreso y tiempo de ejecución.
* No modifica directamente NetBox.

Analyzes phpIPAM exports, detects manufacturers and roles, validates data, and generates NetBox CSV files with progress tracking.

## Archivos generados / Generated files

```text
manufacturers.csv
roles.csv
device_types.csv
devices.csv
vlans.csv
prefixes.csv
ip_addresses.csv
vrfs.csv
```

## Requisitos / Requirements

* Windows
* Python 3.12 o superior / Python 3.12 or newer
* Conexión a Internet para la instalación inicial de dependencias / Internet connection for the initial dependency installation

Dependencias Python / Python dependencies:

* pandas
* requests

## Instalación / Installation

Primero instalá **Python 3.12 o superior** desde:

https://www.python.org/downloads/

Después ejecutá:

```text
install.bat
```

El script verifica que Python esté instalado e instala las dependencias necesarias.

The script checks that Python is installed and installs the required dependencies.

## Uso / Usage

Una vez instalado, ejecutá:

```text
run.bat
```

La aplicación se abrirá automáticamente.

The application will start automatically.

Desde la interfaz:

1. Seleccioná la carpeta de exportación phpIPAM.
2. Seleccioná la carpeta de destino.
3. Ingresá el **Site de NetBox**.
4. Presioná **Analizar**.
5. Revisá los resultados.
6. Presioná **Convertir**.

## Importante / Important

La herramienta **genera archivos CSV y no modifica directamente NetBox**.

Revisá los archivos generados antes de importarlos en NetBox.

The tool **generates CSV files and does not directly modify NetBox**.

Review the generated files before importing them into NetBox.

## Licencia / License

MIT License.
