## 📋 Descripción

Paquete Python para análisis estadístico de datos circulares en biología, con enfoque en patrones temporales de actividad animal a partir de cámaras trampa y otros dispositivos de monitoreo.

**Características principales:**
- ✅ **Prueba de Rayleigh** para datos circulares (horas, direcciones, ciclos)
- ✅ **Transformación automática** de datos temporales
- ✅ **Visualización avanzada** circular y de rosa de los vientos
- ✅ **Análisis para múltiples especies** o grupos
- ✅ **Exportación de resultados** en múltiples formatos (Excel, PDF, PNG)
- ✅ **Interfaz CLI y programática** para diferentes necesidades
- ✅ **Validación de datos** robusta con manejo de errores

# Fundamentos Teóricos de la Prueba de Rayleigh

## Introducción

La prueba de Rayleigh es una prueba estadística utilizada para determinar si existe una dirección media significativa en datos circulares...

## Supuestos

1. Los datos son independientes
2. Los datos siguen una distribución de von Mises
3. La muestra es aleatoria

## Consideraciones
1. Se recomienda n ≥ 30 observaciones para resultados confiables
2. La prueba de Rayleigh no detecta bimodalidad
3. Para patrones crepusculares, considerar análisis complementarios

## Fórmulas

El estadístico de Rayleigh se calcula como:

\[
R = \sqrt{(\sum \cos \theta_i)^2 + (\sum \sin \theta_i)^2}
\]

## Interpretación

- Valor p < 0.05: Se rechaza la hipótesis nula, existe direccionalidad
- Valor p ≥ 0.05: No hay evidencia de direccionalidad

# Ejemplos Biológicos

## 1. Cámaras trampa

Análisis de patrones de actividad de mamíferos...

## 2. Migración de aves

Dirección de vuelo en aves migratorias...

## 3. Ritmos circadianos

Actividad de insectos a lo largo del día...

# Instrucciones 

## Asegúrese de tener Python 3.8 o superior instalado.

Puede verificarlo ejecutando en la terminal o consola:
python --version
python3 --version

## Descargar el repositorio

Desde GitHub:
git clone https://github.com/Madrid9191/Rayleigh-Test.git
cd Rayleigh-Test

O descargue el repositorio como archivo .zip y descomprímalo.

## Instalar dependencias

Instalar dependencias

pip install -r requirements.txt

Esto instalará automáticamente todas las librerías necesarias.

## Preparar los datos

El archivo de datos debe cumplir las siguientes condiciones:

Formato CSV (.csv) o Excel (.xlsx / .xls)

Contener una columna con la hora del evento en formato decimal (0–24)

Ejemplo válido:
. 6.25 = 06:15
. 22.75 = 22:45

## Ejecutar el programa

Desde la carpeta raíz del proyecto, ejecute:

python src/Rayleigh_Test.py

Se iniciará un menú interactivo en la consola.

## Flujo del análisis (paso a paso)

🔹 Paso 1: Cargar datos

Ingrese la ruta completa del archivo de datos.

El programa acepta archivos CSV o Excel.

🔹 Paso 2: Seleccionar columna de horas

El programa mostrará todas las columnas disponibles.

Escriba exactamente el nombre de la columna que contiene las horas.

🔹 Paso 3: Transformación circular

Las horas se convierten automáticamente a:

Radianes (hora_radianes)

Formato legible (hora_formateada)

🔹 Paso 4: Prueba de Rayleigh

El programa calculará:

Tamaño de muestra (n)

Estadístico de concentración R

Valor p

Hora media de actividad

Interpretación automática del patrón temporal

📊 Interpretación:

p < 0.05 → patrón temporal significativo

p ≥ 0.05 → distribución uniforme (actividad aleatoria)

🔹 Paso 5 (opcional): Intervalo de confianza

Si el patrón es significativo y el tamaño de muestra es adecuado, se calcula:

Intervalo de confianza de la hora media

Amplitud del pico de actividad

🔹 Paso 6 (opcional): Visualización

Puede generar automáticamente:

Histograma horario

Rosa de distribución circular

Densidad de probabilidad y boxplot

Los gráficos pueden guardarse en formato:

PNG

PDF

o ambos

🔹 Paso 7 (opcional): Guardar resultados

Los resultados pueden exportarse a un archivo Excel con:

Hoja de resultados estadísticos

Hoja de datos transformados

Estadísticas descriptivas

## Archivos generados

Según las opciones elegidas, el programa puede generar:

📈 Gráficos: .png, .pdf

📊 Resultados: .xlsx

📄 Datos transformados: .csv

Todos los archivos se guardan en el directorio donde se ejecuta el programa.

## Cerrar el programa

El análisis finaliza automáticamente al terminar el flujo.

Para interrumpir el proceso en cualquier momento:

Ctrl + C


