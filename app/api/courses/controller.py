from flask import request
from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from .dto import CourseDto
from ...models.course import Course
from ...models.user import User
from ... import db

api = CourseDto.api
_course = CourseDto.course
_course_create = CourseDto.course_create
_course_enroll = CourseDto.course_enroll

@api.route('')
class CourseList(Resource):
    @api.marshal_list_with(_course)
    def get(self):
        """List all courses"""
        return Course.query.all()
    
    @api.expect(_course_create, validate=True)
    def post(self):
        """Create a new course"""
        data = request.get_json()
        
        # Check if course code already exists
        existing_course = Course.query.filter_by(code=data['code']).first()
        if existing_course:
            return {'message': 'Course code already exists'}, 409
        
        new_course = Course(
            name=data['name'],
            code=data['code']
        )
        db.session.add(new_course)
        db.session.commit()
        
        return new_course, 201


@api.route('/<int:course_id>')
@api.param('course_id', 'Course ID')
class CourseDetail(Resource):
    @api.marshal_with(_course)
    def get(self, course_id):
        """Get course details"""
        course = Course.query.get_or_404(course_id)
        return course


@api.route('/enroll')
class CourseEnrollment(Resource):
    @jwt_required()
    @api.expect(_course_enroll, validate=True)
    def post(self):
        """Enroll current user in courses"""
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        
        data = request.get_json()
        course_codes = data['course_codes']
        
        enrolled_courses = []
        for code in course_codes:
            course = Course.query.filter_by(code=code).first()
            if not course:
                # Create course if it doesn't exist
                course = Course(name=f"Course {code}", code=code)
                db.session.add(course)
            
            if course not in user.courses:
                user.courses.append(course)
                enrolled_courses.append(code)
        
        db.session.commit()
        
        return {
            'message': f'Enrolled in {len(enrolled_courses)} course(s)',
            'courses': enrolled_courses
        }, 200


@api.route('/my-courses')
class MyCourses(Resource):
    @jwt_required()
    @api.marshal_list_with(_course)
    def get(self):
        """Get courses for current user"""
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        
        return user.courses
