import streamlit as st
import pandas as pd
import hmac

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="Табель посещаемости", layout="wide")

# --- ЗАЩИТА ПАРОЛЕМ ---
def check_password():
    def password_entered():
        # Проверяем пароль из настроек
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input("Введите пароль для доступа к табелю", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state:
        st.error("😕 Неверный пароль. Попробуйте еще раз.")
    return False

if not check_password():
    st.stop()  # Сайт не загрузится, пока не введешь пароль

# --- ЕСЛИ ПАРОЛЬ ВЕРНЫЙ, ПОКАЗЫВАЕМ ТАБЕЛЬ ---

st.markdown("""
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
        <div>Группа: <b>09.02.11</b></div>
        <div>Месяц, год: <b>Ноябрь 2026</b></div>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

students_list = [
    "Алена Ани Кэлвинэй", "Алиса Валерьевна Иванова", "Анастасия Ильинична Мамедова",
    "Ангелина Тимуровна Федосеева", "Батыр Бексолтанович Ахметов", "Валерия Викторовна Ибрагимова",
    "Даниил Вячеславович Кузнецов", "Даниэль Юрьевич Змиевский", "Дмитрий Иванович Калмыков",
    "Дмитрий Валерьевич Клюковкин", "Егор Андреевич Чугунов", "Екатерина Витальевна Малышева",
    "Екатерина Андреевна Пешкова", "Ислам Артурович Ильясов", "Магомед Мусаевич Бекмурзаев",
    "Магомед Тагирович Магомедов", "Милена Романовна Абасова", "Мирзахан Шамилович Абдуллаев",
    "Мурад Асланович Гандалоев", "Муслим Алиханович Исмаилов", "Павел Богданович Аслаханов",
    "Роман Романович Денисенко", "Руслан Ахмедович Эльмурзаев", "Савва Евгеньевич Овчаренко",
    "Сергей Олегович Константинов", "Хамзат Саид-Магомедович Цечоев", "Чингисхан Шарапудинович Курамагомедов"
]

days = [str(i) for i in range(1, 31)]

if 'df' not in st.session_state:
    columns = ['№', 'ФИО'] + days + ['Всего часов', 'Всего дней', '%', 'Примечание']
    df = pd.DataFrame(columns=columns)
    for i, name in enumerate(students_list):
        row = [i+1, name] + [0]*30 + [0, 0, "0.00%", ""]
        df.loc[len(df)] = row
    st.session_state.df = df

column_config = {
    "№": st.column_config.NumberColumn("№", width="small", disabled=True),
    "ФИО": st.column_config.TextColumn("Фамилия, имя, отчество", width="medium", disabled=True),
    "Всего часов": st.column_config.NumberColumn("Всего часов", disabled=True),
    "Всего дней": st.column_config.NumberColumn("Всего дней", disabled=True),
    "%": st.column_config.TextColumn("%", disabled=True),
    "Примечание": st.column_config.TextColumn("Примечание")
}

for day in days:
    column_config[day] = st.column_config.NumberColumn(day, min_value=0, max_value=10, step=1, help="Введите часы пропусков")

st.write("### Ввод данных")
st.info("💡 Вписывайте часы пропусков в клетки (например, 4, 6). Если студент был — оставляйте 0.")

edited_df = st.data_editor(st.session_state.df, column_config=column_config, use_container_width=True, hide_index=True, key="attendance_editor")

edited_df['Всего часов'] = edited_df[days].sum(axis=1)
edited_df['Всего дней'] = (edited_df[days] > 0).sum(axis=1)
total_hours_in_month = 120 
edited_df['%'] = ((total_hours_in_month - edited_df['Всего часов']) / total_hours_in_month * 100).apply(lambda x: f"{max(0, x):.2f}%")

st.session_state.df = edited_df

st.markdown("### Итого по группе за день")
totals_row = edited_df[days].sum().to_dict()
totals_row['ФИО'] = 'ИТОГО:'
totals_row['№'] = ''
df_totals = pd.DataFrame([totals_row])[['№', 'ФИО'] + days]
st.dataframe(df_totals, use_container_width=True, hide_index=True)

st.markdown("---")
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8-sig')

csv = convert_df(edited_df)

st.download_button(label="📥 Скачать в Excel", data=csv, file_name='Табель_посещаемости.csv', mime='text/csv')
