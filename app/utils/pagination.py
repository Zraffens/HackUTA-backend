from flask import request
from flask_restx import fields


def paginate_query(query, page=None, per_page=None, max_per_page=100):
    """
    Paginate a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed). If None, will get from request args
        per_page: Items per page. If None, will get from request args
        max_per_page: Maximum allowed items per page (default 100)
    
    Returns:
        dict with: items, total, pages, current_page, has_next, has_prev
    """
    if page is None:
        page = request.args.get('page', 1, type=int)
    if per_page is None:
        per_page = request.args.get('per_page', 10, type=int)
    
    # Validate and constrain parameters
    page = max(1, page)
    per_page = max(1, min(per_page, max_per_page))
    
    # Get paginated results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'items': pagination.items,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }


def create_pagination_model(api, item_model):
    """
    Create a Flask-RESTX model for paginated responses.
    
    Args:
        api: Flask-RESTX API/Namespace instance
        item_model: The model for individual items
    
    Returns:
        Flask-RESTX model for paginated response
    """
    return api.model(f'{item_model.name}Paginated', {
        'items': fields.List(fields.Nested(item_model)),
        'total': fields.Integer(description='Total number of items'),
        'pages': fields.Integer(description='Total number of pages'),
        'current_page': fields.Integer(description='Current page number'),
        'has_next': fields.Boolean(description='Whether there is a next page'),
        'has_prev': fields.Boolean(description='Whether there is a previous page')
    })
