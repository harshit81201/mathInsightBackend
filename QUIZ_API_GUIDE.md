# Quiz System API Documentation

This document provides examples and testing scenarios for the newly implemented quiz system.

## Authentication Required
All endpoints require authentication using JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## API Endpoints

### 1. Teacher Quiz Management

#### Create a Quiz
```http
POST /api/quizzes/
Content-Type: application/json
Authorization: Bearer <teacher-token>

{
    "title": "Math Quiz 1",
    "description": "Basic algebra and geometry questions",
    "time_limit": 30,
    "deadline": "2025-09-10T15:00",
    "is_active": true
}
```

**Note:** Supported deadline formats:
- `"2025-09-10T15:00"` (YYYY-MM-DDTHH:MM)
- `"2025-09-10T15:00:00Z"` (ISO format with seconds)
- `"2025-09-10 15:00"` (with space separator)

#### Get All Teacher's Quizzes
```http
GET /api/quizzes/
Authorization: Bearer <teacher-token>
```

#### Update a Quiz
```http
PATCH /api/quizzes/1/
Content-Type: application/json
Authorization: Bearer <teacher-token>

{
    "is_active": false,
    "deadline": "2025-09-15T15:00:00Z"
}
```

#### Get Quiz Details
```http
GET /api/quizzes/1/
Authorization: Bearer <teacher-token>
```

### 2. Question Management

#### Add Questions to a Quiz
```http
POST /api/quizzes/1/questions/
Content-Type: application/json
Authorization: Bearer <teacher-token>

{
    "question_text": "What is 2 + 2?",
    "option_a": "3",
    "option_b": "4",
    "option_c": "5",
    "option_d": "6",
    "correct_option": "B",
    "marks": 1
}
```

#### Get All Questions for a Quiz
```http
GET /api/quizzes/1/questions/
Authorization: Bearer <teacher-token>
```

**Note:** For students/parents, this endpoint will NOT include the `correct_option` field.

### 3. Teacher Score Management

#### Get All Students' Score Summary
```http
GET /api/scores/teacher/{teacher_id}/students/
Authorization: Bearer <teacher-token>
```

**Description:** Get all students under a teacher with their basic info and quiz score summary, plus an overview of all quiz attempts by all students.

**Response Example:**
```json
{
    "students": [
        {
            "id": 1,
            "name": "Alice Smith",
            "parent_email": "parent@email.com",
            "class_name": "Grade 5A",
            "total_quizzes_attempted": 5,
            "average_score_percentage": 78.5,
            "latest_quiz_date": "2025-09-15T10:30:00Z",
            "completed_attempts": 4,
            "incomplete_attempts": 1
        },
        {
            "id": 2,
            "name": "Bob Johnson",
            "parent_email": "parent2@email.com",
            "class_name": "Grade 5A",
            "total_quizzes_attempted": 3,
            "average_score_percentage": 85.0,
            "latest_quiz_date": "2025-09-16T14:20:00Z",
            "completed_attempts": 3,
            "incomplete_attempts": 0
        }
    ],
    "all_quiz_attempts": [
        {
            "id": 15,
            "student_name": "Bob Johnson",
            "student_class": "Grade 5A",
            "quiz_title": "Math Quiz 3",
            "score": 9,
            "total_marks": 10,
            "percentage": 90.0,
            "attempted_at": "2025-09-16T14:20:00Z",
            "completed_at": "2025-09-16T14:45:00Z",
            "is_completed": true
        },
        {
            "id": 14,
            "student_name": "Alice Smith",
            "student_class": "Grade 5A",
            "quiz_title": "Math Quiz 2",
            "score": 7,
            "total_marks": 10,
            "percentage": 70.0,
            "attempted_at": "2025-09-15T10:30:00Z",
            "completed_at": "2025-09-15T11:00:00Z",
            "is_completed": true
        }
    ]
}
```

#### Get Detailed Student Scores
```http
GET /api/scores/teacher/{teacher_id}/student/{student_id}/
Authorization: Bearer <teacher-token>
```

