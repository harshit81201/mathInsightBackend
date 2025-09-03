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

### 3. Parent Quiz Access

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

### 4. Quiz Attempts and Submissions

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

This comprehensive quiz system provides all the requested functionality with proper authentication, permissions, and business logic implementation.
