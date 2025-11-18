// burn-care-handler.js - Complete Burn Care Progress Handler for Web Dashboard
export class BurnCareHandler {{
    renderEntryHTML(entry) {{
        const commonData = entry.common_data || {{}};
        const conditionData = entry.condition_data || {{}};
        const painLevel = commonData.pain_level || 0;
        const status = conditionData.status || 'good';
        
        return `
            <tr>
                <td>
                    <strong>${entry.patient_name}</strong>
                    <div style="font-size: 0.8rem; color: #666;">ID: ${entry.patient_id || 'N/A'}</div>
                </td>
                <td>
                    <span class="condition-badge burn_care">Burn Care</span>
                </td>
                <td>
                    <div class="pain-indicator">
                        <span>${painLevel}/10</span>
                        <div class="pain-bar">
                            <div class="pain-fill" style="width: ${painLevel * 10}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${status}">${status.toUpperCase()}</span>
                </td>
                <td>${new Date(entry.created_at).toLocaleDateString()}</td>
                <td>
                    <span class="detail-view" onclick="toggleDetails('${entry.id}')">View Details</span>
                </td>
            </tr>
            <tr id="details-${entry.id}" style="display: none;">
                <td colspan="6">
                    <div class="entry-details">
                        <h4>Complete Burn Care Metrics - ${entry.patient_name}</h4>
                        ${this.getDetailedMetrics(entry)}
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
                    ${this.renderMetric('Temperature', commonData.temperature ? commonData.temperature + '°C' : 'N/A')}
                    ${this.renderMetric('Heart Rate', commonData.heart_rate ? commonData.heart_rate + ' bpm' : 'N/A')}
                    ${this.renderMetric('Respiratory Rate', commonData.respiratory_rate ? commonData.respiratory_rate + '/min' : 'N/A')}
                    ${this.renderMetric('Oxygen Saturation', commonData.oxygen_saturation ? commonData.oxygen_saturation + '%' : 'N/A')}
                    ${this.renderMetric('Blood Pressure', commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic ? 
                        commonData.blood_pressure_systolic + '/' + commonData.blood_pressure_diastolic : 'N/A')}
                </div>
                
                <div class="metric-group">
                    <h5>Pain Assessment</h5>
                    ${this.renderMetric('Pain Level', commonData.pain_level ? commonData.pain_level + '/10' : 'N/A')}
                    ${this.renderMetric('Itching Level', conditionData.itching)}
                </div>
                
                <div class="metric-group">
                    <h5>Wound Assessment</h5>
                    ${this.renderMetric('Wound Appearance', conditionData.wound_appearance)}
                    ${this.renderMetric('Wound Discharge', conditionData.drainage)}
                    ${this.renderMetric('Scar Appearance', conditionData.scar_appearance)}
                </div>

                <div class="metric-group">
                    <h5>Function & Mobility</h5>
                    ${this.renderMetric('ROM Exercises', conditionData.rom_exercises !== undefined ? (conditionData.rom_exercises ? 'Yes' : 'No') : 'N/A')}
                    ${this.renderMetric('Joint Tightness', conditionData.joint_tightness)}
                    ${this.renderMetric('Mobility Level', conditionData.mobility)}
                    ${this.renderMetric('Compression Garment', conditionData.compression_garment !== undefined ? (conditionData.compression_garment ? 'Yes' : 'No') : 'N/A')}
                </div>

                <div class="metric-group">
                    <h5>Nutrition</h5>
                    ${this.renderMetric('Protein Intake', conditionData.protein_intake ? conditionData.protein_intake + ' grams' : 'N/A')}
                    ${this.renderMetric('Fluid Intake', conditionData.fluid_intake ? conditionData.fluid_intake + ' mL' : 'N/A')}
                </div>
            </div>
            
            ${conditionData.additional_notes ? `
                <div class="clinical-notes">
                    <h5>Clinical Notes</h5>
                    <p>${conditionData.additional_notes}</p>
                </div>
            ` : ''}

            ${this.getCriticalAlerts(entry).length > 0 ? `
                <div class="alerts-section">
                    <h5>Clinical Alerts</h5>
                    ${this.getCriticalAlerts(entry).map(alert => `
                        <div class="alert alert-${alert.type}">
                            ${alert.message}
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        `;
    }}

    renderMetric(label, value) {{
        if (!value && value !== 0) return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">N/A</span></div>';
        return '<div class="metric-row"><span class="metric-label">' + label + ':</span><span class="metric-value">' + value + '</span></div>';
    }}

    getWoundAssessmentMetrics(entry) {{
        const conditionData = entry.condition_data || {{}};
        let metrics = [];
        
        if (conditionData.wound_appearance) {{
            metrics.push({{ 
                label: 'Wound Appearance', 
                value: conditionData.wound_appearance,
                severity: this.getWoundSeverity(conditionData.wound_appearance)
            }});
        }}
        if (conditionData.drainage) {{
            metrics.push({{ 
                label: 'Drainage', 
                value: conditionData.drainage,
                severity: conditionData.drainage === 'purulent' ? 'high' : 'low'
            }});
        }}
        if (conditionData.itching) {{
            metrics.push({{ 
                label: 'Itching', 
                value: conditionData.itching,
                severity: this.getSeverityLevel(conditionData.itching)
            }});
        }}
        
        return metrics;
    }}

    getRehabilitationMetrics(entry) {{
        const conditionData = entry.condition_data || {{}};
        let metrics = [];
        
        if (conditionData.rom_exercises !== undefined) {{
            metrics.push({{ label: 'ROM Exercises', value: conditionData.rom_exercises ? 'Performed' : 'Not Performed' }});
        }}
        if (conditionData.joint_tightness) {{
            metrics.push({{ label: 'Joint Tightness', value: conditionData.joint_tightness }});
        }}
        if (conditionData.mobility) {{
            metrics.push({{ label: 'Mobility Level', value: conditionData.mobility }});
        }}
        if (conditionData.compression_garment !== undefined) {{
            metrics.push({{ label: 'Compression Garment', value: conditionData.compression_garment ? 'Wearing' : 'Not Wearing' }});
        }}
        
        return metrics;
    }}
    
    getNutritionMetrics(entry) {{
        const conditionData = entry.condition_data || {{}};
        let metrics = [];
        
        if (conditionData.protein_intake) {{
            metrics.push({{ label: 'Protein Intake', value: conditionData.protein_intake + ' grams' }});
        }}
        if (conditionData.fluid_intake) {{
            metrics.push({{ label: 'Fluid Intake', value: conditionData.fluid_intake + ' mL' }});
        }}
        
        return metrics;
    }}

    getLabMetrics(entry) {{
        const conditionData = entry.condition_data || {{}};
        let metrics = [];
        
        if (conditionData.white_blood_cell_count) {{
            metrics.push({{ label: 'WBC Count', value: conditionData.white_blood_cell_count }});
        }}
        if (conditionData.crp_levels) {{
            metrics.push({{ label: 'CRP Levels', value: conditionData.crp_levels }});
        }}
        if (conditionData.culture_results) {{
            metrics.push({{ label: 'Culture Results', value: conditionData.culture_results }});
        }}
        
        return metrics;
    }}

    getWoundDetailMetrics(entry) {{
        const conditionData = entry.condition_data || {{}};
        let metrics = [];
        
        if (conditionData.burn_surface_area) {{
            metrics.push({{ label: 'Burn Surface Area', value: conditionData.burn_surface_area }});
        }}
        if (conditionData.wound_odor !== undefined) {{
            metrics.push({{ label: 'Wound Odor', value: conditionData.wound_odor ? 'Present' : 'None' }});
        }}
        if (conditionData.eschar_formation !== undefined) {{
            metrics.push({{ label: 'Eschar Formation', value: conditionData.eschar_formation ? 'Yes' : 'No' }});
        }}
        if (conditionData.granulation_tissue !== undefined) {{
            metrics.push({{ label: 'Granulation Tissue', value: conditionData.granulation_tissue ? 'Present' : 'Absent' }});
        }}
        
        return metrics;
    }}
    
    getWoundSeverity(appearance) {{
        const severityMap = {{
            'pink': 'low',
            'red': 'medium',
            'black': 'high',
            'yellow': 'high',
            'mixed': 'medium'
        }};
        return severityMap[appearance] || 'low';
    }}
    
    getSeverityLevel(value) {{
        const severityMap = {{
            'none': 'none',
            'mild': 'low', 
            'moderate': 'medium',
            'severe': 'high'
        }};
        return severityMap[value] || 'low';
    }}
    
    // Critical Burn Care Alert System
    getCriticalAlerts(entry) {{
        const commonData = entry.common_data || {{}};
        const conditionData = entry.condition_data || {{}};
        let alerts = [];
        
        // Temperature alerts
        const temp = parseFloat(commonData.temperature) || 0;
        if (temp > 38.5) {{
            alerts.push({{ type: 'critical', message: 'High fever - possible infection' }});
        }} else if (temp > 37.5) {{
            alerts.push({{ type: 'warning', message: 'Elevated temperature - monitor closely' }});
        }}
        
        // Respiratory alerts
        const respiratoryRate = parseInt(commonData.respiratory_rate) || 0;
        if (respiratoryRate > 24) {{
            alerts.push({{ type: 'warning', message: 'Increased respiratory rate' }});
        }}
        
        const oxygenSat = parseInt(commonData.oxygen_saturation) || 0;
        if (oxygenSat < 92) {{
            alerts.push({{ type: 'critical', message: 'Low oxygen saturation' }});
        }}
        
        // Wound infection alerts
        if (conditionData.drainage === 'purulent') {{
            alerts.push({{ type: 'critical', message: 'Purulent drainage - possible infection' }});
        }}
        if (conditionData.wound_appearance === 'black') {{
            alerts.push({{ type: 'critical', message: 'Black tissue - possible necrosis' }});
        }}
        if (conditionData.wound_odor) {{
            alerts.push({{ type: 'warning', message: 'Foul odor - monitor for infection' }});
        }}
        
        // Pain alerts
        const painLevel = commonData.pain_level || 0;
        if (painLevel > 8) {{
            alerts.push({{ type: 'warning', message: 'Severe pain reported' }});
        }}
        
        // Itching alerts
        if (conditionData.itching === 'severe') {{
            alerts.push({{ type: 'warning', message: 'Severe itching - consider medication' }});
        }}
        
        // Lab value alerts
        if (conditionData.white_blood_cell_count > 12000) {{
            alerts.push({{ type: 'warning', message: 'Elevated WBC - possible infection' }});
        }}
        
        return alerts;
    }}

    // Format metrics for display
    formatMetricValue(value) {{
        if (typeof value === 'boolean') return value ? 'Yes' : 'No';
        if (typeof value === 'string') {{
            if (value.includes('_')) {{
                return value.split('_').map(word => 
                    word.charAt(0).toUpperCase() + word.slice(1)
                ).join(' ');
            }}
            return value.charAt(0).toUpperCase() + value.slice(1);
        }}
        return value;
    }}
}}