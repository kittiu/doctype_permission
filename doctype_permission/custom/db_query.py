import frappe
from frappe.core.doctype.server_script.server_script_utils import get_server_script_map


def get_permission_query_conditions(self) -> str:
    conditions = []
    hooks = frappe.get_hooks("permission_query_conditions", {})
    condition_methods = hooks.get(self.doctype, []) + hooks.get("*", [])
    for method in condition_methods:
        if c := frappe.call(frappe.get_attr(method), self.user, doctype=self.doctype):
            conditions.append(c)

    if permission_script_name := get_server_script_map().get("permission_query", {}).get(self.doctype):
        script = frappe.get_doc("Server Script", permission_script_name)
        if condition := script.get_permission_query_conditions(self.user):
            conditions.append(condition)
    
    # Monkey Patch - DocType Permission
    # ... and cond1 and cond2 and (false or perm_cond_1 or perm_cond_2)
    user_roles = frappe.get_roles(self.user)
    if doctype_permission_names := get_doctype_permission_map().get(self.doctype):
        doc_perm_conditions = ['false']
        for name in doctype_permission_names:
            dt_perm = frappe.get_doc("DocType Permission", name)
            for c in dt_perm.conditions:
                if c.role not in user_roles:  # Matched user role for this condition
                    continue
                if condition := dt_perm.get_doctype_permission_conditions(self.user, c.script):
                    doc_perm_conditions.append(condition)
        conditions.append(f"({' or '.join(doc_perm_conditions)})")
    # --
    return " and ".join(conditions) if conditions else ""


def get_doctype_permission_map():
	# fetch doctype_permission_map
	# {
	# 	'DocType': ['[doctype_permission]', '[doctype_permission 2]']
	# }
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