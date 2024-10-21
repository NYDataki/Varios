import pandas as pd
from datetime import timedelta
import numpy as np






def contiene(valor):
    pautaValidas = ['google','instagram','facebook','yelp','tripadvisor','YELP']
    for i in pautaValidas:
        if i in valor:
            return True
    return False
    

def clean_inf_values(df):
    # Replace inf values with NaN
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # Optionally, fill NaN values with 0 or other strategies
    df.fillna(0, inplace=True)
    
    return df



# Logica de Atribucion para la Pauta
def atribucion(google,openTable,auxOP):
    for i,x in enumerate(openTable['Google Fecha']):
        if openTable['Fuente'][i] == 'Tu red' or openTable['Fuente'][i] == 'Red de OpenTable':
            mayorTiempo = 0
            pauta = 0
            for j,y in enumerate(google['Fecha y hora (AAAAMMDDHH)']):
                if x == y:  
                    if contiene(google['Fuente/medio de la sesión'][j]) == True:
                        print(1)
                        if google['Tiempo de interacción medio por sesión'][j] >= mayorTiempo:
                            mayorTiempo = google['Tiempo de interacción medio por sesión'][j]
                            pauta = google['Fuente/medio de la sesión'][j]
    
            if pauta != 0 and openTable['Fuente'][i] == 'Tu red' or openTable['Fuente'][i] == 'Red de OpenTable':
                auxOP.loc[i,'Pauta'] = pauta

    return auxOP


def generate_table(csv_path, output_csv_path):
    # Load the CSV
    df = pd.read_csv(csv_path)


    # Ensure 'Título de la experiencia' is a string
    df['Título de la experiencia'] = df['Título de la experiencia'].astype(str)

    # Define the conditions for 'Spice'
    spice_conditions = [
        'Miami Spice meets Salty Flame!',
        'Miami Spice meets Salty Flame | Dinner menu!',
        'Miami Spice meets Salty Flame | Lunch menu!',
        'Miami Spice meets Salty Flame | Brunch menu!'
    ]

    # Create a new column to count 'Spice' based on multiple conditions
    df['Spice'] = df['Título de la experiencia'].apply(lambda x: any(item in x for item in spice_conditions))

    # Create a new column to count 'Brunch'
    brunch_condition = "Salty Flame's New Bubbly Brunch"
    df['Brunch'] = df['Título de la experiencia'].apply(lambda x: brunch_condition in x)

    # Convert 'Hora de la visita' to datetime to simplify time comparisons
    df['Hora de la visita'] = pd.to_datetime(df['Hora de la visita'], format='%H:%M').dt.time

    # Define time ranges
    mediodia_start, mediodia_end = pd.to_datetime('07:00', format='%H:%M').time(), pd.to_datetime('16:00', format='%H:%M').time()
    noche_start = pd.to_datetime('16:00', format='%H:%M').time()

    # Create columns based on time conditions
    df['Mediodia Totales'] = df['Hora de la visita'].apply(lambda x: mediodia_start <= x <= mediodia_end)
    df['Noche Totales'] = df['Hora de la visita'].apply(lambda x: x > noche_start)

    # Group by 'Pauta' and aggregate the counts
    result = df.groupby('Pauta').agg({
        'Spice': 'sum',
        'Brunch': 'sum',
        'Mediodia Totales': 'sum',
        'Noche Totales': 'sum'
    }).reset_index()

    # Calculate totals row and create a DataFrame
    total_row = pd.DataFrame([['Total'] + result[['Spice', 'Brunch', 'Mediodia Totales', 'Noche Totales']].sum().tolist()], columns=result.columns)

    # Concatenate the result with the totals row
    final_result = pd.concat([result, total_row], ignore_index=True)

    # Save to CSV
    final_result.to_csv(output_csv_path, index=False)
    return final_result

def tablaInfo(csv_path):
    # Leer el archivo CSV
    df_original = pd.read_csv(csv_path)

    # Limpiar valores 'inf' en el DataFrame
    df_original = clean_inf_values(df_original)

    # Convertir las columnas a numérico, manejando valores no numéricos
    for col in ['Ingresos totales', 'Propina total']:
        df_original[col] = pd.to_numeric(df_original[col], errors='coerce').fillna(0)

    # Crear la columna de ingresos totales
    df_original['Ingresos Totales Temp'] = df_original['Ingresos totales'] + df_original['Propina total']

    # Agrupar por 'Pauta' y calcular las sumas y conteos necesarios
    resultado = df_original.groupby('Pauta').agg({
        'Ingresos Totales Temp': 'sum',   # Sumar ingresos totales por pauta
        'Tamaño': 'sum',             # Sumar todos los invitados por pauta
        'Pauta': 'size'             # Contar entradas (reservaciones) por pauta
    }).rename(columns={'Pauta': 'Reservaciones Totales', 'Ingresos Totales Temp': 'Ingresos Totales'})

    # Resetear el índice para que 'Pauta' sea una columna y no el índice
    resultado.reset_index(inplace=True)

    # Renombrar las columnas según los requerimientos
    resultado.columns = ['Pauta', 'Ingresos Totales', 'Invitados Totales', 'Reservaciones Totales']

    # Añadir dos columnas de separación
    num_columns = len(df_original.columns)
    df_original[num_columns] = ''  # Primera columna de separación
    df_original[num_columns+1] = ''  # Segunda columna de separación

    # Insertar los datos de 'resultado' en el DataFrame original
    for col in resultado.columns:
        df_original[f"{col} (agregado)"] = resultado[col]

    # Guardar el DataFrame modificado
    df_original.to_csv('14-20Oct/SaltyFlame14a20OctubreCruzado.csv', index=False)

    return df_original

# Codigo principal 
def main():
    # Leer los archivos CSV
    google = pd.read_csv('14-20Oct/data-export (31).csv', header=9)
    openTable = pd.read_csv('14-20Oct/GuestCenter__1334533_2024-10-21_1206.csv')
    output_csv_path = '14-20Oct/TablaInfo.csv'

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


    tablaInfo('auxTabla.csv')
    generate_table('auxTabla.csv', output_csv_path)
    

if __name__ == "__main__":
    main()