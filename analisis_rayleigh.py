import pandas as pd
import os
import numpy as np
from scipy.stats import chi2
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def cargar_datos():

    print("="*60)
    print("ANÁLISIS DE PATRONES TEMPORALES CON PRUEBA DE RAYLEIGH")
    print("="*60)

    while True:
        archivo = input("\nIngrese la ruta completa del archivo (CSV o Excel): ").strip()

        if not os.path.exists(archivo):
            print(f"❌ Error: El archivo '{archivo}' no existe.")
            continue

        # Verificar extensión del archivo
        if archivo.endswith('.csv'):
            try:
                df = pd.read_csv(archivo)
                print(f"✅ Archivo CSV cargado correctamente. Dimensiones: {df.shape}")
                return df
            except Exception as e:
                print(f"❌ Error al leer el archivo CSV: {e}")

        elif archivo.endswith(('.xlsx', '.xls')):
            try:
                # Si es Excel, preguntar por el nombre de la hoja
                hoja = input("Ingrese el nombre de la hoja (deje vacío para la primera): ").strip()
                if hoja:
                    df = pd.read_excel(archivo, sheet_name=hoja)
                else:
                    df = pd.read_excel(archivo)
                print(f"✅ Archivo Excel cargado correctamente. Dimensiones: {df.shape}")
                return df
            except Exception as e:
                print(f"❌ Error al leer el archivo Excel: {e}")
        else:
            print("❌ Formato no soportado. Use archivos .csv, .xlsx o .xls")

def transformar_horas_a_radianes(df):

    print("\n" + "-"*60)
    print("TRANSFORMACIÓN DE HORAS A DATOS CIRCULARES")
    print("-"*60)

    # Mostrar las columnas disponibles
    print("\nColumnas disponibles en el dataset:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col} (tipo: {df[col].dtype})")

    while True:
        columna_horas = input("\nIngrese el nombre exacto de la columna con las horas (formato decimal 0-24): ").strip()

        if columna_horas not in df.columns:
            print(f"❌ La columna '{columna_horas}' no existe en el dataset.")
            continue

        # Verificar que los datos sean numéricos
        if not pd.api.types.is_numeric_dtype(df[columna_horas]):
            print(f"❌ La columna '{columna_horas}' no contiene datos numéricos.")
            continue

        # Verificar rango de horas (0-24)
        if df[columna_horas].min() < 0 or df[columna_horas].max() > 24:
            print("⚠️  Advertencia: Algunos valores están fuera del rango 0-24 horas.")
            resp = input("¿Desea continuar de todas formas? (s/n): ").lower()
            if resp != 's':
                continue

        # Transformar a radianes
        print(f"\nTransformando {len(df)} registros...")

        # Asegurar que las horas estén en rango 0-24
        horas = df[columna_horas].copy()
        horas = horas % 24  # Para manejar horas > 24 o negativas

        # Convertir a radianes: 24 horas = 2π radianes
        df['hora_radianes'] = (horas / 24) * 2 * np.pi

        # Crear columna con hora en formato legible (HH:MM)
        df['hora_formateada'] = df[columna_horas].apply(
            lambda x: str(timedelta(hours=x % 24))[:-3] if not pd.isna(x) else None
        )

        print(f"✅ Transformación completada.")
        print(f"   - Hora mínima: {df['hora_formateada'].min()}")
        print(f"   - Hora máxima: {df['hora_formateada'].max()}")
        print(f"   - Nuevas columnas creadas: 'hora_radianes', 'hora_formateada'")

        return df, columna_horas

def prueba_rayleigh_manual(angulos):

    n = len(angulos)

    # Calcular componentes C y S
    C = np.sum(np.cos(angulos))
    S = np.sum(np.sin(angulos))

    # Calcular R (longitud del vector resultante)
    R = np.sqrt(C**2 + S**2)

    # Estadístico de Rayleigh normalizado
    R_norm = R / n

    # Calcular valor p (aproximación para n > 50, corrección para n pequeña)
    if n > 50:
        # Aproximación para n grande
        z = n * R_norm**2
        p_valor = np.exp(-z)
    else:
        # Fórmula exacta para n pequeña
        z = R_norm**2 * n
        if n <= 10:
            # Corrección para muestras muy pequeñas
            p_valor = np.exp(np.sqrt(1 + 4*n + 4*(n**2 - R**2)) - (1 + 2*n))
        else:
            # Aproximación de chi-cuadrado con 2 grados de libertad
            p_valor = chi2.sf(2 * z, df=2)

    return R_norm, p_valor, R, C, S

