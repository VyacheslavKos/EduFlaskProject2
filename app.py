from flask import Flask
from flask import render_template

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import HiddenField
from wtforms import SubmitField
from wtforms import RadioField

import json

import os

import random


app = Flask(__name__)
app.secret_key = "randomstring777"

days = {'mon': 'Понедельник', 'tue': 'Вторник', 'wed': 'Среда', 'thu': 'Четверг', 'fri': 'Пятница', 'sat': 'Суббота',
        'sun': 'Воскресенье'}
pics = {'travel': '⛱', 'study': '🏫', 'work': '🏢', 'relocate': '🚜', 'programming': '✌'}


class BookingForm(FlaskForm):
    clientName = StringField("Вас зовут")
    clientPhone = StringField("Ваш телефон")
    clientWeekday = HiddenField()
    clientTime = HiddenField()
    clientTeacher = HiddenField()
    submit = SubmitField('Записаться на пробный урок')


class RequestForm(FlaskForm):
    clientGoal = RadioField('Цель', choices=[('Для путешествий', 'Для путешествий'), ('Для учебы', 'Для учебы'),
                                             ('Для работы', 'Для работы'), ('Для переезда', 'Для переезда'),
                                             ('Для программирования', 'Для программирования')],
                            default='Для путешествий')
    clientWeektime = RadioField('Время', choices=[('1-2 часа в неделю', '1-2 часа в неделю'), ('3-5 часов в неделю', '3-5 часов в неделю'),
                                                  ('5-7 часов в неделю', '5-7 часов в неделю'), ('7-10 часов в неделю', '7-10 часов в неделю')],
                                default='1-2 часа в неделю')
    clientName = StringField("Вас зовут")
    clientPhone = StringField("Ваш телефон")
    submit = SubmitField('Найдите мне преподавателя')


@app.route('/')
def re_main():
    random_teachers = []
    with open("teachers.json", "r") as f:
        teachers = json.load(f)
    with open("goals.json", "r") as f:
        goals = json.load(f)
    random.shuffle(teachers)
    for teacher in teachers:
        if len(random_teachers) < 6:
            random_teachers.append(teacher)
    return render_template('index.html', pics=pics, goals=goals, random_teachers=random_teachers)


@app.route('/goals/<goal>/')
def re_goals(goal):
    goal_teachers = []
    with open("teachers.json", "r") as f:
        teachers = json.load(f)
    with open("goals.json", "r") as f:
        goals = json.load(f)
    for teacher in teachers:
        if goal in teacher['goals']:
            goal_teachers.append(teacher)
    return render_template('goal.html', goal_teachers=goal_teachers, goal=goal, goals=goals, pics=pics)


@app.route('/profiles/<int:id_teacher>/')
def re_profiles(id_teacher):
    with open("teachers.json", "r") as f:
        teachers = json.load(f)
    with open("goals.json", "r") as f:
        goals = json.load(f)
    for teacher in teachers:
        if id_teacher == teacher['id']:
            return render_template('profile.html', teacher=teacher, goals=goals, days=days)


@app.route('/request/')
def re_request():
    form = RequestForm()
    return render_template('request.html', form=form)


@app.route('/request_done/', methods=["POST"])
def re_request_done():
    form = RequestForm()
    clientGoal = form.clientGoal.data
    clientWeektime = form.clientWeektime.data
    clientName = form.clientName.data
    clientPhone = form.clientPhone.data
    if os.stat("request.json").st_size == 0:
        with open("request.json", "w") as f:
            records = [{'clientGoal': clientGoal, 'clientWeektime': clientWeektime, 'clientName': clientName,
                        'clientPhone': clientPhone}]
            json.dump(records, f)
    else:
        with open("request.json", "r") as f:
            records = json.load(f)
        records.append({'clientGoal': clientGoal, 'clientWeektime': clientWeektime, 'clientName': clientName,
                        'clientPhone': clientPhone})
        with open("request.json", "w") as f:
            json.dump(records, f)
    return render_template('request_done.html', clientGoal=clientGoal, clientWeektime=clientWeektime,
                           clientName=clientName, clientPhone=clientPhone)


@app.route('/booking/<int:id_teacher>/<day>/<time>/')
def re_booking(id_teacher, day, time):
    form = BookingForm()
    with open("teachers.json", "r") as f:
        teachers = json.load(f)
    for teacher in teachers:
        if id_teacher == teacher['id']:
            return render_template('booking.html', teacher=teacher, day=day, time=time, days=days, form=form)


@app.route('/booking_done/', methods=["POST"])
def re_booking_done():
    form = BookingForm()
    clientName = form.clientName.data
    clientPhone = form.clientPhone.data
    clientWeekday = form.clientWeekday.data
    clientTime = form.clientTime.data
    clientTeacher = int(form.clientTeacher.data)

    with open("teachers.json", "r") as f:
        teachers = json.load(f)
    for teacher in teachers:
        if clientTeacher == teacher['id']:
            for day, time in teacher['free'].items():
                if day == clientWeekday:
                    time[clientTime] = False
    with open("teachers.json", "w") as f:
        json.dump(teachers, f)

    if os.stat("booking.json").st_size == 0:
        with open("booking.json", "w") as f:
            records = [{'clientName': clientName, 'clientPhone': clientPhone, 'clientWeekday': clientWeekday,
                        'clientTime': clientTime, 'clientTeacher': clientTeacher}]
            json.dump(records, f)
    else:
        with open("booking.json", "r") as f:
            records = json.load(f)
        records.append({'clientName': clientName, 'clientPhone': clientPhone, 'clientWeekday': clientWeekday,
                        'clientTime': clientTime, 'clientTeacher': clientTeacher})
        with open("booking.json", "w") as f:
            json.dump(records, f)

    return render_template('booking_done.html', clientName=clientName, clientPhone=clientPhone,
                           clientWeekday=clientWeekday, clientTime=clientTime, days=days)


@app.route('/all/')
def re_all():
    with open("teachers.json", "r") as f:
        teachers = json.load(f)
    with open("goals.json", "r") as f:
        goals = json.load(f)
    return render_template('all.html', pics=pics, goals=goals, teachers=teachers)


if __name__ == '__main__':
    app.run()
