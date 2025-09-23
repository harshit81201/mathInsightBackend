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

---

## Parent Performance Endpoints

The following endpoints provide comprehensive performance tracking and analytics for parents to monitor their children's quiz performance.

### 1. Get All Children Performance Overview

#### Endpoint
```http
GET /api/parent/performance/
Authorization: Bearer <parent-token>
```

#### Description
Returns a comprehensive performance overview for all children of the authenticated parent, including summary statistics and individual child performance metrics.

#### Response Format
```json
{
    "children_count": 2,
    "overall_statistics": {
        "total_children": 2,
        "total_quiz_attempts": 15,
        "overall_average_percentage": 87.5,
        "total_marks_earned": 245,
        "total_possible_marks": 280
    },
    "children_performance": [
        {
            "student_id": 1,
            "student_name": "Alice Smith",
            "class_name": "Grade 5A",
            "teacher_name": "John Doe",
            "total_quizzes_attempted": 8,
            "completed_quizzes": 7,
            "incomplete_quizzes": 1,
            "average_score_percentage": 89.2,
            "highest_score_percentage": 95.0,
            "lowest_score_percentage": 78.5,
            "total_marks_earned": 125,
            "total_possible_marks": 140,
            "recent_performance_trend": "improving",
            "last_quiz_date": "2025-09-20T14:30:00Z",
            "performance_level": "Very Good"
        }
    ]
}
```

#### Field Descriptions
| Field | Type | Description |
|-------|------|-------------|
| `children_count` | Integer | Total number of children |
| `overall_statistics` | Object | Aggregated performance statistics |
| `children_performance` | Array | Individual performance data for each child |
| `recent_performance_trend` | String | "improving", "declining", "stable", or "insufficient_data" |
| `performance_level` | String | "Excellent", "Very Good", "Good", "Fair", "Needs Improvement" |

### 2. Get Individual Child Detailed Performance

#### Endpoint
```http
GET /api/parent/performance/child/{child_id}/
Authorization: Bearer <parent-token>
```

#### Description
Returns detailed performance data for a specific child, including all quiz attempts and performance trends over time.

#### Response Format
```json
{
    "student_id": 1,
    "student_name": "Alice Smith",
    "class_name": "Grade 5A",
    "teacher_name": "John Doe",
    "performance_summary": {
        "student_id": 1,
        "student_name": "Alice Smith",
        "class_name": "Grade 5A",
        "teacher_name": "John Doe",
        "total_quizzes_attempted": 8,
        "completed_quizzes": 7,
        "incomplete_quizzes": 1,
        "average_score_percentage": 89.2,
        "highest_score_percentage": 95.0,
        "lowest_score_percentage": 78.5,
        "total_marks_earned": 125,
        "total_possible_marks": 140,
        "recent_performance_trend": "improving",
        "last_quiz_date": "2025-09-20T14:30:00Z",
        "performance_level": "Very Good"
    },
    "quiz_attempts": [
        {
            "id": 1,
            "quiz_title": "Math Quiz 1",
            "quiz_description": "Basic algebra and geometry",
            "quiz_total_marks": 20,
            "quiz_total_questions": 10,
            "teacher_name": "John Doe",
            "score": 18,
            "total_marks": 20,
            "percentage": 90.0,
            "correct_answers": 9,
            "incorrect_answers": 1,
            "unanswered_questions": 0,
            "attempted_at": "2025-09-20T14:00:00Z",
            "completed_at": "2025-09-20T14:25:00Z",
            "is_completed": true,
            "time_taken_display": "25m 0s",
            "performance_level": "Excellent"
        }
    ],
    "performance_trends": {
        "monthly": [
            {
                "period": "2025-09",
                "average_percentage": 89.2,
                "quizzes_taken": 7,
                "total_marks": 125,
                "possible_marks": 140
            }
        ],
        "weekly": [
            {
                "period": "2025-W38",
                "average_percentage": 92.5,
                "quizzes_taken": 3,
                "total_marks": 55,
                "possible_marks": 60
            }
        ]
    }
}
```

### 3. Get Quiz Attempt Detailed Results

