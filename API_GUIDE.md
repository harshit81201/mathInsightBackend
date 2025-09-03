# MathInsight Django API Guide for LLMs

This guide provides context and usage examples for the MathInsight Django backend API, enabling LLMs to generate compatible frontend code and requests.

## Authentication
- Use JWT tokens for all requests after login.
- Login endpoint returns token and user info.
- Include `Authorization: Bearer <token>` in headers for protected endpoints.

## User Roles
- `teacher`: Can manage students, view dashboard, add assignments.
- `parent`: Can view their children, assignments, and dashboard.

## Endpoints Overview
- `/api/auth/login/` — Login for both teachers and parents.
- `/api/teachers/{id}/students/` — Get students for a teacher.
- `/api/students/` — Add, edit, delete, and get students.
- `/api/parent/me/` — Get parent profile and children.
- `/api/assignments/` — Get assignments for a student.

## Example API Calls

### Login
```js
fetch('/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
})
```

### Get Current User
```js
fetch('/api/auth/me/', {
  headers: { 'Authorization': 'Bearer ' + token }
})
```

### Add Student
```js
fetch('/api/students/', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
  body: JSON.stringify({ name, parent_name, parent_email, class_name })
})
```

### Edit Student
```js
fetch(`/api/students/${studentId}/`, {
  method: 'PATCH',
  headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' },
  body: JSON.stringify({ name, class_name })
})
```

### Delete Student
```js
fetch(`/api/students/${studentId}/`, {
  method: 'DELETE',
  headers: { 'Authorization': 'Bearer ' + token }
})
```

### Get Parent's Children
```js
fetch('/api/parent/children/', {
  headers: { 'Authorization': 'Bearer ' + token }
})
```

## Error Handling
- All errors return `{ "error": "message" }` in JSON.

## Frontend Migration Tips
- Replace Firebase service calls with fetch/axios to these endpoints.
- Store JWT token in localStorage or context after login.
- Use role checks to redirect users to the correct dashboard.
- Use the same data shape as before for minimal frontend changes.
