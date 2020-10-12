from flask import Flask
from flask import render_template

from flask_wtf import FlaskForm

from wtforms import StringField
from wtforms import HiddenField
from wtforms import SubmitField
from wtforms import RadioField

from wtforms.validators import InputRequired

import json

import os

import random

app = Flask(__name__)
app.secret_key = "randomstring777"

# Задаем словарики для удобства вывода в шаблонах

days = {'mon': 'Понедельник', 'tue': 'Вторник', 'wed': 'Среда', 'thu': 'Четверг', 'fri': 'Пятница', 'sat': 'Суббота',
        'sun': 'Воскресенье'}
pics = {'travel': '⛱', 'study': '🏫', 'work': '🏢', 'relocate': '🚜', 'programming': '✌'}

# Определяем классы под две формы бронирования (Booking) и запроса (Request)


class BookingForm(FlaskForm):
    clientName = StringField("Вас зовут", [InputRequired()])
    clientPhone = StringField("Ваш телефон", [InputRequired()])
    clientWeekday = HiddenField()
    clientTime = HiddenField()
    clientTeacher = HiddenField()
    submit = SubmitField('Записаться на пробный урок')


class RequestForm(FlaskForm):
    clientGoal = RadioField('Цель', choices=[('Для путешествий', 'Для путешествий'), ('Для учебы', 'Для учебы'),
                                             ('Для работы', 'Для работы'), ('Для переезда', 'Для переезда'),
                                             ('Для программирования', 'Для программирования')],
                            default='Для путешествий')
    clientWeektime = RadioField('Время', choices=[('1-2 часа в неделю', '1-2 часа в неделю'),
                                                  ('3-5 часов в неделю', '3-5 часов в неделю'),
                                                  ('5-7 часов в неделю', '5-7 часов в неделю'),
                                                  ('7-10 часов в неделю', '7-10 часов в неделю')],
                                default='1-2 часа в неделю')
    clientName = StringField("Вас зовут", [InputRequired()])
    clientPhone = StringField("Ваш телефон", [InputRequired()])
    submit = SubmitField('Найдите мне преподавателя')


@app.route('/')
def re_main():
    # Выбираем произвольные 6 преподавателей и отправляем их в шаблон
    random_teachers = []
    with open("json/teachers.json", "r") as f:
        teachers = json.load(f)
    with open("json/goals.json", "r") as f:
        goals = json.load(f)
    random.shuffle(teachers)
    for teacher in teachers:
        if len(random_teachers) < 6:
            random_teachers.append(teacher)
    return render_template('index.html', pics=pics, goals=goals, random_teachers=random_teachers)


@app.route('/goals/<goal>/')
def re_goals(goal):
    # Фильтруем преподавателей по принадлежности к цели заказчика и передаем в шаблон
    goal_teachers = []
    with open("json/teachers.json", "r") as f:
        teachers = json.load(f)
    with open("json/goals.json", "r") as f:
        goals = json.load(f)
    for teacher in teachers:
        if goal in teacher['goals']:
            goal_teachers.append(teacher)
    return render_template('goal.html', goal_teachers=goal_teachers, goal=goal, goals=goals, pics=pics)


@app.route('/profiles/<int:id_teacher>/')
def re_profiles(id_teacher):
    # Фильтруем конкретного преподавателя и передаем его в шаблон подробной странички по преподу
    with open("json/teachers.json", "r") as f:
        teachers = json.load(f)
    with open("json/goals.json", "r") as f:
        goals = json.load(f)
    for teacher in teachers:
        if id_teacher == teacher['id']:
            return render_template('profile.html', teacher=teacher, goals=goals, days=days)


@app.route('/request/', methods=["GET", "POST"])
def re_request():
    # Отправляем/получаем форму запроса на преподавателя через валидацию
    form = RequestForm()
    if form.validate_on_submit():
        clientGoal = form.clientGoal.data
        clientWeektime = form.clientWeektime.data
        clientName = form.clientName.data
        clientPhone = form.clientPhone.data
        # Формируем json-файл с запросами с проверкой на пустоту и корректным занесением
        if os.stat("json/request.json").st_size == 0:
            with open("json/request.json", "w") as f:
                records = [{'clientGoal': clientGoal, 'clientWeektime': clientWeektime, 'clientName': clientName,
                            'clientPhone': clientPhone}]
                json.dump(records, f)
        else:
            with open("json/request.json", "r") as f:
                records = json.load(f)
            records.append({'clientGoal': clientGoal, 'clientWeektime': clientWeektime, 'clientName': clientName,
                            'clientPhone': clientPhone})
            with open("json/request.json", "w") as f:
                json.dump(records, f)
        return render_template('request_done.html', clientGoal=clientGoal, clientWeektime=clientWeektime,
                               clientName=clientName, clientPhone=clientPhone)
    return render_template('request.html', form=form)


@app.route('/booking/<int:id_teacher>/<day>/<time>/', methods=["GET", "POST"])
def re_booking(id_teacher, day, time):
    # Отправляем/получаем форму бронирования преподавателя через валидацию
    form = BookingForm()
    if form.validate_on_submit():
        clientName = form.clientName.data
        clientPhone = form.clientPhone.data
        clientWeekday = form.clientWeekday.data
        clientTime = form.clientTime.data
        clientTeacher = int(form.clientTeacher.data)
        # Исключае из файла json с преподавателями забронированное время
        with open("json/teachers.json", "r") as f:
            teachers = json.load(f)
        for teacher in teachers:
            if clientTeacher == teacher['id']:
                for day, time in teacher['free'].items():
                    if day == clientWeekday:
                        time[clientTime] = False
        with open("json/teachers.json", "w") as f:
            json.dump(teachers, f)
        # Формируем json-файл с данными бронирования с проверкой на пустоту и корректным занесением
        if os.stat("json/booking.json").st_size == 0:
            with open("json/booking.json", "w") as f:
                records = [{'clientName': clientName, 'clientPhone': clientPhone, 'clientWeekday': clientWeekday,
                            'clientTime': clientTime, 'clientTeacher': clientTeacher}]
                json.dump(records, f)
        else:
            with open("json/booking.json", "r") as f:
                records = json.load(f)
            records.append({'clientName': clientName, 'clientPhone': clientPhone, 'clientWeekday': clientWeekday,
                            'clientTime': clientTime, 'clientTeacher': clientTeacher})
            with open("json/booking.json", "w") as f:
                json.dump(records, f)
        return render_template('booking_done.html', clientName=clientName, clientPhone=clientPhone,
                               clientWeekday=clientWeekday, clientTime=clientTime, days=days)
    # Фильтруем нужного преподавателя
    with open("json/teachers.json", "r") as f:
        teachers = json.load(f)
    for teacher in teachers:
        if id_teacher == teacher['id']:
            return render_template('booking.html', teacher=teacher, day=day, time=time, days=days, form=form)


@app.route('/all/')
def re_all():
    # Вывод всех преподователей из базы
    with open("json/teachers.json", "r") as f:
        teachers = json.load(f)
    with open("json/goals.json", "r") as f:
        goals = json.load(f)
    return render_template('all.html', pics=pics, goals=goals, teachers=teachers)


if __name__ == '__main__':
    app.run()
