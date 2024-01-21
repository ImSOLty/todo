from datetime import datetime, timedelta
import random


def random_str(length=5):
    return ''.join([chr(random.randint(33, 126)) for _ in range(length)])


def random_color():
    return '#%06X' % random.randint(0, 256 ** 3 - 1)


def random_data_task(**kw):
    title, description, completed, target, due = \
        kw.get('title'), kw.get('description'), kw.get('completed'), kw.get('target'), kw.get('due')
    return {
        'title': random_str() if title is None else title,
        'description': random_str() if description is None else description,
        'completed': bool(random.randint(0, 1)) if completed is None else completed,
        'due': (datetime.today() + timedelta(days=random.randint(0, 20))).date() if due is None else due,
        'target': kw['target']
    }


def random_data_taskgroup(**kw):
    title, description, type_tag = kw.get('title'), kw.get('description'), kw.get('type_tag')
    return {
        'title': random_str() if title is None else title,
        'description': random_str() if description is None else description,
        'type_tag': random_str() if type_tag is None else type_tag
    }
