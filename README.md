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

* Python 3.12+
* pandas
* requests

## Instalación / Installation

```bash
python -m pip install -r requirements.txt
```

## Uso / Usage

```bash
python main.py
```

Seleccioná la carpeta de exportación phpIPAM, la carpeta de destino e ingresá el **Site de NetBox**.

Select the phpIPAM export folder, destination folder, and the **NetBox Site**.

## Importante / Important

La herramienta **genera CSV y no modifica directamente NetBox**. Revisá los archivos antes de importarlos.

The tool **generates CSV files and does not directly modify NetBox**. Review the generated files before importing them.

## Licencia / License

MIT License.
