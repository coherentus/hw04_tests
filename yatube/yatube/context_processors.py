import datetime as dt


def current_year(request):
    return {
        'year': dt.date.today().year,
    }
