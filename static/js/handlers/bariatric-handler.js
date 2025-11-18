// bariatric-handler.js - Comprehensive Bariatric Surgery Progress Handler
export class BariatricHandler {
    getKeyMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // CRITICAL BARIATRIC METRICS
        if (commonData.temperature) {
            metrics.push({ label: 'Temperature', value: commonData.temperature + '°C' });
        }
        if (commonData.pain_level !== undefined) {
            metrics.push({ label: 'Pain Level', value: commonData.pain_level + '/10' });
        }
        if (commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic) {
            metrics.push({ label: 'Blood Pressure', value: commonData.blood_pressure_systolic + '/' + commonData.blood_pressure_diastolic });
        }
        
        // BARIATRIC-SPECIFIC KEY METRICS
        if (conditionData.fluid_intake) {
            metrics.push({ label: 'Fluid Intake', value: conditionData.fluid_intake + ' mL' });
        }
        if (conditionData.urine_output) {
            metrics.push({ label: 'Urine Output', value: conditionData.urine_output + ' mL' });
        }
        if (conditionData.nausea_level) {
            metrics.push({ label: 'Nausea', value: this.formatMetricValue(conditionData.nausea_level) });
        }
        if (conditionData.diet_stage) {
            metrics.push({ label: 'Diet Stage', value: this.formatMetricValue(conditionData.diet_stage) });
        }
        
