import streamlit as st
import pandas as pd
import calendar
import streamlit_persist_session
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="Табель посещаемости", layout="wide")

# --- КЛАСС ДЛЯ АВТОСОХРАНЕНИЯ ---
# Этот класс будет автоматически сохраняться на сервере и привязываться к твоему браузеру
@streamlit_persist_session.persist("attendance-state")
class AppState:
    def __init__(self):
        self.df = None
        self.current_month = 11
        self.current_year = 2026
        self.weekends = []

# Инициализация состояния (загружается из файла, если он есть)
state = AppState()

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.header("⚙️ Настройки")
    months_names = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    
    selected_month = st.selectbox("Месяц", options=range(1, 13), format_func=lambda x: months_names[x-1], index=state.current_month - 1)
    selected_year = st.number_input("Год", min_value=2020, max_value=2030, value=state.current_year)
    
    if selected_month != state.current_month or selected_year != state.current_year:
        state.current_month = selected_month
        state.current_year = selected_year
        state.df = None  # Сбрасываем таблицу при смене месяца
        st.rerun()

    st.markdown("---")
    st.header("📅 Выходные")
    num_days_in_month = calendar.monthrange(state.current_year, state.current_month)[1]
    
    selected_weekends = st.multiselect(
        "Выберите числа:",
        options=list(range(1, num_days_in_month + 1)),
        default=state.weekends
    )
    
    if selected_weekends != state.weekends:
        state.weekends = selected_weekends
        st.rerun()