def aplicar_prueba_rayleigh(df):

    print("\n" + "="*60)
    print("APLICACIÓN DE LA PRUEBA DE RAYLEIGH")
    print("="*60)

    if 'hora_radianes' not in df.columns:
        print("❌ Error: Primero debe transformar las horas a radianes.")
        return None

    # Eliminar valores NaN
    angulos = df['hora_radianes'].dropna()
    n = len(angulos)

    print(f"\n📊 Análisis de {n} registros válidos:")

    # Aplicar prueba de Rayleigh
    R_norm, p_valor, R, C, S = prueba_rayleigh_manual(angulos)

    # Calcular dirección media en radianes
    angulo_medio = np.arctan2(S, C)
    if angulo_medio < 0:
        angulo_medio += 2 * np.pi

    # Convertir a horas
    hora_media = (angulo_medio / (2 * np.pi)) * 24

    # Resultados
    print(f"\n📈 RESULTADOS DE LA PRUEBA DE RAYLEIGH:")
    print(f"   • Tamaño de muestra (n): {n}")
    print(f"   • Estadístico R (concentración): {R_norm:.4f}")
    print(f"   • Valor p: {p_valor:.6f}")
    if p_valor < 0.001:
        print(f"   • Significancia: p < 0.001 (***)")
    elif p_valor < 0.01:
        print(f"   • Significancia: p < 0.01 (**)")
    elif p_valor < 0.05:
        print(f"   • Significancia: p < 0.05 (*)")
    else:
        print(f"   • Significancia: No significativo")

    print(f"\n⏰ HORA MEDIA DE ACTIVIDAD: {hora_media:.2f} horas ({str(timedelta(hours=hora_media))[:-3]})")

    # Interpretación
    print("\n" + "-"*60)
    print("INTERPRETACIÓN:")

    if p_valor < 0.05:
        print("✅ Se rechaza la hipótesis nula (H₀).")
        print("   → Los datos NO están distribuidos uniformemente en el tiempo.")
        print("   → Existe un patrón temporal SIGNIFICATIVO en la actividad.")

        # Interpretar R (concentración)
        if R_norm < 0.3:
            print("   → Concentración BAJA: patrón débil pero significativo")
        elif R_norm < 0.6:
            print("   → Concentración MODERADA: patrón claro")
        else:
            print("   → Concentración ALTA: patrón muy marcado")

        # Interpretar hora media
        if 5 <= hora_media < 11:
            print(f"   → Patrón DIURNO/MAÑANERO (pico ~{hora_media:.1f}h)")
        elif 11 <= hora_media < 17:
            print(f"   → Patrón DIURNO/VESPERTINO (pico ~{hora_media:.1f}h)")
        elif 17 <= hora_media < 23:
            print(f"   → Patrón NOCTURNO/TEMPRANO (pico ~{hora_media:.1f}h)")
        else:
            print(f"   → Patrón NOCTURNO/TARDÍO (pico ~{hora_media:.1f}h)")

        return True, hora_media, R_norm, p_valor

    else:
        print("❌ NO se rechaza la hipótesis nula (H₀).")
        print("   → Los datos SÍ están distribuidos uniformemente en el tiempo.")
        print("   → NO existe un patrón temporal significativo en la actividad.")
        print("   → La actividad es ALEATORIA a lo largo del día.")
        return False, hora_media, R_norm, p_valor

