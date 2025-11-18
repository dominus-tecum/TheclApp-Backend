// lifelong-handler.js - COMPREHENSIVE handler for ALL lifelong chronic condition fields
export class LifelongHandler {
    getKeyMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // VITAL SIGNS - Always show these if available
        if (commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic) {
            metrics.push({ label: 'Blood Pressure', value: commonData.blood_pressure_systolic + '/' + commonData.blood_pressure_diastolic + ' mmHg' });
        }
        
        // ENERGY & SLEEP - Core wellness indicators
        if (commonData.energy_level !== undefined) {
            metrics.push({ label: 'Energy', value: commonData.energy_level + '/10' });
        }
        if (commonData.sleep_hours !== undefined) {
            metrics.push({ label: 'Sleep', value: commonData.sleep_hours + ' hrs' });
        }
        
        // CONDITION-SPECIFIC CRITICAL METRICS
        // Diabetes - Blood glucose is critical
        if (conditionData.blood_glucose) {
            metrics.push({ label: 'Blood Glucose', value: conditionData.blood_glucose + ' mg/dL' });
        }
        
        // Heart Disease - Chest pain is critical
        if (conditionData.chest_pain_level !== undefined && conditionData.chest_pain_level > 0) {
            metrics.push({ label: 'Chest Pain', value: conditionData.chest_pain_level + '/10' });
        }
        
        // Cancer - Pain level is critical
        if (conditionData.pain_level !== undefined && conditionData.pain_level > 0) {
            metrics.push({ label: 'Pain Level', value: conditionData.pain_level + '/10' });
        }
        
        // Kidney Disease - Swelling and urine output are critical
        if (conditionData.swelling_level !== undefined && conditionData.swelling_level > 0) {
            metrics.push({ label: 'Swelling', value: this.formatSwellingLevel(conditionData.swelling_level) });
        }
        
        // HYPERTENSION - Blood pressure is the key metric (already included above)
        
