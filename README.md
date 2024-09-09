## DocType Permission

This app is the answer to the topic **[Design of User Permissions is Dangerous](https://discuss.frappe.io/t/the-design-of-user-permissions-is-dangerous/109103)**, where data is grant first and then add more restriction later.

The DocType Permission is the opposite, it allow system admin to restrict first, and then grant more permission later.

Behind the scene, it is using **permission_query_conditions** and **has_permission** in hooks.py and so, it works as additional security measurement with existing User Permission and Permission query.

#### Key DocTypes:

1. **DocType Permission**, a submittable document that restrict and then grant different permission to different role
2. **DocType Permission Level**, master data for pre-built permission query script

#### Benefit:

* Intuitive and easy to us. Restrict first permit later.
* Can work along side with standard user permissions, permission queries.

#### Problem with Current System:

Given example of a sensitive document such as Salary Slip.

* Employees to see only his/her own Salary Slip
* Payroll Users to see all Salary Slips

Without this app, following setup is required.

* For Employees, create each User Permission for each employee. If there are 1,000 employees then 1,000 User Permissions is required.
* For Payroll Users, make sure there is no User Permissions created for them.

As you can see it is now difficult to keep track of the amount of User Permissions. And if for some reason either system or human, a User Permission is missing for someone, this can be a very serious data breach!

#### Solution with DocType Permission:

Given the same example, no 1,000 User Pemissions is needed, just create 1 DocType Permission as following,

![doctype_permission](https://github.com/user-attachments/assets/4e3a483f-49e9-4793-8690-3f6b5dbc6aa2)

As soon as this document is created for Salary Slip, all documents will be restrictred. And then by adding each Role’s Additional Permission, the permission will be granted (using OR condition).

#### Notes:

* The combined SQL condition would be, (false **OR** Role-1 **OR** Role-2)
* This consition will then be **AND** with other SQL condition from User Permissiona and/or Permission Query (if used)
* DocType Prmission Level are canned permission query which can be exteded by ourself

![doctype_permission_level](https://github.com/user-attachments/assets/73520437-6cad-4396-86bd-dee6f19b9769)


#### License

MIT
