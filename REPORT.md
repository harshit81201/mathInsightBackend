# MathInsight API Endpoint Reference Report

## Authentication

### 1. POST /api/auth/login/
- **Usage:** User login (teacher/parent).
- **Request:**
  ```json
  { "email": "user@example.com", "password": "yourpassword" }
  ```
- **Response:**
  ```json
  { "token": "jwt_token", "user": { ...user fields... } }
  ```
- **Notes:** Uses JWT. Returns user info and access token.

### 2. GET /api/auth/me/
- **Usage:** Get current authenticated user.
- **Headers:**  Authorization: Bearer <token>
- **Response:**
  ```json
  { "id": 1, "email": "...", "role": "teacher|parent", ... }
  ```
- **Notes:** Requires JWT. Returns user details.

---

## Teachers

### 3. GET /api/teachers/{id}/
- **Usage:** Get teacher profile by ID.
- **Headers:**  Authorization: Bearer <token>
- **Response:**
  ```json
  { "id": 1, "email": "...", "role": "teacher", ... }
  ```
- **Notes:** Only for users with role `teacher`.

### 4. GET /api/teachers/{id}/students/
- **Usage:** Get all students for a teacher.
- **Headers:**  Authorization: Bearer <token>
- **Response:**
  ```json
  [
    { "id": 1, "name": "...", "class_name": "..." },
    ...
  ]
  ```
- **Notes:** Returns students assigned to the teacher.

---

## Students

### 5. POST /api/students/
- **Usage:** Add a new student (by teacher).
- **Headers:**  Authorization: Bearer <token>
- **Request:**
  ```json
  { "name": "...", "parent_name": "...", "parent_email": "...", "class_name": "..." }
  ```
- **Response:**
  ```json
  { "id": 1, ...student fields..., "temp_password": "string" }
  ```
- **Notes:** Returns created student and a temporary password.

### 6. PATCH /api/students/{id}/
- **Usage:** Edit student details.
- **Headers:**  Authorization: Bearer <token>
- **Request:**
  ```json
  { "name": "...", "class_name": "..." }
  ```
- **Response:**
  ```json
  { "id": 1, ...updated fields... }
  ```

### 7. DELETE /api/students/{id}/
- **Usage:** Delete student (by teacher).
- **Headers:**  Authorization: Bearer <token>
- **Response:**  204 No Content

### 8. GET /api/students/{id}/
- **Usage:** Get student details.
- **Headers:**  Authorization: Bearer <token>
- **Response:**
  ```json
  { "id": 1, "name": "...", ... }
  ```

---

## Parent Dashboard

### 9. GET /api/parent/me/
- **Usage:** Get parent profile and children.
- **Headers:**  Authorization: Bearer <token>
- **Response:**
  ```json
  { "id": 2, "role": "parent", "children": [ ... ] }
  ```

### 10. GET /api/parent/children/
- **Usage:** Get all children for the logged-in parent.
- **Headers:**  Authorization: Bearer <token>
- **Response:**
  ```json
  [
    { "id": 1, "name": "...", "class_name": "..." },
    ...
  ]
  ```

---

## Assignments

### 11. GET /api/assignments/?student_id={id}
- **Usage:** Get assignments for a student.
- **Headers:**  Authorization: Bearer <token>
- **Response:**
  ```json
  [
    { "id": 1, "title": "...", "description": "...", ... },
    ...
  ]
  ```

---

**General Notes:**
- All endpoints require JWT authentication except login.
- All errors return `{ "error": "message" }` in JSON.
- Use the correct role for access control.
- Data shapes match frontend expectations for minimal migration effort.
