from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import os
from app.database import engine, Base
from sqlalchemy import inspect
from app.health_progress.urological.models import UrologicalSurgeryEntry
from app.health_progress.gynecologic.models import GynecologicSurgeryEntry
from app.models import User
from app.medical_record.models import MedicalRecord
from app.health_progress.cesarean.models import CesareanSectionEntry
from app.health_progress.hypertension.models import HypertensionEntry
from app.health_progress.diabetes.models import DiabetesEntry
from app.health_progress.orthopedic.models import OrthopedicSurgeryEntry
from app.health_progress.bariatric.models import BariatricEntry
from app.health_progress.burn_care.models import BurnCareEntry
from app.health_progress.general.models import GeneralHealthEntry
from app.health_progress.heart.models import HeartEntry
from app.health_progress.diabetes.routers import router as diabetes_router
from app.health_progress.hypertension.routers import router as hypertension_router
from app.health_progress.heart.routers import router as heart_router
from app.health_progress.kidney.models import KidneyEntry
from app.health_progress.cancer.models import CancerEntry
from app.health_progress.kidney.routers import router as kidney_router
from app.health_progress.cancer.routers import router as cancer_router
from app.skin_analysis.skin_prediction import router as skin_analysis_router
from app.prenatal.models import PrenatalEntry
from app.postnatal.models import PostnatalEntry, PostnatalProfile  # ✅ Only once
from app.postnatal.routers import router as postnatal_router  # ✅ Only once

# Create tables
Base.metadata.create_all(bind=engine)

# Create postnatal tables
try:
    PostnatalEntry.__table__.create(engine, checkfirst=True)
    print("✅ postnatal_entries table created successfully")
except Exception as e:
    print(f"⚠️ Postnatal entries table creation note: {e}")

try:
    PostnatalProfile.__table__.create(engine, checkfirst=True)
    print("✅ postnatal_profiles table created successfully")
except Exception as e:
    print(f"⚠️ Postnatal profiles table creation note: {e}")

# Check users
from app.database import SessionLocal
db = SessionLocal()
users = db.query(User).all()
db.close()

app = FastAPI(
    title="Healthcare Management API",
    description="A comprehensive healthcare management system with progress tracking, appointments, and medical records",
    version="1.0.0"
)

# Import all routers
from app.authentication.routers import router as auth_router
from app.users.routers import router as users_router
from app.appointments.routers import router as appointments_router
from app.health_progress.routers import router as progress_router
from app.chatbot.routers import router as chatbot_router
from app.telemedicine.transcription import router as transcription_router
from app.symptom_tracker.health_tracker_api import router as health_tracker_router
from app.staff.routers import router as staff_router
from app.prenatal.routers import router as prenatal_router
from app.medical_record.routers import router as medical_record_router
from app.health_progress.abdominal.routers import router as abdominal_router
from app.health_progress.general.routers import router as general_router
from app.health_progress.bariatric.routers import router as bariatric_router
from app.health_progress.burn_care.routers import router as burn_care_router
from app.health_progress.cardiac.routers import router as cardiac_router
from app.health_progress.lifelong.routers import router as lifelong_router
from app.health_progress.cesarean.routers import router as cesarean_router
from app.health_progress.gynecologic.routers import router as gynecologic_router
from app.health_progress.orthopedic.routers import router as orthopedic_router
from app.health_progress.urological.routers import router as urological_router
from app.health_progress.abdominal.models import AbdominalEntry

# CORS middleware for ngrok
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directories
os.makedirs("static", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js/handlers", exist_ok=True)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve JavaScript handler files
@app.get("/static/js/handlers/{filename}")
async def serve_js_handler(filename: str):
    file_path = f"static/js/handlers/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/javascript")
    else:
        return {"error": f"Handler file {filename} not found"}, 404

# Health endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Backend is running!"}

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Healthcare Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "staff_login": "/staff"
    }

@app.get("/api/health-progress/general-entries/{patient_id}/{date}")
async def check_general_entry(patient_id: str, date: str):
    try:
        from datetime import datetime
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
        
        db = SessionLocal()
        try:
            existing_entry = db.query(GeneralHealthEntry).filter(
                GeneralHealthEntry.patient_id == patient_id,
                GeneralHealthEntry.submission_date == date
            ).first()
            
            return {
                "exists": existing_entry is not None,
                "data": {
                    "id": existing_entry.id if existing_entry else None,
                    "patient_id": existing_entry.patient_id if existing_entry else None,
                    "patient_name": existing_entry.patient_name if existing_entry else None,
                    "submission_date": existing_entry.submission_date if existing_entry else None,
                    "common_data": existing_entry.common_data if existing_entry else None,
                    "condition_data": existing_entry.condition_data if existing_entry else None,
                    "status": existing_entry.status if existing_entry else None,
                    "created_at": existing_entry.created_at if existing_entry else None
                } if existing_entry else None
            }
        finally:
            db.close()
    except Exception as e:
        return {"exists": False, "error": "Internal server error"}


