import streamlit as st
import pandas as pd
import os
import calendar

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="Табель посещаемости", layout="wide")

# --- ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЙ ---
if 'current_month' not in st.session_state:
    st.session_state.current_month = 11
if 'current_year' not in st.session_state:
    st.session_state.current_year = 2026
if 'weekends' not in st.session_state:
    st.session_state.weekends = [] 

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.header("⚙️ Настройки")
    months_names = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    
    selected_month = st.selectbox("Месяц", options=range(1, 13), format_func=lambda x: months_names[x-1], index=st.session_state.current_month - 1)
    selected_year = st.number_input("Год", min_value=2020, max_value=2030, value=st.session_state.current_year)
    
    if selected_month != st.session_state.current_month or selected_year != st.session_state.current_year:
        st.session_state.current_month = selected_month
        st.session_state.current_year = selected_year
        if 'df' in st.session_state:
            del st.session_state.df
        st.rerun()

    st.markdown("---")
    st.header("📅 Выходные")
    num_days_in_month = calendar.monthrange(st.session_state.current_year, st.session_state.current_month)[1]
    
    selected_weekends = st.multiselect(
        "Выберите числа:",
        options=list(range(1, num_days_in_month + 1)),
        default=st.session_state.weekends
    )
    
    if selected_weekends != st.session_state.weekends:
        st.session_state.weekends = selected_weekends
        st.rerun()

    st.markdown("---")
    st.header("💾 Резервное копирование")
    st.write("На бесплатном хостинге данные могут стираться. Скачивайте копию в конце дня.")
    
    uploaded_file = st.file_uploader("Загрузить сохраненный табель (CSV)", type="csv")
    if uploaded_file is not None:
        try:
            loaded_data = pd.read_csv(uploaded_file)
            st.session_state.df = loaded_data
            st.success("Файл успешно загружен!")
        except Exception as e:
            st.error(f"Ошибка загрузки: {e}")

