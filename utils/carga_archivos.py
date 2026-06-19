import pandas as pd

def cargar_archivo(
        archivo,
        hoja=0,
        fila_encabezado=1):

    if archivo.name.endswith(".csv"):
        return pd.read_csv(
            archivo
        )

    elif archivo.name.endswith(".xls"):
        return pd.read_excel(
            archivo,
            sheet_name=hoja,
            header=fila_encabezado - 1,
            engine="xlrd"
        )

    else:  # .xlsx
        return pd.read_excel(
            archivo,
            sheet_name=hoja,
            header=fila_encabezado - 1,
            engine="openpyxl"
        )