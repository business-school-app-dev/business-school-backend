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
    Recommend UMD courses based on user's comfort level and time commitment (credits).

    Query params:
      - comfort: 'beginner' | 'intermediate' | 'advanced' | 'n/a'
      - max_credits: integer as string (e.g. '3') or 'n/a'

    Behavior:
      - comfort != 'n/a' and max_credits != 'n/a':
          filter by BOTH comfort level AND credits (original behavior)
      - comfort != 'n/a' and max_credits == 'n/a':
          filter by comfort level ONLY (ignore credits)
      - comfort == 'n/a' and max_credits != 'n/a':
          filter by credits ONLY (ignore comfort level)
      - comfort == 'n/a' and max_credits == 'n/a':
          return ALL BMGT courses
    """
    # Raw query params
    comfort_raw = (request.args.get("comfort") or "").lower()
    credits_raw = (request.args.get("max_credits") or "").lower()

    # Map comfort level -> course level digit
    level_map = {
        "beginner": "1",      # BMGT1xx
        "intermediate": "2",  # BMGT2xx
        "advanced": "3",      # BMGT3xx
    }

    # Determine if we have a comfort filter
    if comfort_raw and comfort_raw != "n/a":
        level = level_map.get(comfort_raw)
    else:
        level = None  # no comfort filter

    # Determine if we have a credit filter
    max_credits = None
    if credits_raw and credits_raw != "n/a":
        try:
            max_credits = int(credits_raw)
        except ValueError:
            return jsonify({"error": "max_credits must be an integer or 'N/A'"}), 400

    # Fetch all BMGT courses
    r = requests.get(f"{UMD_API}?dept_id=BMGT")
    if r.status_code != 200:
        return jsonify({"error": "Failed to fetch courses"}), 500
    all_courses = r.json()

    # --------------------------
    # Build filtered list based on which filters we have
    # --------------------------
    def matches_level(course):
        if not level:
            return True
        return re.match(rf"BMGT{level}\d{{2}}", course["course_id"])

    def matches_credits(course):
        if max_credits is None:
          # no credit filter
            return True
        try:
            return int(course.get("credits", 0)) <= max_credits
        except (TypeError, ValueError):
            return False

    # Apply filters:
    # - both level and credits
    # - only level
    # - only credits
    recommended = [
        c for c in all_courses
        if matches_level(c) and matches_credits(c)
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

    # Build response metadata
    response_comfort = comfort_raw if comfort_raw else "n/a"
    response_difficulty = f"{level}xx" if level else "all"
    response_max_credits = max_credits if max_credits is not None else "all"

    return jsonify({
        "comfort_level": response_comfort,
        "difficulty": response_difficulty,
        "max_credits": response_max_credits,
        "recommendations": results[:10],  # limit output
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
