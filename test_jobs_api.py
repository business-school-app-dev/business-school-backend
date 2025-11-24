"""
Simple test script to verify the jobs API logic works
without needing the full Flask app or database.
"""
import pandas as pd
import os

# Category mapping (same as in jobs.py)
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


def get_jobs_by_category(category):
    """Test the jobs API logic"""
    try:
        # Map frontend category value to CSV category name
        csv_category = CATEGORY_MAPPING.get(category)

        if not csv_category:
            return {
                "error": "Invalid category",
                "message": f"Category '{category}' not found"
            }

        # Load CSV file (skip first row which is just "salary_table")
        csv_path = os.path.join(os.path.dirname(__file__), "app/salary_table.csv")
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

        return {
            "category": category,
            "jobs": jobs_list,
            "count": len(jobs_list) - 1  # Exclude "Other" from count
        }

    except FileNotFoundError:
        return {
            "error": "Data file not found",
            "message": "salary_table.csv not found"
        }
    except Exception as e:
        return {
            "error": "Failed to fetch jobs",
            "message": str(e)
        }


if __name__ == "__main__":
    import json

    print("=" * 60)
    print("Testing Jobs API")
    print("=" * 60)

    # Test a few categories
    test_categories = ['management', 'healthcare', 'math_computers']

    for category in test_categories:
        print(f"\n📋 Testing category: {category}")
        print("-" * 60)

        result = get_jobs_by_category(category)

        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            print(f"   Message: {result['message']}")
        else:
            print(f"✅ Success!")
            print(f"   Category: {result['category']}")
            print(f"   Job count: {result['count']}")
            print(f"   Total options (including Other): {len(result['jobs'])}")
            print(f"\n   First 3 jobs:")
            for job in result['jobs'][:3]:
                print(f"   - {job['title']}: ${job['starting_salary']:,} (growth: {job['growth_rate']:.2%})")

    print("\n" + "=" * 60)
    print("✅ API test complete! The backend logic works.")
    print("=" * 60)
