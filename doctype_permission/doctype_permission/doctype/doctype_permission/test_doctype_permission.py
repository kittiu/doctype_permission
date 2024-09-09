# Copyright (c) 2024, Kitti U. and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestDocTypePermission(FrappeTestCase):

	def setUp(self):
		frappe.set_user("Administrator")
		self.create_doctype_permission()

	def tearDown(self):
		frappe.db.rollback()

	def test_employee_see_own_docs(self):
		# As Admin, create new user/employee
		frappe.set_user("Administrator")
		(user, employee) = make_employee("employee@company.com", "EMP01")
		user.add_roles(["Employee"])
		# Change to Employee
		frappe.set_user("employee@company.com")
		count = len(frappe.get_list("Employee", pluck="name"))
		# Test See Own Doc
		self.assertEqual(count, 1)

	def test_manager_see_all_docs(self):
		# As Admin, create new user/employee
		frappe.set_user("Administrator")
		(user, employee) = make_employee("manager@company.com", "EMP02")
		user.add_roles(["System Manager"])
		# Change to System Manager
		frappe.set_user("manager@company.com")
		count = len(frappe.get_list("Employee", pluck="name"))
		# Test See All Docs
		self.assertGreater(count, 1)

	def create_doctype_permission(self):
		"""
		- Employee - See Employee's Docs
		- System Manager - See All Docs
		"""
		perm_levels = dict(frappe.get_all(
			"DocType Permission Level",
			fields=["name", "script"],
			as_list=1
		))
		doc_perm = frappe.get_doc(
			{
				"doctype": "DocType Permission",
				"title": "Employee Permission",
				"ref_doctype": "Employee",
				"conditions": [
					{
						"role": "Employee",
						"permlevel": "Employee's Docs",
						"script": perm_levels["Employee's Docs"],
					},
					{
						"role": "System Manager",
						"permlevel": "Full Access",
						"script": perm_levels["Full Access"],
					},
				]
			}
		).insert(ignore_if_duplicate=True, ignore_mandatory=True)
		doc_perm.reload()
		doc_perm.submit()
		return doc_perm


def make_employee(user, emp):
	new_user = frappe.get_doc(
		{
			"doctype": "User",
			"email": user,
			"first_name": user,
			"new_password": "password",
			"send_welcome_email": 0,
			"roles": [{"doctype": "Has Role", "role": "Employee"}],
		}
	).insert(ignore_if_duplicate=True, ignore_mandatory=True)
	new_employee = frappe.get_doc(
		{
			"doctype": "Employee",
			"name": emp,
			"first_name": user,
			"user_id": user,
			"status": "Active",
			"create_user_permission": 0,  # Do not create user permission
		}
	).insert(ignore_if_duplicate=True, ignore_mandatory=True)
	new_user.reload()
	new_employee.reload()
	return (new_user, new_employee)