#### Endpoint
```http
GET /api/parent/performance/child/{child_id}/quiz/{attempt_id}/
Authorization: Bearer <parent-token>
```

#### Description
Returns detailed results for a specific quiz attempt, including question-by-question breakdown and analysis.

#### Response Format
```json
{
    "attempt_details": {
        "id": 1,
        "quiz_title": "Math Quiz 1",
        "quiz_description": "Basic algebra and geometry",
        "quiz_total_marks": 20,
        "quiz_total_questions": 10,
        "teacher_name": "John Doe",
        "score": 18,
        "total_marks": 20,
        "percentage": 90.0,
        "correct_answers": 9,
        "incorrect_answers": 1,
        "unanswered_questions": 0,
        "attempted_at": "2025-09-20T14:00:00Z",
        "completed_at": "2025-09-20T14:25:00Z",
        "is_completed": true,
        "time_taken_display": "25m 0s",
        "performance_level": "Excellent"
    },
    "question_breakdown": [
        {
            "question_id": 1,
            "question_text": "What is 2 + 2?",
            "option_a": "3",
            "option_b": "4",
            "option_c": "5",
            "option_d": "6",
            "correct_option": "B",
            "selected_option": "B",
            "is_correct": true,
            "marks": 2,
            "marks_earned": 2
        },
        {
            "question_id": 2,
            "question_text": "What is 5 x 3?",
            "option_a": "12",
            "option_b": "15",
            "option_c": "18",
            "option_d": "20",
            "correct_option": "B",
            "selected_option": "A",
            "is_correct": false,
            "marks": 2,
            "marks_earned": 0
        }
    ],
    "summary": {
        "total_questions": 10,
        "answered_questions": 10,
        "correct_answers": 9,
        "incorrect_answers": 1,
        "unanswered_questions": 0,
        "total_marks_possible": 20,
        "marks_earned": 18,
        "percentage": 90.0
    }
}
```

#### Error Responses
- **401 Unauthorized**: Invalid or missing authentication token
- **403 Forbidden**: User is not a parent or doesn't have permission
- **404 Not Found**: Child or quiz attempt not found

### Performance Metrics Explained

#### Performance Levels
- **Excellent**: 90-100% average score
- **Very Good**: 80-89% average score
- **Good**: 70-79% average score
- **Fair**: 60-69% average score
- **Needs Improvement**: Below 60% average score

#### Performance Trends
- **Improving**: Recent average is 5+ points higher than previous period
- **Declining**: Recent average is 5+ points lower than previous period
- **Stable**: Recent average is within 5 points of previous period
- **Insufficient Data**: Not enough quiz attempts to determine trend

#### Time Periods
- **Monthly**: Grouped by calendar month (YYYY-MM format)
- **Weekly**: Grouped by ISO week number (YYYY-WNN format)
- **Trends**: Show up to 12 months or 8 weeks of historical data

### Example Usage

```javascript
// Get overview of all children's performance
const allPerformance = await fetch(`${API_BASE}/parent/performance/`, {
    headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

console.log(`Parent has ${allPerformance.children_count} children`);
console.log(`Overall average: ${allPerformance.overall_statistics.overall_average_percentage}%`);

// Get detailed performance for specific child
const childId = allPerformance.children_performance[0].student_id;
const childDetails = await fetch(`${API_BASE}/parent/performance/child/${childId}/`, {
    headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

console.log(`${childDetails.student_name} has taken ${childDetails.quiz_attempts.length} quizzes`);

// Get detailed results for specific quiz attempt
if (childDetails.quiz_attempts.length > 0) {
    const attemptId = childDetails.quiz_attempts[0].id;
    const quizDetails = await fetch(`${API_BASE}/parent/performance/child/${childId}/quiz/${attemptId}/`, {
        headers: { 'Authorization': `Bearer ${token}` }
    }).then(r => r.json());

    console.log(`Quiz: ${quizDetails.attempt_details.quiz_title}`);
    console.log(`Score: ${quizDetails.summary.marks_earned}/${quizDetails.summary.total_marks_possible}`);
}
```