@app.get("/staff/health-progress", response_class=HTMLResponse, tags=["Staff Web"])
async def staff_health_progress(request: Request):
                     
    base_url = str(request.base_url).rstrip('/')
             
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Health Progress Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        body {{
            background: #f8fafc;
            color: #334155;
            line-height: 1.6;
            padding: 20px;
            min-height: 100vh;
        }}
        .dashboard-container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .dashboard-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            position: relative;
        }}
        .header-content h1 {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        .header-content p {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            padding: 2rem;
            background: #f8fafc;
        }}
        .stat-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        .stat-number {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0.5rem;
        }}
        .stat-label {{
            color: #64748b;
            font-weight: 600;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .content-section {{
            padding: 2rem;
        }}
        .controls {{
            display: flex;
            gap: 1rem;
            align-items: center;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }}
        .control-button {{
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
            background: #3b82f6;
            color: white;
        }}
        .control-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}
        #conditionFilter, #dateFilter {{
            padding: 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            background: white;
            font-size: 0.9rem;
            min-width: 200px;
        }}
        .section-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #1e293b;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e2e8f0;
        }}
        .entries-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .entries-table th {{
            background: #f1f5f9;
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            color: #475569;
            border-bottom: 2px solid #e2e8f0;
        }}
        .entries-table td {{
            padding: 1rem;
            border-bottom: 1px solid #e2e8f0;
        }}
        .entries-table tr:hover {{
            background: #f8fafc;
        }}
        .condition-badge {{
            padding: 0.5rem 1rem;
            border-radius: 20px;
            color: white;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .condition-badge.abdominal {{
            background: #FF9800;
        }}
        .condition-badge.cesarean {{
            background: #9C27B0;
        }}
        .condition-badge.diabetes {{
            background: #4CAF50;
        }}
        .condition-badge.orthopedic {{
            background: #607D8B;
        }}
        .condition-badge.cardiac {{
            background: #dc3545;
        }}    
        .condition-badge.gynecologic {{
            background: #E91E63;  
        }}
        .condition-badge.bariatric {{
            background: #FF6B35;

        }}    
        .condition-badge.burn_care {{
            background: #FF5722;

        }}
        .condition-badge.lifelong {{
            background: #8B5CF6;

        }}
        .condition-badge.hypertension {{
            background: #FF6B6B;

        }}
        .condition-badge.heart {{
            background: #dc3545;

        }}
        .condition-badge.kidney {{
            background: #4CAF50;

        }}
        .condition-badge.cancer {{
            background: #9C27B0;
        
        }}
        .condition-badge.general {{
            background: #8B5CF6;

        }}
        .condition-badge.prenatal {{
            background: #EC4899;




        }}
        .pain-indicator {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .pain-bar {{
            flex: 1;
            height: 6px;
            background: #e2e8f0;
            border-radius: 3px;
            overflow: hidden;
        }}
        .pain-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981, #ef4444);
            transition: width 0.3s ease;
        }}
        .status-badge {{
            padding: 0.375rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .status-urgent {{ background: #ef4444; color: white; }}
        .status-monitor {{ background: #f59e0b; color: white; }}
        .status-good {{ background: #10b981; color: white; }}
        .status-poor {{ background: #6b7280; color: white; }}
        .detail-view {{
            color: #3b82f6;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9rem;
        }}
        .detail-view:hover {{
            text-decoration: underline;
        }}
        .entry-details {{
            background: #f8fafc;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }}
        .entry-details h4 {{
            margin-bottom: 1rem;
            color: #1e293b;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        .metric-group {{
            background: white;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}
        .metric-group h5 {{
            margin-bottom: 0.5rem;
            color: #374151;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .metric-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            padding: 0.25rem 0;
        }}
        .metric-label {{
            color: #64748b;
            font-weight: 500;
            font-size: 0.85rem;
        }}
        .metric-value {{
            color: #1e293b;
            font-weight: 600;
            font-size: 0.85rem;
        }}
        .loading {{
            text-align: center;
            padding: 2rem;
            color: #64748b;
            font-style: italic;
        }}
        .error-message {{
            background: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border: 1px solid #f5c6cb;
        }}
        @media (max-width: 768px) {{
            .controls {{
                flex-direction: column;
                align-items: stretch;
            }}
            #conditionFilter, #dateFilter {{
                min-width: auto;
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="dashboard-header">
            <div class="header-content">
                <h1>Health Progress Dashboard</h1>
                <p>Comprehensive patient monitoring across all conditions</p>
            </div>
        </div>

        <div class="stats-grid" id="statsGrid">
            <div class="loading">Loading statistics...</div>
        </div>


                             



        <div class="content-section">
            <div class="controls">
                <button class="control-button" onclick="loadHealthData()">🔄 Refresh Data</button>
                <select id="conditionFilter" onchange="filterEntries()">
                    <option value="all">All Conditions</option>
                    <option value="abdominal">Abdominal Surgery</option>
                    <option value="cesarean">Cesarean Section</option>
                    <option value="diabetes">Diabetes</option>
                    <option value="hypertension">Hypertension</option> <!-- ✅ ADD THIS -->
                    <option value="orthopedic">Orthopedic Surgery</option>
                    <option value="cardiac">Cardiac Surgery</option>
                    <option value="urological">Urological Surgery</option>
                    <option value="heart">Heart Disease</option>
                    <option value="general_health">General Health</option>
                    <option value="burn_care">Burn Care</option>
                    <option value="gynecologic">Gynecologic Surgery</option>
                    <option value="bariatric">Bariatric Surgery</option>
                    <option value="lifelong">Lifelong Conditions</option>
                    <option value="kidney">Kidney Disease</option>  <!-- ADD THIS -->
                    <option value="cancer">Cancer</option>
                    <option value="prenatal">Prenatal</option>
                    <option value="postnatal">Postnatal</option>

                </select>
                <input type="date" id="dateFilter" onchange="filterEntries()">
            </div>
        
            <div class="section-title">Patient Health Entries</div>
            <div id="entriesContainer">
                <div class="loading">Loading health entries...</div>
            </div>
        </div>
    </div>

    <script>

                        


        // Enhanced Handlers with Complete Metrics Display
        class AbdominalHandler {{
            renderEntryHTML(entry) {{
                const commonData = entry.common_data || {{}};
                const conditionData = entry.condition_data || {{}};
                const painLevel = commonData.pain_level || 0;
                const status = conditionData.status || 'good';
                
                return `
                    <tr>
                        <td>
                            <strong>${{entry.patient_name}}</strong>
                            <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patient_id || 'N/A'}}</div>
                        </td>
                        <td>
                            <span class="condition-badge abdominal">Abdominal</span>
                        </td>
                        <td>
                            <div class="pain-indicator">
                                <span>${{painLevel}}/10</span>
                                <div class="pain-bar">
                                    <div class="pain-fill" style="width: ${{painLevel * 10}}%"></div>
                                </div>
                            </div>
                        </td>
                        <td>
                            <span class="status-badge status-${{status}}">${{status.toUpperCase()}}</span>
                        </td>
                        <td>${{commonData.day_post_op || 'N/A'}}</td>
                        <td>${{new Date(entry.created_at).toLocaleDateString()}}</td>
                        <td>
                            <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                        </td>
                    </tr>
                    <tr id="details-${{entry.id}}" style="display: none;">
                        <td colspan="7">
                            <div class="entry-details">
                                <h4>Complete Health Metrics - ${{entry.patient_name}}</h4>
                                ${{this.getDetailedMetrics(entry)}}
                            </div>
                        </td>
                    </tr>
                `;
            }}
            
            getDetailedMetrics(entry) {{
                const commonData = entry.common_data || {{}};
                const conditionData = entry.condition_data || {{}};
                
                return `
                    <div class="metrics-grid">
                        <div class="metric-group">
                            <h5>Vital Signs</h5>
                            ${{this.renderMetric('Pain Level', commonData.pain_level ? commonData.pain_level + '/10' : 'N/A')}}
                            ${{this.renderMetric('Temperature', commonData.temperature ? commonData.temperature + '°C' : 'N/A')}}
                            ${{this.renderMetric('Heart Rate', commonData.heart_rate ? commonData.heart_rate + ' bpm' : 'N/A')}}
                            ${{this.renderMetric('Blood Pressure', commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic ? 
                                commonData.blood_pressure_systolic + '/' + commonData.blood_pressure_diastolic : 'N/A')}}
                        </div>
                        
                        <div class="metric-group">
                            <h5>Surgical Recovery</h5>
                            ${{this.renderMetric('Days Post-Op', commonData.day_post_op)}}
                            ${{this.renderMetric('GI Function', conditionData.gi_function)}}
                            ${{this.renderMetric('Appetite', conditionData.appetite)}}
                            ${{this.renderMetric('Wound Condition', conditionData.wound_condition)}}
                        </div>
                        
                        <div class="metric-group">
                            <h5>Additional Info</h5>
                            ${{this.renderMetric('Status', conditionData.status)}}
                            ${{this.renderMetric('Mobility', conditionData.mobility)}}
                            ${{this.renderMetric('Additional Notes', conditionData.additional_notes)}}
                        </div>
                    </div>
                `;
            }}
            
            renderMetric(label, value) {{
                if (!value && value !== 0) return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">N/A</span></div>';
                return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">' + value + '</span></div>';
            }}
        }}

      
      
      
      


class CesareanHandler {{
    renderEntryHTML(entry) {{
        const commonData = entry.common_data || {{}};
        const conditionData = entry.condition_data || {{}};
        const painLevel = commonData.pain_level || 0;
        const status = conditionData.status || 'good';
        
        return `
            <tr>
                <td>
                    <strong>${{entry.patient_name}}</strong>
                    <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patient_id || 'N/A'}}</div>
                </td>
                <td>
                    <span class="condition-badge cesarean">Cesarean</span>
                </td>
                <td>
                    <div class="pain-indicator">
                        <span>${{painLevel}}/10</span>
                        <div class="pain-bar">
                            <div class="pain-fill" style="width: ${{painLevel * 10}}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${{status}}">${{status.toUpperCase()}}</span>
                </td>
                <td>${{new Date(entry.submission_date || entry.created_at).toLocaleDateString()}}</td>
                <td>
                    <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                </td>
            </tr>
            <tr id="details-${{entry.id}}" style="display: none;">
                <td colspan="6">
                    <div class="entry-details">
                        <h4>Cesarean Recovery Details - ${{entry.patient_name}}</h4>
                        ${{this.getDetailedMetrics(entry)}}
                    </div>
                </td>
            </tr>
        `;
    }}
    
    getDetailedMetrics(entry) {{
        const commonData = entry.common_data || {{}};
        const conditionData = entry.condition_data || {{}};
        
        return `
            <div class="metrics-grid">
                <div class="metric-group">
                    <h5>Vital Signs</h5>
                    ${{this.renderMetric('Temperature', commonData.temperature ? commonData.temperature + '°C' : 'N/A')}}
                    ${{this.renderMetric('Blood Pressure', commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic ? 
                        commonData.blood_pressure_systolic + '/' + commonData.blood_pressure_diastolic + ' mmHg' : 'N/A')}}
                    ${{this.renderMetric('Heart Rate', commonData.heart_rate ? commonData.heart_rate + ' bpm' : 'N/A')}}
                    ${{this.renderMetric('Respiratory Rate', commonData.respiratory_rate ? commonData.respiratory_rate + '/min' : 'N/A')}}
                    ${{this.renderMetric('Pain Level', commonData.pain_level ? commonData.pain_level + '/10' : 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Uterine Recovery & Lochia</h5>
                    ${{this.renderMetric('Fundal Height', conditionData.fundal_height ? conditionData.fundal_height + ' cm below umbilicus' : 'N/A')}}
                    ${{this.renderMetric('Uterine Firmness', conditionData.uterine_firmness)}}
                    ${{this.renderMetric('Lochia Color', conditionData.lochia_color)}}
                    ${{this.renderMetric('Lochia Amount', conditionData.lochia_amount)}}
                    ${{this.renderMetric('Lochia Odor', conditionData.lochia_odor)}}
                </div>
                
                <div class="metric-group">
                    <h5>Incision Site</h5>
                    ${{this.renderMetric('Wound Condition', conditionData.wound_condition)}}
                    ${{this.renderMetric('Wound Discharge', conditionData.wound_discharge_type)}}
                    ${{this.renderMetric('Wound Tenderness', conditionData.wound_tenderness)}}
                </div>
                
                <div class="metric-group">
                    <h5>Urinary & Bowel Function</h5>
                    ${{this.renderMetric('Urine Output', conditionData.urine_output ? conditionData.urine_output + ' mL/24h' : 'N/A')}}
                    ${{this.renderMetric('Urinary Retention', conditionData.urinary_retention ? 'Yes' : 'No')}}
                    ${{this.renderMetric('Bowel Sounds', conditionData.bowel_sounds)}}
                    ${{this.renderMetric('Flatus Passed', conditionData.flatus_passed ? 'Yes' : 'No')}}
                    ${{this.renderMetric('Bowel Movement', conditionData.bowel_movement ? 'Yes' : 'No')}}
                </div>
                
                <div class="metric-group">
                    <h5>Pain & Mobility</h5>
                    ${{this.renderMetric('Mobility Level', conditionData.mobility_level)}}
                    ${{this.renderMetric('Ambulation Distance', conditionData.ambulation_distance)}}
                </div>
                
                ${{conditionData.breastfeeding ? `
                <div class="metric-group">
                    <h5>Breast & Lactation</h5>
                    ${{this.renderMetric('Breastfeeding', 'Yes')}}
                    ${{this.renderMetric('Breast Engorgement', conditionData.breast_engorgement)}}
                    ${{this.renderMetric('Breast Tenderness', conditionData.breast_tenderness)}}
                    ${{this.renderMetric('Nipple Condition', conditionData.nipple_condition)}}
                    ${{this.renderMetric('Feeding Frequency', conditionData.feeding_frequency)}}
                </div>
                ` : this.renderMetric('Breastfeeding', 'No', true)}}
                
                <div class="metric-group full-width">
                    <h5>Additional Information</h5>
                    ${{this.renderMetric('Status', conditionData.status, true)}}
                    ${{this.renderMetric('Additional Notes', conditionData.additional_notes, true)}}
                    ${{this.renderMetric('Submission Date', new Date(entry.submission_date || entry.created_at).toLocaleString(), true)}}
                </div>
            </div>
        `;
    }}
    
    renderMetric(label, value, fullWidth = false) {{
        if (!value && value !== 0 && value !== false) return '';
        
        const displayValue = value === true ? 'Yes' : 
                           value === false ? 'No' : 
                           value;
        
        const widthClass = fullWidth ? 'full-width' : '';
        return `
            <div class="metric-row ${{widthClass}}">
                <span class="metric-label">${{label}}:</span>
                <span class="metric-value">${{displayValue}}</span>
            </div>
        `;
    }}
}}














       class DiabetesHandler {{
    renderEntryHTML(entry) {{
        const status = entry.status || 'good';
        
        return `
            <tr>
                <td>
                    <strong>${{entry.patient_name}}</strong>
                    <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patient_id || 'N/A'}}</div>
                </td>
                <td>
                    <span class="condition-badge diabetes">Diabetes</span>
                </td>
                <td>
                    <div class="pain-indicator">
                        <span>N/A</span>
                        <div class="pain-bar">
                            <div class="pain-fill" style="width: 0%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${{status}}">${{status.toUpperCase()}}</span>
                </td>
                <td>N/A</td>
                <td>${{new Date(entry.created_at).toLocaleDateString()}}</td>
                <td>
                    <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                </td>
            </tr>
            <tr id="details-${{entry.id}}" style="display: none;">
                <td colspan="7">
                    <div class="entry-details">
                        <h4>Complete Health Metrics - ${{entry.patient_name}}</h4>
                        ${{this.getDetailedMetrics(entry)}}
                    </div>
                </td>
            </tr>
        `;
    }}
    
    getDetailedMetrics(entry) {{
        return `
            <div class="metrics-grid">
                <div class="metric-group">
                    <h5>Diabetes Metrics</h5>
                    ${{this.renderMetric('Blood Glucose', entry.blood_glucose ? entry.blood_glucose + ' mg/dL' : 'N/A')}}
                    ${{this.renderMetric('Blood Pressure', entry.blood_pressure_systolic && entry.blood_pressure_diastolic ? 
                        entry.blood_pressure_systolic + '/' + entry.blood_pressure_diastolic + ' mmHg' : 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Medications</h5>
                    ${{this.renderMetric('Morning', this.formatMedicationTime(entry.medications, 'morning'))}}
                    ${{this.renderMetric('Afternoon', this.formatMedicationTime(entry.medications, 'afternoon'))}}
                    ${{this.renderMetric('Evening', this.formatMedicationTime(entry.medications, 'evening'))}}
                    ${{this.renderMetric('Side Effects', this.formatSideEffects(entry.medications))}}
                </div>
                
                <div class="metric-group">
                    <h5>General Health</h5>
                    ${{this.renderMetric('Status', entry.status || 'N/A')}}
                    ${{this.renderMetric('Energy Level', entry.energy_level !== undefined ? entry.energy_level + '/10' : 'N/A')}}
                    ${{this.renderMetric('Sleep Hours', entry.sleep_hours !== undefined ? entry.sleep_hours + ' hours' : 'N/A')}}
                    ${{this.renderMetric('Sleep Quality', entry.sleep_quality !== undefined ? entry.sleep_quality + '/5' : 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Symptoms & Notes</h5>
                    ${{this.renderMetric('Symptoms', this.formatSymptoms(entry.symptoms))}}
                    ${{this.renderMetric('Patient Notes', entry.notes || 'N/A')}}
                </div>
            </div>
        `;
    }}
    
    formatMedicationTime(medications, time) {{
        if (!medications) return 'No';
        
        try {{
            const meds = typeof medications === 'string' ? JSON.parse(medications) : medications;
            return meds[time] ? 'Yes' : 'No';
        }} catch (e) {{
            return 'No';
        }}
    }}
    
    formatSideEffects(medications) {{
        if (!medications) return 'N/A';
        
        try {{
            const meds = typeof medications === 'string' ? JSON.parse(medications) : medications;
            return meds.sideEffects || meds.side_effects || 'None reported';
        }} catch (e) {{
            return 'N/A';
        }}
    }}
    
    formatSymptoms(symptoms) {{
        if (!symptoms) return 'N/A';
        
        try {{
            const symptomsObj = typeof symptoms === 'string' ? JSON.parse(symptoms) : symptoms;
            
            const activeSymptoms = [];
            
            if (symptomsObj.fatigue) activeSymptoms.push('Fatigue');
            if (symptomsObj.nausea) activeSymptoms.push('Nausea');
            if (symptomsObj.breathingIssues) activeSymptoms.push('Breathing Issues');
            if (symptomsObj.pain) activeSymptoms.push('Pain');
            if (symptomsObj.swelling) activeSymptoms.push('Swelling');
            if (symptomsObj.other) activeSymptoms.push('Other: ' + symptomsObj.other);
            
            return activeSymptoms.length > 0 ? activeSymptoms.join(', ') : 'None';
        }} catch (e) {{
            return 'N/A';
        }}
    }}
    
    renderMetric(label, value) {{
        if (!value && value !== 0) return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">N/A</span></div>';
        return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">' + value + '</span></div>';
    }}
}}









        class OrthopedicHandler {{
    renderEntryHTML(entry) {{
        const commonData = entry.common_data || {{}};
        const conditionData = entry.condition_data || {{}};
        const painLevel = commonData.pain_level || 0;
        const status = conditionData.status || 'good';
        
        return `
            <tr>
                <td>
                    <strong>${{entry.patient_name}}</strong>
                    <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patient_id || 'N/A'}}</div>
                </td>
                <td>
                    <span class="condition-badge orthopedic">Orthopedic</span>
                </td>
                <td>
                    <div class="pain-indicator">
                        <span>${{painLevel}}/10</span>
                        <div class="pain-bar">
                            <div class="pain-fill" style="width: ${{painLevel * 10}}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${{status}}">${{status.toUpperCase()}}</span>
                </td>
                <td>${{new Date(entry.submission_date || entry.created_at).toLocaleDateString()}}</td>
                <td>
                    <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                </td>
            </tr>
            <tr id="details-${{entry.id}}" style="display: none;">
                <td colspan="6">
                    <div class="entry-details">
                        <h4>Orthopedic Recovery Details - ${{entry.patient_name}}</h4>
                        ${{this.getDetailedMetrics(entry)}}
                    </div>
                </td>
            </tr>
        `;
    }}
    
    getDetailedMetrics(entry) {{
        const commonData = entry.common_data || {{}};
        const conditionData = entry.condition_data || {{}};
        
        return `
            <div class="metrics-grid">
                <div class="metric-group">
                    <h5>Pain Assessment</h5>
                    ${{this.renderMetric('Pain Level', commonData.pain_level ? commonData.pain_level + '/10' : 'N/A')}}
                    ${{this.renderMetric('Pain Location', conditionData.pain_location)}}
                    ${{this.renderMetric('Temperature', commonData.temperature ? commonData.temperature + '°C' : 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Limb Neurovascular Status</h5>
                    ${{this.renderMetric('Limb Color', conditionData.limb_color)}}
                    ${{this.renderMetric('Limb Temperature', conditionData.limb_temperature)}}
                    ${{this.renderMetric('Capillary Refill', conditionData.capillary_refill)}}
                    ${{this.renderMetric('Limb Movement', conditionData.limb_movement)}}
                    ${{this.renderMetric('Limb Sensation', conditionData.limb_sensation)}}
                    ${{this.renderMetric('Distal Pulse', conditionData.distal_pulse)}}
                </div>
                
                <div class="metric-group">
                    <h5>Wound Condition</h5>
                    ${{this.renderMetric('Wound Condition', conditionData.wound_condition)}}
                    ${{this.renderMetric('Discharge Type', conditionData.wound_discharge_type)}}
                    ${{this.renderMetric('Swelling', conditionData.wound_swelling)}}
                </div>
                
                <div class="metric-group">
                    <h5>Mobility & Weight-Bearing</h5>
                    ${{this.renderMetric('Mobility Level', conditionData.mobility_level)}}
                    ${{this.renderMetric('Weight-Bearing Status', conditionData.weight_bearing_status)}}
                    ${{this.renderMetric('Assistive Device', conditionData.assistive_device)}}
                </div>
                
                ${{conditionData.has_drain ? `
                <div class="metric-group">
                    <h5>Drain Information</h5>
                    ${{this.renderMetric('Has Drain', conditionData.has_drain ? 'Yes' : 'No')}}
                    ${{this.renderMetric('Drain Output', conditionData.drain_output ? conditionData.drain_output + ' mL' : 'N/A')}}
                    ${{this.renderMetric('Drain Color', conditionData.drain_color)}}
                </div>
                ` : ''}}
                
                <div class="metric-group full-width">
                    <h5>Additional Information</h5>
                    ${{this.renderMetric('Status', conditionData.status, true)}}
                    ${{this.renderMetric('Additional Notes', conditionData.additional_notes, true)}}
                    ${{this.renderMetric('Submission Date', new Date(entry.submission_date || entry.created_at).toLocaleString(), true)}}
                </div>
            </div>
        `;
    }}
    
    renderMetric(label, value, fullWidth = false) {{
        if (!value && value !== 0 && value !== false) return '';
        
        const displayValue = value === true ? 'Yes' : 
                           value === false ? 'No' : 
                           value;
        
        const widthClass = fullWidth ? 'full-width' : '';
        return `
            <div class="metric-row ${{widthClass}}">
                <span class="metric-label">${{label}}:</span>
                <span class="metric-value">${{displayValue}}</span>
            </div>
        `;
    }}
}}







         class CardiacHandler {{
    renderEntryHTML(entry) {{
        // Direct access to the spread data structure from your component
        const painLevel = entry.painLevel || 0;
        const status = entry.status || 'good';
        
        return `
            <tr>
                <td>
                    <strong>${{entry.patientName}}</strong>
                    <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patientId || 'N/A'}}</div>
                </td>
                <td>
                    <span class="condition-badge cardiac">Cardiac</span>
                </td>
                <td>
                    <div class="pain-indicator">
                        <span>${{painLevel}}/10</span>
                        <div class="pain-bar">
                            <div class="pain-fill" style="width: ${{painLevel * 10}}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${{status}}">${{status.toUpperCase()}}</span>
                </td>
                <td>${{entry.dayPostOp || 'N/A'}}</td>
                <td>${{new Date(entry.submissionDate || entry.submittedAt).toLocaleDateString()}}</td>
                <td>
                    <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                </td>
            </tr>
            <tr id="details-${{entry.id}}" style="display: none;">
                <td colspan="7">
                    <div class="entry-details">
                        <h4>Cardiac Surgery Recovery Details - ${{entry.patientName}}</h4>
                        ${{this.getDetailedMetrics(entry)}}
                    </div>
                </td>
            </tr>
        `;
    }}
    
    getDetailedMetrics(entry) {{
        return `
            <div class="metrics-grid">
                <div class="metric-group">
                    <h5>Vital Signs & Cardiac Rhythm</h5>
                    ${{this.renderMetric('Temperature', entry.temperature, '°C')}}
                    ${{this.renderMetric('Blood Pressure', 
                        entry.bloodPressureSystolic && entry.bloodPressureDiastolic ? 
                        entry.bloodPressureSystolic + '/' + entry.bloodPressureDiastolic + ' mmHg' : 'N/A')}}
                    ${{this.renderMetric('Heart Rate', entry.heartRate, ' bpm')}}
                    ${{this.renderMetric('Respiratory Rate', entry.respiratoryRate, '/min')}}
                    ${{this.renderMetric('Oxygen Saturation', entry.oxygenSaturation, '%')}}
                    ${{this.renderMetric('Cardiac Rhythm', entry.cardiacRhythm)}}
                    ${{this.renderMetric('Rhythm Stable', entry.rhythmStable, '', true)}}
                </div>
                
                <div class="metric-group">
                    <h5>Respiratory Function</h5>
                    ${{this.renderMetric('Breathing Effort', entry.breathingEffort)}}
                    ${{this.renderMetric('Oxygen Therapy', entry.oxygenTherapy, '', true)}}
                    ${{this.renderMetric('Oxygen Flow', entry.oxygenFlow, ' L/min')}}
                    ${{this.renderMetric('Incentive Spirometer', entry.incentiveSpirometer)}}
                    ${{this.renderMetric('Cough Effectiveness', entry.coughEffectiveness)}}
                </div>
                
                <div class="metric-group">
                    <h5>Chest Tube & Fluid Balance</h5>
                    ${{this.renderMetric('Chest Tube', entry.hasChestTube, '', true)}}
                    ${{this.renderMetric('Chest Tube Output', entry.chestTubeOutput, ' mL/24h')}}
                    ${{this.renderMetric('Drain Color', entry.chestDrainColor)}}
                    ${{this.renderMetric('Drain Consistency', entry.chestDrainConsistency)}}
                    ${{this.renderMetric('Urine Output', entry.urineOutput, ' mL/hr')}}
                    ${{this.renderMetric('Fluid Balance', entry.fluidBalance, ' mL')}}
                </div>
                
                <div class="metric-group">
                    <h5>Wound Assessment</h5>
                    ${{this.renderMetric('Sternal Wound', entry.sternalWoundCondition)}}
                    ${{this.renderMetric('Graft Site Wound', entry.graftWoundCondition)}}
                    ${{this.renderMetric('Wound Discharge', entry.woundDischargeType)}}
                    ${{this.renderMetric('Wound Tenderness', entry.woundTenderness)}}
                </div>
                
                <div class="metric-group">
                    <h5>Neurological & Mobility</h5>
                    ${{this.renderMetric('Consciousness Level', entry.consciousnessLevel)}}
                    ${{this.renderMetric('Orientation', entry.orientation)}}
                    ${{this.renderMetric('Limb Movement', entry.limbMovement)}}
                    ${{this.renderMetric('Mobility Level', entry.mobilityLevel)}}
                    ${{this.renderMetric('Ambulation Distance', entry.ambulationDistance)}}
                </div>
                
                <div class="metric-group">
                    <h5>Pain & Emotional State</h5>
                    ${{this.renderMetric('Pain Level', entry.painLevel, '/10')}}
                    ${{this.renderMetric('Pain Location', entry.painLocation)}}
                    ${{this.renderMetric('Mood State', entry.moodState)}}
                    ${{this.renderMetric('Sleep Quality', entry.sleepQuality)}}
                </div>
                
                <div class="metric-group full-width">
                    <h5>Additional Information</h5>
                    ${{this.renderMetric('Status', entry.status, '', true)}}
                    ${{this.renderMetric('Days Post-Op', entry.dayPostOp, '', true)}}
                    ${{this.renderMetric('Additional Notes', entry.additionalNotes, '', true)}}
                    ${{this.renderMetric('Submission Date', new Date(entry.submissionDate || entry.submittedAt).toLocaleString(), '', true)}}
                </div>
            </div>
        `;
    }}
    
    renderMetric(label, value, unit = '', isBoolean = false) {{
        if (value === undefined || value === null || value === '') return '';
        
        let displayValue;
        if (isBoolean) {{
            displayValue = value === true ? 'Yes' : value === false ? 'No' : 'N/A';
        }} else {{
            displayValue = value === true ? 'Yes' : 
                          value === false ? 'No' : 
                          value;
        }}
        
        const fullValue = unit && displayValue !== 'N/A' ? `${{displayValue}}${{unit}}` : displayValue;
        
        return `
            <div class="metric-row">
                <span class="metric-label">${{label}}:</span>
                <span class="metric-value">${{fullValue}}</span>
            </div>
        `;
    }}
}}

     

                   
        class UrologicalHandler {{
            renderEntryHTML(entry) {{
                const commonData = entry.common_data || {{}};
                const conditionData = entry.condition_data || {{}};
                const painLevel = commonData.pain_level || 0;
                const status = conditionData.status || 'good';
                
                return `
                    <tr>
                        <td>
                            <strong>${{entry.patient_name}}</strong>
                            <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patient_id || 'N/A'}}</div>
                        </td>
                        <td>
                            <span class="condition-badge abdominal" style="background: #2196F3;">Urological</span>
                        </td>
                        <td>
                            <div class="pain-indicator">
                                <span>${{painLevel}}/10</span>
                                <div class="pain-bar">
                                    <div class="pain-fill" style="width: ${{painLevel * 10}}%"></div>
                                </div>
                            </div>
                        </td>
                        <td>
                            <span class="status-badge status-${{status}}">${{status.toUpperCase()}}</span>
                        </td>
                        <td>N/A</td>
                        <td>${{new Date(entry.created_at).toLocaleDateString()}}</td>
                        <td>
                            <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                        </td>
                    </tr>
                    <tr id="details-${{entry.id}}" style="display: none;">
                        <td colspan="7">
                            <div class="entry-details">
                                <h4>Complete Health Metrics - ${{entry.patient_name}}</h4>
                                ${{this.getDetailedMetrics(entry)}}
                            </div>
                        </td>
                    </tr>
                `;
            }}
            
            getDetailedMetrics(entry) {{
                const commonData = entry.common_data || {{}};
                const conditionData = entry.condition_data || {{}};
                
                return `
                    <div class="metrics-grid">
                        <div class="metric-group">
                            <h5>Vital Signs</h5>
                            ${{this.renderMetric('Pain Level', commonData.pain_level ? commonData.pain_level + '/10' : 'N/A')}}
                            ${{this.renderMetric('Temperature', commonData.temperature ? commonData.temperature + '°C' : 'N/A')}}
                            ${{this.renderMetric('Heart Rate', commonData.heart_rate ? commonData.heart_rate + ' bpm' : 'N/A')}}
                            ${{this.renderMetric('Blood Pressure', commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic ? 
                                commonData.blood_pressure_systolic + '/' + commonData.blood_pressure_diastolic : 'N/A')}}
                        </div>
                        
                        <div class="metric-group">
                            <h5>Urinary Assessment</h5>
                            ${{this.renderMetric('Urine Output', conditionData.urine_output ? conditionData.urine_output + ' mL' : 'N/A')}}
                            ${{this.renderMetric('Urine Color', conditionData.urine_color)}}
                            ${{this.renderMetric('Urine Clarity', conditionData.urine_clarity)}}
                            ${{this.renderMetric('Urine Odor', conditionData.urine_odor)}}
                        </div>
                        
                        <div class="metric-group">
                            <h5>Catheter & Drain</h5>
                            ${{this.renderMetric('Has Catheter', conditionData.has_catheter ? 'Yes' : 'No')}}
                            ${{this.renderMetric('Catheter Patency', conditionData.catheter_patency)}}
                            ${{this.renderMetric('Has Drain', conditionData.has_drain ? 'Yes' : 'No')}}
                            ${{this.renderMetric('Drain Output', conditionData.drain_output ? conditionData.drain_output + ' mL' : 'N/A')}}
                        </div>

                        <div class="metric-group">
                            <h5>Wound & Recovery</h5>
                            ${{this.renderMetric('Wound Condition', conditionData.wound_condition)}}
                            ${{this.renderMetric('Insertion Site', conditionData.insertion_site)}}
                            ${{this.renderMetric('Nausea Level', conditionData.nausea_level)}}
                            ${{this.renderMetric('Hydration Status', conditionData.hydration_status)}}
                        </div>
                    </div>
                `;
            }}
            
            renderMetric(label, value) {{
                if (!value && value !== 0) return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">N/A</span></div>';
                return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">' + value + '</span></div>';
            }}
        }}



                   
        class GynecologicHandler {{
            renderEntryHTML(entry) {{
                // 🔍 DEBUG: Check what data we're receiving
                console.log("🔍 ========== GYNECOLOGY ENTRY DEBUG ==========");
                console.log("🔍 Full entry:", entry);
                console.log("🔍 Entry ID:", entry.id);
                console.log("🔍 Patient name:", entry.patient_name);
                console.log("🔍 Common data:", entry.common_data);
                console.log("🔍 Condition data:", entry.condition_data);
                
                // Check specific fields in common_data
                if (entry.common_data) {{
                    console.log("🔍 Common data - painLevel:", entry.common_data.painLevel);
                    console.log("🔍 Common data - pain_level:", entry.common_data.pain_level);
                    console.log("🔍 Common data - temperature:", entry.common_data.temperature);
                    console.log("🔍 Common data - dayPostOp:", entry.common_data.dayPostOp);
                    console.log("🔍 Common data - day_post_op:", entry.common_data.day_post_op);
                }}
                
                // Check specific fields in condition_data
                if (entry.condition_data) {{
                    console.log("🔍 Condition data - bleedingAmount:", entry.condition_data.bleedingAmount);
                    console.log("🔍 Condition data - dischargeColor:", entry.condition_data.dischargeColor);
                    console.log("🔍 Condition data - status:", entry.condition_data.status);
                }}
                console.log("🔍 ============================================");
                
                const commonData = entry.common_data || {{}};
                const conditionData = entry.condition_data || {{}};
                const painLevel = commonData.painLevel || 0;
                const status = conditionData.status || 'good';
                
                return `
                    <tr>
                        <td>
                            <strong>${{entry.patient_name}}</strong>
                            <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patient_id || 'N/A'}}</div>
                        </td>
                        <td>
                            <span class="condition-badge gynecologic">Gynecologic</span>
                        </td>
                        <td>
                            <div class="pain-indicator">
                                <span>${{painLevel}}/10</span>
                                <div class="pain-bar">
                                    <div class="pain-fill" style="width: ${{painLevel * 10}}%"></div>
                                </div>
                            </div>
                        </td>
                        <td>
                            <span class="status-badge status-${{status}}">${{status.toUpperCase()}}</span>
                        </td>
                        <td>${{commonData.dayPostOp || 'N/A'}}</td>
                        <td>${{new Date(entry.created_at).toLocaleDateString()}}</td>
                        <td>
                            <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                        </td>
                    </tr>
                    <tr id="details-${{entry.id}}" style="display: none;">
                        <td colspan="7">
                            <div class="entry-details">
                                <h4>Complete Health Metrics - ${{entry.patient_name}}</h4>
                                ${{this.getDetailedMetrics(entry)}}
                            </div>
                        </td>
                    </tr>
                `;
            }}
            
            getDetailedMetrics(entry) {{
                // 🔍 DEBUG: Check what data we have for details
                console.log("🔍 getDetailedMetrics called for entry:", entry.id);
                console.log("🔍 Details common_data:", entry.common_data);
                console.log("🔍 Details condition_data:", entry.condition_data);
                
                const commonData = entry.common_data || {{}};
                const conditionData = entry.condition_data || {{}};
                
                return `
                    <div class="metrics-grid">
                        <div class="metric-group">
                            <h5>Vital Signs</h5>
                            ${{this.renderMetric('Pain Level', commonData.painLevel ? commonData.painLevel + '/10' : 'N/A')}}
                            ${{this.renderMetric('Temperature', commonData.temperature ? commonData.temperature + '°C' : 'N/A')}}
                            ${{this.renderMetric('Heart Rate', commonData.heartRate ? commonData.heartRate + ' bpm' : 'N/A')}}
                            ${{this.renderMetric('Blood Pressure', commonData.bloodPressureSystolic && commonData.bloodPressureDiastolic ? 
                                commonData.bloodPressureSystolic + '/' + commonData.bloodPressureDiastolic : 'N/A')}}
                        </div>
                        
                        <div class="metric-group">
                            <h5>Gynecologic Assessment</h5>
                            ${{this.renderMetric('Bleeding Amount', conditionData.bleedingAmount)}}
                            ${{this.renderMetric('Discharge Color', conditionData.dischargeColor)}}
                            ${{this.renderMetric('Discharge Odor', conditionData.dischargeOdor)}}
                            ${{this.renderMetric('Clots Present', conditionData.clotsPresent ? 'Yes' : 'No')}}
                            ${{this.renderMetric('Clot Size', conditionData.clotSize)}}
                        </div>
                        
                        <div class="metric-group">
                            <h5>Urinary & Wound</h5>
                            ${{this.renderMetric('Urinary Frequency', conditionData.urinaryFrequency)}}
                            ${{this.renderMetric('Has Catheter', conditionData.hasCatheter ? 'Yes' : 'No')}}
                            ${{this.renderMetric('Wound Condition', conditionData.woundCondition)}}
                            ${{this.renderMetric('Wound Tenderness', conditionData.woundTenderness)}}
                            ${{this.renderMetric('Has Drain', conditionData.hasDrain ? 'Yes' : 'No')}}
                        </div>

                        <div class="metric-group">
                            <h5>Recovery Status</h5>
                            ${{this.renderMetric('Nausea Level', conditionData.nauseaLevel)}}
                            ${{this.renderMetric('Vomiting Episodes', conditionData.vomitingEpisodes)}}
                            ${{this.renderMetric('Bowel Movement', conditionData.bowelMovement ? 'Yes' : 'No')}}
                            ${{this.renderMetric('Mobility Level', conditionData.mobilityLevel)}}
                            ${{this.renderMetric('Mood State', conditionData.moodState)}}
                        </div>
                    </div>
                `;
            }}
            
            renderMetric(label, value) {{
                if (!value && value !== 0) return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">N/A</span></div>';
                return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">' + value + '</span></div>';
            }}
        }}


class BariatricHandler {{
    renderEntryHTML(entry) {{
        const commonData = entry.common_data || {{}};
        const conditionData = entry.condition_data || {{}};
        const painLevel = commonData.pain_level || 0;
        const status = conditionData.status || 'good';
        
        return `
            <tr>
                <td>
                    <strong>${{entry.patient_name}}</strong>
                    <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patient_id || 'N/A'}}</div>
                </td>
                <td>
                    <span class="condition-badge abdominal" style="background: #FF6B35;">Bariatric</span>
                </td>
                <td>
                    <div class="pain-indicator">
                        <span>${{painLevel}}/10</span>
                        <div class="pain-bar">
                            <div class="pain-fill" style="width: ${{painLevel * 10}}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${{status}}">${{status.toUpperCase()}}</span>
                </td>
                <td>${{commonData.day_post_op || 'N/A'}}</td>
                <td>${{new Date(entry.created_at).toLocaleDateString()}}</td>
                <td>
                    <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                </td>
            </tr>
            <tr id="details-${{entry.id}}" style="display: none;">
                <td colspan="7">
                    <div class="entry-details">
                        <h4>Complete Health Metrics - ${{entry.patient_name}}</h4>
                        ${{this.getDetailedMetrics(entry)}}
                    </div>
                </td>
            </tr>
        `;
    }}
    
    getDetailedMetrics(entry) {{
        const commonData = entry.common_data || {{}};
        const conditionData = entry.condition_data || {{}};
        
        return `
            <div class="metrics-grid">
                <div class="metric-group">
                    <h5>Vital Signs</h5>
                    ${{this.renderMetric('Pain Level', commonData.pain_level ? commonData.pain_level + '/10' : 'N/A')}}
                    ${{this.renderMetric('Temperature', commonData.temperature ? commonData.temperature + '°C' : 'N/A')}}
                    ${{this.renderMetric('Heart Rate', commonData.heart_rate ? commonData.heart_rate + ' bpm' : 'N/A')}}
                    ${{this.renderMetric('Blood Pressure', commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic ? 
                        commonData.blood_pressure_systolic + '/' + commonData.blood_pressure_diastolic : 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Bariatric Metrics</h5>
                    ${{this.renderMetric('Weight', conditionData.weight ? conditionData.weight + ' kg' : 'N/A')}}
                    ${{this.renderMetric('Weight Change', conditionData.weight_change ? conditionData.weight_change + ' kg' : 'N/A')}}
                    ${{this.renderMetric('Food Intake', conditionData.food_intake)}}
                    ${{this.renderMetric('Protein Intake', conditionData.protein_intake ? conditionData.protein_intake + ' g' : 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Recovery Status</h5>
                    ${{this.renderMetric('Fluid Intake', conditionData.fluid_intake ? conditionData.fluid_intake + ' mL' : 'N/A')}}
                    ${{this.renderMetric('Exercise Level', conditionData.exercise_level)}}
                    ${{this.renderMetric('Nausea Level', conditionData.nausea_level)}}
                    ${{this.renderMetric('Additional Notes', conditionData.additional_notes)}}
                </div>
            </div>
        `;
    }}
    
    renderMetric(label, value) {{
        if (!value && value !== 0) return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">N/A</span></div>';
        return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">' + value + '</span></div>';
    }}
}}
          



 class BurnCareHandler {{
    renderEntryHTML(entry) {{
        const commonData = entry.common_data || {{}};
        const conditionData = entry.condition_data || {{}};
        const painLevel = commonData.pain_level || 0;
        const status = conditionData.status || 'good';
        
        return `
            <tr>
                <td>
                    <strong>${{entry.patient_name}}</strong>
                    <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patient_id || 'N/A'}}</div>
                </td>
                <td>
                    <span class="condition-badge burn_care">Burn Care</span>
                </td>
                <td>
                    <div class="pain-indicator">
                        <span>${{painLevel}}/10</span>
                        <div class="pain-bar">
                            <div class="pain-fill" style="width: ${{painLevel * 10}}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${{status}}">${{status.toUpperCase()}}</span>
                </td>
                <td>${{commonData.day_post_op || 'N/A'}}</td>
                <td>${{new Date(entry.created_at).toLocaleDateString()}}</td>
                <td>
                    <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                </td>
            </tr>
            <tr id="details-${{entry.id}}" style="display: none;">
                <td colspan="7">
                    <div class="entry-details">
                        <h4>Complete Burn Care Metrics - ${{entry.patient_name}}</h4>
                        ${{this.getDetailedMetrics(entry)}}
                    </div>
                </td>
            </tr>
        `;
    }}
    
    getDetailedMetrics(entry) {{
        const commonData = entry.common_data || {{}};
        const conditionData = entry.condition_data || {{}};
        
        return `
            <div class="metrics-grid">
                <div class="metric-group">
                    <h5>Vital Signs</h5>
                    ${{this.renderMetric('Pain Level', commonData.pain_level ? commonData.pain_level + '/10' : 'N/A')}}
                    ${{this.renderMetric('Temperature', commonData.temperature ? commonData.temperature + '°C' : 'N/A')}}
                    ${{this.renderMetric('Heart Rate', commonData.heart_rate ? commonData.heart_rate + ' bpm' : 'N/A')}}
                    ${{this.renderMetric('Blood Pressure', commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic ? 
                        commonData.blood_pressure_systolic + '/' + commonData.blood_pressure_diastolic : 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Wound Assessment</h5>
                    ${{this.renderMetric('Itching', conditionData.itching)}}
                    ${{this.renderMetric('Wound Appearance', conditionData.wound_appearance)}}
                    ${{this.renderMetric('Drainage', conditionData.drainage)}}
                    ${{this.renderMetric('Scar Appearance', conditionData.scar_appearance)}}
                </div>
                
                <div class="metric-group">
                    <h5>Function & Mobility</h5>
                    ${{this.renderMetric('ROM Exercises', conditionData.rom_exercises !== undefined ? (conditionData.rom_exercises ? 'Yes' : 'No') : 'N/A')}}
                    ${{this.renderMetric('Joint Tightness', conditionData.joint_tightness)}}
                    ${{this.renderMetric('Mobility Level', conditionData.mobility)}}
                    ${{this.renderMetric('Compression Garment', conditionData.compression_garment !== undefined ? (conditionData.compression_garment ? 'Yes' : 'No') : 'N/A')}}
                </div>

                <div class="metric-group">
                    <h5>Nutrition & Recovery</h5>
                    ${{this.renderMetric('Protein Intake', conditionData.protein_intake ? conditionData.protein_intake + ' g/day' : 'N/A')}}
                    ${{this.renderMetric('Fluid Intake', conditionData.fluid_intake ? conditionData.fluid_intake + ' mL/day' : 'N/A')}}
                    ${{this.renderMetric('Additional Notes', conditionData.additional_notes)}}
                </div>
            </div>
        `;
    }}
    
    renderMetric(label, value) {{
        if (!value && value !== 0) return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">N/A</span></div>';
        return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">' + value + '</span></div>';
    }}
}}

















































class LifelongHandler {{
    renderEntryHTML(entry) {{
        const commonData = entry.common_data || {{}};
        const conditionData = entry.condition_data || {{}};
        const selectedConditions = conditionData.selected_conditions || [];
        const status = conditionData.status || 'good';
        
        return `
            <tr>
                <td>
                    <strong>${{entry.patient_name}}</strong>
                    <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patient_id || 'N/A'}}</div>
                </td>
                <td>
                    <span class="condition-badge lifelong">Lifelong</span>
                    <div style="font-size: 0.7rem; margin-top: 4px; color: #6B7280;">
                        ${{selectedConditions.join(', ')}}
                    </div>
                </td>
                <td>
                    <div class="pain-indicator">
                        <span>N/A</span>
                        <div class="pain-bar">
                            <div class="pain-fill" style="width: 0%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${{status}}">${{status.toUpperCase()}}</span>
                </td>
                <td>N/A</td>
                <td>${{new Date(entry.created_at).toLocaleDateString()}}</td>
                <td>
                    <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                </td>
            </tr>
            <tr id="details-${{entry.id}}" style="display: none;">
                <td colspan="7">
                    <div class="entry-details">
                        <h4>Complete Health Metrics - ${{entry.patient_name}}</h4>
                        ${{this.getDetailedMetrics(entry)}}
                    </div>
                </td>
            </tr>
        `;
    }}
    
    getDetailedMetrics(entry) {{
        const commonData = entry.common_data || {{}};
        const conditionData = entry.condition_data || {{}};
        const selectedConditions = conditionData.selected_conditions || [];
        
        // Fix the problematic line by calculating symptoms count separately
        const symptomsCount = commonData.symptoms ? Object.keys(commonData.symptoms).filter(key => commonData.symptoms[key]).length : 0;
        const symptomsText = symptomsCount > 0 ? symptomsCount + ' symptoms' : 'None';
        
        return `
            <div class="metrics-grid">
                <div class="metric-group">
                    <h5>Tracked Conditions</h5>
                    ${{selectedConditions.map(condition => 
                        `<div class="metric-row">
                            <span class="metric-label">${{condition.charAt(0).toUpperCase() + condition.slice(1)}}:</span>
                            <span class="metric-value">✓ Tracking</span>
                        </div>`
                    ).join('')}}
                </div>
                
                <div class="metric-group">
                    <h5>Common Health Metrics</h5>
                    ${{this.renderMetric('Blood Pressure', commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic ? 
                        commonData.blood_pressure_systolic + '/' + commonData.blood_pressure_diastolic : 'N/A')}}
                    ${{this.renderMetric('Energy Level', commonData.energy_level ? commonData.energy_level + '/10' : 'N/A')}}
                    ${{this.renderMetric('Sleep Hours', commonData.sleep_hours || 'N/A')}}
                    ${{this.renderMetric('Sleep Quality', commonData.sleep_quality ? commonData.sleep_quality + '/5' : 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Additional Information</h5>
                    ${{this.renderMetric('Medications Taken', commonData.medications ? 'Yes' : 'No')}}
                    ${{this.renderMetric('Symptoms Reported', symptomsText)}}
                    ${{this.renderMetric('Notes', commonData.notes || 'None')}}
                    ${{this.renderMetric('Status', conditionData.status || 'Good')}}
                </div>
            </div>
        `;
    }}
    
    renderMetric(label, value) {{
        if (!value && value !== 0) return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">N/A</span></div>';
        return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">' + value + '</span></div>';
    }}
}}




class HypertensionHandler {{
    renderEntryHTML(entry) {{
        const status = entry.status || 'good';
        
        return `
            <tr>
                <td>
                    <strong>${{entry.patient_name}}</strong>
                    <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patient_id || 'N/A'}}</div>
                </td>
                <td>
                    <span class="condition-badge hypertension">Hypertension</span>
                </td>
                <td>
                    <div class="pain-indicator">
                        <span>N/A</span>
                        <div class="pain-bar">
                            <div class="pain-fill" style="width: 0%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${{status}}">${{status.toUpperCase()}}</span>
                </td>
                <td>N/A</td>
                <td>${{new Date(entry.created_at).toLocaleDateString()}}</td>
                <td>
                    <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                </td>
            </tr>
            <tr id="details-${{entry.id}}" style="display: none;">
                <td colspan="7">
                    <div class="entry-details">
                        <h4>Complete Health Metrics - ${{entry.patient_name}}</h4>
                        ${{this.getDetailedMetrics(entry)}}
                    </div>
                </td>
            </tr>
        `;
    }}
    
    getDetailedMetrics(entry) {{
        return `
            <div class="metrics-grid">
                <div class="metric-group">
                    <h5>Blood Pressure & Vitals</h5>
                    ${{this.renderMetric('Systolic BP', entry.blood_pressure_systolic ? entry.blood_pressure_systolic + ' mmHg' : 'N/A')}}
                    ${{this.renderMetric('Diastolic BP', entry.blood_pressure_diastolic ? entry.blood_pressure_diastolic + ' mmHg' : 'N/A')}}
                    ${{this.renderMetric('Heart Rate', 'N/A')}}
                    ${{this.renderMetric('Respiratory Rate', 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Daily Health Metrics</h5>
                    ${{this.renderMetric('Energy Level', entry.energy_level !== undefined ? entry.energy_level + '/10' : 'N/A')}}
                    ${{this.renderMetric('Sleep Hours', entry.sleep_hours !== undefined ? entry.sleep_hours + ' hours' : 'N/A')}}
                    ${{this.renderMetric('Sleep Quality', entry.sleep_quality !== undefined ? entry.sleep_quality + '/5' : 'N/A')}}
                    ${{this.renderMetric('Activity Level', 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Medications</h5>
                    ${{this.renderMetric('Morning', this.formatMedicationTime(entry.medications, 'morning'))}}
                    ${{this.renderMetric('Afternoon', this.formatMedicationTime(entry.medications, 'afternoon'))}}
                    ${{this.renderMetric('Evening', this.formatMedicationTime(entry.medications, 'evening'))}}
                    ${{this.renderMetric('Side Effects', this.formatSideEffects(entry.medications))}}
                </div>
                
                <div class="metric-group">
                    <h5>Symptoms & Notes</h5>
                    ${{this.renderMetric('Symptoms', this.formatSymptoms(entry.symptoms))}}
                    ${{this.renderMetric('Notes', entry.notes || 'N/A')}}
                    ${{this.renderMetric('Status', entry.status || 'N/A')}}
                </div>
            </div>
        `;
    }}
    
    formatMedicationTime(medications, time) {{
        if (!medications) return 'No';
        
        try {{
            const meds = typeof medications === 'string' ? JSON.parse(medications) : medications;
            return meds[time] ? 'Yes' : 'No';
        }} catch (e) {{
            return 'No';
        }}
    }}
    
    formatSideEffects(medications) {{
        if (!medications) return 'None';
        
        try {{
            const meds = typeof medications === 'string' ? JSON.parse(medications) : medications;
            return meds.sideEffects || meds.side_effects || 'None';
        }} catch (e) {{
            return 'None';
        }}
    }}
    
    formatSymptoms(symptoms) {{
        if (!symptoms) return 'None';
        
        try {{
            const symptomsObj = typeof symptoms === 'string' ? JSON.parse(symptoms) : symptoms;
            
            const activeSymptoms = [];
            
            if (symptomsObj.fatigue) activeSymptoms.push('Fatigue');
            if (symptomsObj.nausea) activeSymptoms.push('Nausea');
            if (symptomsObj.breathingIssues) activeSymptoms.push('Breathing Issues');
            if (symptomsObj.pain) activeSymptoms.push('Pain');
            if (symptomsObj.swelling) activeSymptoms.push('Swelling');
            if (symptomsObj.other) activeSymptoms.push('Other: ' + symptomsObj.other);
            
            return activeSymptoms.length > 0 ? activeSymptoms.join(', ') : 'None';
        }} catch (e) {{
            return 'None';
        }}
    }}
    
    renderMetric(label, value) {{
        if (!value && value !== 0) return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">N/A</span></div>';
        return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">' + value + '</span></div>';
    }}
}}




class HeartDiseaseHandler {{
    renderEntryHTML(entry) {{
        const status = entry.status || 'good';
        
        return `
            <tr>
                <td>
                    <strong>${{entry.patient_name}}</strong>
                    <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patient_id || 'N/A'}}</div>
                </td>
                <td>
                    <span class="condition-badge heart">Heart Disease</span>
                </td>
                <td>
                    <div class="pain-indicator">
                        <span>${{entry.chest_pain_level !== undefined ? entry.chest_pain_level + '/10' : 'N/A'}}</span>
                        <div class="pain-bar">
                            <div class="pain-fill" style="width: ${{entry.chest_pain_level !== undefined ? (entry.chest_pain_level * 10) : 0}}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${{status}}">${{status.toUpperCase()}}</span>
                </td>
                <td>${{entry.pain_location || 'N/A'}}</td>
                <td>${{new Date(entry.created_at).toLocaleDateString()}}</td>
                <td>
                    <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                </td>
            </tr>
            <tr id="details-${{entry.id}}" style="display: none;">
                <td colspan="7">
                    <div class="entry-details">
                        <h4>Complete Health Metrics - ${{entry.patient_name}}</h4>
                        ${{this.getDetailedMetrics(entry)}}
                    </div>
                </td>
            </tr>
        `;
    }}
    
    getDetailedMetrics(entry) {{
        return `
            <div class="metrics-grid">
                <div class="metric-group">
                    <h5>Heart & Blood Pressure</h5>
                    ${{this.renderMetric('Systolic BP', entry.blood_pressure_systolic ? entry.blood_pressure_systolic + ' mmHg' : 'N/A')}}
                    ${{this.renderMetric('Diastolic BP', entry.blood_pressure_diastolic ? entry.blood_pressure_diastolic + ' mmHg' : 'N/A')}}
                    ${{this.renderMetric('Chest Pain Level', entry.chest_pain_level !== undefined ? entry.chest_pain_level + '/10' : 'N/A')}}
                    ${{this.renderMetric('Pain Location', entry.pain_location || 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Daily Health Metrics</h5>
                    ${{this.renderMetric('Energy Level', entry.energy_level !== undefined ? entry.energy_level + '/10' : 'N/A')}}
                    ${{this.renderMetric('Sleep Hours', entry.sleep_hours !== undefined ? entry.sleep_hours + ' hours' : 'N/A')}}
                    ${{this.renderMetric('Sleep Quality', entry.sleep_quality !== undefined ? entry.sleep_quality + '/5' : 'N/A')}}
                    ${{this.renderMetric('Breathing Difficulty', entry.breathing_difficulty !== undefined ? entry.breathing_difficulty + '/10' : 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Weight & Swelling</h5>
                    ${{this.renderMetric('Weight', entry.weight || 'N/A')}}
                    ${{this.renderMetric('Swelling Level', this.formatSwellingLevel(entry.swelling_level))}}
                </div>
                
                <div class="metric-group">
                    <h5>Medications</h5>
                    ${{this.renderMetric('Morning', this.formatMedicationTime(entry.medications, 'morning'))}}
                    ${{this.renderMetric('Afternoon', this.formatMedicationTime(entry.medications, 'afternoon'))}}
                    ${{this.renderMetric('Evening', this.formatMedicationTime(entry.medications, 'evening'))}}
                    ${{this.renderMetric('Side Effects', this.formatSideEffects(entry.medications))}}
                </div>
                
                <div class="metric-group">
                    <h5>Symptoms & Notes</h5>
                    ${{this.renderMetric('Symptoms', this.formatSymptoms(entry.symptoms))}}
                    ${{this.renderMetric('Notes', entry.notes || 'N/A')}}
                    ${{this.renderMetric('Status', entry.status || 'N/A')}}
                </div>
            </div>
        `;
    }}
    
    formatSwellingLevel(level) {{
        if (level === undefined || level === null) return 'N/A';
        const levels = ['None', 'Mild', 'Moderate', 'Severe'];
        return levels[level] || 'N/A';
    }}
    
    formatMedicationTime(medications, time) {{
        if (!medications) return 'No';
        
        try {{
            const meds = typeof medications === 'string' ? JSON.parse(medications) : medications;
            return meds[time] ? 'Yes' : 'No';
        }} catch (e) {{
            return 'No';
        }}
    }}
    
    formatSideEffects(medications) {{
        if (!medications) return 'None';
        
        try {{
            const meds = typeof medications === 'string' ? JSON.parse(medications) : medications;
            return meds.sideEffects || meds.side_effects || 'None';
        }} catch (e) {{
            return 'None';
        }}
    }}
    
    formatSymptoms(symptoms) {{
        if (!symptoms) return 'None';
        
        try {{
            const symptomsObj = typeof symptoms === 'string' ? JSON.parse(symptoms) : symptoms;
            
            const activeSymptoms = [];
            
            if (symptomsObj.fatigue) activeSymptoms.push('Fatigue');
            if (symptomsObj.nausea) activeSymptoms.push('Nausea');
            if (symptomsObj.breathingIssues) activeSymptoms.push('Breathing Issues');
            if (symptomsObj.pain) activeSymptoms.push('Pain');
            if (symptomsObj.swelling) activeSymptoms.push('Swelling');
            if (symptomsObj.other) activeSymptoms.push('Other: ' + symptomsObj.other);
            
            return activeSymptoms.length > 0 ? activeSymptoms.join(', ') : 'None';
        }} catch (e) {{
            return 'None';
        }}
    }}
    
    renderMetric(label, value) {{
        if (!value && value !== 0) return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">N/A</span></div>';
        return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">' + value + '</span></div>';
    }}
}}



class KidneyHandler {{
    renderEntryHTML(entry) {{
        // ✅ Use FLAT fields directly (no common_data or condition_data nesting)
        const painLevel = entry.energy_level || 0;
        const status = entry.status || 'good';
        
        return `
            <tr>
                <td>
                    <strong>${{entry.patient_name}}</strong>
                    <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patient_id || 'N/A'}}</div>
                </td>
                <td>
                    <span class="condition-badge kidney">Kidney</span>
                </td>
                <td>
                    <div class="pain-indicator">
                        <span>${{painLevel}}/10</span>
                        <div class="pain-bar">
                            <div class="pain-fill" style="width: ${{painLevel * 10}}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${{status}}">${{status.toUpperCase()}}</span>
                </td>
                <td>${{entry.urgency_status || 'N/A'}}</td>
                <td>${{new Date(entry.submitted_at).toLocaleDateString()}}</td>
                <td>
                    <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                </td>
            </tr>
            <tr id="details-${{entry.id}}" style="display: none;">
                <td colspan="7">
                    <div class="entry-details">
                        <h4>Complete Health Metrics - ${{entry.patient_name}}</h4>
                        ${{this.getDetailedMetrics(entry)}}
                    </div>
                </td>
            </tr>
        `;
    }}
    
    getDetailedMetrics(entry) {{
        // ✅ All fields are FLAT at the top level
        return `
            <div class="metrics-grid">
                <div class="metric-group">
                    <h5>Vital Signs</h5>
                    ${{this.renderMetric('Blood Pressure', entry.blood_pressure_systolic && entry.blood_pressure_diastolic ? 
                        entry.blood_pressure_systolic + '/' + entry.blood_pressure_diastolic : 'N/A')}}
                    ${{this.renderMetric('Energy Level', entry.energy_level ? entry.energy_level + '/10' : 'N/A')}}
                    ${{this.renderMetric('Sleep Hours', entry.sleep_hours || 'N/A')}}
                    ${{this.renderMetric('Sleep Quality', entry.sleep_quality ? entry.sleep_quality + '/5' : 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Kidney Metrics</h5>
                    ${{this.renderMetric('Weight', entry.weight)}}
                    ${{this.renderMetric('Swelling Level', entry.swelling_level)}}
                    ${{this.renderMetric('Urine Output', entry.urine_output)}}
                    ${{this.renderMetric('Fluid Intake', entry.fluid_intake)}}
                </div>
                
                <div class="metric-group">
                    <h5>Symptoms</h5>
                    ${{this.renderMetric('Breathing Difficulty', entry.breathing_difficulty ? entry.breathing_difficulty + '/10' : 'N/A')}}
                    ${{this.renderMetric('Fatigue Level', entry.fatigue_level ? entry.fatigue_level + '/10' : 'N/A')}}
                    ${{this.renderMetric('Nausea Level', entry.nausea_level ? entry.nausea_level + '/10' : 'N/A')}}
                    ${{this.renderMetric('Itching Level', entry.itching_level ? entry.itching_level + '/10' : 'N/A')}}
                </div>

                <div class="metric-group">
                    <h5>Additional Info</h5>
                    ${{this.renderMedications(entry.medications)}}
                    ${{this.renderSymptoms(entry.symptoms)}}
                    ${{this.renderMetric('Notes', entry.notes)}}
                </div>
            </div>
        `;
    }}
    
    renderMetric(label, value) {{
        if (!value && value !== 0) return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">N/A</span></div>';
        return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">' + value + '</span></div>';
    }}
    
    renderMedications(medications) {{
        if (!medications) return '<div class="metric-row"><span class="metric-label">Medications:</span><span class="metric-value">N/A</span></div>';
        
        try {{
            const meds = typeof medications === 'string' ? JSON.parse(medications) : medications;
            let medText = '';
            if (meds.morning) medText += 'Morning ';
            if (meds.afternoon) medText += 'Afternoon ';
            if (meds.evening) medText += 'Evening';
            if (meds.sideEffects) medText += (medText ? ' | Side Effects: ' + meds.sideEffects : 'Side Effects: ' + meds.sideEffects);
            
            return '<div class="metric-row"><span class="metric-label">Medications:</span><span class="metric-value">' + (medText || 'None') + '</span></div>';
        }} catch (e) {{
            return '<div class="metric-row"><span class="metric-label">Medications:</span><span class="metric-value">Error parsing</span></div>';
        }}
    }}
    
    renderSymptoms(symptoms) {{
        if (!symptoms) return '<div class="metric-row"><span class="metric-label">Symptoms:</span><span class="metric-value">N/A</span></div>';
        
        try {{
            const symps = typeof symptoms === 'string' ? JSON.parse(symptoms) : symptoms;
            let symptomList = [];
            if (symps.fatigue) symptomList.push('Fatigue');
            if (symps.nausea) symptomList.push('Nausea');
            if (symps.breathingIssues) symptomList.push('Breathing Issues');
            if (symps.pain) symptomList.push('Pain');
            if (symps.swelling) symptomList.push('Swelling');
            if (symps.other) symptomList.push(symps.other);
            
            return '<div class="metric-row"><span class="metric-label">Symptoms:</span><span class="metric-value">' + 
                   (symptomList.length > 0 ? symptomList.join(', ') : 'None') + '</span></div>';
        }} catch (e) {{
            return '<div class="metric-row"><span class="metric-label">Symptoms:</span><span class="metric-value">Error parsing</span></div>';
        }}
    }}
}}








class CancerHandler {{
    renderEntryHTML(entry) {{
        // ✅ Use FLAT fields directly (no common_data or condition_data nesting)
        const painLevel = entry.pain_level || 0;
        const status = entry.status || 'good';
        
        return `
            <tr>
                <td>
                    <strong>${{entry.patient_name}}</strong>
                    <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patient_id || 'N/A'}}</div>
                </td>
                <td>
                    <span class="condition-badge cancer">Cancer</span>
                </td>
                <td>
                    <div class="pain-indicator">
                        <span>${{painLevel}}/10</span>
                        <div class="pain-bar">
                            <div class="pain-fill" style="width: ${{painLevel * 10}}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${{status}}">${{status.toUpperCase()}}</span>
                </td>
                <td>${{entry.urgency_status || 'N/A'}}</td>
                <td>${{new Date(entry.submitted_at).toLocaleDateString()}}</td>
                <td>
                    <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                </td>
            </tr>
            <tr id="details-${{entry.id}}" style="display: none;">
                <td colspan="7">
                    <div class="entry-details">
                        <h4>Complete Health Metrics - ${{entry.patient_name}}</h4>
                        ${{this.getDetailedMetrics(entry)}}
                    </div>
                </td>
            </tr>
        `;
    }}
    
    getDetailedMetrics(entry) {{
        // ✅ All fields are FLAT at the top level
        return `
            <div class="metrics-grid">
                <div class="metric-group">
                    <h5>Vital Signs</h5>
                    ${{this.renderMetric('Blood Pressure', entry.blood_pressure_systolic && entry.blood_pressure_diastolic ? 
                        entry.blood_pressure_systolic + '/' + entry.blood_pressure_diastolic : 'N/A')}}
                    ${{this.renderMetric('Energy Level', entry.energy_level ? entry.energy_level + '/10' : 'N/A')}}
                    ${{this.renderMetric('Sleep Hours', entry.sleep_hours || 'N/A')}}
                    ${{this.renderMetric('Sleep Quality', entry.sleep_quality ? entry.sleep_quality + '/5' : 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Cancer Metrics</h5>
                    ${{this.renderMetric('Pain Level', entry.pain_level ? entry.pain_level + '/10' : 'N/A')}}
                    ${{this.renderMetric('Pain Location', entry.pain_location)}}
                    ${{this.renderMetric('Side Effects', entry.side_effects ? entry.side_effects + '/10' : 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Additional Info</h5>
                    ${{this.renderMedications(entry.medications)}}
                    ${{this.renderSymptoms(entry.symptoms)}}
                    ${{this.renderMetric('Notes', entry.notes || 'None')}}
                    ${{this.renderMetric('Status', entry.status || 'Good')}}
                </div>
            </div>
        `;
    }}
    
    renderMedications(medications) {{
        if (!medications) return '<div class="metric-row"><span class="metric-label">Medications:</span><span class="metric-value">N/A</span></div>';
        
        try {{
            const meds = typeof medications === 'string' ? JSON.parse(medications) : medications;
            let medText = '';
            if (meds.morning) medText += 'Morning ';
            if (meds.afternoon) medText += 'Afternoon ';
            if (meds.evening) medText += 'Evening';
            if (meds.sideEffects) medText += (medText ? ' | Side Effects: ' + meds.sideEffects : 'Side Effects: ' + meds.sideEffects);
            
            return '<div class="metric-row"><span class="metric-label">Medications:</span><span class="metric-value">' + (medText || 'None') + '</span></div>';
        }} catch (e) {{
            return '<div class="metric-row"><span class="metric-label">Medications:</span><span class="metric-value">Error parsing</span></div>';
        }}
    }}
    
    renderSymptoms(symptoms) {{
        if (!symptoms) return '<div class="metric-row"><span class="metric-label">Symptoms:</span><span class="metric-value">N/A</span></div>';
        
        try {{
            const symps = typeof symptoms === 'string' ? JSON.parse(symptoms) : symptoms;
            let symptomList = [];
            if (symps.fatigue) symptomList.push('Fatigue');
            if (symps.nausea) symptomList.push('Nausea');
            if (symps.breathingIssues) symptomList.push('Breathing Issues');
            if (symps.pain) symptomList.push('Pain');
            if (symps.swelling) symptomList.push('Swelling');
            if (symps.other) symptomList.push(symps.other);
            
            return '<div class="metric-row"><span class="metric-label">Symptoms:</span><span class="metric-value">' + 
                   (symptomList.length > 0 ? symptomList.join(', ') : 'None') + '</span></div>';
        }} catch (e) {{
            return '<div class="metric-row"><span class="metric-label">Symptoms:</span><span class="metric-value">Error parsing</span></div>';
        }}
    }}
    
    renderMetric(label, value) {{
        if (!value && value !== 0) return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">N/A</span></div>';
        return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">' + value + '</span></div>';
    }}
}}




class GeneralHealthHandler {{
    renderEntryHTML(entry) {{
        // 🔍 ADD DEBUG TO SEE WHAT DATA WE'RE GETTING
        console.log("🟢 GENERAL HEALTH HANDLER DEBUG:");
        console.log("Entry received:", entry);
        console.log("Available fields:", Object.keys(entry));
        console.log("overall_wellbeing:", entry.overall_wellbeing);
        console.log("status:", entry.status);
        console.log("submitted_at:", entry.submitted_at);
        console.log("urgency_status:", entry.urgency_status);
        
        // ✅ Use FLAT fields directly (no condition_data or common_data nesting)
        const overallWellbeing = entry.overall_wellbeing || 0;
        const status = entry.status || 'good';
        
        return `
            <tr>
                <td>
                    <strong>${{entry.patient_name}}</strong>
                    <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patient_id || 'N/A'}}</div>
                </td>
                <td>
                    <span class="condition-badge abdominal" style="background: #8B5CF6;">General Health</span>
                </td>
                <td>
                    <div class="pain-indicator">
                        <span>${{overallWellbeing}}/10</span>
                        <div class="pain-bar">
                            <div class="pain-fill" style="width: ${{overallWellbeing * 10}}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${{status}}">${{status.toUpperCase()}}</span>
                </td>
                <td>${{entry.urgency_status || 'N/A'}}</td>
                <td>${{new Date(entry.submitted_at).toLocaleDateString()}}</td>
                <td>
                    <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                </td>
            </tr>
            <tr id="details-${{entry.id}}" style="display: none;">
                <td colspan="7">
                    <div class="entry-details">
                        <h4>Complete Health Metrics - ${{entry.patient_name}}</h4>
                        ${{this.getDetailedMetrics(entry)}}
                    </div>
                </td>
            </tr>
        `;
    }}
    
    getDetailedMetrics(entry) {{
        // ✅ All fields are FLAT at the top level
        return `
            <div class="metrics-grid">
                <div class="metric-group">
                    <h5>Health Overview</h5>
                    ${{this.renderMetric('Health Trend', entry.health_trend)}}
                    ${{this.renderMetric('Overall Wellbeing', entry.overall_wellbeing ? entry.overall_wellbeing + '/10' : 'N/A')}}
                    ${{this.renderMetric('Status', entry.status || 'Good')}}
                    ${{this.renderMetric('Urgency', entry.urgency_status || 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Primary Symptom</h5>
                    ${{this.renderMetric('Symptom Description', entry.primary_symptom_description)}}
                    ${{this.renderMetric('Symptom Severity', entry.primary_symptom_severity ? entry.primary_symptom_severity + '/10' : 'N/A')}}
                </div>
                
                <div class="metric-group">
                    <h5>Additional Information</h5>
                    ${{this.renderMetric('Notes', entry.notes || 'None')}}
                    ${{this.renderMetric('Submission Date', entry.submission_date)}}
                    ${{this.renderMetric('Condition Type', entry.condition_type || 'general_health')}}
                </div>
            </div>
        `;
    }}
    
    renderMetric(label, value) {{
        if (!value && value !== 0) return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">N/A</span></div>';
        return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">' + value + '</span></div>';
    }}
}}






class PrenatalHandler {{
    renderEntryHTML(entry) {{
        // Read from FLAT FIELDS, not from common_data/condition_data
        const fetalMovement = entry.fetal_movement || 'normal';
        const status = entry.status || 'good';
        
        return `
            <tr>
                <td>
                    <strong>${{entry.patient_name}}</strong>
                    <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patient_id || 'N/A'}}</div>
                    <div style="font-size: 0.8rem; color: #666;">${{entry.gestational_age || 'N/A'}}</div>
                </td>
                <td>
                    <span class="condition-badge prenatal">Prenatal</span>
                    ${{entry.high_risk ? '<span class="high-risk-badge">High Risk</span>' : ''}}
                </td>
                <td>
                    <div class="fetal-movement-indicator">
                        <span>${{this.formatMetricValue(fetalMovement)}}</span>
                        <div class="movement-status movement-${{fetalMovement}}"></div>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${{status}}">${{status.toUpperCase()}}</span>
                </td>
                <td>${{entry.gestational_age || 'N/A'}}</td>
                <td>${{entry.submission_date ? new Date(entry.submission_date).toLocaleDateString() : 'N/A'}}</td>
                <td>
                    <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                </td>
            </tr>
            <tr id="details-${{entry.id}}" style="display: none;">
                <td colspan="7">
                    <div class="entry-details">
                        <h4>Prenatal Care Details - ${{entry.patient_name}}</h4>
                        ${{this.getDetailedMetrics(entry)}}
                    </div>
                </td>
            </tr>
        `;
    }}
    
    getDetailedMetrics(entry) {{
        return `
            <div class="metrics-grid">
                <div class="metric-group">
                    <h5>Maternal Vital Signs</h5>
                    ${{this.renderMetric('Temperature', entry.maternal_temperature, '°C')}}
                    ${{this.renderMetric('Blood Pressure', 
                        entry.blood_pressure_systolic && entry.blood_pressure_diastolic ? 
                        entry.blood_pressure_systolic + '/' + entry.blood_pressure_diastolic + ' mmHg' : 'N/A')}}
                    ${{this.renderMetric('Heart Rate', entry.maternal_heart_rate, ' bpm')}}
                    ${{this.renderMetric('Respiratory Rate', entry.respiratory_rate, '/min')}}
                    ${{this.renderMetric('Oxygen Saturation', entry.oxygen_saturation, '%')}}
                    ${{this.renderMetric('Weight', entry.weight, ' kg')}}
                </div>
                
                <div class="metric-group">
                    <h5>Maternal Symptoms</h5>
                    ${{this.renderMetric('Swelling (Edema)', entry.edema)}}
                    ${{this.renderMetric('Swelling Location', entry.edema_location)}}
                    ${{this.renderMetric('Headache', entry.headache)}}
                    ${{this.renderMetric('Visual Disturbances', entry.visual_disturbances, '', true)}}
                    ${{this.renderMetric('Upper Abdominal Pain', entry.epigastric_pain, '', true)}}
                    ${{this.renderMetric('Nausea Level', entry.nausea_level)}}
                    ${{this.renderMetric('Vomiting Episodes', entry.vomiting_episodes, ' times')}}
                </div>
                
                <div class="metric-group">
                    <h5>Fetal Movement & Activity</h5>
                    ${{this.renderMetric('Fetal Movement', entry.fetal_movement)}}
                    ${{this.renderMetric('Kick Count', entry.movement_count, ' movements')}}
                    ${{this.renderMetric('Movement Duration', entry.movement_duration, ' min')}}
                </div>
                
                <div class="metric-group">
                    <h5>Contractions</h5>
                    ${{this.renderMetric('Contractions Present', entry.contractions, '', true)}}
                    ${{this.renderMetric('Contraction Frequency', entry.contraction_frequency, ' min apart')}}
                    ${{this.renderMetric('Contraction Duration', entry.contraction_duration, ' seconds')}}
                    ${{this.renderMetric('Contraction Intensity', entry.contraction_intensity)}}
                </div>
                
                <div class="metric-group">
                    <h5>Vaginal Symptoms</h5>
                    ${{this.renderMetric('Vaginal Bleeding', entry.vaginal_bleeding)}}
                    ${{this.renderMetric('Bleeding Color', entry.bleeding_color)}}
                    ${{this.renderMetric('Fluid Leak', entry.fluid_leak, '', true)}}
                    ${{this.renderMetric('Fluid Color', entry.fluid_color)}}
                    ${{this.renderMetric('Fluid Amount', entry.fluid_amount)}}
                </div>
                
                <div class="metric-group">
                    <h5>Urinary & Gastrointestinal</h5>
                    ${{this.renderMetric('Urinary Frequency', entry.urinary_frequency)}}
                    ${{this.renderMetric('Painful Urination', entry.dysuria)}}
                    ${{this.renderMetric('Urinary Incontinence', entry.urinary_incontinence, '', true)}}
                    ${{this.renderMetric('Appetite', entry.appetite)}}
                    ${{this.renderMetric('Heartburn', entry.heartburn)}}
                    ${{this.renderMetric('Constipation', entry.constipation)}}
                </div>
                
                <div class="metric-group">
                    <h5>Medication & Additional Info</h5>
                    ${{this.renderMetric('Medications Taken', entry.medications_taken, '', true)}}
                    ${{this.renderMetric('Missed Medications', entry.missed_medications)}}
                    ${{this.renderMetric('Gestational Age', entry.gestational_age)}}
                    ${{this.renderMetric('High Risk Pregnancy', entry.high_risk, '', true)}}
                    ${{this.renderMetric('Additional Notes', entry.additional_notes)}}
                </div>
                
                <div class="metric-group full-width">
                    <h5>Submission Information</h5>
                    ${{this.renderMetric('Status', entry.status)}}
                    ${{this.renderMetric('Submission Date', new Date(entry.submission_date || entry.submitted_at).toLocaleString())}}
                </div>
            </div>
        `;
    }}
    
    renderMetric(label, value, unit = '', isBoolean = false) {{
        if (value === undefined || value === null || value === '') return '';
        
        let displayValue;
        if (isBoolean) {{
            displayValue = value === true ? 'Yes' : value === false ? 'No' : 'N/A';
        }} else {{
            displayValue = value === true ? 'Yes' : 
                          value === false ? 'No' : 
                          value;
        }}
        
        const fullValue = unit && displayValue !== 'N/A' ? `${{displayValue}}${{unit}}` : displayValue;
        
        return `
            <div class="metric-row">
                <span class="metric-label">${{label}}:</span>
                <span class="metric-value">${{fullValue}}</span>
            </div>
        `;
    }}
    
    formatMetricValue(value) {{
        if (typeof value === 'boolean') return value ? 'Yes' : 'No';
        if (typeof value === 'string') {{
            if (value === 'blood_tinged') return 'Blood-tinged';
            return value.split('_').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
        }}
        return value;
    }}
}}












        // Handler registry
const conditionHandlers = {{
    abdominal: new AbdominalHandler(),
    cesarean: new CesareanHandler(),
    diabetes: new DiabetesHandler(),
    hypertension: new HypertensionHandler(),
    orthopedic: new OrthopedicHandler(),
    cardiac: new CardiacHandler(),
    urological: new UrologicalHandler(),
    heart: new HeartDiseaseHandler(),
    general_health: new GeneralHealthHandler(),
    burn_care: new BurnCareHandler(),
    gynecologic: new GynecologicHandler(),
    bariatric: new BariatricHandler(),
    lifelong: new LifelongHandler(),
    kidney: new KidneyHandler(),
    cancer: new CancerHandler(),
    prenatal: new PrenatalHandler()
}};

console.log("🔍 === DASHBOARD DEBUG - HANDLERS REGISTERED ===");
console.log("🔍 Available handlers:", Object.keys(conditionHandlers));

// Function to process and display entries
function displayEntries(entries) {{
    console.log("🔍 === PROCESSING ENTRIES ===");
    console.log("🔍 Total entries received:", entries.length);
    
    const tableBody = document.getElementById('entries-table-body');
    tableBody.innerHTML = '';
    
    entries.forEach((entry, index) => {{
        console.log(`🔍 === ENTRY ${{index + 1}} ===`);
        console.log("🔍 Full entry data:", entry);
        console.log("🔍 Condition type:", entry.condition_type);
        console.log("🔍 Blood pressure check:", {{
            systolic: entry.blood_pressure_systolic,
            diastolic: entry.blood_pressure_diastolic
        }});
        console.log("🔍 Temperature:", entry.maternal_temperature);
        console.log("🔍 All entry keys:", Object.keys(entry));
        
        const handler = conditionHandlers[entry.condition_type];
        if (handler) {{
            console.log("🔍 Handler found:", entry.condition_type);
            const html = handler.renderEntryHTML(entry);
            tableBody.innerHTML += html;
        }} else {{
            console.log("❌ No handler found for:", entry.condition_type);
        }}
    }});
}}












// 🕵️ STEP-BY-STEP DEBUG
console.log("🚨 STEP 1: After conditionHandlers");
console.log("🚨 conditionHandlers.burn_care:", conditionHandlers.burn_care);

console.log("🚨 STEP 2: Before error check");
console.log("=== ERROR CHECK ===");
try {{
    if (conditionHandlers.burn_care) {{
        console.log("🚨 STEP 3: Inside if condition");
        const burnCareHandler = conditionHandlers.burn_care;
        console.log("BurnCareHandler object:", burnCareHandler);
        console.log("Available methods:", Object.getOwnPropertyNames(burnCareHandler));
    }} else {{
        console.log("❌ conditionHandlers.burn_care is falsy");
    }}
}} catch (error) {{
    console.log("❌ Error checking BurnCareHandler:", error.message);
}}

console.log("🚨 STEP 4: After error check");


// 🔧 ADD THIS DEBUG CODE RIGHT HERE:
console.log("🔧 DEBUG: Checking BurnCareHandler instance");
console.log("🔧 BurnCareHandler instance:", conditionHandlers.burn_care);
console.log("🔧 BurnCareHandler constructor:", conditionHandlers.burn_care?.constructor?.name);
console.log("🔧 Available methods on burn_care handler:", Object.getOwnPropertyNames(conditionHandlers.burn_care));
console.log("🔧 Has renderEntryHTML?", 'renderEntryHTML' in conditionHandlers.burn_care);
console.log("🔧 Has testMethod?", 'testMethod' in conditionHandlers.burn_care);

// Also test one other handler for comparison
console.log("🔧 For comparison - GynecologicHandler methods:", Object.getOwnPropertyNames(conditionHandlers.gynecologic));







let allEntries = [];
function toggleDetails(entryId) {{
    const details = document.getElementById('details-' + entryId);
    if (details) {{
        const isCurrentlyHidden = details.style.display === 'none';
        details.style.display = isCurrentlyHidden ? 'table-row' : 'none';
        
        const links = document.querySelectorAll('.detail-view');
        links.forEach(function(link) {{
            if (link.getAttribute('onclick') && link.getAttribute('onclick').includes(entryId)) {{
                link.textContent = isCurrentlyHidden ? 'Hide Details' : 'View Details';
            }}
        }});
    }}
}}

// 🔍 DEBUG: Add this function to test data when it loads
function renderDashboard(entries) {{
    console.log("🔍 Total entries:", entries.length);
    console.log("🔍 First few entries:", entries.slice(0, 3));
    console.log("🔍 All condition types found:", [...new Set(entries.map(function(e) {{ return e.condition_type; }}))]);
    
    // 🔍 DEBUG: Detailed burn care analysis
    const burnCareEntries = entries.filter(function(e) {{ return e.condition_type === 'burn_care'; }});
    console.log("Burn care entries in data:", burnCareEntries.length);
    if (burnCareEntries.length > 0) {{
        console.log("Sample burn care entry:", burnCareEntries[0]);
        // 🔍 DEBUG: TEST HANDLER DIRECTLY
        console.log("Testing burn care handler canHandle:", 
            conditionHandlers.burn_care?.canHandle?.(burnCareEntries[0]));
    }} else {{
        console.log("❌ No burn care entries found in dataset");
    }}
    
    // 🔍 DEBUG: Test all handlers against their data
    Object.keys(conditionHandlers).forEach(function(condition) {{
        const conditionEntries = entries.filter(function(e) {{ return e.condition_type === condition; }});
        console.log("Condition " + condition + ": " + conditionEntries.length + " entries, handler test:", 
            conditionEntries.length > 0 ? 
            conditionHandlers[condition]?.canHandle?.(conditionEntries[0]) : 'No data');
    }});
    
    // Call your existing functions
    renderStats(entries);
    renderEntries(entries);
}}





    
 async function loadHealthData() {{
    
    try {{
        console.log("🔄 Fetching health data from individual endpoints...");

        const responses = await Promise.all([
            fetch('/api/health-progress/abdominal/entries'),
            fetch('/api/health-progress/cesarean/entries'),
            fetch('/api/health-progress/diabetes/entries'),
            fetch('/api/health-progress/hypertension/entries'),
            fetch('/api/health-progress/orthopedic/entries'),
            fetch('/api/health-progress/cardiac/entries'),
            fetch('/api/health-progress/urological/entries'),
            fetch('/api/health-progress/heart/entries'),
            fetch('/api/health-progress/general/entries'),
            fetch('/api/health-progress/burn-care/entries'),
            fetch('/api/health-progress/gynecologic/entries'),
            fetch('/api/health-progress/bariatric-entries'),
            fetch('/api/health-progress/lifelong/entries'),
            fetch('/api/health-progress/kidney/entries'),  
            fetch('/api/health-progress/cancer/entries'),
            fetch('/api/prenatal/entries'),

        ]);

   
        const [
            abdominalRes, cesareanRes, diabetesRes, hypertensionRes,
            orthopedicRes, cardiacRes, urologicalRes, heartRes, generalRes, 
            burnCareRes, gynecologicRes, bariatricRes, lifelongRes, kidneyRes, cancerRes, prenatalRes
        ] = responses;

        // ✅ DEBUG: Check what the APIs actually return - AFTER variable definitions
        console.log("=== EXACT API RESPONSE ===");
        
        const abdominalData = await abdominalRes.json();
        const cesareanData = await cesareanRes.json();
        const diabetesData = await diabetesRes.json();
        const hypertensionData = await hypertensionRes.json();
        const orthopedicData = await orthopedicRes.json();
        const cardiacData = await cardiacRes.json();
        const urologicalData = await urologicalRes.json();
        const heartData = await heartRes.json();
        const generalData = await generalRes.json();
        const burnCareData = await burnCareRes.json();
        const gynecologicData = await gynecologicRes.json();
        const bariatricData = await bariatricRes.json();
        const lifelongData = await lifelongRes.json();
        const kidneyData = await kidneyRes.json();
        const cancerData = await cancerRes.json();
        const prenatalData = await prenatalRes.json();



        console.log("🔍 PRENATAL API DEBUG:");
console.log("🔍 Prenatal response status:", prenatalRes.status);
console.log("🔍 Prenatal data:", prenatalData);
console.log("🔍 Prenatal entries:", prenatalData.entries);
console.log("🔍 Prenatal entries length:", prenatalData.entries ? prenatalData.entries.length : 0);





     

        allEntries = [
            ...(abdominalData.entries ? abdominalData.entries.map(e => ({{ ...e, condition_type: 'abdominal' }})) : []),
            ...(cesareanData.entries ? cesareanData.entries.map(e => ({{ ...e, condition_type: 'cesarean' }})) : []),
            ...(diabetesData.entries ? diabetesData.entries.map(e => ({{ ...e, condition_type: 'diabetes' }})) : []),
            ...(hypertensionData.entries ? hypertensionData.entries.map(e => ({{ ...e, condition_type: 'hypertension' }})) : []),
            ...(orthopedicData.entries ? orthopedicData.entries.map(e => ({{ ...e, condition_type: 'orthopedic' }})) : []),
            ...(cardiacData.entries ? cardiacData.entries.map(e => ({{ ...e, condition_type: 'cardiac' }})) : []),
            ...(urologicalData.entries ? urologicalData.entries.map(e => ({{ ...e, condition_type: 'urological' }})) : []),
            ...(heartData.entries ? heartData.entries.map(e => ({{ ...e, condition_type: 'heart' }})) : []),
            ...(generalData.entries ? generalData.entries.map(e => ({{ ...e, condition_type: 'general_health' }})) : []),
            ...(burnCareData.entries ? burnCareData.entries.map(e => ({{ ...e, condition_type: 'burn_care' }})) : []),
            ...(gynecologicData.entries ? gynecologicData.entries.map(e => ({{ ...e, condition_type: 'gynecologic' }})) : []),
            ...(bariatricData.entries ? bariatricData.entries.map(e => ({{ ...e, condition_type: 'bariatric' }})) : []),
            ...(lifelongData.entries ? lifelongData.entries.map(e => ({{ ...e, condition_type: 'lifelong' }})) : []),
            ...(kidneyData.entries ? kidneyData.entries.map(e => ({{ ...e, condition_type: 'kidney' }})) : []), 
            ...(cancerData.entries ? cancerData.entries.map(e => ({{ ...e, condition_type: 'cancer' }})) : []),
            ...(prenatalData.entries ? prenatalData.entries.map(e => ({{ ...e, condition_type: 'prenatal' }})) : [])
        ];

       

        renderDashboard(allEntries);
    }} catch (error) {{
        console.error("❌ Error loading health data:", error);
        showError('Failed to load health data: ' + error.message);
    }}
}}







function filterEntries() {{
    const conditionFilter = document.getElementById('conditionFilter').value;
    const dateFilter = document.getElementById('dateFilter').value;
    
    let filtered = allEntries;
    
    // Filter by condition
    if (conditionFilter !== 'all') {{
        filtered = filtered.filter(entry => entry.condition_type === conditionFilter);
    }}
    
    // Simple date filter - just check if the date string exists in any format
    if (dateFilter) {{
        // Convert filter date to DD/MM/YYYY format for comparison
        const [year, month, day] = dateFilter.split('-');
        const ddMmYyyy = `${{day}}/${{month}}/${{year}}`;
        
        filtered = filtered.filter(entry => {{
            const entryDate = entry.submission_date || entry.created_at?.split('T')[0] || '';
            return entryDate.includes(dateFilter) || entryDate.includes(ddMmYyyy);
        }});
    }}
    
    renderEntries(filtered);
}}



























function renderDashboard(entries) {{
    renderStats(entries);
    renderEntries(entries);
}}










function renderStats(entries) {{
    const statsGrid = document.getElementById('statsGrid');
    const totalPatients = entries.length;
    const orthopedicCount = entries.filter(entry => entry.condition_type === 'orthopedic').length;
    
    statsGrid.innerHTML = `
        <div class="stat-card">
            <div class="stat-number">${{totalPatients}}</div>
            <div class="stat-label">Total Patients</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${{orthopedicCount}}</div>
            <div class="stat-label">Orthopedic</div>
        </div>
    `;
}}











// 🕵️ TASK: Check BurnCareHandler methods
console.log("=== BURN CARE HANDLER METHODS ===");
if (conditionHandlers && conditionHandlers.burn_care) {{
    const burnCareHandler = conditionHandlers.burn_care;
    console.log("BurnCareHandler object:", burnCareHandler);
    console.log("Available methods:", Object.getOwnPropertyNames(burnCareHandler));
    console.log("has renderEntryHTML:", typeof burnCareHandler.renderEntryHTML === 'function');
    console.log("has render:", typeof burnCareHandler.render === 'function');
}} else {{
    console.log("❌ BurnCareHandler not found in conditionHandlers");
}}



function renderEntries(entries) {{
    const container = document.getElementById('entriesContainer');
    
    if (entries.length === 0) {{
        container.innerHTML = '<div class="loading">No health entries found</div>';
        return;
    }}

    let html = `
        <table class="entries-table">
            <thead>
                <tr>
                    <th>Patient</th>
                    <th>Condition</th>
                    <th>Key Metric</th>
                    <th>Status</th>
                    <th>Timeframe</th>
                    <th>Last Updated</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    entries.forEach((entry) => {{
        // ✅ ADD DEBUG FOR PRENATAL ENTRIES
        if (entry.condition_type === 'prenatal') {{
            console.log("🔍 PRENATAL ENTRY DATA FOR HANDLER:", entry);
            console.log("🔍 Blood pressure fields:", {{
                systolic: entry.blood_pressure_systolic,
                diastolic: entry.blood_pressure_diastolic
            }});
            console.log("🔍 Temperature:", entry.maternal_temperature);
            console.log("🔍 All prenatal fields:", Object.keys(entry));
        }}
        
        const handler = conditionHandlers[entry.condition_type];
        if (handler && handler.renderEntryHTML) {{
            html += handler.renderEntryHTML(entry);
        }} else {{
            // Fallback for unknown condition types
            html += `
                <tr>
                    <td>
                        <strong>${{entry.patient_name}}</strong>
                        <div style="font-size: 0.8rem; color: #666;">ID: ${{entry.patient_id || 'N/A'}}</div>
                    </td>
                    <td>
                        <span class="condition-badge abdominal">${{entry.condition_type}}</span>
                    </td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>${{new Date(entry.submitted_at).toLocaleDateString()}}</td>
                    <td>
                        <span class="detail-view" onclick="toggleDetails('${{entry.id}}')">View Details</span>
                    </td>
                </tr>
            `;
        }}
    }});

    html += '</tbody></table>';
    container.innerHTML = html;
}}



















// Start loading data when page loads
document.addEventListener('DOMContentLoaded', function() {{
    console.log("=== PAGE LOADED ===");
    loadHealthData();
}});


 
                   

    

       function renderDashboard(entries) {{
            console.log("🔍 First few entries:", entries.slice(0, 3));
            console.log("🔍 All condition types found:", [...new Set(entries.map(e => e.condition_type))]);
            
            renderStats(entries);
            renderEntries(entries);
        }}

        


       function renderStats(entries) {{
    const statsGrid = document.getElementById('statsGrid');
    const totalPatients = entries.length;
    const abdominalCount = entries.filter(entry => entry.condition_type === 'abdominal').length;
    const cesareanCount = entries.filter(entry => entry.condition_type === 'cesarean').length;
    const diabetesCount = entries.filter(entry => entry.condition_type === 'diabetes').length;
    const hypertensionCount = entries.filter(entry => entry.condition_type === 'hypertension').length;
    const orthopedicCount = entries.filter(entry => entry.condition_type === 'orthopedic').length;
    const cardiacCount = entries.filter(entry => entry.condition_type === 'cardiac').length;              
    const urologicalCount = entries.filter(entry => entry.condition_type === 'urological').length;         
    const heartCount = entries.filter(entry => entry.condition_type === 'heart').length;
    const generalCount = entries.filter(entry => entry.condition_type === 'general_health').length;  
    const burnCareCount = entries.filter(entry => entry.condition_type === 'burn_care').length;
    const gynecologicCount = entries.filter(entry => entry.condition_type === 'gynecologic').length;
    const bariatricCount = entries.filter(entry => entry.condition_type === 'bariatric').length; 
    const lifelongCount = entries.filter(entry => entry.condition_type === 'lifelong').length;
    const kidneyCount = entries.filter(entry => entry.condition_type === 'kidney').length;
    const cancerCount = entries.filter(entry => entry.condition_type === 'cancer').length;
    const prenatalCount = entries.filter(entry => entry.condition_type === 'prenatal').length;

    statsGrid.innerHTML = `
        <div class="stat-card">
            <div class="stat-number">${{totalPatients}}</div>
            <div class="stat-label">Total Patients</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${{abdominalCount}}</div>
            <div class="stat-label">Abdominal</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${{cesareanCount}}</div>
            <div class="stat-label">Cesarean</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${{diabetesCount}}</div>
            <div class="stat-label">Diabetes</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${{hypertensionCount}}</div>
            <div class="stat-label">Hypertension</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${{orthopedicCount}}</div>
            <div class="stat-label">Orthopedic</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${{cardiacCount}}</div>
            <div class="stat-label">Cardiac</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${{urologicalCount}}</div>
            <div class="stat-label">Urological</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${{heartCount}}</div>
            <div class="stat-label">Heart Disease</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${{generalCount}}</div>
            <div class="stat-label">General Health</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${{burnCareCount}}</div>
            <div class="stat-label">Burn Care</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${{gynecologicCount}}</div>
            <div class="stat-label">Gynecologic</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${{bariatricCount}}</div>
            <div class="stat-label">Bariatric</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${{lifelongCount}}</div>
            <div class="stat-label">Lifelong</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${{kidneyCount}}</div>
            <div class="stat-label">Kidney</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${{cancerCount}}</div>
            <div class="stat-label">Cancer</div>
        </div>

        <div class="stat-card">
            <div class="stat-number">${{prenatalCount}}</div>
            <div class="stat-label">Prenatal</div>
        </div>



    `;
}}





       





        function filterEntries() {{
    console.log("=== 🚨 FILTER DEBUG START ===");
    
    const conditionFilter = document.getElementById('conditionFilter');
    const dateFilter = document.getElementById('dateFilter');
    
    console.log("1. Filter elements found:", {{
        conditionFilter: !!conditionFilter,
        dateFilter: !!dateFilter
    }});
    
    if (!conditionFilter) {{
        console.error("❌ conditionFilter element not found!");
        return;
    }}
    
    const filterValue = conditionFilter.value;
    const dateValue = dateFilter.value;
    
    console.log("2. Filter values:", {{
        condition: filterValue,
        date: dateValue
    }});
    
    console.log("3. allEntries status:", {{
        exists: !!allEntries,
        type: typeof allEntries,
        length: allEntries ? allEntries.length : 'undefined'
    }});
    
    if (!allEntries || !Array.isArray(allEntries)) {{
        console.error("❌ allEntries is not a valid array");
        showError('Data not loaded properly. Please refresh the page.');
        return;
    }}
    
    console.log("4. Current allEntries content:", {{
        total: allEntries.length,
        conditionTypes: [...new Set(allEntries.map(e => e.condition_type))],
        sampleEntries: allEntries.slice(0, 3).map(e => ({{
            id: e.id,
            condition_type: e.condition_type,
            patient_name: e.patient_name
        }}))
    }});
    

















    let filtered = allEntries;
    
    // Filter by condition
    if (filterValue !== 'all') {{
        const before = filtered.length;
        filtered = filtered.filter(entry => {{
            const matches = entry.condition_type === filterValue;
            console.log(`   Checking ${{entry.condition_type}} === ${{filterValue}}: ${{matches}}`);
            return matches;
        }});
        console.log(`5. Condition filter result: ${{before}} → ${{filtered.length}}`);
    }}
    




















    // Filter by date
    if (dateValue) {{
        const before = filtered.length;
        filtered = filtered.filter(entry => {{
            if (!entry.created_at) {{
                console.log(`   Entry ${{entry.id}} has no created_at`);
                return false;
            }}
            const entryDate = new Date(entry.created_at).toISOString().split('T')[0];
            const matches = entryDate === dateValue;
            console.log(`   Date check: ${{entryDate}} === ${{dateValue}}: ${{matches}}`);
            return matches;
        }});
        console.log(`6. Date filter result: ${{before}} → ${{filtered.length}}`);
    }}
    
    console.log("7. Final filtered data:", {{
        count: filtered.length,
        entries: filtered.map(e => ({{
            id: e.id,
            condition_type: e.condition_type,
            patient_name: e.patient_name
        }}))
    }});
    
    console.log("=== 🚨 FILTER DEBUG END ===");
    
    renderEntries(filtered);
}}




    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

# Include all your existing routers (no debug prints)
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(appointments_router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(progress_router)
app.include_router(chatbot_router, prefix="/api/chatbot", tags=["Chatbot"])
app.include_router(transcription_router, prefix="/api/telemedicine", tags=["Telemedicine"])
app.include_router(health_tracker_router, prefix="/api/health-tracker", tags=["Health Tracker"])
app.include_router(staff_router, prefix="/staff", tags=["Staff Pages"])
app.include_router(medical_record_router, prefix="/api/medical-record", tags=["Medical Record"])
app.include_router(abdominal_router, prefix="/api/progress", tags=["Progress"])
app.include_router(general_router, prefix="/api/health-progress/general", tags=["general-health"])
app.include_router(bariatric_router, prefix="/api/health-progress", tags=["Health Progress"])
app.include_router(burn_care_router, prefix="/api/health-progress", tags=["Health Progress"])
app.include_router(cardiac_router, prefix="/api/health-progress", tags=["Health Progress"])
app.include_router(cesarean_router, prefix="/api/health-progress", tags=["Health Progress"])
app.include_router(gynecologic_router, prefix="/api/health-progress", tags=["Health Progress"])
app.include_router(orthopedic_router, prefix="/api/health-progress", tags=["Health Progress"])
app.include_router(urological_router, prefix="/api/health-progress", tags=["Health Progress"])
app.include_router(lifelong_router, prefix="/api/health-progress", tags=["Health Progress"])
app.include_router(diabetes_router, prefix="/api/health-progress/diabetes", tags=["diabetes"])
app.include_router(hypertension_router, prefix="/api/health-progress/hypertension", tags=["hypertension"])
app.include_router(skin_analysis_router, prefix="/api/skin-analysis", tags=["Skin Analysis"]) 
app.include_router(heart_router, prefix="/api/health-progress/heart", tags=["Heart Disease"])
app.include_router(kidney_router, prefix="/api/health-progress/kidney", tags=["Kidney Disease"])
app.include_router(cancer_router, prefix="/api/health-progress/cancer", tags=["Cancer"])
app.include_router(prenatal_router, prefix="/api/prenatal", tags=["Prenatal"])
app.include_router(postnatal_router, prefix="/api/postnatal", tags=["Postnatal"])


# Optional events (keep these)
@app.on_event("startup")
async def startup_event():
    print("Healthcare Management API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    print("Healthcare Management API shutting down...")