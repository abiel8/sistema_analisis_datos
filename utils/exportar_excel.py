from io import BytesIO
import pandas as pd


def exportar_excel(df):

    buffer = BytesIO()

    with pd.ExcelWriter(
            buffer,
            engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Reporte",
            index=False
        )

    return buffer.getvalue()