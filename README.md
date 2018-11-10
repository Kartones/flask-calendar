[![CircleCI](https://circleci.com/gh/Kartones/flask-calendar/tree/master.svg?style=svg)](https://circleci.com/gh/Kartones/flask-calendar/tree/master)

# flask-calendar

## Introduction

I recently (dec 2017) decided I wanted to opt out from Google services as much as possible. One of the services that tied me most was Calendar. There are not many alternatives, and even fewer web-based. I decided to try using a Trello board with due dates and some labels for a while, but proved to be harder to maintain. Add the lack of a month calendar view, and no support for recurrent/repetitive tasks, and I decided to do good use of a holidays to spend some hours and build a simple GCalendar clone.


### Details

Main calendar view:

![Main calendar view](doc/sample_01.png)

Create new task view:

![Create new task view](doc/sample_02.png)

Supports a basic drag & drop on desktop of days (like Google Calendar), edition of existing tasks, creation of repetitive tasks (daily, montly, by weekday, by month day or on specific day number), custom colors, and a few options like hiding past tasks or being able to manually hide those repetitive task ocurrences (I like a "clean view" and usually remove/hide past tasks).

It is mobile friendly (buttons for actions are ugly and cannot drag & drop days on mobile, but otherwise works), might not be perfectly designed for all resolutions but at least works.


## Remarks

Compatible with Firefox, Brave and Chrome. No plans for other browser support (but PRs are welcome).

No Javascript libraries and no CSS frameworks used, so this means the corresponding code and styles are accordingly non-impressive.

No databases, as I don't need to do any querying or complex stuff I couldn't also do with JSON files and basic dictionaries.

Authentication works using werkzeug SimpleCache for storage, which means if the application runs with more than one thread you'll get into problems. Run it with a single process uwsgi or similar.

HTML inputs are favoring HTML5 ones instead of fancy jquery-like plugins to reduce support and increase mobile compatibility.

Overall, lessons learned:

- Next project will be Django. What I win in speed building the routing and views, I lose then building forms and validations.
- I suck at CSS so I'll stick to Bootstrap/Foundation. This time what I did works but I've spent more time fighting with CSS than building code.
- I'll give a try next time to turbolinks, to trully try to avoid javascript for tiny projects.
- Introduce tests (including application ones) from the beginning, at least for critical paths always pays off. At least next project can benefit from the docker setup (with pytest, mypy, flake8 and coverage).

### Changelog

List of new features added to the original project commits

- 2018-11-10: Basic rate limiter for failed login attempts. Needs new config.FAILED_LOGIN_DELAY_BASE value, makes user wait exponentially more on each failed attempt, just to hinder brute forcing.
- 2018-11-10: Fallback to Python 3.5 as it's more commonly found at Linux distros, etc.
- 2018-10-03: Fix favicon.ico request creating error log traces & tiny code cleanup.
- 2018-07-29: CSS adjustments, show task name at delete/hide modal. User creation & deletion (by [@linuxnico](https://github.com/linuxnico)).
- 2018-06-29: Less round buttons, bigger task details textbox, trim task title (strip spaces pre and post text) upon create/update. WIP of ICal export feature (controlled via config.FEATURE_FLAG_ICAL_EXPORT boolean value).
- 2018-03-08: Changed yellow color preset by orange, made brown darker. Double click "window" increased to 300ms. Small CSS adjustments.
- 2018-02-25: Double-click on a day triggers new task creation at that day number (instead of day 1/current day as new task button does).
- 2018-02-24: Added locale support. Tasks font 5% bigger.
- 2018-02-04: Dockerized project for local running of both web and tests. Status bar to see when there's a pending AJAX request.
- 2018-02-03: Better redirect upon login (and root/index action no longer 404s). Authorization working.
- 2018-02-03: Basic user authentication and authorization. There is no user creation so password needs to be manually created and stored into the users data json (salted SHA256 hexdigest). At least authorization is easily managed just adding authorized user ids to corresponding calendar json section.
- 2018-01-27: Reconvert `<br>` to `\n` upon edition. Cleanup of past hidden repetition task instances (when saving a calendar and month changes). Improved tests (more to come).
- 2018-01-09: Bring back action buttons for small (phone) screens. Improved (less terrible) favicon and colors.
- 2017-12-22: "Hide" button to remove individual instances of repetitive/recurrent tasks
- 2017-12-21: Cleanup of internal data files when a day/month becomes empty of tasks
- 2017-12-20: Basic drag & drop (to change day inside same month of a non-recurring task). Intended only for desktop, probably rough on the edges but working.
- 2017-12-30: Event edition. Mobile drag & drop disabled. Mobile CSS improvements.


## Requirements

### Production

- Python 3.5+ (type hints are compatible with 3.5 upwards)

Other requirements are on the `requirements.txt` file. Install them with `pip` or similar.

### Development

- Docker and Docker Compose

## Running

- copy `config.py.sample` to `config.py` and fill in.

```bash
make run
```

Sample username is `a_username` with password `a_password`.

### Locale

`dev` Dockerfile installs a sample locale (`es_ES`), but does not activate it. Refer to that file and to the `config.py` file for setting up any locale or commenting the lines that install them to speed up container bootup if you're sure don't want them.

Remember you can check which locales you have installed with `locale -a` and add new ones with the following commands:
```bash
cd /usr/share/locales
sudo ./install-language-pack es_ES
sudo dpkg-reconfigure locales
```


## Testing
- Install requirements from `requirements-dev.txt` file.

```bash
make test
```

- To extract code coverage:
```bash
make coverage
```

## Miscellaneous

### User creation/deletion

As there is no admin interface, to create or delete users you should create a python file with code similar to the following example:

```python
from authentication import Authentication
import config


authentication = Authentication(data_folder=config.USERS_DATA_FOLDER, password_salt=config.PASSWORD_SALT)

# Create a user
authentication.add_user(
    username="a username",
    plaintext_password="a plain password",
    default_calendar="a default calendar id"
)

# Delete a user
authentication.delete_user(username="a username")
```


## TODOs / Roadmap

This are initially the only features I plan to build:

- TESTS! Need to increase coverage
- ICAL export (ongoing at /exporters/)
- fortify cookie
- desktop notifications (only for specific hour tasks)
- decent time selector for desktop only
- min and max dates for input type date: min="xxxx-xx-xx" max="xxxx-xx-xx"
- a decent weekday and month day choosers when recurrency is selected
- Yearly repetition? (would need month and day)
- search: simple, just python lowercased search at task titles. think how to represent results, if to go to the month or what
- Multi-day tasks?
- task copy/clone functionality?
- multi-calendars: json structure already supports a user having N calendars and a calendar having N users. Should also be trivial to add to the cookie a list of calendar names + ids to do a quick switcher combobox topright
