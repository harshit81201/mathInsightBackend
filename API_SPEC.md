# MathInsight Django API Specification

This document describes the REST API endpoints for the MathInsight backend, designed to replace Firebase and allow the React frontend to work with minimal changes.

## Authentication

### POST /api/auth/login/
- Login for teachers and parents.
- Request: `{ "email": "string", "password": "string" }`
- Response: `{ "token": "jwt", "user": { ...user fields... } }`

### GET /api/auth/me/
- Get current authenticated user.
- Header: `Authorization: Bearer <token>`
- Response: `{ "id": 1, "email": "...", "role": "teacher|parent", ... }`

---

## Teachers

### GET /api/teachers/{id}/
- Get teacher profile.
- Header: `Authorization: Bearer <token>`

### GET /api/teachers/{id}/students/
- Get all students for a teacher.
- Header: `Authorization: Bearer <token>`

---

## Students

### POST /api/students/
- Add a new student (by teacher).
- Request: `{ "name": "string", "parent_name": "string", "parent_email": "string", "class_name": "string" }`
- Header: `Authorization: Bearer <token>`
- Response: `{ "id": 1, ...student fields..., "temp_password": "string" }`

### PATCH /api/students/{id}/
- Edit student details.
- Header: `Authorization: Bearer <token>`

### DELETE /api/students/{id}/
- Delete student (by teacher).
- Header: `Authorization: Bearer <token>`

### GET /api/students/{id}/
- Get student details.
- Header: `Authorization: Bearer <token>`

---

## Parent Dashboard

### GET /api/parent/me/
- Get parent profile and children.
- Header: `Authorization: Bearer <token>`

### GET /api/parent/children/
- Get all children for the logged-in parent.
- Header: `Authorization: Bearer <token>`

---

## Assignments (Demo)

### GET /api/assignments/?student_id={id}
- Get assignments for a student.
- Header: `Authorization: Bearer <token>`

---

## Example Usage

- All requests use JWT authentication.
- All endpoints return JSON.
- Error responses: `{ "error": "message" }`

---

## Notes
- Roles: `teacher` and `parent` are checked on login and for permissions.
- Endpoints are designed to match the frontend's current data needs.
- Extend as needed for more features (messages, analytics, etc).