        return metrics;
    }
    
    getDetailedMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // PATIENT IDENTIFICATION
        metrics.push({ label: 'Patient ID', value: entry.patient_id || 'N/A' });
        metrics.push({ label: 'Submission Date', value: entry.submission_date || 'N/A' });
        
        // ========== VITAL SIGNS SECTION ==========
        metrics.push({ label: '---', value: 'VITAL SIGNS' });
        
        if (commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic) {
            const bpStatus = this.assessBloodPressure(commonData.blood_pressure_systolic, commonData.blood_pressure_diastolic);
            metrics.push({ label: 'Blood Pressure', value: commonData.blood_pressure_systolic + '/' + commonData.blood_pressure_diastolic + ' mmHg ' + bpStatus });
        }
        if (commonData.energy_level !== undefined) {
            metrics.push({ label: 'Energy Level', value: commonData.energy_level + '/10' });
        }
        if (commonData.sleep_hours !== undefined) {
            metrics.push({ label: 'Sleep Hours', value: commonData.sleep_hours + ' hours' });
        }
        if (commonData.sleep_quality !== undefined) {
            metrics.push({ label: 'Sleep Quality', value: commonData.sleep_quality + '/5' });
        }
        
        // ========== HYPERTENSION SPECIFIC METRICS ==========
        // Hypertension primarily tracks blood pressure with additional context
        if (this.isHypertensionTracked(conditionData, commonData)) {
            metrics.push({ label: '---', value: 'HYPERTENSION METRICS' });
            
            if (commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic) {
                const bpCategory = this.getBloodPressureCategory(commonData.blood_pressure_systolic, commonData.blood_pressure_diastolic);
                metrics.push({ label: 'Blood Pressure Category', value: bpCategory });
                
                // Add BP trends if we had historical data
                metrics.push({ label: 'Monitoring Focus', value: 'Blood Pressure Control' });
            }
            
            // Hypertension-relevant symptoms
            if (commonData.symptoms) {
                const htSymptoms = [];
                const symptoms = commonData.symptoms;
                
                if (symptoms.headache) htSymptoms.push('Headache');
                if (symptoms.dizziness) htSymptoms.push('Dizziness');
                if (symptoms.vision_changes) htSymptoms.push('Vision Changes');
                if (symptoms.chest_pain) htSymptoms.push('Chest Pain');
                
                if (htSymptoms.length > 0) {
                    metrics.push({ label: 'Hypertension Symptoms', value: htSymptoms.join(', ') });
                }
            }
        }
        
        // ========== MEDICATIONS SECTION ==========
        if (commonData.medications) {
            metrics.push({ label: '---', value: 'MEDICATIONS' });
            
            const meds = commonData.medications;
            if (meds.morning !== undefined) {
                metrics.push({ label: 'Morning Medications', value: meds.morning ? '✅ Taken' : '❌ Missed' });
            }
            if (meds.afternoon !== undefined) {
                metrics.push({ label: 'Afternoon Medications', value: meds.afternoon ? '✅ Taken' : '❌ Missed' });
            }
            if (meds.evening !== undefined) {
                metrics.push({ label: 'Evening Medications', value: meds.evening ? '✅ Taken' : '❌ Missed' });
            }
            if (meds.side_effects) {
                metrics.push({ label: 'Medication Side Effects', value: meds.side_effects });
            }
        }
        
        // ========== SYMPTOMS SECTION ==========
        if (commonData.symptoms) {
            metrics.push({ label: '---', value: 'SYMPTOMS' });
            
            const symptoms = commonData.symptoms;
            const activeSymptoms = [];
            
            if (symptoms.fatigue) activeSymptoms.push('😴 Fatigue');
            if (symptoms.nausea) activeSymptoms.push('🤢 Nausea');
            if (symptoms.breathing_issues) activeSymptoms.push('😮‍💨 Breathing Issues');
            if (symptoms.pain) activeSymptoms.push('😣 Pain');
            if (symptoms.swelling) activeSymptoms.push('🦵 Swelling');
            
            if (activeSymptoms.length > 0) {
                metrics.push({ label: 'Reported Symptoms', value: activeSymptoms.join(', ') });
            } else {
                metrics.push({ label: 'Reported Symptoms', value: 'None reported' });
            }
            
            if (symptoms.other) {
                metrics.push({ label: 'Other Symptoms', value: symptoms.other });
            }
        }
        
        // ========== DIABETES SPECIFIC METRICS ==========
        if (conditionData.blood_glucose) {
            metrics.push({ label: '---', value: 'DIABETES METRICS' });
            metrics.push({ label: 'Blood Glucose', value: conditionData.blood_glucose + ' mg/dL' });
            
            // Add glucose level assessment
            const glucoseLevel = parseInt(conditionData.blood_glucose);
            if (!isNaN(glucoseLevel)) {
                let status = 'Normal';
                if (glucoseLevel < 70) status = '⚠️ Low';
                else if (glucoseLevel > 180) status = '⚠️ High';
                else if (glucoseLevel > 140) status = 'Elevated';
                metrics.push({ label: 'Glucose Status', value: status });
            }
        }
        
        // ========== HEART DISEASE SPECIFIC METRICS ==========
        if (conditionData.chest_pain_level !== undefined || conditionData.heartWeight) {
            metrics.push({ label: '---', value: 'HEART DISEASE METRICS' });
            
            if (conditionData.chest_pain_level !== undefined) {
                metrics.push({ label: 'Chest Pain Level', value: conditionData.chest_pain_level + '/10' });
            }
            if (conditionData.pain_location && conditionData.pain_location !== 'none') {
                metrics.push({ label: 'Pain Location', value: this.formatPainLocation(conditionData.pain_location) });
            }
            if (conditionData.weight) {
                metrics.push({ label: 'Daily Weight', value: conditionData.weight });
            }
            if (conditionData.swelling_level !== undefined) {
                metrics.push({ label: 'Swelling Level', value: this.formatSwellingLevel(conditionData.swelling_level) });
            }
            if (conditionData.breathing_difficulty !== undefined) {
                metrics.push({ label: 'Breathing Difficulty', value: conditionData.breathing_difficulty + '/10' });
            }
            if (conditionData.activity_level) {
                metrics.push({ label: 'Activity Level', value: this.formatActivityLevel(conditionData.activity_level) });
            }
        }
        
        // ========== CANCER SPECIFIC METRICS ==========
        if (conditionData.cancer_pain_level !== undefined || conditionData.side_effects !== undefined) {
            metrics.push({ label: '---', value: 'CANCER METRICS' });
            
            if (conditionData.pain_level !== undefined) {
                metrics.push({ label: 'Pain Level', value: conditionData.pain_level + '/10' });
            }
            if (conditionData.pain_location) {
                metrics.push({ label: 'Pain Location', value: conditionData.pain_location });
            }
            if (conditionData.side_effects !== undefined) {
                metrics.push({ label: 'Treatment Side Effects', value: conditionData.side_effects + '/10' });
            }
            if (conditionData.activity_level) {
                metrics.push({ label: 'Activity Level', value: this.formatActivityLevel(conditionData.activity_level) });
            }
        }
        
        // ========== KIDNEY DISEASE SPECIFIC METRICS ==========
        if (conditionData.kidney_weight || conditionData.urine_output) {
            metrics.push({ label: '---', value: 'KIDNEY DISEASE METRICS' });
            
            if (conditionData.weight) {
                metrics.push({ label: 'Daily Weight', value: conditionData.weight });
            }
            if (conditionData.swelling_level !== undefined) {
                metrics.push({ label: 'Swelling Level', value: this.formatSwellingLevel(conditionData.swelling_level) });
            }
            if (conditionData.urine_output) {
                metrics.push({ label: 'Urine Output', value: this.formatUrineOutput(conditionData.urine_output) });
            }
            if (conditionData.fluid_intake) {
                metrics.push({ label: 'Fluid Intake', value: conditionData.fluid_intake + ' cups' });
            }
            if (conditionData.breathing_difficulty !== undefined) {
                metrics.push({ label: 'Breathing Difficulty', value: conditionData.breathing_difficulty + '/10' });
            }
            if (conditionData.fatigue_level !== undefined) {
                metrics.push({ label: 'Fatigue Level', value: conditionData.fatigue_level + '/10' });
            }
            if (conditionData.nausea_level !== undefined) {
                metrics.push({ label: 'Nausea Level', value: conditionData.nausea_level + '/10' });
            }
            if (conditionData.itching_level !== undefined) {
                metrics.push({ label: 'Itching Level', value: conditionData.itching_level + '/10' });
            }
        }
        
        // ========== NOTES & STATUS ==========
        metrics.push({ label: '---', value: 'ADDITIONAL INFORMATION' });
        
        if (commonData.notes) {
            metrics.push({ label: 'Patient Notes', value: commonData.notes });
        }
        if (conditionData.status) {
            metrics.push({ label: 'Health Status', value: this.formatMetricValue(conditionData.status) });
        }
        
        // Tracked conditions
        const trackedConditions = this.getTrackedConditions(conditionData, commonData);
        if (trackedConditions.length > 0) {
            metrics.push({ label: 'Tracked Conditions', value: trackedConditions.join(', ') });
        }
        
        return metrics;
    }
    
    isHypertensionTracked(conditionData, commonData) {
        // Hypertension is tracked if blood pressure is monitored and no other specific conditions are present
        // OR if it's explicitly selected in selected_conditions
        const hasOtherConditions = conditionData.blood_glucose || 
                                 conditionData.chest_pain_level !== undefined ||
                                 conditionData.pain_level !== undefined ||
                                 conditionData.kidney_weight;
        
        return commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic && !hasOtherConditions;
    }
    
    getTrackedConditions(conditionData, commonData) {
        const trackedConditions = [];
        
        if (conditionData.blood_glucose) trackedConditions.push('Diabetes');
        if (conditionData.chest_pain_level !== undefined || conditionData.heartWeight) trackedConditions.push('Heart Disease');
        if (conditionData.cancer_pain_level !== undefined || conditionData.side_effects !== undefined) trackedConditions.push('Cancer');
        if (conditionData.kidney_weight || conditionData.urine_output) trackedConditions.push('Kidney Disease');
        
        // Hypertension is tracked if blood pressure is monitored but no other specific conditions
        if (this.isHypertensionTracked(conditionData, commonData)) {
            trackedConditions.push('Hypertension');
        }
        
        return trackedConditions;
    }
    
    assessBloodPressure(systolic, diastolic) {
        const sys = parseInt(systolic);
        const dia = parseInt(diastolic);
        
        if (isNaN(sys) || isNaN(dia)) return '';
        
        if (sys >= 180 || dia >= 120) return '🚨 HYPERTENSIVE CRISIS';
        if (sys >= 140 || dia >= 90) return '⚠️ STAGE 2 HYPERTENSION';
        if (sys >= 130 || dia >= 80) return '⚠️ STAGE 1 HYPERTENSION';
        if (sys >= 120) return '↑ ELEVATED';
        
        return '✅ NORMAL';
    }
    
    getBloodPressureCategory(systolic, diastolic) {
        const sys = parseInt(systolic);
        const dia = parseInt(diastolic);
        
        if (isNaN(sys) || isNaN(dia)) return 'Unknown';
        
        if (sys < 120 && dia < 80) return 'Normal';
        if (sys < 130 && dia < 80) return 'Elevated';
        if (sys < 140 && dia < 90) return 'Stage 1 Hypertension';
        if (sys >= 140 || dia >= 90) return 'Stage 2 Hypertension';
        if (sys >= 180 || dia >= 120) return 'Hypertensive Crisis';
        
        return 'Unknown';
    }
    
    renderEntryHTML(entry) {
        const keyMetrics = this.getKeyMetrics(entry);
        const detailedMetrics = this.getDetailedMetrics(entry);
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        const trackedConditions = this.getTrackedConditions(conditionData, commonData);
        
        return `
            <div class="entry-header">
                <h3>${entry.patient_name || 'Unknown Patient'}</h3>
                <span class="condition-badge lifelong">Lifelong: ${trackedConditions.join(', ') || 'General Health'}</span>
            </div>
            <div class="entry-content">
                <div class="key-metrics">
                    <h4>🩺 Key Health Indicators</h4>
                    ${this.formatMetricsHTML(keyMetrics)}
                </div>
                <div class="detailed-metrics">
                    <h4>📊 Comprehensive Health Assessment</h4>
                    ${this.formatMetricsHTML(detailedMetrics)}
                </div>
            </div>
            <div class="entry-footer">
                <span class="timestamp">Recorded: ${new Date(entry.created_at).toLocaleString()}</span>
            </div>
        `;
    }
    
    formatMetricsHTML(metrics) {
        if (!metrics || metrics.length === 0) {
            return '<div class="no-metrics">No health metrics recorded</div>';
        }
        
        return metrics.map(metric => {
            if (metric.label === '---') {
                return `<div class="metric-section-divider"><strong>${metric.value}</strong></div>`;
            }
            return `
                <div class="metric-item">
                    <span class="metric-label">${metric.label}:</span>
                    <span class="metric-value">${metric.value}</span>
                </div>
            `;
        }).join('');
    }
    
    formatMetricValue(value) {
        if (typeof value === 'boolean') return value ? 'Yes' : 'No';
        if (typeof value === 'string') {
            return value.split('_').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
        }
        return value;
    }
    
    formatPainLocation(location) {
        const locations = {
            'none': 'No Pain',
            'chest': 'Chest',
            'upper_back': 'Upper Back', 
            'arm_jaw': 'Arm/Jaw',
            'other': 'Other Location'
        };
        return locations[location] || location;
    }
    
    formatActivityLevel(level) {
        const levels = {
            'bed_rest': 'Bed Rest',
            'light': 'Light Activity',
            'normal': 'Normal Activity',
            'active': 'Active'
        };
        return levels[level] || level;
    }
    
    formatSwellingLevel(level) {
        const levels = {
            0: 'None',
            1: 'Mild',
            2: 'Moderate', 
            3: 'Severe'
        };
        return levels[level] || 'Unknown';
    }
    
    formatUrineOutput(output) {
        const outputs = {
            'less': 'Less than usual',
            'normal': 'Normal amount', 
            'more': 'More than usual'
        };
        return outputs[output] || output;
    }
}