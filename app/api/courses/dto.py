from flask_restx import Namespace, fields

class CourseDto:
    api = Namespace('courses', description='Course related operations')
    
    course = api.model('Course', {
        'id': fields.Integer(description='Course ID'),
        'name': fields.String(description='Course name'),
        'code': fields.String(description='Course code'),
    })
    
    course_create = api.model('CourseCreate', {
        'name': fields.String(required=True, description='Course name'),
        'code': fields.String(required=True, description='Course code'),
    })
    
    course_enroll = api.model('CourseEnroll', {
        'course_codes': fields.List(fields.String, required=True, description='List of course codes to enroll in')
    })
