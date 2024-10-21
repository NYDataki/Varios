import pandas as pd
from datetime import timedelta
import os
import numpy as np







def contiene(valor):
    pautaValidas = ['google','instagram','facebook','yelp','tripadvisor','YELP']
    for i in pautaValidas:
        if i in valor:
            return True
    return False
    



# Logica de Atribucion para la Pauta
def atribucion(google,openTable,auxOP):
    for i,x in enumerate(openTable['Google Fecha']):
        if openTable['Fuente'][i] == 'Tu red':
            mayorTiempo = 0
            pauta = 0
            for j,y in enumerate(google['Fecha y hora (AAAAMMDDHH)']):
                if x == y:  
                    if contiene(google['Fuente/medio de la sesión'][j]) == True:
                        print(1)
                        if google['Tiempo de interacción medio por sesión'][j] >= mayorTiempo:
                            mayorTiempo = google['Tiempo de interacción medio por sesión'][j]
                            pauta = google['Fuente/medio de la sesión'][j]
    
            if pauta != 0 and openTable['Fuente'][i] == 'Tu red':
                auxOP.loc[i,'Pauta'] = pauta

    return auxOP

def get_avg_check_value(csv_path):
    # Dictionary mapping locations or datasheet names to avg_check values
    avg_check_values = {
        'Barsecco': 55.24,
        'Marabu': 53.43,
        'Paperfish B': 63.01,
        'Paperfish SoBe': 54.72,
        'CA Brickell': 31.78,
        'Salty Flame': 65.14,
        'Havana EW': 45.34,
        'Havana LR': 44.38,
        'Havana PP': 45.07,
        'Havana OD 14': 48.22,
        'Havana OD 9': 48.13,
        'Oh Mex EW': 43.83,
        'Oh Mex LR': 42.24,
        'MDP EW': 69.30,
        'News Cafe': 35.37,
        'Oh Mex OD': 41.06,
        'ODM': 36.87,
        'MDM': 41.88,
        'CA Collins': 36.87,
        'CA CPV': 33.95,
        'CA PV': 29.06,
        'MDP V': 42.75,
        'CA OD': 41.88,
        # Add more mappings as needed
    }

    # Extract the name of the datasheet (assuming it's part of the file name)
    datasheet_name = os.path.basename(csv_path).split('.')[0]

    # Get the avg_check value from the dictionary, default to 0 if not found
    avg_check = avg_check_values.get(datasheet_name, 0)

    return avg_check

def tablaInfo(csv_path, avg_check, openTable_path):
    # Leer el archivo CSV
    df_original = pd.read_csv(csv_path)

    # Replace "inf" values with NaN, and then fill NaN with 0
    df_original.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_original.fillna(0, inplace=True)  # If you want to replace with 0
    # Alternatively, you can use fillna('') if you want to replace with an empty cell

    # Convertir las columnas a numérico, manejando valores no numéricos
    for col in ['Ingresos totales', 'Propina total']:
        df_original[col] = pd.to_numeric(df_original[col], errors='coerce').fillna(0)

    # Crear la columna de ingresos totales
    df_original['Ingresos Totales Temp'] = df_original['Ingresos totales'] + df_original['Propina total']

    # Definir los estados que se consideran completados
    estados_completados = ["Listo", "Confirmado", "Marcado como sentado", "Asumido como terminado"]

    # Filtrar las filas que tienen un estado completado
    df_completados = df_original[df_original['Estado'].isin(estados_completados)]

    # Agrupar por 'Pauta' y calcular las sumas y conteos necesarios
    resultado = df_original.groupby('Pauta').agg({
        'Ingresos Totales Temp': 'sum',   # Sumar ingresos totales por pauta
        'Tamaño': 'sum',                  # Sumar todos los invitados por pauta
        'Pauta': 'size'                   # Contar entradas (reservaciones) por pauta
    }).rename(columns={'Pauta': 'Reservaciones Totales', 'Ingresos Totales Temp': 'Ingresos Totales'})

    # Calcular las nuevas columnas
    completados = df_completados.groupby('Pauta').agg({
        'Estado': 'size',   # Contar el número de visitas completadas
        'Tamaño': 'sum'     # Sumar el número de invitados completados
    }).rename(columns={'Estado': 'Visitas Completadas', 'Tamaño': 'Invitados Completados'})

    # Añadir las columnas de visitas completadas e invitados completados
    resultado = resultado.join(completados, on='Pauta', how='left').fillna(0)

    # Calcular la columna de 'Ingresos x Avg Check'
    resultado['Ingresos x Avg Check'] = resultado['Invitados Completados'] * avg_check

    # Resetear el índice para que 'Pauta' sea una columna y no el índice
    resultado.reset_index(inplace=True)

    # Replace 0 with "Sin Pauta" in the 'Pauta' column
    resultado['Pauta'] = resultado['Pauta'].replace(0, 'Sin Pauta')

    # Renombrar las columnas según los requerimientos
    resultado.columns = ['Pauta', 'Ingresos Totales', 'Invitados Totales', 'Reservaciones Totales',
                         'Visitas Completadas', 'Invitados Completados', 'Ingresos x Avg Check']

    # Añadir dos columnas de separación
    num_columns = len(df_original.columns)
    df_original[num_columns] = ''  # Primera columna de separación
    df_original[num_columns+1] = ''  # Segunda columna de separación

    # Insertar los datos de 'resultado' en el DataFrame original
    for col in resultado.columns:
        df_original[f"{col} (agregado)"] = resultado[col]

    # Guardar el DataFrame modificado
    datasheet_name = os.path.basename(openTable_path).split('.')[0]
    df_original.to_csv(f'Cruzado Septiembre/{datasheet_name} con Pauta y Visitas Terminadas.csv', index=False)

    return df_original



# Codigo principal 
def main():
    # Leer los archivos CSV
    google_path = 'Google Exports Septiembre/Salty Sep.csv'
    openTable_path = 'OT Exports Septiembre/Salty Flame.csv'
    google = pd.read_csv(google_path, header=9)
    openTable = pd.read_csv(openTable_path)

    # Auxiliar para Open Table
    auxOP = []
    auxOP = openTable


    # Asegúrate de que las columnas se llamen 'fecha' y 'hora', o cambia los nombres en el código
    # Convertir las columnas de fecha y hora en datetime
    openTable['datetime'] = pd.to_datetime(openTable['Fecha de creación'] + ' ' + openTable['Hora de creación'])

    # Restar tres horas
    openTable['datetime'] = openTable['datetime'] - timedelta(hours=3)

    # Crear la nueva columna en el formato AAAAMMDDHH
    openTable['Google Fecha'] = openTable['datetime'].dt.strftime('%Y%m%d%H')

    # Transformar datos a INT
    google['Fecha y hora (AAAAMMDDHH)'].fillna(0, inplace=True)
    google['Fecha y hora (AAAAMMDDHH)'] = google['Fecha y hora (AAAAMMDDHH)'].astype(int)

    # Transformar datos a INT
    openTable['Google Fecha'].fillna(0, inplace=True)
    openTable['Google Fecha'] = openTable['Google Fecha'].astype(int)

    atribucion(google,openTable,auxOP)


    # Transformar Auxilar a Archivo CSV
    auxOP.to_csv('auxTabla.csv', index=False)

    avg_check = get_avg_check_value(openTable_path)
    print(avg_check)
    tablaInfo('auxTabla.csv',avg_check,openTable_path)
    

if __name__ == "__main__":
    main()
