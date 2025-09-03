# Parent API Endpoints

This document provides comprehensive documentation for all parent-specific API endpoints.

## Authentication Required
All endpoints require authentication using JWT tokens for users with `role = 'parent'`.
```
Authorization: Bearer <parent-jwt-token>
```

## Parent Endpoints

### 1. Get Children List

#### Endpoint
```http
GET /api/parent/children/
Authorization: Bearer <parent-token>
```

#### Description
Returns a list of all children associated with the authenticated parent user.

#### Response Format
```json
[
    {
        "id": 1,
        "name": "Alice Smith",
        "class_name": "Grade 5A",
        "teacher_details": {
            "id": 3,
            "email": "teacher@school.com",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "school_name": "Springfield Elementary"
        }
    }
]
```

#### Field Descriptions
| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Unique student ID |
| `name` | String | Student's full name |
| `class_name` | String | Class/grade the student is in |
| `teacher_details` | Object | Information about the student's teacher |
| `teacher_details.id` | Integer | Teacher's user ID |
| `teacher_details.email` | String | Teacher's email address |
| `teacher_details.first_name` | String | Teacher's first name |
| `teacher_details.last_name` | String | Teacher's last name |
| `teacher_details.full_name` | String | Teacher's full name |
| `teacher_details.school_name` | String | School name |

#### Error Responses
- **401 Unauthorized**: Invalid or missing authentication token
- **403 Forbidden**: User is not a parent or doesn't have permission
- **200 OK**: Returns empty array `[]` if parent has no children

### 2. Get Available Quizzes

#### Endpoint
```http
GET /api/parent/quizzes/
Authorization: Bearer <parent-token>
```

#### Description
Returns a list of active quizzes available for the parent's children.

#### Response Format
```json
[
    {
        "id": 1,
        "title": "Math Quiz 1",
        "description": "Basic algebra and geometry questions",
        "time_limit": 30,
        "deadline": "2025-09-10T15:00:00Z",
        "is_active": true,
        "total_questions": 5,
        "total_marks": 10,
        "teacher_name": "John Doe"
    }
]
```

### 3. Start Quiz Attempt

#### Endpoint
```http
POST /api/quizzes/{quiz_id}/attempt/
Authorization: Bearer <parent-token>
```

#### Request Body
```json
{
    "student_id": 1
}
```

#### Description
Starts a quiz attempt for the specified child. The child must belong to the authenticated parent.

### 4. Submit Quiz

#### Endpoint
```http
POST /api/quizzes/{quiz_id}/submit/
Authorization: Bearer <parent-token>
```

#### Request Body
```json
{
    "student_id": 1,
    "answers": [
        {
            "question_id": "1",
            "selected_option": "B"
        },
        {
            "question_id": "2",
            "selected_option": "A"
        }
    ]
}
```

#### Description
Submits quiz answers and returns immediate results with scoring.

### 5. Get Quiz Results

#### Endpoint
```http
GET /api/quizzes/{quiz_id}/results/?student_id={student_id}
Authorization: Bearer <parent-token>
```

#### Description
Retrieves the quiz results for a specific child's completed attempt.

## Usage Examples

### Getting All Children for a Parent
```javascript
// Frontend example
const response = await fetch(`${API_BASE}/parent/children/`, {
    headers: {
        'Authorization': `Bearer ${parentToken}`,
        'Content-Type': 'application/json'
    }
});

const children = await response.json();
console.log('Parent has', children.length, 'children');
```

### Complete Quiz Flow
```javascript
// 1. Get children
const children = await fetch(`${API_BASE}/parent/children/`, {
    headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

// 2. Get available quizzes
const quizzes = await fetch(`${API_BASE}/parent/quizzes/`, {
    headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

// 3. Start quiz for first child
const attempt = await fetch(`${API_BASE}/quizzes/${quizzes[0].id}/attempt/`, {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ student_id: children[0].id })
}).then(r => r.json());

// 4. Submit answers
const results = await fetch(`${API_BASE}/quizzes/${quizzes[0].id}/submit/`, {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        student_id: children[0].id,
        answers: [
            { question_id: "1", selected_option: "B" },
            { question_id: "2", selected_option: "A" }
        ]
    })
}).then(r => r.json());
```

## Notes

- All endpoints require the user to have `role = 'parent'`
- Parents can only access data for their own children
- Students are automatically linked to parents when created by teachers
- Quiz attempts are tracked per student and can only be done once per quiz
- Results are available immediately after quiz submission
