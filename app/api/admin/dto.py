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
    'action': fields.String(required=True, description='Action to perform', enum=['promote', 'demote', 'suspend', 'activate'])
})

note_action_model = admin_ns.model('NoteAction', {
    'action': fields.String(required=True, description='Action to perform', enum=['hide', 'unhide', 'delete'])
})

pagination_model = admin_ns.model('Pagination', {
    'page': fields.Integer(description='Current page'),
    'per_page': fields.Integer(description='Items per page'),
    'total': fields.Integer(description='Total items'),
    'pages': fields.Integer(description='Total pages'),
    'has_prev': fields.Boolean(description='Has previous page'),
    'has_next': fields.Boolean(description='Has next page')
})

paginated_users_model = admin_ns.model('PaginatedUsers', {
    'users': fields.List(fields.Nested(admin_user_list_model)),
    'pagination': fields.Nested(pagination_model)
})

paginated_notes_model = admin_ns.model('PaginatedNotes', {
    'notes': fields.List(fields.Nested(admin_note_list_model)),
    'pagination': fields.Nested(pagination_model)
})