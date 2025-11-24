from flask import jsonify, Blueprint, current_app
import pandas as pd
import os

jobs_bp = Blueprint('jobs', __name__)

# Category mapping from frontend values to CSV values
CATEGORY_MAPPING = {
    'management': 'Management',
    'business_finance': 'Business/Finance',
    'math_computers': 'Math and Computers',
    'architecture_engineering': 'Architecture/Engineering',
    'science': 'Life, Physical, and Social Science',
    'public_service': 'Public Service',
    'legal': 'Legal Occupations',
    'education': 'Educational Instruction and Library Occupations',
    'arts_media': 'Arts, Design, Entertainment, Sports, and Media Occupations',
    'healthcare': 'Healthcare',
    'protective_service': 'Protective Service',
    'food_preparation': 'Food Preparation and Serving',
    'personal_care': 'Personal Care and Service',
    'sales': 'Sales',
    'office_admin': 'Office and Administrative Support',
    'construction': 'Construction and Extraction',
    'installation_maintenance': 'Installation, Maintenance, and Repair',
    'production': 'Production Operations',
    'transportation': 'Transportation'
}


@jobs_bp.route("/jobs/<category>", methods=["GET"])
def get_jobs_by_category(category):
    """
    Get all jobs for a specific career category from CSV.

    Args:
        category: Career category (e.g., 'management', 'healthcare', 'math_computers')

    Returns:
        JSON response with list of jobs for the category
    """
    try:
        # Map frontend category value to CSV category name
        csv_category = CATEGORY_MAPPING.get(category)

        if not csv_category:
            return jsonify({
                "error": "Invalid category",
                "message": f"Category '{category}' not found"
            }), 400

        # Load CSV file (skip first row which is just "salary_table")
        csv_path = os.path.join(current_app.root_path, "salary_table.csv")
        df = pd.read_csv(csv_path, skiprows=1)

        # Filter jobs by category
        category_jobs = df[df['Category'] == csv_category]

        # Convert to list of dicts
        jobs_list = []
        for _, row in category_jobs.iterrows():
            # Skip rows with unknown or missing data
            if pd.isna(row['Career_Title']) or row['Career_Title'] == 'Unknown Title':
                continue
            if pd.isna(row['Starting Salary']) or row['Starting Salary'] == 'Unknown start':
                continue

            jobs_list.append({
                "id": str(row['Career_ID']),
                "title": row['Career_Title'],
                "value": row['Career_Title'].lower().replace(" ", "_").replace(",", ""),
                "starting_salary": int(row['Starting Salary']),
                "growth_rate": float(row['Salary_growth_mean'])
            })

        # Always add "Other" option at the end
        jobs_list.append({
            "id": "other",
            "title": "Other",
            "value": "other",
            "starting_salary": None,
            "growth_rate": None
        })

        return jsonify({
            "category": category,
            "jobs": jobs_list,
            "count": len(jobs_list) - 1  # Exclude "Other" from count
        }), 200

    except FileNotFoundError:
        return jsonify({
            "error": "Data file not found",
            "message": "salary_table.csv not found"
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Failed to fetch jobs",
            "message": str(e)
        }), 500