# --- ШАПКА ---
st.markdown(f"""
    <div style="text-align: center; font-size: 20px; margin-bottom: 20px;">
        <b>ТАБЕЛЬ УЧЕТА ПОСЕЩАЕМОСТИ</b><br>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 10px;">
        <div>Группа: <b>РУПО 26/11</b></div>
        <div>Месяц, год: <b>{months_names[st.session_state.current_month - 1]} {st.session_state.current_year}</b></div>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

students_list = [
    "Бабенцев Егор Маркович", "Агаев Али Камилович", "Алирзаев Магомед Ифтихар оглы",
    "Апшиков Даниял Анурович", "Ахметшин Тимур Филюсович", "Варшавец Елисей Александрович",
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

# --- ЛОГИКА СОЗДАНИЯ ТАБЛИЦЫ (ПУСТЫЕ ЯЧЕЙКИ ВМЕСТО НУЛЕЙ) ---
if 'df' not in st.session_state:
    columns = ['№', 'ФИО'] + days + ['Всего часов', 'Всего дней', '%', 'Примечание']
    df = pd.DataFrame(columns=columns)
    for i, name in enumerate(students_list):
        # Вместо 0 используем None (пустоту). В ячейках будет пусто.
        row = [str(i+1), name] + [None]*len(days) + [0, 0, "0.00%", ""]
        df.loc[len(df)] = row
    st.session_state.df = df

# --- НАСТРОЙКА ТАБЛИЦЫ ---
column_config = {
    "№": st.column_config.TextColumn("№", width="small"), 
    "ФИО": st.column_config.TextColumn("Фамилия, имя, отчество", width="large"), 
    "Всего часов": st.column_config.NumberColumn("Всего часов", disabled=True),
    "Всего дней": st.column_config.NumberColumn("Всего дней", disabled=True),
    "%": st.column_config.TextColumn("%", disabled=True),
    "Примечание": st.column_config.TextColumn("Примечание")
}
for day in days:
    is_weekend = int(day) in st.session_state.weekends
    # Разрешаем пустые значения (None)
    column_config[day] = st.column_config.NumberColumn(day, min_value=0, max_value=20, step=1, disabled=is_weekend)

st.info("💡 Вводите часы вручную. Пустые клетки означают, что студент был. Нажмите кнопку ниже для пересчета.")

edited_df = st.data_editor(
    st.session_state.df, 
    column_config=column_config, 
    use_container_width=True, 
    hide_index=True, 
    key="editor_input",
    num_rows="dynamic" 
)

# --- КНОПКА ПЕРЕСЧЕТА ---
st.markdown("---")
if st.button("🔄 Пересчитать проценты и обновить итоги", type="primary", use_container_width=True):
    # Обнуляем выходные дни
    for wd in st.session_state.weekends:
        if str(wd) in edited_df.columns:
            edited_df[str(wd)] = None # В выходные тоже ставим пустоту
            
    # Перед расчетами заменяем все None (пустые клетки) на 0
    df_for_calc = edited_df.copy()
    for d in days:
        df_for_calc[d] = pd.to_numeric(df_for_calc[d], errors='coerce').fillna(0)

    total_hours_in_month = len(days) * 6 
    weekend_hours = len(st.session_state.weekends) * 6
    actual_study_hours = total_hours_in_month - weekend_hours

    df_for_calc['Всего часов'] = df_for_calc[days].sum(axis=1)
    df_for_calc['Всего дней'] = (df_for_calc[days] > 0).sum(axis=1)
    df_for_calc['%'] = ((actual_study_hours - df_for_calc['Всего часов']) / actual_study_hours * 100).apply(lambda x: f"{max(0, x):.2f}%" if actual_study_hours > 0 else "100.00%")
    
    # Возвращаем пустые клетки обратно в редактируемый датафрейм, но обновляем расчеты
    for d in days:
        edited_df[d] = df_for_calc[d].replace(0, None) # Если 0, снова делаем пустоту для красоты
        
    edited_df['Всего часов'] = df_for_calc['Всего часов']
    edited_df['Всего дней'] = df_for_calc['Всего дней']
    edited_df['%'] = df_for_calc['%']
    
    st.session_state.df = edited_df
    st.success("Расчеты обновлены!")
    st.rerun()

# --- БЛОК СВОДКИ И БЫСТРОЙ ОТМЕТКИ ---
st.markdown("---")
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Краткая сводка")
    avg_percent = pd.to_numeric(st.session_state.df['%'].str.replace('%', ''), errors='coerce').mean()
    df_sorted = st.session_state.df.sort_values(by='%', ascending=True)
    worst_students = df_sorted.head(3)[['ФИО', '%']]
    
    st.metric(label="Средняя посещаемость группы", value=f"{avg_percent:.1f}%" if pd.notna(avg_percent) else "0%")
    
    st.write("**Топ-3 должников:**")
    for index, row in worst_students.iterrows():
        st.write(f"- {row['ФИО']} — {row['%']}")

with col2:
    st.subheader("⚡ Быстрая отметка")
    st.write("Отметьте галочками тех, кто **ПРИШЕЛ**. Остальным прибавятся часы пропуска.")
    
    col_date, col_lesson, col_hours = st.columns(3)
    with col_date:
        selected_day = st.selectbox("День:", options=days, index=0)
    with col_lesson:
        lesson_num = st.selectbox("Пара №:", options=[1, 2, 3, 4, 5], index=0)
    with col_hours:
        hours_per_lesson = st.number_input("Часов в паре:", min_value=1, max_value=4, value=2)
        
    with st.form("quick_attendance_form"):
        attendance_checks = {}
        for i, name in enumerate(st.session_state.df['ФИО']):
            attendance_checks[i] = st.checkbox(f"{name}", value=True, key=f"check_{i}")
            
        submit_quick = st.form_submit_button(f"Применить (Пара №{lesson_num})", type="primary")
        
        if submit_quick:
            if selected_day in st.session_state.weekends:
                st.error("Этот день отмечен как выходной. Сначала уберите его из выходных в левом меню.")
            else:
                for i, was_present in attendance_checks.items():
                    current_val = st.session_state.df.at[i, selected_day]
                    if pd.isna(current_val):
                        current_val = 0
                        
                    if not was_present:
                        # Прибавляем часы
                        st.session_state.df.at[i, selected_day] = current_val + hours_per_lesson
                
                # Сразу пересчитываем для обновления таблицы
                df_for_calc = st.session_state.df.copy()
                for d in days:
                    df_for_calc[d] = pd.to_numeric(df_for_calc[d], errors='coerce').fillna(0)

                total_hours_in_month = len(days) * 6 
                weekend_hours = len(st.session_state.weekends) * 6
                actual_study_hours = total_hours_in_month - weekend_hours

                df_for_calc['Всего часов'] = df_for_calc[days].sum(axis=1)
                df_for_calc['Всего дней'] = (df_for_calc[days] > 0).sum(axis=1)
                df_for_calc['%'] = ((actual_study_hours - df_for_calc['Всего часов']) / actual_study_hours * 100).apply(lambda x: f"{max(0, x):.2f}%" if actual_study_hours > 0 else "100.00%")
                
                for d in days:
                    st.session_state.df[d] = df_for_calc[d].replace(0, None)
                
                st.session_state.df['Всего часов'] = df_for_calc['Всего часов']
                st.session_state.df['Всего дней'] = df_for_calc['Всего дней']
                st.session_state.df['%'] = df_for_calc['%']
                
                st.success(f"Отметки за {selected_day} число (Пара №{lesson_num}) применены!")
                st.rerun()

# --- СКАЧАТЬ РЕЗЕРВНУЮ КОПИЮ ---
st.markdown("---")
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8-sig')

# При скачивании заменяем пустые клетки (NaN) на 0, чтобы в Excel было понятно
df_to_download = st.session_state.df.copy()
for d in days:
    df_to_download[d] = pd.to_numeric(df_to_download[d], errors='coerce').fillna(0)

csv = convert_df(df_to_download)

st.download_button(
    label=f"📥 Скачать табель в Excel ({months_names[st.session_state.current_month - 1]})", 
    data=csv, 
    file_name=f'Табель_{st.session_state.current_month}_{st.session_state.current_year}.csv', 
    mime='text/csv',
    use_container_width=True
)