        return metrics;
    }
    
    getDetailedMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // VITAL SIGNS & PAIN ASSESSMENT
        if (commonData.temperature) {
            metrics.push({ label: 'Temperature', value: commonData.temperature + '°C' });
        }
        if (commonData.pain_level !== undefined) {
            metrics.push({ label: 'Pain Level', value: commonData.pain_level + '/10' });
        }
        if (commonData.pain_location) {
            metrics.push({ label: 'Pain Location', value: this.formatMetricValue(commonData.pain_location) });
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
        
        // HYDRATION & FLUID MANAGEMENT (Critical for Bariatric)
        if (conditionData.fluid_intake) {
            metrics.push({ label: 'Daily Fluid Intake', value: conditionData.fluid_intake + ' mL' });
        }
        if (conditionData.fluid_types && conditionData.fluid_types.length > 0) {
            metrics.push({ label: 'Fluid Types', value: conditionData.fluid_types.map(type => this.formatMetricValue(type)).join(', ') });
        }
        if (conditionData.urine_output) {
            metrics.push({ label: 'Urine Output (24h)', value: conditionData.urine_output + ' mL' });
        }
        if (conditionData.urine_color) {
            metrics.push({ label: 'Urine Color', value: this.formatMetricValue(conditionData.urine_color) });
        }
        if (conditionData.water_goal_met !== undefined) {
            metrics.push({ label: 'Water Goal Met', value: conditionData.water_goal_met ? 'Yes' : 'No' });
        }
        
        // GASTROINTESTINAL SYMPTOMS (Key Bariatric Indicators)
        if (conditionData.nausea_level) {
            metrics.push({ label: 'Nausea Level', value: this.formatMetricValue(conditionData.nausea_level) });
        }
        if (conditionData.vomiting_episodes !== undefined) {
            metrics.push({ label: 'Vomiting Episodes', value: conditionData.vomiting_episodes });
        }
        if (conditionData.abdominal_pain) {
            metrics.push({ label: 'Abdominal Pain', value: this.formatMetricValue(conditionData.abdominal_pain) });
        }
        if (conditionData.abdominal_distension) {
            metrics.push({ label: 'Abdominal Distension', value: this.formatMetricValue(conditionData.abdominal_distension) });
        }
        if (conditionData.bloating !== undefined) {
            metrics.push({ label: 'Bloating', value: conditionData.bloating ? 'Yes' : 'No' });
        }
        
        // NUTRITIONAL COMPLIANCE (Bariatric Specific)
        if (conditionData.diet_stage) {
            metrics.push({ label: 'Current Diet Stage', value: this.formatMetricValue(conditionData.diet_stage) });
        }
        if (conditionData.protein_intake) {
            metrics.push({ label: 'Protein Intake', value: conditionData.protein_intake + ' grams' });
        }
        if (conditionData.cravings !== undefined) {
            metrics.push({ label: 'Food Cravings', value: conditionData.cravings ? 'Yes' : 'No' });
        }
        
        // WOUND & DRAIN ASSESSMENT
        if (conditionData.wound_condition) {
            metrics.push({ label: 'Incision Condition', value: this.formatMetricValue(conditionData.wound_condition) });
        }
        if (conditionData.wound_discharge_type) {
            metrics.push({ label: 'Discharge Type', value: this.formatMetricValue(conditionData.wound_discharge_type) });
        }
        if (conditionData.wound_tenderness) {
            metrics.push({ label: 'Wound Tenderness', value: this.formatMetricValue(conditionData.wound_tenderness) });
        }
        if (conditionData.has_drain !== undefined) {
            metrics.push({ label: 'Surgical Drain', value: conditionData.has_drain ? 'Yes' : 'No' });
        }
        if (conditionData.drain_output) {
            metrics.push({ label: 'Drain Output', value: conditionData.drain_output + ' mL' });
        }
        if (conditionData.drain_color) {
            metrics.push({ label: 'Drain Color', value: this.formatMetricValue(conditionData.drain_color) });
        }
        
        // RESPIRATORY FUNCTION & MOBILITY
        if (conditionData.breathing_effort) {
            metrics.push({ label: 'Breathing Effort', value: this.formatMetricValue(conditionData.breathing_effort) });
        }
        if (conditionData.oxygen_therapy !== undefined) {
            metrics.push({ label: 'Oxygen Therapy', value: conditionData.oxygen_therapy ? 'Yes' : 'No' });
        }
        if (conditionData.oxygen_flow) {
            metrics.push({ label: 'Oxygen Flow Rate', value: conditionData.oxygen_flow + ' L/min' });
        }
        if (conditionData.mobility_level) {
            metrics.push({ label: 'Mobility Level', value: this.formatMetricValue(conditionData.mobility_level) });
        }
        if (conditionData.ambulation_frequency) {
            metrics.push({ label: 'Walking Frequency', value: this.formatMetricValue(conditionData.ambulation_frequency) });
        }
        if (conditionData.physiotherapy_sessions !== undefined) {
            metrics.push({ label: 'Physio Sessions', value: conditionData.physiotherapy_sessions });
        }
        
        // PSYCHOLOGICAL STATUS & MENTAL WELLBEING
        if (conditionData.mood_state) {
            metrics.push({ label: 'Mood State', value: this.formatMetricValue(conditionData.mood_state) });
        }
        if (conditionData.motivation_level) {
            metrics.push({ label: 'Motivation Level', value: this.formatMetricValue(conditionData.motivation_level) });
        }
        
        // SURGICAL PROGRESS & RECOVERY STATUS
        if (commonData.day_post_op !== undefined) {
            metrics.push({ label: 'Days Post-Op', value: commonData.day_post_op });
        }
        if (conditionData.status) {
            metrics.push({ label: 'Recovery Status', value: this.formatMetricValue(conditionData.status) });
        }
        
        // ADDITIONAL CLINICAL NOTES
        if (conditionData.additional_notes) {
            metrics.push({ label: 'Clinical Notes', value: conditionData.additional_notes });
        }
        
        return metrics;
    }
    
    renderEntryHTML(entry) {
        const keyMetrics = this.getKeyMetrics(entry);
        const detailedMetrics = this.getDetailedMetrics(entry);
        
        return `
            <div class="entry-header">
                <h3>${entry.patient_name || 'Unknown Patient'}</h3>
                <span class="condition-badge bariatric">Bariatric Surgery</span>
                ${entry.common_data?.day_post_op ? `<span class="days-post-op">Day ${entry.common_data.day_post_op}</span>` : ''}
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
                ${entry.condition_data?.status ? `<span class="status-indicator status-${entry.condition_data.status}">${this.formatMetricValue(entry.condition_data.status)}</span>` : ''}
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
            // Handle different string formats
            if (value.includes('_')) {
                return value.split('_').map(word => 
                    word.charAt(0).toUpperCase() + word.slice(1)
                ).join(' ');
            }
            return value.charAt(0).toUpperCase() + value.slice(1);
        }
        return value;
    }
    
    // BARIATRIC-SPECIFIC METHODS
    getNutritionMetrics(entry) {
        const conditionData = entry.condition_data || {};
        let metrics = [];
        
        if (conditionData.diet_stage) {
            metrics.push({ label: 'Diet Stage', value: this.formatMetricValue(conditionData.diet_stage) });
        }
        if (conditionData.protein_intake) {
            metrics.push({ label: 'Protein Intake', value: conditionData.protein_intake + 'g' });
        }
        if (conditionData.fluid_intake) {
            metrics.push({ label: 'Fluid Intake', value: conditionData.fluid_intake + 'mL' });
        }
        if (conditionData.fluid_types && conditionData.fluid_types.length > 0) {
            metrics.push({ label: 'Fluid Types', value: conditionData.fluid_types.map(this.formatMetricValue).join(', ') });
        }
        
        return metrics;
    }
    
    getComplicationMetrics(entry) {
        const conditionData = entry.condition_data || {};
        let metrics = [];
        
        // Early warning signs for bariatric complications
        if (conditionData.nausea_level && conditionData.nausea_level !== 'none') {
            metrics.push({ label: 'Nausea', value: this.formatMetricValue(conditionData.nausea_level), severity: this.getSeverityLevel(conditionData.nausea_level) });
        }
        if (conditionData.vomiting_episodes > 0) {
            metrics.push({ label: 'Vomiting', value: conditionData.vomiting_episodes + ' episodes', severity: conditionData.vomiting_episodes > 2 ? 'high' : 'medium' });
        }
        if (conditionData.abdominal_pain && conditionData.abdominal_pain !== 'none') {
            metrics.push({ label: 'Abdominal Pain', value: this.formatMetricValue(conditionData.abdominal_pain), severity: this.getSeverityLevel(conditionData.abdominal_pain) });
        }
        if (conditionData.wound_condition && conditionData.wound_condition !== 'clean') {
            metrics.push({ label: 'Wound Issue', value: this.formatMetricValue(conditionData.wound_condition), severity: 'high' });
        }
        
        return metrics;
    }
    
    getSeverityLevel(value) {
        const severityMap = {
            'none': 'none',
            'mild': 'low', 
            'moderate': 'medium',
            'severe': 'high'
        };
        return severityMap[value] || 'low';
    }
}