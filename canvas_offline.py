from canvasapi import Canvas
from functools import lru_cache

# import configparser
# config = configparser.ConfigParser()
# config.optionxform = str
# config.read('config.ini')

'''
Cached functions
'''

@lru_cache
def get_canvas(api_url, api_key):
    # global canvas, config
    try:
        #canvas = Canvas(config['Environment']['API_URL'],
        #                config['Environment']['API_KEY'])
        canvas = Canvas(api_url, api_key)
        canvas.api_url = api_url
        canvas.api_key = api_key
        canvas.courses = [x for x in canvas.get_courses()]
        canvas.courses_dict = {x.id: x for x in canvas.courses}
        return canvas
    except:
        return None

@lru_cache
def get_course(api_url, api_key, course_id):
    canvas = get_canvas(api_url, api_key)
    try:
        course = canvas.get_course(course_id)
        course.assignments = course.get_assignments()
        course.assignment_groups = course.get_assignment_groups()
        return course
    except:
        return None
