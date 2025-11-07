from flask import Flask, jsonify, request, Blueprint
import requests
import re

courses_bp = Blueprint('courses', __name__)

UMD_API = "https://api.umd.io/v0/courses"

# ----------------------------
# Helper: Fetch a single course by ID
# ----------------------------
def get_course(course_id):
    url = f"{UMD_API}/{course_id}"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        return None

# ----------------------------
# Helper: Build regex filter pattern for prereqs
# ----------------------------
def get_filter_pattern(course_id: str) -> str:
    match = re.match(r"([A-Z]{4})(\d)x{2}", course_id, re.IGNORECASE)
    if not match:
        return r"[A-Z]{4}\d{3}"
    dept = match.group(1).upper()
    level = int(match.group(2))
    levels_to_allow = [str(level), str(level - 1)]
    level_pattern = f"[{''.join(levels_to_allow)}]"
    return f"({dept}{level_pattern}\\d{{2}})"

# ----------------------------
# Recursive prereq builder (filtered)
# ----------------------------
def build_prereq_filtered(course_id, filter_pattern, visited=None):
    if visited is None:
        visited = set()
    if course_id in visited:
        return {"course": course_id, "prereqs": []}
    visited.add(course_id)

    response = get_course(course_id)
    if not response:
        return {"course": course_id, "prereqs": []}

    prereq_text = response.get("relationships", {}).get("prereqs")
    course_name = response.get("name", "")
    if not prereq_text:
        return {"course": course_id, "name": course_name, "prereqs": []}
    
    description = response.get("description", "")
    restriction = response.get("restrictions", "")

    all_prereq_courses = re.findall(r"[A-Z]{4}\d{3}", prereq_text)
    courses_to_build = [c for c in all_prereq_courses if re.match(filter_pattern, c)]

    prereq_list = [build_prereq_filtered(c, filter_pattern, visited) for c in courses_to_build]
    return {
        "course": course_id,
        "name": course_name,
        "description": description,
        "restriction": restriction,
        "prereqs": prereq_list
    }

# ----------------------------
# Recursive prereq builder (unfiltered)
# ----------------------------
def build_prereq(course_id, visited=None):
    if visited is None:
        visited = set()
    if course_id in visited:
        return {"course": course_id, "prereqs": []}
    visited.add(course_id)

    response = get_course(course_id)
    if not response:
        return {"course": course_id, "prereqs": []}

    prereq_text = response.get("relationships", {}).get("prereqs")
    course_name = response.get("name", "")

    description = response.get("description", "")
    restriction = response.get("restrictions", "")

    if not prereq_text:
        return {"course": course_id, "name": course_name, "prereqs": []}

    prereq_courses = re.findall(r"[A-Z]{4}\d{3}", prereq_text)
    prereq_list = [build_prereq(c, visited) for c in prereq_courses]
    return {
        "course": course_id,
        "name": course_name,
        "description": description,
        "restriction": restriction,
        "prereqs": prereq_list
    }

# ----------------------------
# Endpoint: Get all BMGT courses
# ----------------------------
@courses_bp.route("/courses/all")
def get_all_courses():
    r = requests.get(f"{UMD_API}?dept_id=BMGT")
    if r.status_code != 200:
        return jsonify({"error": "Failed to fetch courses"}), 500
    return jsonify(r.json())

# ----------------------------
# Endpoint: Get full prereq plan
# ----------------------------
@courses_bp.route("/plan/<course_id>")
def get_plan(course_id):
    tree = build_prereq(course_id.upper())
    return jsonify(tree)

# ----------------------------
# Endpoint: Get filtered prereq plan
# ----------------------------
@courses_bp.route("/planTrim/<course_id>")
def get_planTrim(course_id):
    course_id = course_id.upper()
    filter_pattern = get_filter_pattern(course_id)
    tree = build_prereq_filtered(course_id, filter_pattern)
    return jsonify(tree)



# ----------------------------
# NEW FEATURE: Rule-based course recommender
# ----------------------------
@courses_bp.route("/recommend", methods=["GET"])
def recommend_courses():
    """
    Recommend UMD courses based on user's comfort level (1-3) and time commitment (credits).
    Example: /recommend?comfort=1&max_credits=3
    """
    comfort = str(request.args.get("comfort", "beginner"))  # beginner, intermediate, advanced
    max_credits = int(request.args.get("max_credits", 3))  # max allowed credits

    # Map comfort to difficulty
    level_map = {
        "beginner": "1",  # easy
        "intermediate": "2",  # moderate
        "advanced": "3"   # challenging
    }
    level = level_map.get(comfort, "beginner")

    # Fetch all BMGT courses
    r = requests.get(f"{UMD_API}?dept_id=BMGT")
    if r.status_code != 200:
        return jsonify({"error": "Failed to fetch courses"}), 500

    all_courses = r.json()

    # Filter by level and credits
    recommended = [
        c for c in all_courses
        if re.match(rf"BMGT{level}\d{{2}}", c["course_id"])
        and int(c.get("credits", 0)) <= max_credits
    ]

    if not recommended:
        return jsonify({"message": "No suitable courses found."}), 404

    # Prepare clean response
    results = [
        {
            "course_id": c["course_id"],
            "name": c["name"],
            "credits": c.get("credits"),
            "description": c.get("description", ""), 
            "restrictions": c.get("restrictions", "")
        }
        for c in recommended
    ]

    return jsonify({
        "comfort_level": comfort,
        "difficulty": f"{level}xx",
        "max_credits": max_credits,
        "recommendations": results[:10]  # limit output
    })

# ----------------------------
# Root route: API overview
# ----------------------------
@courses_bp.route("/")
def home():
    return jsonify({
        "message": "UMD Course Planner API",
        "endpoints": {
            "/courses/all": "Get all BMGT courses",
            "/plan/<course_id>": "Get full prerequisite plan (e.g., /plan/BMGT340)",
            "/planTrim/<course_id>": "Get filtered prerequisite plan by course level",
            "/recommend?comfort=2&max_credits=3": "Recommend courses by comfort level (1-3) and time commitment"
        }
    })

# ----------------------------
# Run server
# ----------------------------
if __name__ == "courses":
    courses_bp.run(debug=True)