def calcular_intervalo_confianza(df, hora_media, R_norm, confianza=0.95):

    print("\n" + "="*60)
    print("CÁLCULO DEL INTERVALO DE CONFIANZA")
    print("="*60)

    angulos = df['hora_radianes'].dropna()
    n = len(angulos)

    # Calcular error estándar circular
    R = R_norm * n

    # Para n grande, usar aproximación normal
    if n > 30 and R_norm > 0.7:
        # Fórmula simplificada
        sigma = np.sqrt((1 - R_norm**2) / (2 * n * R_norm**2))
        margen = 1.96 * sigma  # Z para 95% confianza

        # Convertir a horas
        margen_horas = margen * 24 / (2 * np.pi)

        # Calcular intervalo
        hora_min = (hora_media - margen_horas) % 24
        hora_max = (hora_media + margen_horas) % 24

        print(f"\n📊 Para un nivel de confianza del {confianza*100:.0f}%:")
        print(f"   • Hora media estimada: {hora_media:.2f}h ({str(timedelta(hours=hora_media))[:-3]})")
        print(f"   • Intervalo de confianza: [{hora_min:.2f}h, {hora_max:.2f}h]")
        print(f"     ≈ [{str(timedelta(hours=hora_min))[:-3]}, {str(timedelta(hours=hora_max))[:-3]}]")

        # Interpretación ecológica
        print("\n🌿 INTERPRETACIÓN ECOLÓGICA:")
        amplitud = (hora_max - hora_min) % 24
        print(f"   • Amplitud del pico de actividad: {amplitud:.1f} horas")

        if amplitud < 4:
            print("   • Actividad muy concentrada en pocas horas")
        elif amplitud < 8:
            print("   • Actividad moderadamente concentrada")
        else:
            print("   • Actividad distribuida en gran parte del día")

    else:
        print(f"⚠️  El tamaño de muestra (n={n}) o concentración (R={R_norm:.3f})")
        print("   no son suficientes para calcular intervalo de confianza confiable.")
        print("   Se recomienda aumentar el tamaño de muestra.")

