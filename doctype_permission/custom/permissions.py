import frappe
from .db_query import get_doctype_permission_map


def has_controller_permissions(doc, ptype, user=None, debug=False) -> bool:
	"""Return controller permissions if denied, True if not defined.

	Controllers can only deny permission, they can not explicitly grant any permission that wasn't
	already present."""
	if not user:
		user = frappe.session.user

	hooks = frappe.get_hooks("has_permission")
	methods = hooks.get(doc.doctype, []) + hooks.get("*", [])

	for method in reversed(methods):
		controller_permission = frappe.call(method, doc=doc, ptype=ptype, user=user, debug=debug)
		debug and _debug_log(f"Controller permission check from {method}: {controller_permission}")
		if controller_permission is not None:
			return bool(controller_permission)
	
	# Monkey Patch
	# If DocType Permission is used for this doctype, double check for doc permission
	if get_doctype_permission_map().get(doc.doctype):
		doc = frappe.get_list(
			doc.doctype,
			filters={"name": doc.name},
			pluck="name"
		)
		if not doc:
			return False
	# --

	# None of the controller hooks returned anything conclusive
	return True