import frappe


def get_doctype_permission(user, doctype):
	user_roles = frappe.get_roles(user)
	if doctype_permission_names := get_doctype_permission_map().get(doctype):
		doc_perm_conditions = ["false"]
		for name in doctype_permission_names:
			dt_perm = frappe.get_doc("DocType Permission", name)
			for c in dt_perm.conditions:
				if c.role not in user_roles:  # Matched user role for this condition
					continue
				if condition := dt_perm.get_doctype_permission_conditions(user, c.script):
					doc_perm_conditions.append(condition)
		return f"({' or '.join(doc_perm_conditions)})"
	return None


def get_doctype_permission_map():
	if frappe.flags.in_patch and not frappe.db.table_exists("DocType Permission"):
		return {}

	permission_map = frappe.cache.get_value("doctype_permission_map")
	if permission_map is None:
		permission_map = {}
		doc_perms = frappe.get_all(
			"DocType Permission",
			fields=("name", "ref_doctype"),
			or_filters=[
				["testing", "=", 1],
				["docstatus", "=", 1],
			],
		)
		for perm in doc_perms:
			if not permission_map.get(perm.ref_doctype):
				permission_map[perm.ref_doctype] = []
			permission_map[perm.ref_doctype] += [perm.name]
		frappe.cache.set_value("doctype_permission_map", permission_map)
	return permission_map


def has_permission(doc):
	if get_doctype_permission_map().get(doc.doctype):
		if doc.is_new():
			return True
		doc = frappe.get_list(doc.doctype, filters={"name": doc.name}, pluck="name")
		if not doc:
			return False
