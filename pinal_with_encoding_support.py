import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import base64
from io import BytesIO
from datetime import datetime, timedelta
import requests
import json
import msal
import io

import chardet
import csv

COMMON_DELIMITERS = [',', ';', '\t', '|', ' ']

def detect_encoding(file_bytes):
    result = chardet.detect(file_bytes)
    encoding = result['encoding'] or 'utf-8'
    return encoding, result['confidence']

def detect_delimiter(sample_text):
    lines = sample_text.splitlines()[:5]
    delimiter_scores = {}
    for delim in COMMON_DELIMITERS:
        try:
            reader = csv.reader(lines, delimiter=delim)
            lengths = [len(row) for row in reader if row]
            if lengths and len(set(lengths)) == 1 and lengths[0] > 1:
                delimiter_scores[delim] = lengths[0]
        except Exception:
            continue
    return max(delimiter_scores, key=delimiter_scores.get) if delimiter_scores else ','



# Page Config
st.set_page_config(
    page_title="Agile Project Management Suite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS and JS for Apple-style animations
st.markdown("""
<script src="app/assets/animations.js"></script>
<style>
    /* Include Apple-style animations */
    @import url('app/assets/apple_style.css');
    

    /* Base styling */
    .main {
        background-color:  #0e1117 ;
        color: #e0e0e0;
    }
    .metric-card {
        background-color: #1e2130;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 16px;
    }
    .download-link {
        background-color: #1e8e3e;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
        text-decoration: none;
        display: inline-block;
        margin-top: 10px;
    }
    .download-link:hover {
        background-color: #166e2e;
    }
    .azure-section {
        background-color: #0078d4;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: white;
    }
    .nav-link {
        display: inline-block;
        padding: 10px 15px;
        margin: 10px 5px;
        border-radius: 5px;
        text-decoration: none;
        background-color: 1e2130;
        color: #e0e0e0;
        transition: background-color 0.3s;
    }
    .nav-link:hover {
        background-color: #2a2e3a;
    }
    .nav-link.active {
        background-color: #1E88E5;
        color: white;
    }
    .banner {
        margin-bottom: 20px;
        text-align: center;
    }
    .tabbed-interface .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
    }
    .tabbed-interface .stTabs [data-baseweb="tab"] {
        background-color: #1e2130;
        border-radius: 4px 4px 0 0;
    }
    .tabbed-interface .stTabs [aria-selected="true"] {
        background-color: #1E88E5;
    }
    
    /* Animation keyframes */
    @keyframes float {
        0% {
            transform: translateY(0) translateX(0);
        }
        25% {
            transform: translateY(-15px) translateX(15px);
        }
        50% {
            transform: translateY(0) translateX(30px);
        }
        75% {
            transform: translateY(15px) translateX(15px);
        }
        100% {
            transform: translateY(0) translateX(0);
        }
    }

    @keyframes fadeInUp {
        from {
            transform: translateY(40px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    @keyframes gradientBG {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }

    @keyframes pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        50% {
            transform: scale(1.05);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
        }
        100% {
            transform: scale(1);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
    }
    
    /* Animated header */
    .animated-header {
        background: linear-gradient(-45deg, #1E88E5, #4CAF50, #9C27B0, #F44336);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        color: white;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    /* Floating elements container */
    .floating-container {
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        overflow: hidden;
        z-index: -1;
    }
    
    .floating-element {
        position: absolute;
        border-radius: 50%;
        opacity: 0.6;
        pointer-events: none;
        animation: float 15s infinite linear;
    }
    
    /* Apple-style cards */
    .apple-card {
        background-color: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
        animation: fadeInUp 0.8s ease-out forwards;
    }
    
    .apple-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #1E88E5, #4CAF50);
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 30px !important;
        font-weight: bold !important;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stButton > button::after {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0));
    }
    
    .stButton > button:hover::after {
        animation: button-shine 1.5s;
    }
    
    @keyframes button-shine {
        0% {
            left: -100%;
        }
        100% {
            left: 100%;
        }
    }
</style>

<script>
// Helper functions for Apple-style animations
document.addEventListener("DOMContentLoaded", function() {
    // Create floating elements in header
    const createFloatingElements = () => {
        const header = document.querySelector('.animated-header');
        if (!header) return;
        
        for (let i = 0; i < 8; i++) {
            const element = document.createElement('div');
            element.className = 'floating-element';
            
            // Set random properties
            const size = Math.random() * 50 + 20;
            element.style.width = `${size}px`;
            element.style.height = `${size}px`;
            element.style.left = `${Math.random() * 80 + 10}%`;
            element.style.top = `${Math.random() * 80 + 10}%`;
            
            // Set random colors
            const hue = Math.random() * 360;
            element.style.backgroundColor = `hsla(${hue}, 70%, 70%, 0.3)`;
            
            // Set random animation delays
            element.style.animationDelay = `${Math.random() * 5}s`;
            element.style.animationDuration = `${Math.random() * 10 + 10}s`;
            
            header.appendChild(element);
        }
    };
    
    // Add parallax effect to elements
    const addParallaxEffect = () => {
        document.addEventListener('mousemove', (e) => {
            const cards = document.querySelectorAll('.apple-card');
            const mouseX = e.clientX;
            const mouseY = e.clientY;
            
            cards.forEach(card => {
                const rect = card.getBoundingClientRect();
                const cardCenterX = rect.left + rect.width / 2;
                const cardCenterY = rect.top + rect.height / 2;
                
                const offsetX = (mouseX - cardCenterX) / 30;
                const offsetY = (mouseY - cardCenterY) / 30;
                
                card.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
            });
        });
    };
    
    // Initialize animations
    setTimeout(() => {
        createFloatingElements();
        addParallaxEffect();
    }, 1000);
});
</script>
""", unsafe_allow_html=True)

# Session state initialization
if "current_app" not in st.session_state:
    st.session_state.current_app = "home"

# Common session state for Sprint Task Planner
if "df_tasks" not in st.session_state:
    st.session_state.df_tasks = None
if "team_members" not in st.session_state:
    st.session_state.team_members = {}
if "results" not in st.session_state:
    st.session_state.results = None
if "capacity_per_sprint" not in st.session_state:
    st.session_state.capacity_per_sprint = 80  # Default: 2 weeks * 5 days * 8 hours
if "azure_config" not in st.session_state:
    st.session_state.azure_config = {
        "org_url": "",
        "project": "",
        "team": "",
        "access_token": "",
        "connected": False
    }

# For Retrospective Analysis Tool
if "retro_feedback" not in st.session_state:
    st.session_state.retro_feedback = None
if "ai_messages" not in st.session_state:
    st.session_state.ai_messages = [
        {"role": "assistant", "content": "Hi! I'm your retrospective and sprint assistant. How can I help?"}
    ]

# Add main app navigation after the initialization of session state
def set_app(app_name):
    """Set the current app in session state"""
    st.session_state.current_app = app_name

# =========== SHARED HELPER FUNCTIONS ===========

def to_excel(df):
    """Convert DataFrame to Excel bytes"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Tasks')
    return output.getvalue()

def get_download_link(df, filename, format_type):
    """Generate a download link for dataframe"""
    if format_type == 'excel':
        data = to_excel(df)
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}" class="download-link">Download Excel File</a>'
    elif format_type == 'csv':
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:text/csv;base64,{b64}" download="{filename}" class="download-link">Download CSV File</a>'
    return href


# =========== SPRINT TASK PLANNER FUNCTIONS ===========

def get_azure_access_token(client_id, client_secret, tenant_id):
    """Get access token for Azure DevOps using service principal"""
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret
    )
    result = app.acquire_token_for_client(scopes=["499b84ac-1321-427f-aa17-267ca6975798/.default"])
    return result.get("access_token")

def get_azure_devops_tasks(org_url, project, team, access_token):
    """Fetch tasks from Azure DevOps"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Get current iteration path
    iterations_url = f"{org_url}/{project}/{team}/_apis/work/teamsettings/iterations?$timeframe=current&api-version=7.0"
    iterations_response = requests.get(iterations_url, headers=headers)
    iterations = iterations_response.json().get("value", [])
    
    if not iterations:
        st.error("No current iteration found in Azure DevOps")
        return None
    
    current_iteration = iterations[0]["path"]
    
    # Get work items in current iteration
    wiql_query = {
        "query": f"SELECT [System.Id], [System.Title], [System.State], [System.IterationPath], [System.AssignedTo], [Microsoft.VSTS.Common.Priority], [Microsoft.VSTS.Scheduling.OriginalEstimate] FROM WorkItems WHERE [System.IterationPath] = '{current_iteration}' AND [System.WorkItemType] IN ('Task', 'User Story', 'Bug')"
    }
    
    wiql_url = f"{org_url}/{project}/_apis/wit/wiql?api-version=7.0"
    wiql_response = requests.post(wiql_url, headers=headers, json=wiql_query)
    work_items = wiql_response.json().get("workItems", [])
    
    if not work_items:
        st.error("No work items found in current iteration")
        return None
    
    # Get details for each work item
    work_item_ids = [str(item["id"]) for item in work_items]
    batch_size = 200  # Azure DevOps has a limit on batch size
    all_items = []
    
    for i in range(0, len(work_item_ids), batch_size):
        batch_ids = work_item_ids[i:i + batch_size]
        details_url = f"{org_url}/{project}/_apis/wit/workitems?ids={','.join(batch_ids)}&$expand=all&api-version=7.0"
        details_response = requests.get(details_url, headers=headers)
        all_items.extend(details_response.json().get("value", []))
    
    # Process items into DataFrame
    tasks = []
    for item in all_items:
        fields = item.get("fields", {})
        tasks.append({
            "ID": item.get("id"),
            "Title": fields.get("System.Title"),
            "State": fields.get("System.State"),
            "Priority": fields.get("Microsoft.VSTS.Common.Priority"),
            "Original Estimates": fields.get("Microsoft.VSTS.Scheduling.OriginalEstimate", 0),
            "Assigned To": fields.get("System.AssignedTo", {}).get("displayName", "") if isinstance(fields.get("System.AssignedTo"), dict) else fields.get("System.AssignedTo", ""),
            "Iteration Path": fields.get("System.IterationPath"),
            "Sprint": fields.get("System.IterationPath").split("\\")[-1] if fields.get("System.IterationPath") else ""
        })
    
    return pd.DataFrame(tasks)

def update_azure_devops_tasks(org_url, project, access_token, updates):
    """Update tasks in Azure DevOps in batch"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json-patch+json"
    }
    
    batch_size = 200  # Azure DevOps has a limit on batch size
    results = []
    
    for i in range(0, len(updates), batch_size):
        batch_updates = updates[i:i + batch_size]
        batch_url = f"{org_url}/{project}/_apis/wit/workitemsbatch?api-version=7.0"
        
        batch_payload = {
            "ids": [update["id"] for update in batch_updates],
            "document": [
                {
                    "op": "add",
                    "path": f"/fields/{field}",
                    "value": value
                } for update in batch_updates for field, value in update["fields"].items()
            ]
        }
        
        response = requests.post(batch_url, headers=headers, json=batch_payload)
        results.extend(response.json().get("value", []))
    
    return results

def optimize_sprint_assignment(tasks_df, team_members, capacity_per_sprint, max_sprints=3):
    """Optimize task assignment across sprints and team members"""
    # Create a copy of the DataFrame to work with
    df = tasks_df.copy()
    
    # Convert priority to numeric values (higher is more important)
    priority_map = {'1': 3, '2': 2, '3': 1}
    if 'Priority' in df.columns:
        df['Priority_Value'] = df['Priority'].astype(str).map(priority_map).fillna(1)
    else:
        df['Priority_Value'] = 1  # Default priority if not specified
    
    # Sort tasks by priority (high to low)
    df = df.sort_values('Priority_Value', ascending=False)
    
    # Initialize results structure
    results = {
        'assignments': {},
        'sprint_summary': {},
        'team_member_summary': {},
        'unassigned': []
    }
    
    # Initialize sprints
    sprints = {}
    for i in range(1, max_sprints + 1):
        sprint_name = f"Sprint {i}"
        sprints[sprint_name] = {
            'tasks': [],
            'total_hours': 0,
            'capacity': capacity_per_sprint,
            'team_member_hours': {member: 0 for member in team_members.keys()}
        }
    
    # Clone team members with their capacity
    available_capacity = {member: float(capacity) for member, capacity in team_members.items()}
    
    # Try to assign tasks based on priority, estimate, and available capacity
    for idx, row in df.iterrows():
        task_id = row['ID']
        task_title = row['Title']
        task_estimate = float(row['Original Estimates']) if pd.notna(row['Original Estimates']) else 0
        task_priority = row['Priority_Value']
        
        # Skip tasks with no estimates
        if task_estimate == 0:
            results['unassigned'].append({
                'id': task_id,
                'title': task_title,
                'reason': 'No estimate provided'
            })
            continue
        
        # Find the best team member and sprint for this task
        assigned = False
        
        # First, try to assign to team members with highest available capacity
        team_capacity = sorted(available_capacity.items(), key=lambda x: x[1], reverse=True)
        
        for member, capacity in team_capacity:
            if capacity >= task_estimate:
                # Find the first sprint with enough capacity
                for sprint_name, sprint_data in sprints.items():
                    if sprint_data['total_hours'] + task_estimate <= sprint_data['capacity']:
                        # Assign the task
                        sprint_data['tasks'].append({
                            'id': task_id,
                            'title': task_title,
                            'estimate': task_estimate,
                            'priority': task_priority,
                            'assigned_to': member
                        })
                        
                        # Update capacities
                        sprint_data['total_hours'] += task_estimate
                        sprint_data['team_member_hours'][member] += task_estimate
                        available_capacity[member] -= task_estimate
                        
                        # Record assignment
                        results['assignments'][task_id] = {
                            'sprint': sprint_name,
                            'assigned_to': member,
                            'estimate': task_estimate
                        }
                        
                        assigned = True
                        break
                
                if assigned:
                    break
        
        if not assigned:
            # Couldn't assign this task to any member or sprint
            results['unassigned'].append({
                'id': task_id,
                'title': task_title,
                'estimate': task_estimate,
                'reason': 'Insufficient capacity'
            })
    
    # Compile sprint summaries
    for sprint_name, sprint_data in sprints.items():
        results['sprint_summary'][sprint_name] = {
            'task_count': len(sprint_data['tasks']),
            'total_hours': sprint_data['total_hours'],
            'capacity': sprint_data['capacity'],
            'utilization': sprint_data['total_hours'] / sprint_data['capacity'] if sprint_data['capacity'] > 0 else 0,
            'team_member_hours': sprint_data['team_member_hours']
        }
    
    # Compile team member summaries
    total_team_capacity = sum(team_members.values())
    used_capacity = total_team_capacity - sum(available_capacity.values())
    
    for member, capacity in team_members.items():
        results['team_member_summary'][member] = {
            'initial_capacity': capacity,
            'remaining_capacity': available_capacity[member],
            'utilization': (capacity - available_capacity[member]) / capacity if capacity > 0 else 0
        }
    
    # Add overall statistics
    results['stats'] = {
        'total_tasks': len(df),
        'assigned_tasks': len(results['assignments']),
        'unassigned_tasks': len(results['unassigned']),
        'total_capacity': total_team_capacity,
        'used_capacity': used_capacity,
        'overall_utilization': used_capacity / total_team_capacity if total_team_capacity > 0 else 0
    }
    
    return results

# =========== RETROSPECTIVE ANALYSIS FUNCTIONS ===========

def compare_retrospectives(file_objects, min_votes, max_votes):
    """
    Process multiple retrospective CSV files and consolidate feedback with vote counts.
    
    Args:
        file_objects: List of uploaded file objects
        min_votes: Minimum vote threshold for filtering
        max_votes: Maximum vote threshold for filtering
        
    Returns:
        List of tuples containing (feedback, task_id, votes)
    """
    feedback_counts = {}
    feedback_tasks = {}  # Dictionary to store associated task numbers
    processing_results = []

    for uploaded_file in file_objects:
        try:
            # Convert to string content
            content = uploaded_file.getvalue().decode('utf-8')
            lines = content.split('\n')
            
            # Find the header row
            header_index = next((i for i, line in enumerate(lines) if "Type,Description,Votes" in line), None)
            if header_index is None:
                processing_results.append(f"⚠️ Warning: Skipping {uploaded_file.name} - Required columns not found.")
                continue
                
            # Read CSV content after header
            df = pd.read_csv(io.StringIO(content), skiprows=header_index)
            
            # Check for required columns
            if 'Description' not in df.columns or 'Votes' not in df.columns:
                processing_results.append(f"⚠️ Warning: Skipping {uploaded_file.name} - Required columns missing after header detection.")
                continue
                
            # Process feedback and votes
            df = df[['Description', 'Votes']].dropna()
            df['Votes'] = pd.to_numeric(df['Votes'], errors='coerce').fillna(0).astype(int)
            
            for _, row in df.iterrows():
                feedback = row['Description']
                votes = row['Votes']
                
                if feedback in feedback_counts:
                    feedback_counts[feedback] += votes
                else:
                    feedback_counts[feedback] = votes
            
            # Look for Work Items section
            work_items_header = next((i for i, line in enumerate(lines) 
                                  if "Feedback Description,Work Item Title,Work Item Type,Work Item Id," in line), None)
            
            if work_items_header is not None:
                work_items_df = pd.read_csv(io.StringIO(content), skiprows=work_items_header)
                
                if 'Feedback Description' in work_items_df.columns and 'Work Item Id' in work_items_df.columns:
                    for _, row in work_items_df.iterrows():
                        feedback_desc = row['Feedback Description']
                        work_item_id = row['Work Item Id']
                        if pd.notna(feedback_desc) and pd.notna(work_item_id):
                            feedback_tasks[feedback_desc] = work_item_id
            
            processing_results.append(f"✅ Successfully processed {uploaded_file.name}")
            
        except Exception as e:
            processing_results.append(f"❌ Error processing {uploaded_file.name}: {str(e)}")
    
    if not feedback_counts:
        return [("No valid feedback found.", None, 0)], processing_results
    
    filtered_feedback = [(feedback, feedback_tasks.get(feedback, None), votes)
                         for feedback, votes in feedback_counts.items()
                         if min_votes <= votes <= max_votes]
    
    # Sort by votes in descending order
    filtered_feedback.sort(key=lambda x: x[2], reverse=True)
    
    return filtered_feedback, processing_results

def create_dataframe_from_results(feedback_results):
    """Convert feedback results to a pandas DataFrame for visualization and export"""
    data = {
        "Feedback": [item[0] for item in feedback_results],
        "Task ID": [str(item[1]) if item[1] else "None" for item in feedback_results],
        "Votes": [item[2] for item in feedback_results]
    }
    return pd.DataFrame(data)

def process_ai_message(prompt, retro_feedback, api_key):
    """Process message with AI assistant using OpenRouter API"""
    df = create_dataframe_from_results(retro_feedback)
    
    # Build context from feedback
    context = "You are a helpful assistant summarizing retrospective feedback:\n"
    for _, row in df.iterrows():
        task_info = f" [Task ID: {row['Task ID']}]" if row['Task ID'] != "None" else ""
        context += f"- {row['Feedback']} ({row['Votes']} votes){task_info}\n"
    
    try:
        # Prepare the request payload
        payload = {
            "model": "anthropic/claude-2",
            "messages": [
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ]
        }
        
        # Make the API request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

# =========== APPLICATION PAGES ===========

def render_home():
    st.markdown("""
    <style>
    body, .stApp {
    background-color: black !important;
    color: #e0e0e0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    
    # Apple-style animated header with floating elements
    st.markdown(
        """
        <div class="animated-header">
            <div class="floating-container"></div>
            <h1 class="typing-effect" style="color: white; font-size: 48px; margin-bottom: 15px; text-align: center;">Agile Project Management</h1>
            <h3 style="color: white; font-size: 24px; text-align: center; animation: fadeInUp 1s 0.5s forwards; opacity: 0;">Sprint Planning + Retrospective Analysis</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Create a floating container for background elements
    st.markdown("""
    <div class="floating-container">
        <div class="floating-element" style="width: 100px; height: 100px; left: 15%; top: 20%; background-color: rgba(30, 136, 229, 0.1); filter: blur(30px);"></div>
        <div class="floating-element" style="width: 150px; height: 150px; left: 75%; top: 10%; background-color: rgba(76, 175, 80, 0.1); filter: blur(40px);"></div>
        <div class="floating-element" style="width: 80px; height: 80px; left: 85%; top: 60%; background-color: rgba(156, 39, 176, 0.1); filter: blur(25px);"></div>
        <div class="floating-element" style="width: 120px; height: 120px; left: 25%; top: 80%; background-color: rgba(244, 67, 54, 0.1); filter: blur(35px);"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Apple-style description
    st.markdown("""
    <div class="apple-card" style='background-color: rgba(130, 133, 48, 0.7); padding: 30px; border-radius: 20px; margin: 40px 0 30px 0; backdrop-filter: blur(15px); animation: fadeInUp 0.8s ease-out;'>
        <h2 style="margin-bottom: 20px; font-size: 28px; font-weight: 500;">All-in-One Tool for Agile Teams</h2>
        <p style="margin-bottom: 20px; font-size: 18px; line-height: 1.6;">This integrated application provides comprehensive tools for managing agile projects with a beautiful, intuitive interface:</p>
        <ul class="staggered-fade" style="padding-left: 20px;">
            <li style="margin-bottom: 12px; font-size: 16px;"><strong>Sprint Task Planning:</strong> Optimize task assignment across sprints and team members</li>
            <li style="margin-bottom: 12px; font-size: 16px;"><strong>Retrospective Analysis:</strong> Analyze feedback from multiple retrospectives</li>
            <li style="margin-bottom: 12px; font-size: 16px;"><strong>Seamless Integration:</strong> Connect with Azure DevOps and other tools</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="apple-card" style='background-color: rgba(30, 136, 229, 0.8); color: white; padding: 20px; border-radius: 15px; height: auto; backdrop-filter: blur(10px);'>
            <h3 style="font-size: 24px; margin-bottom: 15px;">Sprint Task Planner</h3>
            <p style="font-size: 16px; margin-bottom: 15px;">Plan and distribute tasks across sprints to optimize team capacity</p>
            <ul class="staggered-fade">
                <li style="margin-bottom: 8px;">Fair distribution of tasks based on priority</li>
                <li style="margin-bottom: 8px;">Optimal capacity utilization</li>
                <li style="margin-bottom: 8px;">Azure DevOps integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ Open Sprint Task Planner ✨", key="sprint-planner-btn"):
            st.session_state.current_app = "sprint_planner"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="apple-card" style='background-color: rgba(76, 175, 80, 0.8); color: white; padding: 20px; border-radius: 15px; height: auto; backdrop-filter: blur(10px);'>
            <h3 style="font-size: 24px; margin-bottom: 15px;">Retrospective Analysis Tool</h3>
            <p style="font-size: 16px; margin-bottom: 15px;">Consolidate and analyze feedback from team retrospectives</p>
            <ul class="staggered-fade">
                <li style="margin-bottom: 8px;">Process multiple retrospective files</li>
                <li style="margin-bottom: 8px;">Visualize feedback with vote counts</li>
                <li style="margin-bottom: 8px;">AI-powered insights</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ Open Retrospective Analysis ✨", key="retro-analysis-btn"):
            st.session_state.current_app = "retro_analysis"
            st.rerun()

def render_sprint_task_planner():
    # Apple-style animated header
    st.markdown("""
    <div class="animated-header">
        <div class="floating-container"></div>
        <h1 style="color: white; font-size: 48px; margin-bottom: 15px; text-align: center;">Sprint Task Planner</h1>
        <p style="color: white; font-size: 18px; text-align: center; animation: fadeInUp 1s 0.5s forwards; opacity: 0; line-height: 1.6;">
            Optimize your sprint planning with intelligent task distribution
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Description with Apple-style card
    st.markdown("""
    <div class="apple-card" style='background-color: rgba(30, 133, 148, 0.7); padding: 25px; border-radius: 20px; margin: 30px 0; backdrop-filter: blur(10px);'>
        <h3 style="margin-bottom: 15px; font-size: 22px;">Intelligent Sprint Planning</h3>
        <p style="margin-bottom: 20px; font-size: 16px; line-height: 1.6;">This application helps you plan and distribute tasks across multiple sprints with sophisticated algorithms, ensuring:</p>
        <ul class="staggered-fade" style="padding-left: 20px;">
            <li style="margin-bottom: 10px; animation-delay: 100ms;">Fair distribution of tasks with different priorities</li>
            <li style="margin-bottom: 10px; animation-delay: 300ms;">Optimal capacity utilization across team members</li>
            <li style="margin-bottom: 10px; animation-delay: 500ms;">Remaining capacity is carried forward between sprints</li>
            <li style="margin-bottom: 10px; animation-delay: 700ms;">Integration with Azure DevOps for task updates</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Create floating elements
    st.markdown("""
    <div class="floating-container">
        <div class="floating-element" style="width: 80px; height: 80px; left: 10%; top: 30%; background-color: rgba(30, 136, 229, 0.1); filter: blur(20px);"></div>
        <div class="floating-element" style="width: 120px; height: 120px; left: 80%; top: 20%; background-color: rgba(76, 175, 80, 0.1); filter: blur(30px);"></div>
        <div class="floating-element" style="width: 60px; height: 60px; left: 70%; top: 70%; background-color: rgba(156, 39, 176, 0.1); filter: blur(15px);"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create main tabs with Apple-style
    upload_tab, team_tab, assignment_tab, results_tab, azure_tab = st.tabs([
        "1. Upload Tasks", 
        "2. Configure Team", 
        "3. Sprint & Task Assignment", 
        "4. Results",
        "5. Azure DevOps"
    ])
    
    # 1. UPLOAD TASKS TAB
    with upload_tab:
        st.header("Upload Task Data")
        
        # File upload
        uploaded_file = st.file_uploader("Upload your CSV file with tasks", type=["csv"], key="task_file_uploader")
        
        if uploaded_file is not None:
            try:
                # Load data
                df = file_bytes = uploaded_file.read()
encoding, confidence = detect_encoding(file_bytes)
sample_text = file_bytes.decode(encoding, errors='replace')
delimiter = detect_delimiter(sample_text)
st.write(f"Detected Encoding: **{encoding}** (Confidence: {confidence:.2f})")
st.write(f"Detected Delimiter: **'{delimiter}'**")
pd.read_csv(io.StringIO(sample_text), encoding=encoding, sep=delimiter)
                
                # Preview data
                st.subheader("Data Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Check if required columns are present
                required_columns = ["ID", "Title", "Priority", "Original Estimates"]
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"Missing required columns: {', '.join(missing_columns)}")
                else:
                    # Process the data
                    # Filter out completed tasks
                    if "State" in df.columns:
                        df = df[df["State"].str.lower() != "done"]
                    
                    # Store the filtered data
                    st.session_state.df_tasks = df
                    
                    # Show some statistics
                    total_tasks = len(df)
                    
                    # Count priority levels
                    priority_counts = df["Priority"].value_counts().to_dict()
                    
                    # Calculate total estimate
                    total_estimate = df["Original Estimates"].sum()
                    
                    # Display stats in columns with Apple-style cards
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="apple-card pulse-card" style='background: linear-gradient(135deg, rgba(255, 215, 0, 0.8), rgba(255, 196, 0, 0.9)); padding: 20px; border-radius: 15px; animation-delay: 100ms;'>
                            <h4 style="font-size: 18px; margin-bottom: 10px; color: rgba(0,0,0,0.8);">Total Tasks</h4>
                            <p style="font-size: 24px; font-weight: 600; color: rgba(0,0,0,0.8);"><b>{total_tasks}</b> active tasks</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="apple-card pulse-card" style='background: linear-gradient(135deg, rgba(255, 165, 0, 0.8), rgba(255, 140, 0, 0.9)); padding: 20px; border-radius: 15px; animation-delay: 300ms;'>
                            <h4 style="font-size: 18px; margin-bottom: 10px; color: rgba(0,0,0,0.8);">Estimated Effort</h4>
                            <p style="font-size: 24px; font-weight: 600; color: rgba(0,0,0,0.8);"><b>{total_estimate:.1f}</b> hours</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        priority_html = "".join([f"<p style='margin-bottom: 5px;'>{k}: <b>{v}</b></p>" for k, v in priority_counts.items()])
                        st.markdown(f"""
                        <div class="apple-card pulse-card" style='background: linear-gradient(135deg, rgba(255, 255, 0, 0.8), rgba(240, 230, 0, 0.9)); padding: 20px; border-radius: 15px; animation-delay: 500ms;'>
                            <h4 style="font-size: 18px; margin-bottom: 10px; color: rgba(0,0,0,0.8);">Priority Breakdown</h4>
                            <div style="font-size: 16px; color: rgba(0,0,0,0.8);">{priority_html}</div>
                        </div>
                        """, unsafe_allow_html=True)
                     
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please make sure your CSV file has the required columns (ID, Title, Priority, Original Estimates)")
        else:
            st.info("Please upload a CSV file with your tasks data")
            
            # Sample structure explanation
            with st.expander("CSV Format Requirements"):
                st.markdown("""
                Your CSV file should include these columns:
                
                - **ID**: Unique identifier for the task
                - **Title**: Task title
                - **Priority**: Task priority (high, medium, low)
                - **Original Estimates**: Estimated hours required for the task
                - **State** (optional): Current state of the task
                """)
    
    # 2. TEAM CONFIGURATION TAB
    with team_tab:
        st.header("Configure Team Members")
        
        st.markdown("""
        <div class="apple-card" style='background: linear-gradient(135deg, rgba(30, 136, 229, 0.8), rgba(0, 100, 255, 0.9)); padding: 20px; border-radius: 15px; margin-bottom: 25px; color: white; backdrop-filter: blur(10px);'>
            <h3 style="margin-bottom: 10px; font-size: 20px;">Team Configuration</h3>
            <p style="font-size: 16px; line-height: 1.6;">Add team members and their available capacity for the entire project duration. Capacity represents the total available working hours for each team member.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Team member management
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Add new team member
            with st.form("add_member_form"):
                st.subheader("Add Team Member")
                
                new_member_name = st.text_input("Name")
                new_member_capacity = st.number_input("Capacity (hours)", min_value=1, value=40)
                
                submitted = st.form_submit_button("Add Team Member")
                if submitted and new_member_name:
                    st.session_state.team_members[new_member_name] = new_member_capacity
                    st.success(f"Added {new_member_name} with {new_member_capacity} hours capacity")
        
        with col2:
            # Quick add multiple team members
            with st.form("quick_add_form"):
                st.subheader("Quick Add Multiple Members")
                
                multiple_members = st.text_area(
                    "Enter one member per line with capacity in hours",
                    help="Format: Name,Capacity (e.g., John,40)",
                    placeholder="John,40\nJane,32\nBob,24"
                )
                
                submitted = st.form_submit_button("Add Multiple Members")
                if submitted and multiple_members:
                    lines = multiple_members.strip().split('\n')
                    for line in lines:
                        if ',' in line:
                            name, capacity = line.split(',', 1)
                            name = name.strip()
                            
                            try:
                                capacity = float(capacity.strip())
                                if name and capacity > 0:
                                    st.session_state.team_members[name] = capacity
                            except ValueError:
                                st.error(f"Invalid capacity for {name}. Skipping.")
                    
                    st.success(f"Added {len(lines)} team members")
        
        # Display current team
        if st.session_state.team_members:
            st.subheader("Current Team")
            
            # Create a DataFrame to display
            team_df = pd.DataFrame({
                "Name": list(st.session_state.team_members.keys()),
                "Capacity (hours)": list(st.session_state.team_members.values())
            })
            
            # Display team table
            st.dataframe(team_df, use_container_width=True)
            
            # Remove member option
            member_to_remove = st.selectbox("Select member to remove:", [""] + list(st.session_state.team_members.keys()))
            if st.button("Remove Selected Member") and member_to_remove:
                del st.session_state.team_members[member_to_remove]
                st.success(f"Removed {member_to_remove} from the team")
                st.rerun()
            
            # Clear all members
            if st.button("Clear All Members"):
                st.session_state.team_members = {}
                st.success("Team cleared")
                st.rerun()
        else:
            st.info("No team members added yet. Please add team members above.")
    
    # 3. SPRINT & TASK ASSIGNMENT TAB
    with assignment_tab:
        st.header("Sprint & Task Assignment")
        
        if st.session_state.df_tasks is None:
            st.warning("Please upload tasks data in the Upload Tasks tab first.")
        elif not st.session_state.team_members:
            st.warning("Please add team members in the Configure Team tab first.")
        else:
            st.markdown("""
            <div style='background-color: #1b5e20; padding: 15px; border-radius: 8px; margin-bottom: 20px; color: #e0e0e0;'>
                <h3 style='margin-top: 0;'>Sprint-Based Priority-Balanced Task Assignment</h3>
                <p>This algorithm distributes work to ensure team members get a fair mix of high, medium, and low priority tasks across multiple sprints.</p>
                <p>Every team member will receive tasks from all priority levels rather than one person getting all high-priority tasks.</p>
                <p>Remaining capacity from earlier sprints will be carried forward to subsequent sprints.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Sprint Configuration Section
            st.subheader("Sprint Configuration")
            
            # Default sprint duration in weeks
            sprint_duration = st.number_input(
                "Sprint Duration (weeks)",
                min_value=1,
                max_value=4,
                value=2,
                help="Duration of each sprint in weeks"
            )
            
            # Number of sprints
            num_sprints = st.number_input(
                "Number of Sprints",
                min_value=1,
                max_value=12,
                value=3,
                help="Number of sprints to plan for"
            )
            
            # Working days per week
            days_per_week = st.number_input(
                "Working Days per Week",
                min_value=1,
                max_value=7,
                value=5,
                help="Number of working days per week"
            )
            
            # Hours per day
            hours_per_day = st.number_input(
                "Working Hours per Day",
                min_value=1,
                max_value=24,
                value=8,
                help="Number of working hours per day"
            )
            
            # Calculate total hours per sprint
            # This will be used to adjust the team members' capacities for each sprint
            st.session_state.capacity_per_sprint = sprint_duration * days_per_week * hours_per_day
            
            # Let user know how many hours each sprint represents
            st.info(f"Each sprint represents {st.session_state.capacity_per_sprint} working hours per team member (assuming full capacity).")
            
            # Assignment Options
            st.subheader("Assignment Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                priority_balance = st.slider(
                    "Priority Balance",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.7,
                    step=0.1,
                    help="Higher values (0.7-1.0) ensure everyone gets a mix of high/medium/low tasks. Lower values focus more on capacity utilization. Default (0.7) gives a good balance."
                )
            
            with col2:
                respect_category = st.checkbox(
                    "Consider Category Specialization",
                    value=False,
                    help="When enabled, members will be assigned tasks from their specialized categories when possible"
                )
                
            # Assignment button
            if st.button("Run Assignment", type="primary", use_container_width=True):
                # Get the data
                df = st.session_state.df_tasks.copy()
                team_members = st.session_state.team_members
                
                # Check for required columns
                required_columns = ["Priority", "Original Estimates"]
                if not all(col in df.columns for col in required_columns):
                    st.error(f"CSV must contain these columns: {', '.join(required_columns)}")
                else:
                    with st.spinner("Assigning tasks across sprints..."):
                        # Prepare data
                        assigned_hours = {member: 0 for member in team_members}
                        assigned_priorities = {member: {"high": 0, "medium": 0, "low": 0, "other": 0} for member in team_members}
                        
                        # Add columns if missing or reset them
                        if "Assigned To" not in df.columns:
                            df["Assigned To"] = ""
                        else:
                            df["Assigned To"] = ""  # Reset assignments
                            
                        if "Iteration Path" not in df.columns:
                            df["Iteration Path"] = ""
                        else:
                            df["Iteration Path"] = ""  # Reset iteration paths
                        
                        if "Sprint" not in df.columns:
                            df["Sprint"] = ""
                        else:
                            df["Sprint"] = ""  # Reset sprint assignments
                        
                        # Define priority order and sort tasks
                        priority_order = {"high": 1, "medium": 2, "low": 3}
                        df["PriorityOrder"] = df["Priority"].str.lower().map(priority_order).fillna(4)
                        df = df.sort_values("PriorityOrder")  # Sort by priority
                        
                        # Calculate priorities distribution targets per member
                        priorities_list = ["high", "medium", "low", "other"]
                        priority_counts = {}
                        for priority in priorities_list:
                            if priority == "other":
                                count = len(df[~df["Priority"].str.lower().isin(["high", "medium", "low"])])
                            else:
                                count = len(df[df["Priority"].str.lower() == priority])
                            priority_counts[priority] = count
                        
                        # Calculate target distribution per member
                        member_count = len(team_members)
                        target_distribution = {
                            priority: max(1, round(count / member_count)) 
                            for priority, count in priority_counts.items() if count > 0
                        }
                        
                        # Create a more detailed info message about sprint planning
                        st.info(f"""
                        Planning {num_sprints} sprints with capacity of {st.session_state.capacity_per_sprint} hours per person per sprint.
                        Total capacity across all sprints: {num_sprints * st.session_state.capacity_per_sprint} hours per person.
                        
                        The algorithm will distribute tasks to ensure:
                        1. Team members get a fair mix of high, medium, and low priority tasks
                        2. Remaining capacity from each sprint is carried forward to the next sprint
                        3. High priority tasks are assigned first
                        """)
                        
                        # Initialize sprint-specific tracking data
                        sprint_assignments = {}
                        sprint_capacities = {}
                        members_sprint_capacity = {}
                        
                        # Set up tracking for each sprint
                        for sprint in range(1, num_sprints + 1):
                            sprint_name = f"Sprint {sprint}"
                            sprint_assignments[sprint_name] = []
                            sprint_capacities[sprint_name] = {member: 0 for member in team_members}
                        
                        # Initialize remaining capacity for each member based on their capacity percentage
                        # This tracks how much capacity is carried forward between sprints
                        remaining_capacity = {member: 0 for member in team_members}
                        
                        # Process each sprint
                        for sprint_num in range(1, num_sprints + 1):
                            sprint_name = f"Sprint {sprint_num}"
                            
                            # Calculate each member's capacity for this sprint
                            # Base capacity + any remaining capacity from previous sprint
                            for member, full_capacity in team_members.items():
                                # Calculate what percentage of full time this person is
                                capacity_percentage = full_capacity / (num_sprints * st.session_state.capacity_per_sprint)
                                # Capacity for this sprint is the percentage of the sprint's total hours + remaining from previous
                                members_sprint_capacity[member] = (capacity_percentage * st.session_state.capacity_per_sprint) + remaining_capacity[member]
                            
                            # For logging/debugging: show the capacity for each member in each sprint
                            capacity_summary = ", ".join([f"{m}: {c:.1f}h" for m, c in members_sprint_capacity.items()])
                            st.text(f"{sprint_name} - Available capacity: {capacity_summary}")
                            
                            # Create a copy of tasks that haven't been assigned yet
                            unassigned_tasks = df[df["Assigned To"] == ""].copy()
                            
                            # Skip if no tasks left to assign
                            if len(unassigned_tasks) == 0:
                                continue
                            
                            # Create priority task groups for this sprint
                            task_groups = {}
                            for priority in priorities_list:
                                if priority == "other":
                                    task_groups[priority] = unassigned_tasks[~unassigned_tasks["Priority"].str.lower().isin(["high", "medium", "low"])].copy()
                                else:
                                    task_groups[priority] = unassigned_tasks[unassigned_tasks["Priority"].str.lower() == priority].copy()
                                
                                # Sort by estimate within priority group (smaller tasks first for better distribution)
                                if len(task_groups[priority]) > 0:
                                    task_groups[priority] = task_groups[priority].sort_values("Original Estimates")
                            
                            # Track assigned priorities for this sprint
                            sprint_assigned_priorities = {member: {"high": 0, "medium": 0, "low": 0, "other": 0} for member in team_members}
                            
                            # First pass: ensure everyone gets a mix of priorities
                            available_priorities = [p for p in priorities_list if len(task_groups[p]) > 0]
                            current_priority_index = 0
                            cycle_count = 0
                            
                            while available_priorities and cycle_count < 100:  # Safety limit
                                cycle_count += 1
                                current_priority = available_priorities[current_priority_index]
                                
                                if len(task_groups[current_priority]) == 0:
                                    # No more tasks of this priority
                                    available_priorities.pop(current_priority_index)
                                    if not available_priorities:
                                        break
                                    current_priority_index = current_priority_index % len(available_priorities)
                                    continue
                                
                                # Sort members by who has the least of this priority in this sprint and most remaining capacity
                                members_sorted = sorted(
                                    team_members.keys(),
                                    key=lambda m: (
                                        sprint_assigned_priorities[m][current_priority],
                                        assigned_priorities[m][current_priority],  # Consider overall assignments too
                                        -members_sprint_capacity[m]  # Negated so higher capacity is first
                                    )
                                )
                                
                                # Try to assign to first member with capacity
                                task_assigned = False
                                for member in members_sorted:
                                    # If no capacity left in this sprint for this member, skip
                                    if members_sprint_capacity[member] <= 0:
                                        continue
                                        
                                    # Try to find a task that fits the member's remaining sprint capacity
                                    for idx in task_groups[current_priority].index:
                                        task = task_groups[current_priority].loc[idx]
                                        estimate = task["Original Estimates"]
                                        
                                        if pd.isna(estimate) or estimate <= 0:
                                            continue
                                            
                                        if estimate <= members_sprint_capacity[member]:
                                            task_id = task["ID"]
                                            
                                            # Assign in the original dataframe
                                            df.loc[df["ID"] == task_id, "Assigned To"] = member
                                            df.loc[df["ID"] == task_id, "Sprint"] = sprint_name
                                            df.loc[df["ID"] == task_id, "Iteration Path"] = f"/{sprint_name}/{current_priority}"
                                            
                                            # Update member statistics (both sprint-specific and overall)
                                            members_sprint_capacity[member] -= estimate
                                            sprint_capacities[sprint_name][member] += estimate
                                            assigned_hours[member] += estimate
                                            
                                            # Update priority counts
                                            sprint_assigned_priorities[member][current_priority] += 1
                                            assigned_priorities[member][current_priority] += 1
                                            
                                            # Add to sprint assignments
                                            sprint_assignments[sprint_name].append(task_id)
                                            
                                            # Remove task from the group
                                            task_groups[current_priority] = task_groups[current_priority].drop(idx)
                                            
                                            task_assigned = True
                                            break
                                    
                                    if task_assigned:
                                        break
                                
                                # If no task assigned this round, move to next priority
                                current_priority_index = (current_priority_index + 1) % len(available_priorities)
                                
                                # If we've gone through all priorities and can't assign any more, break
                                if not task_assigned and current_priority_index == 0:
                                    break
                            
                            # Second pass - assign remaining tasks with balanced approach
                            for priority_level in priorities_list:
                                remaining_tasks = task_groups[priority_level]
                                
                                if len(remaining_tasks) == 0:
                                    continue
                                    
                                for idx in remaining_tasks.index:
                                    task = remaining_tasks.loc[idx]
                                    task_id = task["ID"]
                                    estimate = task["Original Estimates"]
                                    
                                    if pd.isna(estimate) or estimate <= 0:
                                        continue
                                    
                                    # Sort members by who has the least of this priority and most remaining capacity
                                    shuffled_members = sorted(
                                        team_members.keys(),
                                        key=lambda m: (
                                            sprint_assigned_priorities[m][priority_level],
                                            -members_sprint_capacity[m]  # Negated so higher capacity is first
                                        )
                                    )
                                    
                                    # Try to assign to the best-fit member with capacity
                                    for member in shuffled_members:
                                        if members_sprint_capacity[member] <= 0:
                                            continue
                                            
                                        if estimate <= members_sprint_capacity[member]:
                                            # Assign in the original dataframe
                                            df.loc[df["ID"] == task_id, "Assigned To"] = member
                                            df.loc[df["ID"] == task_id, "Sprint"] = sprint_name
                                            df.loc[df["ID"] == task_id, "Iteration Path"] = f"/{sprint_name}/{priority_level}"
                                            
                                            # Update member statistics
                                            members_sprint_capacity[member] -= estimate
                                            sprint_capacities[sprint_name][member] += estimate
                                            assigned_hours[member] += estimate
                                            
                                            # Update priority counts
                                            sprint_assigned_priorities[member][priority_level] += 1
                                            assigned_priorities[member][priority_level] += 1
                                            
                                            # Add to sprint assignments
                                            sprint_assignments[sprint_name].append(task_id)
                                            break
                            
                            # At the end of the sprint, update the remaining capacity that gets carried forward
                            for member in team_members:
                                remaining_capacity[member] = members_sprint_capacity[member]
                                
                            # Log how much capacity is being carried forward
                            remaining_summary = ", ".join([f"{m}: {c:.1f}h" for m, c in remaining_capacity.items()])
                            st.text(f"{sprint_name} - Remaining capacity carried forward: {remaining_summary}")
                        
                        # Clean up
                        if "PriorityOrder" in df.columns:
                            df = df.drop(columns=["PriorityOrder"])
                        
                        # Store results with sprint data
                        st.session_state.results = {
                            "df": df,
                            "assigned_hours": assigned_hours,
                            "assigned_priorities": assigned_priorities,
                            "team_members": team_members,
                            "sprint_data": {
                                "sprint_assignments": sprint_assignments,
                                "sprint_capacities": sprint_capacities,
                                "num_sprints": num_sprints
                            }
                        }
                        
                        # Switch to results tab
                        st.success("Tasks assigned successfully across sprints! See the Results tab for sprint-by-sprint details.")
    with results_tab:
        st.header("Assignment Results")
        
        if st.session_state.results is None:
            st.warning("No assignment results available. Please run the assignment algorithm first.")
        else:
            results = st.session_state.results
            df = results["df"]
            assigned_hours = results["assigned_hours"]
            assigned_priorities = results["assigned_priorities"]
            team_members = results["team_members"]
            
            # Assignment summary
            st.subheader("Summary")
            
            total_assigned = sum(assigned_hours.values())
            total_capacity = sum(team_members.values())
            percent_utilized = (total_assigned / total_capacity * 100) if total_capacity > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Tasks Assigned", len(df[df["Assigned To"] != ""]))
                
            with col2:
                st.metric("Hours Assigned", f"{total_assigned:.1f}/{total_capacity:.1f}")
                
            with col3:
                st.metric("Capacity Utilized", f"{percent_utilized:.1f}%")
                
            # Detailed results
            st.subheader("Assigned Tasks")
            st.dataframe(
                df,
                column_config={
                    "Priority": st.column_config.Column(
                        "Priority",
                        help="Task priority level",
                        width="medium",
                    ),
                    "Original Estimates": st.column_config.NumberColumn(
                        "Hours",
                        help="Estimated work hours",
                        format="%.1f",
                    ),
                    "Assigned To": st.column_config.Column(
                        "Assigned To",
                        help="Team member assigned to the task",
                        width="medium",
                    ),
                    "Sprint": st.column_config.Column(
                        "Sprint",
                        help="Sprint assignment",
                        width="medium",
                    ),
                },
                use_container_width=True
            )
            
            # Visualizations
            st.subheader("Capacity Utilization")
            
            # Prepare data for visualization
            members = list(team_members.keys())
            capacities = [team_members[m] for m in members]
            used_capacities = [assigned_hours[m] for m in members]
            remaining_capacities = [capacities[i] - used_capacities[i] for i in range(len(members))]
            
            # Create capacity chart with dark theme
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(10, 5))
            bar_width = 0.35
            x = np.arange(len(members))
            
            # Use more vibrant colors for dark theme
            ax.bar(x, used_capacities, bar_width, label='Used', color='#81c784')
            ax.bar(x, remaining_capacities, bar_width, bottom=used_capacities, label='Remaining', color='#455a64')
            
            ax.set_ylabel('Hours', color='#e0e0e0')
            ax.set_title('Overall Capacity Utilization by Team Member', color='#81c784')
            ax.set_xticks(x)
            ax.set_xticklabels(members, rotation=45, ha='right', color='#e0e0e0')
            ax.tick_params(axis='y', colors='#e0e0e0')
            ax.spines['bottom'].set_color('#555555')
            ax.spines['top'].set_color('#555555')
            ax.spines['left'].set_color('#555555')
            ax.spines['right'].set_color('#555555')
            ax.grid(color='#333333', linestyle='-', linewidth=0.5, alpha=0.7)
            ax.legend(facecolor='#2d2d2d', edgecolor='#555555', labelcolor='#e0e0e0')
            
            fig.patch.set_facecolor('#1e1e1e')
            plt.tight_layout()
            st.pyplot(fig)
            
            # Priority distribution
            st.subheader("Priority Distribution")
            
            # Prepare data for priority chart
            priorities = ["high", "medium", "low", "other"]
            priority_data = {member: [assigned_priorities[member].get(p, 0) for p in priorities] for member in members}
            
            # Create stacked bar chart with dark theme
            # We're already using dark_background style from the previous chart
            fig, ax = plt.subplots(figsize=(10, 5))
            bottom = np.zeros(len(members))
            
            # Enhanced colors for better visibility on dark background
            colors = {'high': '#ef5350', 'medium': '#ffb74d', 'low': '#81c784', 'other': '#b0bec5'}
            
            for i, priority in enumerate(priorities):
                priority_counts = [priority_data[member][i] for member in members]
                ax.bar(members, priority_counts, bottom=bottom, label=priority.capitalize(), color=colors[priority])
                bottom += priority_counts
            
            ax.set_ylabel('Number of Tasks', color='#e0e0e0')
            ax.set_title('Overall Priority Distribution by Team Member', color='#81c784')
            ax.set_xticks(range(len(members)))
            ax.set_xticklabels(members, rotation=45, ha='right', color='#e0e0e0')
            ax.tick_params(axis='y', colors='#e0e0e0')
            ax.spines['bottom'].set_color('#555555')
            ax.spines['top'].set_color('#555555')
            ax.spines['left'].set_color('#555555')
            ax.spines['right'].set_color('#555555')
            ax.grid(color='#333333', linestyle='-', linewidth=0.5, alpha=0.7)
            ax.legend(facecolor='#2d2d2d', edgecolor='#555555', labelcolor='#e0e0e0')
            
            fig.patch.set_facecolor('#1e1e1e')
            plt.tight_layout()
            st.pyplot(fig)
            
            # Add detailed priority distribution as tables
            st.subheader("Detailed Priority Mix by Team Member")
            st.write("This table shows exactly how many tasks of each priority level were assigned to each team member:")
            
            # Create a dataframe showing the priority distribution
            priority_df = pd.DataFrame(assigned_priorities).T
            priority_df.index.name = "Team Member"
            priority_df.columns = [col.capitalize() for col in priority_df.columns]
            
            # Add percentage columns to show proportion of each priority
            for member in priority_df.index:
                total = priority_df.loc[member].sum()
                if total > 0:
                    for col in priority_df.columns:
                        priority_df.loc[member, f"{col} %"] = round(priority_df.loc[member, col] / total * 100, 1)
                else:
                    for col in priority_df.columns:
                        priority_df.loc[member, f"{col} %"] = 0.0
            
            # Display the dataframe
            st.dataframe(priority_df, use_container_width=True)
            
            # Add a color legend explaining the priority levels
            st.markdown("""
            <div style="margin-top: 10px; padding: 10px; background-color: #2d2d2d; border-radius: 5px;">
                <h4 style="color: #e0e0e0;">Priority Legend</h4>
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                    <div style="display: flex; align-items: center;">
                        <div style="width: 20px; height: 20px; background-color: #ef5350; margin-right: 5px;"></div>
                        <span style="color: #e0e0e0;">High</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 20px; height: 20px; background-color: #ffb74d; margin-right: 5px;"></div>
                        <span style="color: #e0e0e0;">Medium</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 20px; height: 20px; background-color: #81c784; margin-right: 5px;"></div>
                        <span style="color: #e0e0e0;">Low</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 20px; height: 20px; background-color: #b0bec5; margin-right: 5px;"></div>
                        <span style="color: #e0e0e0;">Other</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Check if we have sprint data and display it
            if "sprint_data" in results:
                sprint_data = results["sprint_data"]
                num_sprints = sprint_data["num_sprints"]
                sprint_assignments = sprint_data["sprint_assignments"]
                sprint_capacities = sprint_data["sprint_capacities"]
                
                st.header("Sprint Planning")
                st.markdown("""
                <div style="background-color: #1e3f20; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                    <p style="color: #e0e0e0; margin: 0;">
                        Tasks are distributed across sprints with remaining capacity carried forward. 
                        Each sprint balances priority distribution while respecting capacity constraints.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create sprint tabs for detailed view
                sprint_tabs = st.tabs([f"Sprint {i}" for i in range(1, num_sprints + 1)])
                
                for i, sprint_tab in enumerate(sprint_tabs):
                    sprint_name = f"Sprint {i+1}"
                    
                    with sprint_tab:
                        st.subheader(f"{sprint_name} Assignments")
                        
                        # Sprint Statistics
                        sprint_tasks = df[df["Sprint"] == sprint_name]
                        
                        if len(sprint_tasks) == 0:
                            st.info(f"No tasks assigned to {sprint_name}.")
                            continue
                        
                        # Display key metrics for this sprint
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Tasks", len(sprint_tasks))
                        
                        with col2:
                            sprint_hours = sum(sprint_capacities[sprint_name].values())
                            st.metric("Hours", f"{sprint_hours:.1f}")
                        
                        with col3:
                            # Calculate how much capacity was utilized in this sprint
                            total_sprint_capacity = sum([team_members[m] / num_sprints for m in team_members])
                            sprint_percent = (sprint_hours / total_sprint_capacity * 100) if total_sprint_capacity > 0 else 0
                            st.metric("Sprint Capacity Used", f"{sprint_percent:.1f}%")
                        
                        # Tasks assigned to this sprint
                        st.subheader("Tasks")
                        st.dataframe(
                            sprint_tasks,
                            column_config={
                                "Priority": st.column_config.Column(
                                    "Priority",
                                    help="Task priority level",
                                    width="medium"
                                ),
                                "Original Estimates": st.column_config.NumberColumn(
                                    "Hours",
                                    help="Estimated work hours",
                                    format="%.1f"
                                ),
                                "Assigned To": st.column_config.Column(
                                    "Assigned To",
                                    help="Team member assigned to the task",
                                    width="medium"
                                )
                            },
                            use_container_width=True
                        )
                        
                        # Create visualization of capacity used in this sprint
                        st.subheader("Sprint Capacity")
                        
                        # Prepare data
                        members = list(team_members.keys())
                        sprint_used = [sprint_capacities[sprint_name].get(m, 0) for m in members]
                        
                        # Calculate carried over capacity from previous sprint
                        carried_over = []
                        if i > 0:
                            prev_sprint = f"Sprint {i}"
                            for m in members:
                                member_capacity = team_members[m] / num_sprints  # Base capacity per sprint
                                used_in_prev = sprint_capacities[prev_sprint].get(m, 0)
                                carried = max(0, member_capacity - used_in_prev)
                                carried_over.append(carried)
                        else:
                            carried_over = [0] * len(members)
                        
                        # Create sprint capacity chart
                        plt.style.use('dark_background')
                        fig, ax = plt.subplots(figsize=(10, 5))
                        bar_width = 0.35
                        x = np.arange(len(members))
                        
                        # Member's standard capacity for this sprint
                        standard_capacity = [team_members[m] / num_sprints for m in members]
                        
                        # Visualize standard capacity, carried over capacity, and used capacity
                        ax.bar(x, standard_capacity, bar_width, label='Standard Capacity', color='#455a64', alpha=0.6)
                        if any(c > 0 for c in carried_over):
                            ax.bar(x, carried_over, bar_width, bottom=standard_capacity, label='Carried Over', color='#5c6bc0')
                        ax.bar(x, sprint_used, bar_width/1.5, label='Used', color='#81c784')
                        
                        # Styling
                        ax.set_ylabel('Hours', color='#e0e0e0')
                        ax.set_title(f'{sprint_name} Capacity Utilization', color='#81c784')
                        ax.set_xticks(x)
                        ax.set_xticklabels(members, rotation=45, ha='right', color='#e0e0e0')
                        ax.tick_params(axis='y', colors='#e0e0e0')
                        ax.spines['bottom'].set_color('#555555')
                        ax.spines['top'].set_color('#555555')
                        ax.spines['left'].set_color('#555555')
                        ax.spines['right'].set_color('#555555')
                        ax.grid(color='#333333', linestyle='-', linewidth=0.5, alpha=0.7)
                        ax.legend(facecolor='#2d2d2d', edgecolor='#555555', labelcolor='#e0e0e0')
                        
                        fig.patch.set_facecolor('#1e1e1e')
                        plt.tight_layout()
                        st.pyplot(fig)
                        
                        # Create priority breakdown for this sprint
                        st.subheader("Sprint Priority Distribution")
                        
                        # Get priority distribution for this sprint
                        sprint_priority_counts = {}
                        for member in members:
                            sprint_priority_counts[member] = {"high": 0, "medium": 0, "low": 0, "other": 0}
                        
                        for _, task in sprint_tasks.iterrows():
                            member = task["Assigned To"]
                            priority = task["Priority"].lower()
                            if priority not in ["high", "medium", "low"]:
                                priority = "other"
                            sprint_priority_counts[member][priority] += 1
                        
                        # Create stacked bar chart for sprint priority distribution
                        priority_data = {m: [sprint_priority_counts[m].get(p, 0) for p in priorities] for m in members}
                        
                        fig, ax = plt.subplots(figsize=(10, 5))
                        bottom = np.zeros(len(members))
                        
                        for i, priority in enumerate(priorities):
                            priority_counts = [priority_data[member][i] for member in members]
                            ax.bar(members, priority_counts, bottom=bottom, label=priority.capitalize(), color=colors[priority])
                            bottom += priority_counts
                        
                        ax.set_ylabel('Number of Tasks', color='#e0e0e0')
                        ax.set_title(f'{sprint_name} Priority Distribution', color='#81c784')
                        ax.set_xticks(range(len(members)))
                        ax.set_xticklabels(members, rotation=45, ha='right', color='#e0e0e0')
                        ax.tick_params(axis='y', colors='#e0e0e0')
                        ax.spines['bottom'].set_color('#555555')
                        ax.spines['top'].set_color('#555555')
                        ax.spines['left'].set_color('#555555')
                        ax.spines['right'].set_color('#555555')
                        ax.grid(color='#333333', linestyle='-', linewidth=0.5, alpha=0.7)
                        ax.legend(facecolor='#2d2d2d', edgecolor='#555555', labelcolor='#e0e0e0')
                        
                        fig.patch.set_facecolor('#1e1e1e')
                        plt.tight_layout()
                        st.pyplot(fig)
                
                # Create a Gantt chart visualization of tasks across sprints
                st.header("Sprint Timeline")
                
                # Prepare data for Gantt chart
                gantt_data = []
                for _, task in df.iterrows():
                    if task["Assigned To"] and task["Sprint"]:
                        sprint_num = int(task["Sprint"].split(" ")[1])
                        gantt_data.append({
                            "Task": f"{task['ID']}: {task['Title']}",
                            "Start": sprint_num,
                            "Duration": 1,  # Each task takes 1 sprint
                            "Member": task["Assigned To"],
                            "Priority": task["Priority"]
                        })
                
                if gantt_data:
                    # Convert to DataFrame for easier plotting
                    gantt_df = pd.DataFrame(gantt_data)
                    
                    # Sort by Member and Sprint
                    gantt_df = gantt_df.sort_values(["Member", "Start"])
                    
                    # Create figure and axes - adjust height based on task count
                    max_height = max(8, min(20, len(gantt_df) * 0.3))  # Limit max height 
                    fig, ax = plt.subplots(figsize=(12, max_height))
                    
                    # Plot each task as a horizontal bar
                    y_pos = np.arange(len(gantt_df))
                    
                    # Use colors based on priority
                    task_colors = [colors.get(task["Priority"].lower(), colors.get("other")) for _, task in gantt_df.iterrows()]
                    
                    # Plot bars
                    ax.barh(y_pos, gantt_df["Duration"], left=gantt_df["Start"], color=task_colors, alpha=0.9)
                    
                    # Add vertical lines for sprint boundaries
                    for sprint in range(1, num_sprints + 1):
                        ax.axvline(sprint, color='white', linestyle='--', alpha=0.3)
                    
                    # Set y-axis labels to task names
                    ax.set_yticks(y_pos)
                    ax.set_yticklabels(gantt_df["Task"], fontsize=8, color='#e0e0e0')
                    
                    # Set x-axis labels to sprint numbers
                    ax.set_xticks(range(1, num_sprints + 2))
                    ax.set_xticklabels([f"Sprint {i}" for i in range(1, num_sprints + 2)], color='#e0e0e0')
                    
                    # Add member name annotations
                    for i, (_, task) in enumerate(gantt_df.iterrows()):
                        ax.text(task["Start"] + 0.5, i, task["Member"], 
                            ha='center', va='center', color='#1e1e1e', fontweight='bold')
                    
                    # Add labels
                    ax.set_xlabel('Sprints', color='#e0e0e0')
                    ax.set_title('Task Timeline Across Sprints', color='#81c784')
                    
                    # Style the chart
                    ax.tick_params(axis='x', colors='#e0e0e0')
                    ax.spines['bottom'].set_color('#555555')
                    ax.spines['top'].set_color('#555555')
                    ax.spines['left'].set_color('#555555')
                    ax.spines['right'].set_color('#555555')
                    ax.grid(color='#333333', linestyle='-', linewidth=0.5, alpha=0.7)
                    
                    fig.patch.set_facecolor('#1e1e1e')
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.info("No tasks have been assigned to sprints yet.")
            
            # Download options
            st.subheader("Export Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(get_download_link(df, "Task_Assignments.xlsx", "excel"), unsafe_allow_html=True)
                
            with col2:
                st.markdown(get_download_link(df, "Task_Assignments.csv", "csv"), unsafe_allow_html=True)

    
    
    
    
    
    # 5. AZURE DEVOPS INTEGRATION TAB
    with azure_tab:
        st.header("Azure DevOps Integration")
        
        # Display current connection status
        if st.session_state.azure_config["connected"]:
            st.success(f"Connected to Azure DevOps: {st.session_state.azure_config['org_url']}/{st.session_state.azure_config['project']}")
        else:
            st.info("Not connected to Azure DevOps. Configure connection below.")
        
        # Connection configuration
        with st.expander("Azure DevOps Connection", expanded=not st.session_state.azure_config["connected"]):
            st.subheader("Configure Connection")
            
            # Azure DevOps connection form
            with st.form("azure_connection_form"):
                st.markdown("""
                <div class="azure-section">
                    Enter your Azure DevOps organization and authentication details.
                    Use service principal authentication for automated access.
                </div>
                """, unsafe_allow_html=True)
                
                org_url = st.text_input("Organization URL (e.g., https://dev.azure.com/yourorg)", st.session_state.azure_config["org_url"])
                project = st.text_input("Project Name", st.session_state.azure_config["project"])
                team = st.text_input("Team Name", st.session_state.azure_config["team"])
                
                # Authentication options
                auth_tab1, auth_tab2 = st.tabs(["Service Principal", "PAT Token"])
                
                with auth_tab1:
                    client_id = st.text_input("Client ID", type="password")
                    client_secret = st.text_input("Client Secret", type="password")
                    tenant_id = st.text_input("Tenant ID", type="password")
                    auth_method = "service_principal"
                
                with auth_tab2:
                    pat_token = st.text_input("Personal Access Token (PAT)", type="password")
                    auth_method = "pat"
                
                submitted = st.form_submit_button("Connect to Azure DevOps")
                if submitted:
                    try:
                        if auth_method == "service_principal":
                            if not (client_id and client_secret and tenant_id):
                                st.error("Please provide all Service Principal authentication details")
                            else:
                                access_token = get_azure_access_token(client_id, client_secret, tenant_id)
                                if access_token:
                                    st.session_state.azure_config = {
                                        "org_url": org_url,
                                        "project": project,
                                        "team": team,
                                        "access_token": access_token,
                                        "connected": True
                                    }
                                    st.success("Successfully connected to Azure DevOps!")
                                else:
                                    st.error("Failed to authenticate with Azure DevOps. Check your credentials.")
                        elif auth_method == "pat":
                            if not pat_token:
                                st.error("Please provide a Personal Access Token")
                            else:
                                # For PAT, we just store it as the access token
                                st.session_state.azure_config = {
                                    "org_url": org_url,
                                    "project": project,
                                    "team": team,
                                    "access_token": pat_token,
                                    "connected": True
                                }
                                st.success("Successfully connected to Azure DevOps with PAT!")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
        
        # Import & Export functionality
        if st.session_state.azure_config["connected"]:
            st.subheader("Azure DevOps Actions")
            
            azure_col1, azure_col2 = st.columns(2)
            
            with azure_col1:
                # Import tasks from Azure DevOps
                st.markdown("### Import Tasks")
                
                if st.button("Import Tasks from Current Iteration"):
                    with st.spinner("Fetching tasks from Azure DevOps..."):
                        try:
                            df_tasks = get_azure_devops_tasks(
                                st.session_state.azure_config["org_url"],
                                st.session_state.azure_config["project"],
                                st.session_state.azure_config["team"],
                                st.session_state.azure_config["access_token"]
                            )
                            
                            if df_tasks is not None and not df_tasks.empty:
                                st.session_state.df_tasks = df_tasks
                                st.success(f"Successfully imported {len(df_tasks)} tasks from Azure DevOps!")
                            else:
                                st.error("No tasks found or failed to import.")
                        except Exception as e:
                            st.error(f"Import error: {str(e)}")
            
            with azure_col2:
                # Update task assignments in Azure DevOps
                st.markdown("### Update Task Assignments")
                
                if not st.session_state.results:
                    st.info("Please run sprint planning in the 'Sprint & Task Assignment' tab first.")
                else:
                    if st.button("Update Task Assignments in Azure DevOps"):
                        with st.spinner("Updating tasks in Azure DevOps..."):
                            try:
                                # Prepare updates for Azure DevOps
                                updates = []
                                
                                for task_id, assignment in st.session_state.results["assignments"].items():
                                    updates.append({
                                        "id": task_id,
                                        "fields": {
                                            "System.AssignedTo": assignment["assigned_to"]
                                            # Other fields can be updated here as needed
                                        }
                                    })
                                
                                if updates:
                                    results = update_azure_devops_tasks(
                                        st.session_state.azure_config["org_url"],
                                        st.session_state.azure_config["project"],
                                        st.session_state.azure_config["access_token"],
                                        updates
                                    )
                                    
                                    st.success(f"Successfully updated {len(updates)} tasks in Azure DevOps!")
                                else:
                                    st.warning("No task assignments to update.")
                            except Exception as e:
                                st.error(f"Update error: {str(e)}")
        else:
            st.info("Connect to Azure DevOps to import tasks or update assignments")
    ai_tab = st.tabs(["6. AI Suggestions"])[0]

    with ai_tab:
        st.header("AI Suggestions and Insights")
        st.markdown("Powered by OpenRouter + OpenAI")

        if "ai_messages" not in st.session_state:
            st.session_state.ai_messages = [
                {"role": "assistant", "content": "Hello! I'm your sprint planning assistant. How can I help you with your task assignments today?"}
            ]

        for message in st.session_state.ai_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        api_key = st.text_input("OpenRouter API Key", type="password", key="ai_api_key")

        if st.session_state.df_tasks is None:
            st.info("Please upload task data in the Upload Tasks tab first.")
            st.stop()

        df = st.session_state.df_tasks.copy()

        # 🔍 Extract component expertise from the task file
        expertise_col_member = "Unnamed: 15"
        expertise_col_comp = "Unnamed: 16"
        component_col = None

        if expertise_col_member in df.columns and expertise_col_comp in df.columns:
            expertise_map = df[[expertise_col_member, expertise_col_comp]].dropna()
            expertise_map.columns = ["Member", "Expertise"]
            expertise_dict = expertise_map.set_index("Member")["Expertise"].to_dict()
        else:
            expertise_dict = {}

        # 📦 Extract component name from Title (e.g., "Comp1: something")
        if "Title" in df.columns:
            df["Component"] = df["Title"].str.extract(r"(Comp\d+)", expand=False)

        # 🧠 Analyze mismatches
        df["Assigned To"] = df["Assigned To"].fillna("").str.strip()
        df["Mismatch"] = df.apply(
            lambda row: (
                row["Assigned To"] in expertise_dict and
                pd.notna(row["Component"]) and
                expertise_dict[row["Assigned To"]] != row["Component"]
            ),
            axis=1
        )
        mismatches = df[df["Mismatch"]]

        # 📬 User input
        prompt = st.chat_input("Ask about your sprint plan or say 'fix component mismatches'...")

        if prompt:
            st.session_state.ai_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # If user wants to fix mismatches
            if "fix" in prompt.lower() and "mismatch" in prompt.lower():
                with st.chat_message("assistant"):
                    st.success("Fixing tasks by component expertise...")
                    reassigned = 0
                    for idx, row in mismatches.iterrows():
                        correct_member = next((m for m, c in expertise_dict.items() if c == row["Component"]), None)
                        if correct_member:
                            df.at[idx, "Assigned To"] = correct_member
                            reassigned += 1

                    st.success(f"Reassigned {reassigned} mismatched tasks.")
                    st.dataframe(df[["ID", "Title", "Component", "Assigned To"]], use_container_width=True)

                    st.session_state.df_tasks = df  # Save back corrected

                    st.session_state.ai_messages.append({
                        "role": "assistant",
                        "content": f"I found and reassigned {reassigned} tasks to match component expertise."
                    })

            else:
                # 🧠 AI Context
                context = f"""You are an expert sprint planning assistant.

    There are {len(df)} tasks. Component expertise is as follows:\n"""
                for m, c in expertise_dict.items():
                    context += f"- {m} specializes in {c}\n"

                if not mismatches.empty:
                    context += "\n⚠️ Detected mismatches:\n"
                    for _, row in mismatches.iterrows():
                        context += f"- Task '{row['Title']}' assigned to {row['Assigned To']} but it's {row['Component']}\n"

                context += f"\nUser prompt: {prompt}"

                # 🔁 Stream response from OpenRouter
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""

                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "HTTP-Referer": "https://localhost",
                        "Content-Type": "application/json"
                    }

                    body = {
                        "model": "openai/gpt-3.5-turbo",
                        "messages": [{"role": "system", "content": context}] +
                                    [msg for msg in st.session_state.ai_messages if msg["role"] != "assistant"],
                        "temperature": 0.7,
                        "max_tokens": 1500,
                        "stream": True
                    }

                    try:
                        with requests.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers=headers,
                            json=body,
                            stream=True
                        ) as response:
                            if response.status_code == 200:
                                for chunk in response.iter_lines():
                                    if chunk:
                                        chunk_str = chunk.decode('utf-8')
                                        if chunk_str.startswith("data:"):
                                            try:
                                                data = json.loads(chunk_str[5:])
                                                if "choices" in data and data["choices"]:
                                                    delta = data["choices"][0].get("delta", {})
                                                    if "content" in delta:
                                                        full_response += delta["content"]
                                                        message_placeholder.markdown(full_response + "▌")
                                            except json.JSONDecodeError:
                                                continue
                            else:
                                full_response = f"Error: {response.status_code} - {response.text}"
                    except Exception as e:
                        full_response = f"An error occurred: {str(e)}"

                    message_placeholder.markdown(full_response)
                    st.session_state.ai_messages.append({"role": "assistant", "content": full_response})

def render_retrospective_analysis():
    st.markdown("""
    <div class="animated-header">
        <div class="floating-container"></div>
        <h1 style="color: white; font-size: 48px; margin-bottom: 15px; text-align: center;">RetroSpective Analysis Tool</h1>
        <p style="color: white; font-size: 18px; text-align: center; animation: fadeInUp 1s 0.5s forwards; opacity: 0; line-height: 1.6;">
        A Tool for Analysis of feedback from Team Retrospectives   
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("Upload multiple retrospective CSV files to analyze and compare feedback across team retrospectives.")
    
    # Sidebar for file upload and filtering controls
    with st.sidebar:
        st.header("Controls")
        
        uploaded_files = st.file_uploader(
            "Upload Retrospective CSV Files",
            type=["csv"],
            accept_multiple_files=True,
            help="Upload one or more CSV files containing retrospective data",
            key="retro_upload"
        )
        
        st.subheader("Filter Settings")
        min_votes = st.slider("Minimum Votes", 0, 100, 1, key="retro_min_votes")
        max_votes = st.slider("Maximum Votes", min_votes, 100, 50, key="retro_max_votes")
        
        if uploaded_files:
            st.info(f"Selected {len(uploaded_files)} file(s)")
        else:
            st.warning("Please upload at least one CSV file")
    
    # Main content area
    if not uploaded_files:
        st.info("👈 Please upload retrospective CSV files using the sidebar to begin analysis")
        
        # Show example of expected format
        st.subheader("Expected CSV Format")
        st.markdown(""" 
        Your CSV files should include columns for feedback description and votes, with format like:
        ```
        Type,Description,Votes
        Went Well,The team was collaborative,5
        Needs Improvement,Documentation is lacking,3
        ```
        
        The tool will also recognize associated tasks when formatted as:
        ```
        Feedback Description,Work Item Title,Work Item Type,Work Item Id,
        Documentation is lacking,Improve Docs,Task,12345
        ```
        """)
        
    else:
        # Process the uploaded files when the analyze button is clicked
        analyze_button = st.button("Analyze Retrospectives", type="primary")
        
        if analyze_button:
            with st.spinner("Processing retrospective data..."):
                feedback_results, processing_logs = compare_retrospectives(
                    uploaded_files, min_votes, max_votes
                )
                
                # Save results to session state for later use in the AI assistant
                st.session_state.retro_feedback = feedback_results
                
                # Show processing results
                with st.expander("Processing Logs", expanded=True):
                    for log in processing_logs:
                        st.write(log)
                
                # Convert to DataFrame for easier handling
                results_df = create_dataframe_from_results(feedback_results)
                
                if len(results_df) == 0 or (len(results_df) == 1 and "No valid feedback found" in results_df["Feedback"].iloc[0]):
                    st.error("No feedback items found within the selected vote range. Try adjusting your filters.")
                else:
                    # Display the results
                    st.subheader(f"Consolidated Feedback ({len(results_df)} items)")
                    st.dataframe(
                        results_df,
                        column_config={
                            "Feedback": st.column_config.TextColumn("Feedback"),
                            "Task ID": st.column_config.TextColumn("Task ID"),
                            "Votes": st.column_config.NumberColumn("Votes")
                        },
                        use_container_width=True
                    )
                    
                    # Visualization section
                    st.subheader("Feedback Visualization")
                    
                    # Only show top 15 items in chart to avoid overcrowding
                    chart_data = results_df.head(15) if len(results_df) > 15 else results_df
                    
                    # Create a horizontal bar chart with Plotly
                    fig = px.bar(
                        chart_data,
                        x="Votes",
                        y="Feedback",
                        orientation='h',
                        title=f"Top Feedback Items by Vote Count (min: {min_votes}, max: {max_votes})",
                        color="Votes",
                        color_continuous_scale="Viridis"
                    )
                    fig.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Distribution of votes
                    st.subheader("Vote Distribution")
                    vote_distribution = px.histogram(
                        results_df, 
                        x="Votes",
                        nbins=20,
                        title="Distribution of Votes",
                        labels={"Votes": "Vote Count", "count": "Number of Feedback Items"}
                    )
                    st.plotly_chart(vote_distribution, use_container_width=True)
                    
                    # Count items with and without associated tasks
                    with_tasks = results_df["Task ID"].apply(lambda x: x != "None").sum()
                    without_tasks = len(results_df) - with_tasks
                    
                    # Create pie chart for task association
                    fig3, ax3 = plt.subplots(figsize=(8, 5))
                    ax3.pie(
                        [with_tasks, without_tasks],
                        labels=["With Task ID", "Without Task ID"],
                        autopct='%1.1f%%',
                        startangle=90,
                        colors=['#4CAF50', '#FF9800']
                    )
                    ax3.set_title("Feedback Items With Task Association")
                    ax3.axis('equal')
                    st.pyplot(fig3)
                    
                    # Export options
                    st.subheader("Export Results")
                    export_format = st.radio("Select export format:", ["CSV", "Markdown"])
                    
                    if export_format == "CSV":
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="retrospective_analysis.csv",
                            mime="text/csv"
                        )
                    else:  # Markdown
                        # Generate markdown content
                        markdown_content = "# Retrospective Analysis Results\n\n"
                        markdown_content += f"Filter settings: Min Votes = {min_votes}, Max Votes = {max_votes}\n\n"
                        markdown_content += "| Feedback | Task ID | Votes |\n| --- | --- | --- |\n"
                        for _, row in results_df.iterrows():
                            markdown_content += f"| {row['Feedback']} | {row['Task ID']} | {row['Votes']} |\n"
                        
                        st.download_button(
                            label="Download Markdown",
                            data=markdown_content,
                            file_name="retrospective_analysis.md",
                            mime="text/markdown"
                        )
    
    # AI SUGGESTIONS TAB
    ai_tab = st.tabs(["AI Suggestions"])[0]
    with ai_tab:
        st.header("AI Suggestions & Insights")
        st.markdown("Powered by OpenRouter + OpenAI")

        if "ai_messages" not in st.session_state:
            st.session_state.ai_messages = [
                {"role": "assistant", "content": "Hi! I'm your SPrint assistant. How can I help?"}
            ]

        for msg in st.session_state.ai_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        api_key = st.text_input("🔑 OpenRouter API Key", type="password", key="ai_api_key")

        if "retro_feedback" not in st.session_state or st.session_state.retro_feedback is None:
            st.info("Analyze retrospectives first in the previous tab.")
            st.stop()

        df = create_dataframe_from_results(st.session_state.retro_feedback)

        # Build context from feedback
        context = "You are a helpful assistant summarizing retrospective feedback:\\n"
        for _, row in df.iterrows():
            task_info = f" [Task ID: {row['Task ID']}]" if row['Task ID'] != "None" else ""
            context += f"- {row['Feedback']} ({row['Votes']} votes){task_info}\\n"

        prompt = st.chat_input("Ask me anything about this retrospective...")

        if prompt:
            st.session_state.ai_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                msg_placeholder = st.empty()
                full_response = ""

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://localhost",
                    "Content-Type": "application/json"
                }

                body = {
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [{"role": "system", "content": context}] +
                                [m for m in st.session_state.ai_messages if m["role"] != "assistant"],
                    "temperature": 0.7,
                    "max_tokens": 1500,
                    "stream": True
                }

                try:
                    with requests.post("https://openrouter.ai/api/v1/chat/completions",
                                    headers=headers, json=body, stream=True) as response:
                        if response.status_code == 200:
                            for chunk in response.iter_lines():
                                if chunk:
                                    chunk_str = chunk.decode("utf-8")
                                    if chunk_str.startswith("data:") and chunk_str.strip() != "data: [DONE]":
                                        try:
                                            data = json.loads(chunk_str[5:])
                                            delta = data["choices"][0].get("delta", {})
                                            if "content" in delta:
                                                full_response += delta["content"]
                                                msg_placeholder.markdown(full_response + "▌")
                                        except json.JSONDecodeError:
                                            continue  # Skip invalid chunk
                        else:
                            full_response = f"Error: {response.status_code} - {response.text}"
                except Exception as e:
                    full_response = f"Error: {e}"

                msg_placeholder.markdown(full_response)
                st.session_state.ai_messages.append({"role": "assistant", "content": full_response})
#Main Navigation
st.sidebar.title("Navigation")

# Add navigation options with simple buttons
st.sidebar.markdown("### Choose a section:")

if st.sidebar.button("🏠 Home", key="nav_home", use_container_width=True, 
                     type="primary" if st.session_state.current_app == "home" else "secondary"):
    st.session_state.current_app = "home"
    st.rerun()

if st.sidebar.button("📝 Sprint Task Planner", key="nav_sprint", use_container_width=True,
                    type="primary" if st.session_state.current_app == "sprint_planner" else "secondary"):
    st.session_state.current_app = "sprint_planner"
    st.rerun()

if st.sidebar.button("📊 Retrospective Analysis", key="nav_retro", use_container_width=True,
                    type="primary" if st.session_state.current_app == "retro_analysis" else "secondary"):
    st.session_state.current_app = "retro_analysis"
    st.rerun()

# Render the selected app
if st.session_state.current_app == "home":
    render_home()
elif st.session_state.current_app == "sprint_planner":
    render_sprint_task_planner()
elif st.session_state.current_app == "retro_analysis":
    render_retrospective_analysis()
