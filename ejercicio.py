
import pandas as pd
from zoneinfo import ZoneInfo

groups_df = pd.read_csv('STUDENT_GROUP.csv')
attendance_df = pd.read_csv('attendance.csv')

print("✅ Archivos cargados correctamente")
print("Columnas en groups_df:", groups_df.columns.tolist())
print("Columnas en attendance_df:", attendance_df.columns.tolist())

print("\nTipos de datos en groups_df:")
print(groups_df.dtypes)
print("\nTipos de datos en attendance_df:")
print(attendance_df.dtypes)


groups_df['student_key'] = pd.to_numeric(groups_df['student_id'], errors='coerce') \
    .apply(lambda v: str(int(v)) if pd.notna(v) else None)

attendance_df['student_key'] = pd.to_numeric(attendance_df['STUDENT_ID'], errors='coerce') \
    .apply(lambda v: str(int(v)) if pd.notna(v) else None)


attendance_df['DTTM_utc'] = pd.to_datetime(attendance_df['DTTM'], errors='coerce', utc=True)
attendance_df['DTTM_local'] = attendance_df['DTTM_utc'].dt.tz_convert(ZoneInfo("America/Monterrey"))

attendance_df['DATE_local'] = attendance_df['DTTM_local'].dt.date

merged = groups_df[['group_id', 'student_key']].merge(
    attendance_df[['student_key', 'DATE_local']],
    on='student_key',
    how='inner'
)

print("\n✅ Merge completado. Primeras filas:")
print(merged.head())

roster = groups_df.groupby('group_id')['student_key'].nunique().rename('total_alumnos')

presentes = (
    merged.groupby(['group_id', 'DATE_local'])['student_key']
    .nunique()
    .rename('asistieron')
    .reset_index()
)

presentes = presentes.merge(roster.reset_index(), on='group_id', how='left')

presentes['ausencias'] = (presentes['total_alumnos'] - presentes['asistieron']).clip(lower=0)

max_por_grupo = presentes.groupby('group_id')['ausencias'].transform('max')
presentes['es_max_del_grupo'] = presentes['ausencias'] == max_por_grupo

reporte_max = (
    presentes[presentes['es_max_del_grupo']]
    .sort_values(['group_id', 'DATE_local'])
    .reset_index(drop=True)
)

print("\nResumen (primeras filas):")
print(presentes.head(10).to_string(index=False))

print("\nDías con más ausencias por grupo:")
print(reporte_max.to_string(index=False))
