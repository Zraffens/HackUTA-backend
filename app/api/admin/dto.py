from flask_restx import Namespace, fields

admin_ns = Namespace('admin', description='Admin management operations')

# User management DTOs
user_stats_model = admin_ns.model('UserStats', {
    'total_users': fields.Integer(description='Total number of users'),
    'admin_users': fields.Integer(description='Number of admin users'),
    'new_users_today': fields.Integer(description='New users registered today'),
    'new_users_this_week': fields.Integer(description='New users registered this week'),
    'new_users_this_month': fields.Integer(description='New users registered this month')
})

note_stats_model = admin_ns.model('NoteStats', {
    'total_notes': fields.Integer(description='Total number of notes'),
    'public_notes': fields.Integer(description='Number of public notes'),
    'private_notes': fields.Integer(description='Number of private notes'),
    'notes_today': fields.Integer(description='Notes uploaded today'),
    'notes_this_week': fields.Integer(description='Notes uploaded this week'),
    'notes_this_month': fields.Integer(description='Notes uploaded this month'),
    'total_views': fields.Integer(description='Total note views'),
    'total_downloads': fields.Integer(description='Total note downloads')
})

system_stats_model = admin_ns.model('SystemStats', {
    'total_comments': fields.Integer(description='Total number of comments'),
    'total_bookmarks': fields.Integer(description='Total number of bookmarks'),
    'total_tags': fields.Integer(description='Total number of tags'),
    'total_courses': fields.Integer(description='Total number of courses')
})

dashboard_stats_model = admin_ns.model('DashboardStats', {
    'user_stats': fields.Nested(user_stats_model),
    'note_stats': fields.Nested(note_stats_model),
    'system_stats': fields.Nested(system_stats_model)
})

admin_user_list_model = admin_ns.model('AdminUserList', {
    'id': fields.Integer(description='User ID'),
    'public_id': fields.String(description='User public ID'),
    'username': fields.String(description='Username'),
    'email': fields.String(description='Email address'),
    'full_name': fields.String(description='Full name'),
    'is_admin': fields.Boolean(description='Is admin user'),
    'created_at': fields.DateTime(description='Registration date'),
    'notes_count': fields.Integer(description='Number of notes uploaded'),
    'last_login': fields.DateTime(description='Last login date')
})

admin_note_list_model = admin_ns.model('AdminNoteList', {
    'id': fields.Integer(description='Note ID'),
    'public_id': fields.String(description='Note public ID'),
    'title': fields.String(description='Note title'),
    'owner_username': fields.String(description='Owner username'),
    'is_public': fields.Boolean(description='Is public note'),
    'view_count': fields.Integer(description='View count'),
    'download_count': fields.Integer(description='Download count'),
    'created_at': fields.DateTime(description='Upload date'),
    'ocr_status': fields.String(description='OCR processing status')
})

user_action_model = admin_ns.model('UserAction', {
    'action': fields.String(required=True, description='Action to perform', enum=['promote', 'demote', 'suspend', 'activate', 'delete'])
})

note_action_model = admin_ns.model('NoteAction', {
    'action': fields.String(required=True, description='Action to perform', enum=['hide', 'unhide', 'delete', 'force_delete'])
})

# New models for creating entities
user_create_admin_model = admin_ns.model('AdminUserCreate', {
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email address'),
    'password': fields.String(required=True, description='Password'),
    'is_admin': fields.Boolean(description='Admin privileges', default=False),
    'profile_bio': fields.String(description='Profile bio')
})

note_create_admin_model = admin_ns.model('AdminNoteCreate', {
    'title': fields.String(required=True, description='Note title'),
    'description': fields.String(description='Note description'),
    'owner_id': fields.String(required=True, description='Owner user ID'),
    'is_public': fields.Boolean(description='Public visibility', default=True),
    'file_content': fields.String(description='Base64 encoded file content'),
    'filename': fields.String(description='Original filename')
})

comment_admin_model = admin_ns.model('AdminComment', {
    'id': fields.Integer(description='Comment ID'),
    'content': fields.String(description='Comment content'),
    'author_username': fields.String(description='Author username'),
    'note_title': fields.String(description='Note title'),
    'created_at': fields.DateTime(description='Creation date'),
    'note_id': fields.String(description='Note public ID')
})

comment_action_model = admin_ns.model('CommentAction', {
    'action': fields.String(required=True, description='Action to perform', enum=['delete'])
})

tag_admin_model = admin_ns.model('AdminTag', {
    'id': fields.Integer(description='Tag ID'),
    'name': fields.String(description='Tag name'),
    'created_at': fields.DateTime(description='Creation date'),
    'notes_count': fields.Integer(description='Number of notes with this tag')
})

tag_action_model = admin_ns.model('TagAction', {
    'action': fields.String(required=True, description='Action to perform', enum=['delete'])
})

tag_create_model = admin_ns.model('TagCreate', {
    'name': fields.String(required=True, description='Tag name')
})

course_admin_model = admin_ns.model('AdminCourse', {
    'id': fields.Integer(description='Course ID'),
    'name': fields.String(description='Course name'),
    'code': fields.String(description='Course code'),
    'created_at': fields.DateTime(description='Creation date'),
    'notes_count': fields.Integer(description='Number of notes in this course'),
    'students_count': fields.Integer(description='Number of enrolled students')
})

course_action_model = admin_ns.model('CourseAction', {
    'action': fields.String(required=True, description='Action to perform', enum=['delete'])
})

course_create_model = admin_ns.model('CourseCreate', {
    'name': fields.String(required=True, description='Course name'),
    'code': fields.String(required=True, description='Course code'),
    'description': fields.String(description='Course description')
})

# Define pagination model first before using it
pagination_model = admin_ns.model('Pagination', {
    'page': fields.Integer(description='Current page'),
    'per_page': fields.Integer(description='Items per page'),
    'total': fields.Integer(description='Total items'),
    'pages': fields.Integer(description='Total pages'),
    'has_prev': fields.Boolean(description='Has previous page'),
    'has_next': fields.Boolean(description='Has next page')
})

paginated_comments_model = admin_ns.model('PaginatedComments', {
    'comments': fields.List(fields.Nested(comment_admin_model)),
    'pagination': fields.Nested(pagination_model)
})

paginated_tags_model = admin_ns.model('PaginatedTags', {
    'tags': fields.List(fields.Nested(tag_admin_model)),
    'pagination': fields.Nested(pagination_model)
})

paginated_courses_model = admin_ns.model('PaginatedCourses', {
    'courses': fields.List(fields.Nested(course_admin_model)),
    'pagination': fields.Nested(pagination_model)
})

paginated_users_model = admin_ns.model('PaginatedUsers', {
    'users': fields.List(fields.Nested(admin_user_list_model)),
    'pagination': fields.Nested(pagination_model)
})

paginated_notes_model = admin_ns.model('PaginatedNotes', {
    'notes': fields.List(fields.Nested(admin_note_list_model)),
    'pagination': fields.Nested(pagination_model)
})