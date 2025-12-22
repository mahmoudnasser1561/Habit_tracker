import datetime
import os
from collections import defaultdict
from flask import Blueprint, render_template, request, redirect, url_for
from pymongo import MongoClient

pages = Blueprint(
    "habits", __name__, template_folder="templates", static_folder="static"
)

mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/habit_tracker')
client = MongoClient(mongo_uri)
db = client['habit_tracker'] 
habits_coll = db['habits']   
completions_coll = db['completions'] 

@pages.route('/health')
def health():
    return 'OK', 200

@pages.context_processor
def add_calc_date_range():
    def date_range(start: datetime.date):
        dates = [start + datetime.timedelta(days=diff) for diff in range(-3, 4)]
        return dates
    return {"date_range": date_range}

@pages.route("/")
def index():
    date_str = request.args.get("date")
    if date_str:
        selected_date = datetime.date.fromisoformat(date_str)
    else:
        selected_date = datetime.date.today()

    habits = [habit['name'] for habit in habits_coll.find({}, {'_id': 0, 'name': 1})]

    completions = [comp['habit'] for comp in completions_coll.find({"date": selected_date.isoformat()})]

    return render_template(
        "index.html",
        habits=habits,
        selected_date=selected_date,
        completions=completions,
        title="Habit Tracker - Home",
    )

@pages.route("/complete", methods=["POST"])
def complete():
    date_string = request.form.get("date")
    date = datetime.date.fromisoformat(date_string)
    habit = request.form.get("habitName")

    completions_coll.insert_one({"date": date.isoformat(), "habit": habit})

    return redirect(url_for(".index", date=date_string))

@pages.route("/add", methods=["GET", "POST"])
def add_habit():
    if request.method == 'POST':
        habit_name = request.form.get("habit")
        if habit_name:
            habits_coll.insert_one({"name": habit_name})
        return redirect(url_for(".index")) 

    return render_template(
        "add_habit.html",
        title="Habit Tracker - Add Habit",
        selected_date=datetime.date.today(),
    )