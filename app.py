import streamlit as st
import pandas as pd
import os
import calendar

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="Табель посещаемости", layout="wide")

# (Блок с паролем полностью удален)

# --- ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЙ (Месяц, Год, Выходные) ---
if 'current_month' not in st.session_state:
    st.session_state.current_month = 11
if 'current_year' not in st.session_state:
    st.session_state.current_year = 2026
if 'weekends' not in st.session_state:
    st.session_state.weekends = [] 

# --- БОКОВАЯ ПАНЕЛЬ С НАСТРОЙКАМИ ---
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
    st.header("📅 Выходные и праздники")
    st.write("Отметьте дни, в которые не было учебы. В эти дни нельзя будет вписать часы.")
    
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
    if st.button("🧹 Очистить часы (сделать 0)", type="secondary", use_container_width=True):
        current_db_file = f"tabell_{st.session_state.current_year}_{st.session_state.current_month}.csv"
        if 'df' in st.session_state:
            for d in st.session_state.df.columns:
                if d.isdigit():
                    st.session_state.df[d] = 0
            # Сохраняем локально (на хостинге это просто проигнорируется)
            try:
                st.session_state.df.to_csv(current_db_file, index=False, encoding='utf-8-sig')
            except:
                pass
            st.success("Часы очищены!")
            st.rerun()

# --- ШАПКА ДОКУМЕНТА ---
st.markdown(f"""
    <div style="text-align: center; font-size: 12px; margin-bottom: 10px;">
        <b>РОССИЙСКАЯ ФЕДЕРАЦИЯ</b><br>
        АВТОНОМНАЯ НЕКОММЕРЧЕСКАЯ ОБРАЗОВАТЕЛЬНАЯ ОРГАНИЗАЦИЯ<br>
        ВЫСШЕГО ОБРАЗОВАНИЯ<br>
        <b>«РУССКИЙ УНИВЕРСИТЕТ КООПЕРАЦИИ»</b><br>
        СТРУКТУРНОЕ ПОДРАЗДЕЛЕНИЕ СРЕДНЕГО ПРОФЕССИОНАЛЬНОГО ОБРАЗОВАНИЯ<br>
        КОЛЛЕДЖ<br><br>
    </div>
    <div style="text-align: center; font-size: 20px; margin-bottom: 20px;">
        <b>ТАБЕЛЬ УЧЕТА ПОСЕЩАЕМОСТИ</b><br>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 10px;">
        <div>Группа: <b>РУПО 26/11</b></div>
        <div>Месяц, год: <b>{months_names[st.session_state.current_month - 1]} {st.session_state.current_year}</b></div>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- СПИСОК СТУДЕНТОВ ---
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

# --- ЛОГИКА ЗАГРУЗКИ ДАННЫХ ---
# Пытаемся загрузить с диска (если запускаем локально), иначе создаем пустую таблицу
current_db_file = f"tabell_{st.session_state.current_year}_{st.session_state.current_month}.csv"

if 'df' not in st.session_state:
    file_loaded = False
    # Безопасная попытка загрузить файл
    if os.path.exists(current_db_file):
        try:
            loaded_df = pd.read_csv(current_db_file)
            if len(loaded_df) == len(students_list):
                loaded_df['ФИО'] = loaded_df['ФИО'].astype(str).fillna('')
                loaded_df['Примечание'] = loaded_df['Примечание'].astype(str).replace('nan', '').fillna('')
                if '№' in loaded_df.columns:
                    loaded_df['№'] = loaded_df['№'].astype(str).replace('nan', '').fillna('')
                for d in days:
                    if d in loaded_df.columns:
                        loaded_df[d] = pd.to_numeric(loaded_df[d], errors='coerce').fillna(0).astype(int)
                    else:
                        loaded_df[d] = 0 
                st.session_state.df = loaded_df
                file_loaded = True
        except Exception:
            pass # Если файл битый, просто игнорируем его

    if not file_loaded:
        columns = ['№', 'ФИО'] + days + ['Всего часов', 'Всего дней', '%', 'Примечание']
        df = pd.DataFrame(columns=columns)
        for i, name in enumerate(students_list):
            row = [str(i+1), name] + [0]*len(days) + [0, 0, "0.00%", ""]
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
    column_config[day] = st.column_config.NumberColumn(
        day, min_value=0, max_value=10, step=1, disabled=is_weekend, 
        help="Выходной день" if is_weekend else "Введите часы пропусков"
    )

st.info("💡 Все изменения сохраняются в памяти. Если вы обновите страницу, они сбросятся (если не нажимать скачать).")

edited_df = st.data_editor(
    st.session_state.df, column_config=column_config, use_container_width=True, 
    hide_index=True, key="attendance_editor", num_rows="dynamic" 
)

# --- РАСЧЕТЫ ---
total_hours_in_month = len(days) * 6 
weekend_hours = len(st.session_state.weekends) * 6
actual_study_hours = total_hours_in_month - weekend_hours

for wd in st.session_state.weekends:
    if str(wd) in edited_df.columns:
        edited_df[str(wd)] = 0

edited_df['Всего часов'] = edited_df[days].sum(axis=1)
edited_df['Всего дней'] = (edited_df[days] > 0).sum(axis=1)
edited_df['%'] = ((actual_study_hours - edited_df['Всего часов']) / actual_study_hours * 100).apply(lambda x: f"{max(0, x):.2f}%" if actual_study_hours > 0 else "100.00%")

st.session_state.df = edited_df

# Пробуем сохранить локально (на хостинге просто проигнорирует)
try:
    edited_df.to_csv(current_db_file, index=False, encoding='utf-8-sig')
except:
    pass

# --- ИТОГО ---
st.markdown("### Итого по группе за день")
totals_row = edited_df[days].sum().to_dict()
totals_row['ФИО'] = 'ИТОГО:'
totals_row['№'] = ''
df_totals = pd.DataFrame([totals_row])[['№', 'ФИО'] + days]
st.dataframe(df_totals, use_container_width=True, hide_index=True)

# --- СКАЧАТЬ РЕЗЕРВНУЮ КОПИЮ ---
st.markdown("---")
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8-sig')

csv = convert_df(edited_df)

st.download_button(label=f"📥 Скачать в Excel ({months_names[st.session_state.current_month - 1]})", data=csv, file_name=f'Табель_{st.session_state.current_month}_{st.session_state.current_year}.csv', mime='text/csv')
