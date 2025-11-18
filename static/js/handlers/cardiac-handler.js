// cardiac-handler.js - Reads ALL cardiac fields
export class CardiacHandler {
    getKeyMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // COMMON DATA FIELDS - CRITICAL VITALS
        if (commonData.temperature) {
            metrics.push({ label: 'Temperature', value: commonData.temperature + '°C' });
        }
        if (commonData.pain_level !== undefined) {
            metrics.push({ label: 'Pain Level', value: commonData.pain_level + '/10' });
        }
        if (commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic) {
            metrics.push({ label: 'Blood Pressure', value: commonData.blood_pressure_systolic + '/' + commonData.blood_pressure_diastolic });
        }
        if (commonData.heart_rate) {
            metrics.push({ label: 'Heart Rate', value: commonData.heart_rate + ' bpm' });
        }
        if (commonData.oxygen_saturation) {
            metrics.push({ label: 'O₂ Saturation', value: commonData.oxygen_saturation + '%' });
        }
        
        // CARDIAC SPECIFIC FIELDS
        if (conditionData.cardiac_rhythm) {
            metrics.push({ label: 'Cardiac Rhythm', value: this.formatMetricValue(conditionData.cardiac_rhythm) });
        }
        if (conditionData.rhythm_stable !== undefined) {
            metrics.push({ label: 'Rhythm Stable', value: conditionData.rhythm_stable ? 'Yes' : 'No' });
        }
        if (conditionData.breathing_effort) {
            metrics.push({ label: 'Breathing', value: this.formatMetricValue(conditionData.breathing_effort) });
        }
        