**Description:** Get detailed quiz scores for a specific student under a specific teacher, showing individual quiz attempts with question statistics.

**Response Example:**
```json
{
    "student_id": 1,
    "student_name": "Alice Smith",
    "student_email": "parent@email.com",
    "class_name": "Grade 5A",
    "quiz_attempts": [
        {
            "id": 14,
            "quiz_title": "Math Quiz 2",
            "quiz_total_marks": 10,
            "quiz_total_questions": 5,
            "correct_answers": 4,
            "total_questions": 5,
            "quiz_marks": 7,
            "total_marks": 10,
            "percentage": 70.0,
            "attempted_at": "2025-09-15T10:30:00Z",
            "completed_at": "2025-09-15T11:00:00Z",
            "is_completed": true
        },
        {
            "id": 12,
            "quiz_title": "Math Quiz 1",
            "quiz_total_marks": 10,
            "quiz_total_questions": 5,
            "correct_answers": 5,
            "total_questions": 5,
            "quiz_marks": 10,
            "total_marks": 10,
            "percentage": 100.0,
            "attempted_at": "2025-09-10T09:15:00Z",
            "completed_at": "2025-09-10T09:40:00Z",
            "is_completed": true
        }
    ]
}
```

**Key Features:**
- **Authentication Required:** Teachers can only access their own students' scores
- **Student Summary:** Shows basic student info with quiz statistics
- **Score Format:** Displays "correct_answers/total_questions" and "quiz_marks/total_marks" for easy frontend display
- **Overview Section:** First endpoint includes all quiz attempts by all students for classroom activity overview
- **Percentage Available:** Percentage is calculated and included, but can also be calculated in frontend
- **Ordered Results:** Quiz attempts are ordered by most recent first

### 4. Parent Endpoints

#### Get Parent's Children
```http
GET /api/parent/children/
Authorization: Bearer <parent-token>
```

**Response Example:**
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
    },
    {
        "id": 2,
        "name": "Bob Smith",
        "class_name": "Grade 3B",
        "teacher_details": {
            "id": 4,
            "email": "teacher2@school.com",
            "first_name": "Jane",
            "last_name": "Wilson",
            "full_name": "Jane Wilson",
            "school_name": "Springfield Elementary"
        }
    }
]
```

#### Get Available Active Quizzes for Children
```http
GET /api/parent/quizzes/
Authorization: Bearer <parent-token>
```

**Response Example:**
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

**Note:** Only returns active quizzes from teachers who teach the parent's children.

### 5. Quiz Attempts and Submissions

#### Start a Quiz Attempt
```http
POST /api/quizzes/1/attempt/
Content-Type: application/json
Authorization: Bearer <parent-token>

{
    "student_id": 5
}
```

#### Submit Quiz Answers
```http
POST /api/quizzes/1/submit/
Content-Type: application/json
Authorization: Bearer <parent-token>