def visualizar_datos(df, columna_horas, modo_auto=False):

    print("\n" + "="*60)
    print("VISUALIZACIÓN DE LA DISTRIBUCIÓN HORARIA")
    print("="*60)

    resultado = {}

    try:
        import matplotlib
        # Usar backend 'Agg' para entornos sin display
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np

    except ImportError:
        print("❌ Matplotlib no está instalado.")
        print("   Instálelo con: pip install matplotlib")
        return resultado

    try:
        # ============================================
        # 1. PREPARACIÓN DE DATOS
        # ============================================
        print("\n📊 Preparando datos para visualización...")

        # Asegurar que las horas estén en rango 0-24
        horas = df[columna_horas].copy() % 24

        # Estadísticas descriptivas
        n_registros = len(horas.dropna())
        hora_min = horas.min()
        hora_max = horas.max()
        hora_mediana = horas.median()

        from datetime import timedelta

        print(f"   • Registros válidos: {n_registros}")
        print(f"   • Rango horario: {hora_min:.2f}h - {hora_max:.2f}h")
        print(f"   • Mediana: {hora_mediana:.2f}h")

        # ============================================
        # 2. CREAR FIGURA CON MÚLTIPLES GRÁFICOS
        # ============================================
        print("📈 Generando visualizaciones...")

        # Crear figura con 3 subgráficos
        fig = plt.figure(figsize=(16, 5))

        # --- Gráfico 1: Histograma clásico ---
        ax1 = plt.subplot(131)
        n, bins, patches = ax1.hist(horas, bins=24, range=(0, 24),
                                     alpha=0.7, color='steelblue',
                                     edgecolor='navy', linewidth=0.5)

        # Personalización
        ax1.set_xlabel('Hora del día (formato 24h)', fontsize=10)
        ax1.set_ylabel('Frecuencia absoluta', fontsize=10)
        ax1.set_title('A) Histograma de frecuencias',
                     fontsize=12, fontweight='bold', pad=10)
        ax1.set_xticks(range(0, 25, 3))
        ax1.set_xticklabels([f'{h:02d}:00' for h in range(0, 25, 3)],
                            rotation=45, fontsize=9)
        ax1.grid(True, alpha=0.2, linestyle='--')

        # Resaltar hora con máxima actividad
        if len(n) > 0:
            max_idx = np.argmax(n)
            hora_max_freq = bins[max_idx] + (bins[1] - bins[0])/2
            patches[max_idx].set_facecolor('crimson')
            ax1.axvline(hora_max_freq, color='red', linestyle=':',
                       linewidth=2, alpha=0.7,
                       label=f'Máx: {hora_max_freq:.1f}h')
            ax1.legend(fontsize=8)

        # --- Gráfico 2: Gráfico circular (rosa de los vientos) ---
        ax2 = plt.subplot(132, projection='polar')

        # Calcular ángulos en radianes
        angulos = (horas / 24) * 2 * np.pi

        # Crear histograma circular
        n_bins = 24
        theta = np.linspace(0, 2*np.pi, n_bins, endpoint=False)
        counts, _ = np.histogram(angulos, bins=n_bins)

        # Normalizar para mejor visualización
        if counts.max() > 0:
            radii = counts / counts.max() * 0.8
        else:
            radii = counts * 0.8

        # Crear barras con colormap
        cmap = plt.cm.viridis
        colors = cmap(counts / counts.max() if counts.max() > 0 else counts)

        bars = ax2.bar(theta, radii, width=2*np.pi/n_bins,
                       color=colors, alpha=0.8, edgecolor='white',
                       linewidth=0.5)

        # Configuración del gráfico polar
        ax2.set_theta_zero_location('N')
        ax2.set_theta_direction(-1)
        ax2.set_title('B) Rosa de distribución circular',
                     fontsize=12, fontweight='bold', pad=20)
        ax2.set_xticks(np.linspace(0, 2*np.pi, 8, endpoint=False))
        ax2.set_xticklabels(['0h', '3h', '6h', '9h', '12h', '15h', '18h', '21h'])
        ax2.set_yticklabels([])

        # --- Gráfico 3: Gráfico de densidad y boxplot ---
        ax3 = plt.subplot(133)

        # Crear un subgráfico para densidad
        from scipy import stats
        try:
            # Curva de densidad (KDE)
            kde = stats.gaussian_kde(horas)
            x_range = np.linspace(0, 24, 400)
            y_kde = kde(x_range)

            # Normalizar para que el área sea 1
            y_kde = y_kde / y_kde.max()

            ax3.plot(x_range, y_kde, color='darkgreen',
                    linewidth=2, label='Densidad (KDE)')
            ax3.fill_between(x_range, y_kde, alpha=0.3,
                            color='lightgreen')
        except:
            # Fallback si no se puede calcular KDE
            ax3.hist(horas, bins=24, range=(0, 24),
                     density=True, alpha=0.5, color='lightgreen',
                     label='Densidad')

        # Agregar boxplot horizontal
        bp = ax3.boxplot(horas, vert=False, positions=[0.8],
                        widths=0.3, patch_artist=True)
        bp['boxes'][0].set_facecolor('lightblue')
        bp['boxes'][0].set_alpha(0.7)

        # Personalización
        ax3.set_xlabel('Hora del día', fontsize=10)
        ax3.set_ylabel('Densidad', fontsize=10)
        ax3.set_title('C) Densidad de probabilidad y distribución',
                     fontsize=12, fontweight='bold', pad=10)
        ax3.set_xlim(0, 24)
        ax3.set_ylim(-0.1, 1.2)
        ax3.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        ax3.grid(True, alpha=0.2, axis='x')
        ax3.legend(loc='upper right', fontsize=8)

        # Agregar líneas de referencia horarias
        for hora_ref in [6, 12, 18]:
            ax3.axvline(hora_ref, color='gray', linestyle=':',
                       alpha=0.5, linewidth=0.8)

        # ============================================
        # 3. TÍTULO GENERAL Y AJUSTES
        # ============================================
        # Calcular estadísticas adicionales
        hora_promedio = horas.mean()
        desviacion = horas.std()

        # Convertir a formato legible
        hora_prom_str = str(timedelta(hours=hora_promedio))[:-3]
        hora_min_str = str(timedelta(hours=hora_min))[:-3]
        hora_max_str = str(timedelta(hours=hora_max))[:-3]

        # Título general
        titulo_general = f'ANÁLISIS DE DISTRIBUCIÓN HORARIA\n'
        titulo_general += f'N = {n_registros} registros | '
        titulo_general += f'Media: {hora_prom_str} | '
        titulo_general += f'Rango: {hora_min_str} - {hora_max_str}'

        fig.suptitle(titulo_general, fontsize=13, fontweight='bold', y=1.02)

        # Ajustar diseño
        plt.tight_layout()

        # ============================================
        # 4. GUARDADO DE GRÁFICOS
        # ============================================
        # Generar nombre de archivo basado en fecha y hora
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if modo_auto:
            # Modo automático (script batch)
            nombre_base = f"distribucion_horaria_{timestamp}"
            guardar = 's'
        else:
            # Modo interactivo
            print("\n💾 OPCIONES DE GUARDADO:")
            print("   s - Guardar en PNG (alta resolución)")
            print("   p - Guardar en PDF (vectorial)")
            print("   a - Guardar en ambos formatos")
            print("   n - No guardar")

            guardar = input("\nSeleccione una opción: ").strip().lower()

            if guardar in ['s', 'p', 'a']:
                nombre_base = input("Nombre base (sin extensión): ").strip()
                if not nombre_base:
                    nombre_base = f"distribucion_horaria_{timestamp}"
            else:
                nombre_base = None

        # Guardar según la opción seleccionada
        archivos_guardados = []

        if guardar in ['s', 'a'] and nombre_base:
            ruta_png = f"{nombre_base}.png"
            fig.savefig(ruta_png, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            archivos_guardados.append(ruta_png)
            print(f"✅ Guardado: {ruta_png}")
            resultado['png'] = ruta_png

        if guardar in ['p', 'a'] and nombre_base:
            ruta_pdf = f"{nombre_base}.pdf"
            fig.savefig(ruta_pdf, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            archivos_guardados.append(ruta_pdf)
            print(f"✅ Guardado: {ruta_pdf}")
            resultado['pdf'] = ruta_pdf

        # ============================================
        # 5. RESULTADOS ADICIONALES
        # ============================================
        if archivos_guardados:
            print(f"\n📁 Gráficos guardados en:")
            for archivo in archivos_guardados:
                print(f"   • {archivo}")

        # Mostrar estadísticas en consola
        print("\n" + "-"*60)
        print("ESTADÍSTICAS DESCRIPTIVAS")
        print("-"*60)

        # Calcular percentiles
        percentiles = np.percentile(horas, [25, 50, 75, 90, 95])

        print(f"\nDistribución de horas (n={n_registros}):")
        print(f"   • Media: {hora_promedio:.2f}h ({hora_prom_str})")
        print(f"   • Mediana: {hora_mediana:.2f}h")
        print(f"   • Desviación estándar: {desviacion:.2f}h")
        print(f"\nPercentiles:")
        print(f"   • Q1 (25%): {percentiles[0]:.2f}h")
        print(f"   • Q2 (50%): {percentiles[1]:.2f}h")
        print(f"   • Q3 (75%): {percentiles[2]:.2f}h")
        print(f"   • P90: {percentiles[3]:.2f}h")
        print(f"   • P95: {percentiles[4]:.2f}h")

        # Análisis de periodos del día
        print(f"\nActividad por periodo del día:")
        diurno = ((horas >= 6) & (horas < 18)).sum()
        nocturno = ((horas < 6) | (horas >= 18)).sum()

        print(f"   • Diurno (06:00-17:59): {diurno} registros ({diurno/n_registros*100:.1f}%)")
        print(f"   • Nocturno (18:00-05:59): {nocturno} registros ({nocturno/n_registros*100:.1f}%)")

        # Agregar estadísticas al resultado
        resultado['estadisticas'] = {
            'n_registros': n_registros,
            'media': hora_promedio,
            'mediana': hora_mediana,
            'desviacion': desviacion,
            'min': hora_min,
            'max': hora_max,
            'percentiles': percentiles.tolist(),
            'diurno': int(diurno),
            'nocturno': int(nocturno),
            'porcentaje_diurno': diurno/n_registros*100,
            'porcentaje_nocturno': nocturno/n_registros*100
        }

        # Cerrar figura para liberar memoria
        plt.close(fig)

        print("\n✅ Visualización completada exitosamente!")

        return resultado

    except Exception as e:
        print(f"\n❌ Error durante la visualización: {str(e)}")
        import traceback
        traceback.print_exc()
        return resultado

def guardar_resultados(df, resultados, nombre_archivo="resultados_rayleigh"):

    # Crear DataFrame con resultados
    res_df = pd.DataFrame({
        'Parametro': ['Tamaño muestra (n)', 'Estadístico R', 'Valor p',
                      'Hora media', 'Significativo'],
        'Valor': [len(df['hora_radianes'].dropna()),
                  resultados['R'],
                  resultados['p_valor'],
                  resultados['hora_media'],
                  resultados['significativo']]
    })

    # Crear DataFrame con datos transformados
    datos_df = df[['hora_formateada', 'hora_radianes']].copy()

    # Guardar en Excel con múltiples hojas
    with pd.ExcelWriter(f"{nombre_archivo}.xlsx", engine='openpyxl') as writer:
        res_df.to_excel(writer, sheet_name='Resultados', index=False)
        datos_df.to_excel(writer, sheet_name='Datos_transformados', index=False)

        # Crear hoja con estadísticas descriptivas
        stats = df['hora_formateada'].apply(
            lambda x: float(x.split(':')[0]) + float(x.split(':')[1])/60 if isinstance(x, str) else None
        ).describe()
        stats.to_excel(writer, sheet_name='Estadisticas')

    print(f"\n✅ Resultados guardados en '{nombre_archivo}.xlsx'")

def menu_principal():

    print("="*60)
    print("SISTEMA DE ANÁLISIS DE PATRONES TEMPORALES")
    print("Versión 1.0 - Prueba de Rayleigh para datos biológicos")
    print("="*60)

    # Paso 1: Cargar datos
    df = cargar_datos()

    # Paso 2: Transformar horas
    df, columna_horas = transformar_horas_a_radianes(df)

    # Paso 3: Aplicar prueba de Rayleigh
    significativo, hora_media, R_norm, p_valor = aplicar_prueba_rayleigh(df)

    # Almacenar resultados
    resultados = {
        'significativo': significativo,
        'hora_media': hora_media,
        'R': R_norm,
        'p_valor': p_valor
    }

    # Paso 4: Si hay patrón significativo, calcular intervalo de confianza
    if significativo:
        calcular_intervalo_confianza(df, hora_media, R_norm)

    # Paso 5: Opcional - Visualizar datos
    visualizar_opcion = input("\n¿Desea visualizar la distribución de horas? (s/n): ").lower()
    if visualizar_opcion == 's':
        visualizar_datos(df, columna_horas)

    # Paso 6: Opcional - Guardar resultados
    guardar_opcion = input("\n¿Desea guardar los resultados en un archivo Excel? (s/n): ").lower()
    if guardar_opcion == 's':
        nombre = input("Nombre del archivo (deje vacío para 'resultados_rayleigh'): ").strip()
        if not nombre:
            nombre = "resultados_rayleigh"
        guardar_resultados(df, resultados, nombre)

    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN DEL ANÁLISIS")
    print("="*60)
    print(f"• Archivo analizado: {len(df)} registros")
    print(f"• Patrón temporal: {'SIGNIFICATIVO' if significativo else 'NO significativo'}")
    if significativo:
        print(f"• Hora media de actividad: {hora_media:.2f}h ({str(timedelta(hours=hora_media))[:-3]})")
        print(f"• Concentración (R): {R_norm:.3f}")
    print(f"• Valor p: {p_valor:.6f}")
    print("\n✅ Análisis completado.")

    # Recomendaciones
    print("\n" + "-"*60)
    print("RECOMENDACIONES:")
    if significativo:
        if R_norm < 0.4:
            print("• Considerar aumentar el tamaño de muestra para mayor precisión")
        print("• Puede realizar análisis por estaciones o hábitats separados")
    else:
        print("• El tamaño de muestra puede ser insuficiente (n ≥ 30 recomendado)")
        print("• Verificar si hay bimodalidad (ej., actividad crepuscular)")

    return df, resultados

# Ejecutar el programa si se corre directamente
if __name__ == "__main__":
    try:
        df, resultados = menu_principal()

        # Preguntar si desea exportar datos transformados
        exportar = input("\n¿Desea exportar los datos transformados a CSV? (s/n): ").lower()
        if exportar == 's':
            nombre_csv = input("Nombre del archivo CSV (deje vacío para 'datos_transformados.csv'): ").strip()
            if not nombre_csv:
                nombre_csv = "datos_transformados.csv"
            df.to_csv(nombre_csv, index=False)
            print(f"✅ Datos exportados a '{nombre_csv}'")

    except KeyboardInterrupt:
        print("\n\n❌ Análisis interrumpido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("Por favor, verifique sus datos y vuelva a intentar.")
