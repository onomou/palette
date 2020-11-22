from canvasapi import Canvas
from canvasapi.assignment import Assignment
from canvasapi.course import Course
from functools import lru_cache

# import configparser
# config = configparser.ConfigParser()
# config.optionxform = str
# config.read('config.ini')

'''
Canvas monkey patches
'''

@lru_cache(maxsize=1000)
def courses_list(self):
    print('get_courses')
    return [course for course in self.get_courses()]

Canvas.courses = property(courses_list)

@lru_cache(maxsize=1000)
def courses_dict(self):
    print('courses_dict')
    return {course.id: course for course in self.courses}

Canvas.course = property(courses_dict)

'''
Course monkey patches
'''
@lru_cache(maxsize=1000)
def users_list(self,**kwargs):
    print('users_list', self.id)
    return [user for user in self.get_users()]

Course.users = property(users_list)

@lru_cache(maxsize=1000)
def users_dict(self,**kwargs):
    return {user.id: user for user in self.users}

Course.user = property(users_dict)

@lru_cache(maxsize=1000)
def assignments_list(self,**kwargs):
    print('assignments_list', self.id)
    return [assignment for assignment in self.get_assignments()]

Course.assignments = property(assignments_list)

@lru_cache(maxsize=1000)
def assignments_dict(self,**kwargs):
    return {assignment.id: assignment for assignment in self.assignments}

Course.assignment = property(assignments_dict)

@lru_cache(maxsize=1000)
def enrollments_list(self):
    print('enrollments_list', self.id)
    return [enrollment for enrollment in self.get_enrollments()]

# Course.enrollments = property(enrollments_list)

'''
Assignment monkey patches
'''
@lru_cache(maxsize=1000)
def submissions_list(self,**kwargs):
    print('submissions_list', self.id)
    return [submission for submission in self.get_submissions(include=['submission_comments','submission_history'])]

Assignment.submissions = property(submissions_list)

@lru_cache(maxsize=1000)
def submissions_dict(self,**kwargs):
    return {submission.id: submission for submission in self.get_submissions}
    
Assignment.submission = property(submissions_dict)

'''
Cached functions
'''
@lru_cache(maxsize=1000)
def get_canvas(api_url, api_key):
    # global canvas, config
    try:
        #canvas = Canvas(config['Environment']['API_URL'],
        #                config['Environment']['API_KEY'])
        canvas = Canvas(api_url, api_key)
        # canvas.api_url = api_url
        # canvas.api_key = api_key
        # canvas.courses = [course for course in canvas.get_courses()]
        return canvas
    except:
        return None

@lru_cache(maxsize=1000)
def get_course(api_url, api_key, course_id):
    canvas = get_canvas(api_url, api_key)
    try:
        course = canvas.get_course(course_id)
        course.assignment_groups = course.get_assignment_groups()
        return course
    except:
        return None

@lru_cache(maxsize=1000)
def get_assignment(api_url, api_key, course_id, assignment_id):
    course = get_course(api_url, api_key, course_id)
    try:
        assignment = course.get_assignment(assignment_id)
        return assignment
    except:
        return None