        return metrics;
    }
    
    getDetailedMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // VITAL SIGNS (COMMON DATA)
        if (commonData.temperature) {
            metrics.push({ label: 'Temperature', value: commonData.temperature + '°C' });
        }
        if (commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic) {
            metrics.push({ label: 'Blood Pressure', value: commonData.blood_pressure_systolic + '/' + commonData.blood_pressure_diastolic });
        }
        if (commonData.heart_rate) {
            metrics.push({ label: 'Heart Rate', value: commonData.heart_rate + ' bpm' });
        }
        if (commonData.respiratory_rate) {
            metrics.push({ label: 'Respiratory Rate', value: commonData.respiratory_rate + '/min' });
        }
        if (commonData.oxygen_saturation) {
            metrics.push({ label: 'Oxygen Saturation', value: commonData.oxygen_saturation + '%' });
        }
        if (commonData.pain_level !== undefined) {
            metrics.push({ label: 'Pain Level', value: commonData.pain_level + '/10' });
        }
        
        // CARDIAC RHYTHM & ELECTRICAL ACTIVITY
        if (conditionData.cardiac_rhythm) {
            metrics.push({ label: 'Cardiac Rhythm', value: this.formatMetricValue(conditionData.cardiac_rhythm) });
        }
        if (conditionData.rhythm_stable !== undefined) {
            metrics.push({ label: 'Rhythm Stable', value: conditionData.rhythm_stable ? 'Yes' : 'No' });
        }
        
        // RESPIRATORY FUNCTION & OXYGENATION
        if (conditionData.breathing_effort) {
            metrics.push({ label: 'Breathing Effort', value: this.formatMetricValue(conditionData.breathing_effort) });
        }
        if (conditionData.oxygen_therapy !== undefined) {
            metrics.push({ label: 'Oxygen Therapy', value: conditionData.oxygen_therapy ? 'Yes' : 'No' });
        }
        if (conditionData.oxygen_flow) {
            metrics.push({ label: 'Oxygen Flow Rate', value: conditionData.oxygen_flow + ' L/min' });
        }
        if (conditionData.incentive_spirometer) {
            metrics.push({ label: 'Incentive Spirometer', value: this.formatMetricValue(conditionData.incentive_spirometer) });
        }
        if (conditionData.cough_effectiveness) {
            metrics.push({ label: 'Cough Effectiveness', value: this.formatMetricValue(conditionData.cough_effectiveness) });
        }
        
        // CHEST TUBE DRAINAGE
        if (conditionData.has_chest_tube !== undefined) {
            metrics.push({ label: 'Chest Tube Present', value: conditionData.has_chest_tube ? 'Yes' : 'No' });
        }
        if (conditionData.chest_tube_output) {
            metrics.push({ label: 'Chest Tube Output (24h)', value: conditionData.chest_tube_output + ' mL' });
        }
        if (conditionData.chest_drain_color) {
            metrics.push({ label: 'Drain Color', value: this.formatMetricValue(conditionData.chest_drain_color) });
        }
        if (conditionData.chest_drain_consistency) {
            metrics.push({ label: 'Drain Consistency', value: this.formatMetricValue(conditionData.chest_drain_consistency) });
        }
        
        // FLUID BALANCE & RENAL FUNCTION
        if (conditionData.urine_output) {
            metrics.push({ label: 'Urine Output', value: conditionData.urine_output + ' mL/hr' });
        }
        if (conditionData.fluid_balance) {
            metrics.push({ label: 'Fluid Balance (24h)', value: conditionData.fluid_balance + ' mL' });
        }
        
        // WOUND & INCISION ASSESSMENT
        if (conditionData.sternal_wound_condition) {
            metrics.push({ label: 'Sternal Wound', value: this.formatMetricValue(conditionData.sternal_wound_condition) });
        }
        if (conditionData.graft_wound_condition) {
            metrics.push({ label: 'Graft Site Wound', value: this.formatMetricValue(conditionData.graft_wound_condition) });
        }
        if (conditionData.wound_discharge_type) {
            metrics.push({ label: 'Wound Discharge Type', value: this.formatMetricValue(conditionData.wound_discharge_type) });
        }
        if (conditionData.wound_tenderness) {
            metrics.push({ label: 'Wound Tenderness', value: this.formatMetricValue(conditionData.wound_tenderness) });
        }
        
        // NEUROLOGICAL STATUS
        if (conditionData.consciousness_level) {
            metrics.push({ label: 'Level of Consciousness', value: this.formatMetricValue(conditionData.consciousness_level) });
        }
        if (conditionData.orientation) {
            metrics.push({ label: 'Orientation', value: this.formatMetricValue(conditionData.orientation) });
        }
        if (conditionData.limb_movement) {
            metrics.push({ label: 'Limb Movement', value: this.formatMetricValue(conditionData.limb_movement) });
        }
        
        // MOBILITY & ACTIVITY
        if (conditionData.mobility_level) {
            metrics.push({ label: 'Mobility Level', value: this.formatMetricValue(conditionData.mobility_level) });
        }
        if (conditionData.ambulation_distance) {
            metrics.push({ label: 'Ambulation Distance', value: this.formatMetricValue(conditionData.ambulation_distance) });
        }
        
        // PAIN ASSESSMENT
        if (conditionData.pain_location) {
            metrics.push({ label: 'Pain Location', value: this.formatMetricValue(conditionData.pain_location) });
        }
        
        // EMOTIONAL & PSYCHOLOGICAL STATE
        if (conditionData.mood_state) {
            metrics.push({ label: 'Mood State', value: this.formatMetricValue(conditionData.mood_state) });
        }
        if (conditionData.sleep_quality) {
            metrics.push({ label: 'Sleep Quality', value: this.formatMetricValue(conditionData.sleep_quality) });
        }
        
        // ADDITIONAL INFORMATION
        if (conditionData.additional_notes) {
            metrics.push({ label: 'Additional Notes', value: conditionData.additional_notes });
        }
        if (conditionData.status) {
            metrics.push({ label: 'Clinical Status', value: this.formatMetricValue(conditionData.status) });
        }
        
        return metrics;
    }
    
    renderEntryHTML(entry) {
        const keyMetrics = this.getKeyMetrics(entry);
        const detailedMetrics = this.getDetailedMetrics(entry);
        
        return `
            <div class="entry-header">
                <h3>${entry.patient_name || 'Unknown Patient'}</h3>
                <span class="condition-badge cardiac">Cardiac Surgery</span>
            </div>
            <div class="entry-content">
                <div class="key-metrics">
                    <h4>Critical Metrics</h4>
                    ${this.formatMetricsHTML(keyMetrics)}
                </div>
                <div class="detailed-metrics">
                    <h4>Comprehensive Assessment</h4>
                    ${this.formatMetricsHTML(detailedMetrics)}
                </div>
            </div>
            <div class="entry-footer">
                <span class="timestamp">${new Date(entry.created_at).toLocaleString()}</span>
                ${entry.submission_date ? `<span class="submission-date">Submitted: ${entry.submission_date}</span>` : ''}
            </div>
        `;
    }
    
    formatMetricsHTML(metrics) {
        if (!metrics || metrics.length === 0) {
            return '<div class="no-metrics">No metrics recorded</div>';
        }
        return metrics.map(metric => `
            <div class="metric-item">
                <span class="metric-label">${metric.label}:</span>
                <span class="metric-value">${metric.value}</span>
            </div>
        `).join('');
    }
    
    formatMetricValue(value) {
        if (typeof value === 'boolean') return value ? 'Yes' : 'No';
        if (typeof value === 'string') {
            // Handle special cases for better readability
            const specialCases = {
                'normal_sinus': 'Normal Sinus',
                'atrial_fib': 'Atrial Fibrillation',
                'serosanguinous': 'Serosanguinous',
                'assisted_walking': 'Assisted Walking',
                'disoriented_time': 'Disoriented to Time',
                'disoriented_place': 'Disoriented to Place',
                'disoriented_person': 'Disoriented to Person'
            };
            
            if (specialCases[value]) {
                return specialCases[value];
            }
            
            return value.split('_').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
        }
        return value;
    }
    
    // Additional helper method for cardiac-specific analysis
    getCardiacSummary(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        const summary = [];
        
        // Rhythm stability warning
        if (conditionData.rhythm_stable === false) {
            summary.push('Unstable cardiac rhythm requires attention');
        }
        
        // Respiratory distress
        if (conditionData.breathing_effort && conditionData.breathing_effort.includes('distress')) {
            summary.push('Respiratory distress noted');
        }
        
        // High chest tube output
        const chestOutput = parseInt(conditionData.chest_tube_output || '0');
        if (chestOutput > 100) {
            summary.push(`High chest tube output: ${chestOutput}mL/24h`);
        }
        
        // Low urine output
        const urineOutput = parseInt(conditionData.urine_output || '0');
        if (urineOutput < 30) {
            summary.push(`Low urine output: ${urineOutput}mL/hr`);
        }
        
        return summary;
    }
}