{
    "student_id": 5,
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

#### Get Quiz Results
```http
GET /api/quizzes/1/results/?student_id=5
Authorization: Bearer <parent-token>
```

For teachers (to see all attempts):
```http
GET /api/quizzes/1/results/
Authorization: Bearer <teacher-token>
```

## Response Examples

### Quiz List Response
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
        "teacher_name": "John Doe",
        "created_at": "2025-09-03T14:30:00Z"
    }
]
```

### Question Response (for Students/Parents)
```json
[
    {
        "id": 1,
        "question_text": "What is 2 + 2?",
        "option_a": "3",
        "option_b": "4",
        "option_c": "5",
        "option_d": "6",
        "marks": 1
    }
]
```

### Question Response (for Teachers)
```json
[
    {
        "id": 1,
        "question_text": "What is 2 + 2?",
        "option_a": "3",
        "option_b": "4",
        "option_c": "5",
        "option_d": "6",
        "marks": 1,
        "correct_option": "B"
    }
]
```

### Quiz Results Response
```json
{
    "attempt_id": 1,
    "quiz_title": "Math Quiz 1",
    "student_name": "Alice Smith",
    "score": 8,
    "total_marks": 10,
    "percentage": 80.0,
    "attempted_at": "2025-09-05T10:00:00Z",
    "completed_at": "2025-09-05T10:25:00Z",
    "answers": [
        {
            "question": 1,
            "question_text": "What is 2 + 2?",
            "selected_option": "B",
            "correct_option": "B",
            "is_correct": true,
            "marks": 1
        },
        {
            "question": 2,
            "question_text": "What is 5 x 3?",
            "selected_option": "A",
            "correct_option": "C",
            "is_correct": false,
            "marks": 2
        }
    ]
}
```

## Business Logic Implemented

1. **Teacher Permissions:**
   - Only teachers can create and manage quizzes
   - Teachers can only see/modify their own quizzes
   - Teachers can enable/disable quizzes using `is_active` field

2. **Parent Permissions:**
   - Parents can only see active quizzes for their children
   - Parents can only attempt quizzes for their own children
   - Parents can only see results for their children's attempts

3. **Quiz Attempt Rules:**
   - Students can attempt each quiz only once
   - Quizzes must be active (`is_active=True`)
   - Attempts only allowed before deadline
   - Students can only attempt quizzes from their teacher

4. **Automatic Scoring:**
   - Scores calculated automatically based on correct answers
   - Marks per question are configurable
   - Percentage calculated and included in results

5. **Data Integrity:**
   - Unique constraints prevent duplicate attempts
   - Foreign key relationships maintain data consistency
   - Automatic timestamp tracking for attempts

## Error Handling

The API includes comprehensive error handling for:
- Invalid permissions
- Quiz not found
- Student not found or not parent's child
- Quiz already attempted
- Quiz inactive or past deadline
- Invalid answer format
- Missing required fields

## Admin Interface

The quiz system includes a comprehensive Django admin interface with:
- Quiz management with inline question editing
- Question management
- Quiz attempt tracking
- Answer review
- Proper permissions (teachers see only their content)

## Development Setup

**Important:** This project uses the `uv` package manager. When running any Python/Django commands, use `uv` instead of `pip` or regular Python commands:

```bash
# Install dependencies
uv sync

# Run migrations
uv run python manage.py migrate

# Create superuser
uv run python manage.py createsuperuser

# Run development server
uv run python manage.py runserver

# Run tests
uv run python manage.py test
```

## Testing Steps

1. **Create a teacher account** and login to get JWT token
2. **Create a parent account** and login to get JWT token
3. **Create a student** linked to the parent and teacher
4. **Create a quiz** as the teacher
5. **Add questions** to the quiz
6. **Get quiz list** as parent (should see the active quiz)
7. **Start quiz attempt** as parent for the student
8. **Submit quiz answers** as parent
9. **Get quiz results** as parent
10. **Check results** as teacher for all attempts
11. **Get student score summary** as teacher using `/api/scores/teacher/{teacher_id}/students/`
12. **Get detailed student scores** as teacher using `/api/scores/teacher/{teacher_id}/student/{student_id}/`

### New Score Endpoints Testing

To test the new score management endpoints:

```bash
# Get all students' scores summary (replace {teacher_id} with actual teacher ID)
curl -X GET "http://localhost:8000/api/scores/teacher/1/students/" \
     -H "Authorization: Bearer <teacher-token>"

# Get detailed scores for specific student (replace IDs with actual values)
curl -X GET "http://localhost:8000/api/scores/teacher/1/student/1/" \
     -H "Authorization: Bearer <teacher-token>"
```

**Expected Use Case:**
- Teacher logs in and calls the first endpoint to see all students with summary statistics
- Frontend displays student list with stats and overall classroom quiz activity
- Teacher clicks on a student name, frontend calls second endpoint with student ID
- Detailed view shows all quiz attempts for that student with question/answer statistics

This comprehensive quiz system provides all the requested functionality with proper authentication, permissions, and business logic implementation.
