__version__ = "0.0.1"

# Monkey Patches
from frappe.model.db_query import DatabaseQuery
from doctype_permission.custom.db_query import get_permission_query_conditions
DatabaseQuery.get_permission_query_conditions = get_permission_query_conditions

from frappe import permissions
from doctype_permission.custom.permissions import has_controller_permissions
permissions.has_controller_permissions = has_controller_permissions