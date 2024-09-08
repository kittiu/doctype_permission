# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class DocTypePermissionCondition(Document):
	pass

	def validate(self):
		if self.perm_level == "Employee Docs Only":
			self.script = """
employee = frappe.db.get_value("Employee", {"user_id": user})
conditions = "employee = %s" % frappe.db.escape(employee)
		"""
		if self.perm_level == "Owner Docs Only":
			self.script = 'conditions = "owner = %s" % frappe.db.escape(user)'
		if self.perm_level == "Full Access":
			self.script = 'conditions = "true"'