# --- ШАПКА ---
st.markdown(f"""
    <div style="text-align: center; font-size: 20px; margin-bottom: 20px;">
        <b>ТАБЕЛЬ УЧЕТА ПОСЕЩАЕМОСТИ</b><br>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 10px;">
        <div>Группа: <b>РУПО 26/11</b></div>
        <div>Месяц, год: <b>{months_names[state.current_month - 1]} {state.current_year}</b></div>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- СПИСОК СТУДЕНТОВ ---
students_list = [
    "Агаев Али Камилович", "Алирзаев Магомед Ифтихар оглы", "Апшиков Даниял Анурович",
    "Ахметшин Тимур Филюсович", "Бабенцев Егор Маркович", "Варшавец Елисей Александрович",
    "Гайнуллин Вячеслав Юрьевич", "Гасанбеков Фархад Игнатович", "Гумеров Владимир Яковлевич",
    "Дегтярева Татьяна Николаевна", "Денисенко Егор Андреевич", "Дмитриев Владислав Павлович",
    "Ермаков Артем Ильич", "Колмогоров Даниил Николаевич", "Кузнецов Артем Михайлович",
    "Лазарев Дмитрий Сергеевич", "Макаренко Никита Николаевич", "Марков Степан Александрович",
    "Мельников Богдан Артёмович", "Мирошниченко Алексей Андреевич", "Папымере Илья Алексеевич",
    "Протопопов Ярослав Алексеевич", "Розыков Самандар Орифжонович", "Савченко Владислав Вадимович",
    "Сорокин Олег Константинович", "Хаммадиев Тимур Рафаэльевич", "Чепак Савелий Павлович",
    "Эсонов Шахриер Фаррухович"
]
days = [str(i) for i in range(1, num_days_in_month + 1)]

# --- ЛОГИКА СОЗДАНИЯ ТАБЛИЦЫ ---
# Если таблицы нет в сохраненном состоянии, создаем её
if state.df is None:
    columns = ['№', 'ФИО'] + days + ['Всего часов', 'Всего дней', '%', 'Примечание']
    df = pd.DataFrame(columns=columns)
    for i, name in enumerate(students_list):
        row = [str(i+1), name] + [None]*len(days) + [0, 0, "0.00%", ""]
        df.loc[len(df)] = row
    state.df = df

# --- НАСТРОЙКА ТАБЛИЦЫ ---
column_config = {
    "№": st.column_config.TextColumn("№", width="small", disabled=True),
    "ФИО": st.column_config.TextColumn("Фамилия, имя, отчество", width="large", disabled=True),
    "Всего часов": st.column_config.NumberColumn("Всего часов", disabled=True),
    "Всего дней": st.column_config.NumberColumn("Всего дней", disabled=True),
    "%": st.column_config.TextColumn("%", disabled=True),
    "Примечание": st.column_config.TextColumn("Примечание")
}
for day in days:
    is_weekend = int(day) in state.weekends
    column_config[day] = st.column_config.NumberColumn(day, min_value=0, max_value=20, step=1, disabled=is_weekend)

st.info("💡 Вводите часы вручную. Все изменения сохраняются автоматически на сервере.")

# --- ОТРИСОВКА ТАБЛИЦЫ ---
edited_df = st.data_editor(
    state.df, 
    column_config=column_config, 
    use_container_width=True, 
    hide_index=True, 
    key="editor_input",
    num_rows="fixed" 
)

# Если таблица была отредактирована, сохраняем её в состояние
if not edited_df.equals(state.df):
    state.df = edited_df

# --- КНОПКА ПЕРЕСЧЕТА ---
st.markdown("---")
if st.button("🔄 Пересчитать и обновить итоги", type="primary", use_container_width=True):
    for wd in state.weekends:
        if str(wd) in edited_df.columns:
            edited_df[str(wd)] = None 
            
    df_for_calc = edited_df.copy()
    for d in days:
        df_for_calc[d] = pd.to_numeric(df_for_calc[d], errors='coerce').fillna(0)

    total_hours_in_month = len(days) * 6 
    weekend_hours = len(state.weekends) * 6
    actual_study_hours = total_hours_in_month - weekend_hours

    df_for_calc['Всего часов'] = df_for_calc[days].sum(axis=1)
    df_for_calc['Всего дней'] = (df_for_calc[days] > 0).sum(axis=1)
    df_for_calc['%'] = ((actual_study_hours - df_for_calc['Всего часов']) / actual_study_hours * 100).apply(lambda x: f"{max(0, x):.2f}%" if actual_study_hours > 0 else "100.00%")
    
    for d in days:
        edited_df[d] = df_for_calc[d].replace(0, None)
        
    edited_df['Всего часов'] = df_for_calc['Всего часов']
    edited_df['Всего дней'] = df_for_calc['Всего дней']
    edited_df['%'] = df_for_calc['%']
    
    state.df = edited_df
    st.success("Данные пересчитаны и сохранены!")
    st.rerun()

# --- БЛОК СВОДКИ И БЫСТРОЙ ОТМЕТКИ ---
st.markdown("---")
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Краткая сводка")
    avg_percent = pd.to_numeric(state.df['%'].str.replace('%', ''), errors='coerce').mean()
    df_sorted = state.df.sort_values(by='%', ascending=True)
    worst_students = df_sorted.head(3)[['ФИО', '%']]
    
    st.metric(label="Средняя посещаемость группы", value=f"{avg_percent:.1f}%" if pd.notna(avg_percent) else "0%")
    
    st.write("**Топ-3 должников:**")
    for index, row in worst_students.iterrows():
        st.write(f"- {row['ФИО']} — {row['%']}")

with col2:
    st.subheader("⚡ Быстрая отметка")
    st.write("Отметьте галочками тех, кто **ПРИШЕЛ**. Остальным прибавятся часы.")
    
    col_date, col_lesson, col_hours = st.columns(3)
    with col_date:
        selected_day = st.selectbox("День:", options=days, index=0)
    with col_lesson:
        lesson_num = st.selectbox("Пара №:", options=[1, 2, 3, 4, 5], index=0)
    with col_hours:
        hours_per_lesson = st.number_input("Часов в паре:", min_value=1, max_value=4, value=2)
        
    with st.form("quick_attendance_form"):
        attendance_checks = {}
        for i, name in enumerate(state.df['ФИО']):
            attendance_checks[i] = st.checkbox(f"{name}", value=True, key=f"check_{i}")
            
        submit_quick = st.form_submit_button(f"Применить (Пара №{lesson_num})", type="primary")
        
        if submit_quick:
            if selected_day in state.weekends:
                st.error("Этот день выходной.")
            else:
                for i, was_present in attendance_checks.items():
                    current_val = state.df.at[i, selected_day]
                    if pd.isna(current_val):
                        current_val = 0
                    if not was_present:
                        state.df.at[i, selected_day] = current_val + hours_per_lesson
                
                df_for_calc = state.df.copy()
                for d in days:
                    df_for_calc[d] = pd.to_numeric(df_for_calc[d], errors='coerce').fillna(0)

                total_hours_in_month = len(days) * 6 
                weekend_hours = len(state.weekends) * 6
                actual_study_hours = total_hours_in_month - weekend_hours

                df_for_calc['Всего часов'] = df_for_calc[days].sum(axis=1)
                df_for_calc['Всего дней'] = (df_for_calc[days] > 0).sum(axis=1)
                df_for_calc['%'] = ((actual_study_hours - df_for_calc['Всего часов']) / actual_study_hours * 100).apply(lambda x: f"{max(0, x):.2f}%" if actual_study_hours > 0 else "100.00%")
                
                for d in days:
                    state.df[d] = df_for_calc[d].replace(0, None)
                
                state.df['Всего часов'] = df_for_calc['Всего часов']
                state.df['Всего дней'] = df_for_calc['Всего дней']
                state.df['%'] = df_for_calc['%']
                
                st.success(f"Отметки за {selected_day} число применены!")
                st.rerun()

# --- СКАЧИВАНИЕ EXCEL (оставим на всякий случай) ---
def create_styled_excel(df, month_name, year):
    output = BytesIO()
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = f"Табель {month_name}"

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="center")
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    
    worksheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(df.columns))
    worksheet.cell(row=1, column=1, value=f"ТАБЕЛЬ УЧЕТА ПОСЕЩАЕМОСТИ\nГруппа: РУПО 26/11 | {month_name} {year}").font = Font(bold=True, size=14)
    worksheet.cell(row=1, column=1).alignment = center_align
    worksheet.row_dimensions[1].height = 40

    headers = list(df.columns)
    for col_num, header in enumerate(headers, 1):
        cell = worksheet.cell(row=3, column=col_num, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border
    
    for row_idx, row_data in enumerate(df.values, 4):
        for col_idx, value in enumerate(row_data, 1):
            cell = worksheet.cell(row=row_idx, column=col_idx)
            if pd.isna(value):
                cell.value = ""
            else:
                cell.value = value
            cell.border = thin_border
            cell.alignment = center_align if headers[col_idx-1] not in ["ФИО", "Примечание"] else left_align

    for i in range(1, len(headers) + 1):
        col_letter = get_column_letter(i)
        header_name = headers[i-1]
        if header_name == "№":
            worksheet.column_dimensions[col_letter].width = 5
        elif header_name == "ФИО":
            worksheet.column_dimensions[col_letter].width = 35
        elif header_name in ["Всего часов", "Всего дней", "%", "Примечание"]:
            worksheet.column_dimensions[col_letter].width = 15
        else:
            worksheet.column_dimensions[col_letter].width = 5

    workbook.save(output)
    output.seek(0)
    return output

st.markdown("---")
excel_file = create_styled_excel(state.df, months_names[state.current_month - 1], state.current_year)

st.download_button(
    label=f"📥 Скачать красивый Excel (резервная копия)", 
    data=excel_file, 
    file_name=f'Табель_{state.current_month}_{state.current_year}.xlsx', 
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    use_container_width=True
)
