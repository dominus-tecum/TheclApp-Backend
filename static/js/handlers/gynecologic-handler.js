// gynecologic-handler.js - Reads ALL gynecologic fields
export class GynecologicHandler {
    getKeyMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // VITAL SIGNS - Key Metrics
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
        
        // GYNECOLOGIC SPECIFIC - Key Indicators
        if (conditionData.bleeding_amount && conditionData.bleeding_amount !== 'none') {
            metrics.push({ label: 'Bleeding', value: this.formatMetricValue(conditionData.bleeding_amount) });
        }
        if (conditionData.discharge_color && conditionData.discharge_color !== 'clear') {
            metrics.push({ label: 'Discharge', value: this.formatMetricValue(conditionData.discharge_color) });
        }
        if (conditionData.nausea_level && conditionData.nausea_level !== 'none') {
            metrics.push({ label: 'Nausea', value: this.formatMetricValue(conditionData.nausea_level) });
        }
        if (conditionData.wound_condition) {
            metrics.push({ label: 'Wound', value: this.formatMetricValue(conditionData.wound_condition) });
        }
        
        return metrics;
    }
    
    getDetailedMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // VITAL SIGNS - Complete Set
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
        if (commonData.respiratory_rate) {
            metrics.push({ label: 'Respiratory Rate', value: commonData.respiratory_rate + '/min' });
        }
        if (commonData.oxygen_saturation) {
            metrics.push({ label: 'Oxygen Saturation', value: commonData.oxygen_saturation + '%' });
        }
        
        // PAIN LOCATION
        if (conditionData.pain_location && conditionData.pain_location.length > 0) {
            const painLocations = conditionData.pain_location.map(loc => this.formatMetricValue(loc)).join(', ');
            metrics.push({ label: 'Pain Locations', value: painLocations });
        }
        
        // VAGINAL BLEEDING & DISCHARGE - Complete Assessment
        if (conditionData.bleeding_amount) {
            metrics.push({ label: 'Bleeding Amount', value: this.formatMetricValue(conditionData.bleeding_amount) });
        }
        if (conditionData.discharge_color) {
            metrics.push({ label: 'Discharge Color', value: this.formatMetricValue(conditionData.discharge_color) });
        }
        if (conditionData.discharge_odor && conditionData.discharge_odor !== 'none') {
            metrics.push({ label: 'Discharge Odor', value: this.formatMetricValue(conditionData.discharge_odor) });
        }
        if (conditionData.discharge_consistency) {
            metrics.push({ label: 'Discharge Consistency', value: this.formatMetricValue(conditionData.discharge_consistency) });
        }
        if (conditionData.clots_present !== undefined) {
            metrics.push({ label: 'Blood Clots Present', value: conditionData.clots_present ? 'Yes' : 'No' });
        }
        if (conditionData.clot_size && conditionData.clot_size !== 'none') {
            metrics.push({ label: 'Clot Size', value: this.formatMetricValue(conditionData.clot_size) });
        }
        
        // URINARY FUNCTION - Complete Assessment
        if (conditionData.urinary_frequency) {
            metrics.push({ label: 'Urinary Frequency', value: this.formatMetricValue(conditionData.urinary_frequency) });
        }
        if (conditionData.urinary_retention !== undefined) {
            metrics.push({ label: 'Urinary Retention', value: conditionData.urinary_retention ? 'Yes' : 'No' });
        }
        if (conditionData.dysuria && conditionData.dysuria !== 'none') {
            metrics.push({ label: 'Pain with Urination', value: this.formatMetricValue(conditionData.dysuria) });
        }
        if (conditionData.has_catheter !== undefined) {
            metrics.push({ label: 'Catheter in Place', value: conditionData.has_catheter ? 'Yes' : 'No' });
        }
        if (conditionData.catheter_output) {
            metrics.push({ label: 'Catheter Output', value: conditionData.catheter_output + ' mL' });
        }
        if (conditionData.catheter_patency) {
            metrics.push({ label: 'Catheter Patency', value: this.formatMetricValue(conditionData.catheter_patency) });
        }
        
        // GASTROINTESTINAL FUNCTION - Complete Assessment
        if (conditionData.nausea_level) {
            metrics.push({ label: 'Nausea Level', value: this.formatMetricValue(conditionData.nausea_level) });
        }
        if (conditionData.vomiting_episodes !== undefined && conditionData.vomiting_episodes > 0) {
            metrics.push({ label: 'Vomiting Episodes', value: conditionData.vomiting_episodes + ' times' });
        }
        if (conditionData.abdominal_distension) {
            metrics.push({ label: 'Abdominal Distension', value: this.formatMetricValue(conditionData.abdominal_distension) });
        }
        if (conditionData.bowel_sounds) {
            metrics.push({ label: 'Bowel Sounds', value: this.formatMetricValue(conditionData.bowel_sounds) });
        }
        if (conditionData.flatus_passed !== undefined) {
            metrics.push({ label: 'Passed Gas', value: conditionData.flatus_passed ? 'Yes' : 'No' });
        }
        if (conditionData.bowel_movement !== undefined) {
            metrics.push({ label: 'Bowel Movement', value: conditionData.bowel_movement ? 'Yes' : 'No' });
        }
        if (conditionData.bowel_movement_type) {
            metrics.push({ label: 'Bowel Movement Type', value: this.formatMetricValue(conditionData.bowel_movement_type) });
        }
        
        // WOUND AND DRAIN SITE - Complete Assessment
        if (conditionData.wound_condition) {
            metrics.push({ label: 'Wound Condition', value: this.formatMetricValue(conditionData.wound_condition) });
        }
        if (conditionData.wound_discharge_type) {
            metrics.push({ label: 'Wound Discharge Type', value: this.formatMetricValue(conditionData.wound_discharge_type) });
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
        if (conditionData.drain_consistency) {
            metrics.push({ label: 'Drain Consistency', value: this.formatMetricValue(conditionData.drain_consistency) });
        }
        
        // MOBILITY AND EMOTIONAL STATUS - Complete Assessment
        if (conditionData.mobility_level) {
            metrics.push({ label: 'Mobility Level', value: this.formatMetricValue(conditionData.mobility_level) });
        }
        if (conditionData.ambulation_frequency) {
            metrics.push({ label: 'Walking Frequency', value: this.formatMetricValue(conditionData.ambulation_frequency) });
        }
        if (conditionData.ambulation_distance) {
            metrics.push({ label: 'Walking Distance', value: this.formatMetricValue(conditionData.ambulation_distance) });
        }
        if (conditionData.mood_state) {
            metrics.push({ label: 'Mood State', value: this.formatMetricValue(conditionData.mood_state) });
        }
        if (conditionData.anxiety_level && conditionData.anxiety_level !== 'none') {
            metrics.push({ label: 'Anxiety Level', value: this.formatMetricValue(conditionData.anxiety_level) });
        }
        if (conditionData.sleep_quality) {
            metrics.push({ label: 'Sleep Quality', value: this.formatMetricValue(conditionData.sleep_quality) });
        }
        if (conditionData.emotional_support) {
            metrics.push({ label: 'Emotional Support', value: this.formatMetricValue(conditionData.emotional_support) });
        }
        
        // ADDITIONAL NOTES
        if (conditionData.additional_notes) {
            metrics.push({ label: 'Additional Notes', value: conditionData.additional_notes });
        }
        
        // STATUS
        if (conditionData.status) {
            metrics.push({ label: 'Status', value: this.formatMetricValue(conditionData.status) });
        }
        
        return metrics;
    }
    
    renderEntryHTML(entry) {
        const keyMetrics = this.getKeyMetrics(entry);
        const detailedMetrics = this.getDetailedMetrics(entry);
        
        return `
            <div class="entry-header">
                <h3>${entry.patient_name || 'Unknown Patient'}</h3>
                <span class="condition-badge" style="background: #E91E63;">Gynecologic</span>
            </div>
            <div class="entry-content">
                <div class="key-metrics">
                    <h4>Key Metrics</h4>
                    ${this.formatMetricsHTML(keyMetrics)}
                </div>
                <div class="detailed-metrics">
                    <h4>Complete Gynecologic Assessment</h4>
                    ${this.formatMetricsHTML(detailedMetrics)}
                </div>
            </div>
            <div class="entry-footer">
                <span class="timestamp">${new Date(entry.created_at).toLocaleString()}</span>
            </div>
        `;
    }
    
    formatMetricsHTML(metrics) {
        if (!metrics || metrics.length === 0) {
            return '<div class="no-metrics">No metrics available</div>';
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
            // Handle snake_case to readable text
            return value.split('_').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
        }
        return value;
    }
}