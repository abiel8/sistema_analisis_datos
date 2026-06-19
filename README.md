# Data Quality Platform

---

# Características

## Dashboard

Permite obtener una visión general del archivo cargado:

- Total de registros.
- Total de columnas.
- Valores vacíos.
- Distribución de tipos de datos.
- Histogramas de columnas numéricas.
- Visualizaciones interactivas.

---

## Calidad de Datos

Analiza una columna y permite detectar:

- Valores vacíos.
- Valores duplicados.
- Valores únicos.
- Longitud máxima y mínima.
- Solo números.
- Solo letras.
- Caracteres especiales.
- Correos electrónicos inválidos.

---

## ETL (Extract, Transform, Load)

Permite transformar los datos mediante:

- Eliminación de registros vacíos.
- Eliminación de duplicados.
- Conversión a mayúsculas.
- Limpieza y estandarización de información.
- Exportación del resultado.

---

## Datos Maestros

Valida catálogos empresariales.

### Clientes

- Nombre obligatorio.
- Correo obligatorio.

### Proveedores

- RTN obligatorio.
- País obligatorio.

### Productos

- Código obligatorio.
- Precio mayor que cero.

---

## Reglas Dinámicas

Permite que el usuario defina reglas personalizadas sin modificar código.

Ejemplos:

- Longitud mayor a X caracteres.
- Longitud menor a X caracteres.
- Solo números.
- Solo letras.
- Valores vacíos.
- Valores duplicados.

---

## Perfilado de Datos

Genera información estadística de cada columna:

- Tipo de dato.
- Valores vacíos.
- Valores únicos.
- Duplicados.
- Información descriptiva.

---

## Reportes

Permite:

- Descargar Excel.
- Descargar CSV.
- Obtener resumen de columnas.
- Consultar métricas generales.

---

# Tecnologías Utilizadas

| Tecnología | Función |
|------------|---------|
| Python | Lenguaje principal |
| Streamlit | Interfaz web |
| Pandas | Procesamiento de datos |
| Plotly | Visualizaciones |
| OpenPyXL | Lectura y escritura de Excel |
| Git | Control de versiones |
| GitHub | Repositorio del proyecto |

---

# Estructura del Proyecto

```text
data-quality-platform/
│
├── app.py
│
├── modules/
│   ├── dashboard.py
│   ├── calidad_datos.py
│   ├── etl.py
│   ├── datos_maestros.py
│   ├── reglas_dinamicas.py
│   ├── perfilado.py
│   └── reportes.py
│
├── utils/
│   ├── cargar_archivo.py
│   ├── validaciones.py
│   ├── perfilado_utils.py
│   ├── exportar_excel.py
│   ├── graficos.py
│   └── reglas_utils.py
│
├── assets/
│
├── reports/
│
├── samples/
│
├── requirements.txt
│
└── README.md
```

---

# Instalación

Clonar el repositorio:

```bash
git clone https://github.com/usuario/data-quality-platform.git
```

Entrar al proyecto:

```bash
cd data-quality-platform
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

# Ejecución

Ejecutar:

```bash
python streamlit run app.py
```

La aplicación estará disponible en:

```text
http://localhost:8501
```

---

# Dependencias

Archivo requirements.txt:

```text
streamlit
pandas
plotly
openpyxl
```

---

# Arquitectura

```text
Usuario
    │
    ▼
Streamlit
(app.py)
    │
    ▼
Modules
(Dashboard, Calidad, ETL, Perfilado, etc.)
    │
    ▼
Utils
(Validaciones, Reglas, Exportación)
    │
    ▼
Pandas
    │
    ▼
Excel / CSV
```

---

# Mejoras Futuras

- Motor de reglas.
- Base de datos SQLite o SQL Server.
- Generación de PDF.
- Autenticación de usuarios.
- Historial de ejecuciones.
- Dashboard de calidad global.
- Machine Learning.
- Detección automática de anomalías.
- Integración con SAP.
- Integración con Power BI.

---

# Objetivo del Proyecto

Desarrollar una plataforma modular orientada a la calidad y gobierno de datos, permitiendo analizar, transformar y validar información de manera sencilla y eficiente.

---

# Autor

Abiel Ordóñez

Ingeniería en Ciencias de la Computación

Administrador de Datos Maestros