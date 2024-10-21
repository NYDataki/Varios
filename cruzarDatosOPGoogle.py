import pandas as pd
from datetime import timedelta





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

def tablaInfo(csv_path):
    # Leer el archivo CSV
    df_original = pd.read_csv(csv_path)

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
    df_original.to_csv('PaperfishTemp/Paperfish SoBe con Pauta.csv', index=False)

    return df_original


# Codigo principal 
def main():
    # Leer los archivos CSV
    google = pd.read_csv('PaperfishTemp/data-export (16).csv', header=9)
    openTable = pd.read_csv('PaperfishTemp/Paperfish SoBe.csv')

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
    

if __name__ == "__main__":
    main()
