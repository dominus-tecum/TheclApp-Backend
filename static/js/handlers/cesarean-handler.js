// cesarean-handler.js - Reads ALL cesarean fields
export class CesareanHandler {
    getKeyMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // COMMON DATA FIELDS
        if (commonData.temperature) {
            metrics.push({ label: 'Temperature', value: commonData.temperature + '°C' });
        }
        if (commonData.pain_level !== undefined) {
            metrics.push({ label: 'Pain Level', value: commonData.pain_level + '/10' });
        }
        if (commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic) {
            metrics.push({ label: 'Blood Pressure', value: commonData.blood_pressure_systolic + '/' + commonData.blood_pressure_diastolic });
        }
        
        // CESAREAN SPECIFIC FIELDS
        if (conditionData.uterine_firmness) {
            metrics.push({ label: 'Uterine Firmness', value: this.formatMetricValue(conditionData.uterine_firmness) });
        }
        if (conditionData.lochia_amount) {
            metrics.push({ label: 'Lochia', value: this.formatMetricValue(conditionData.lochia_amount) });
        }
        if (conditionData.wound_condition) {
            metrics.push({ label: 'Incision', value: this.formatMetricValue(conditionData.wound_condition) });
        }
        
        return metrics;
    }
    
    getDetailedMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // VITAL SIGNS
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
        
        // UTERINE & LOCHIA
        if (conditionData.fundal_height) {
            metrics.push({ label: 'Fundal Height', value: conditionData.fundal_height + ' cm below umbilicus' });
        }
        if (conditionData.uterine_firmness) {
            metrics.push({ label: 'Uterine Firmness', value: this.formatMetricValue(conditionData.uterine_firmness) });
        }
        if (conditionData.lochia_amount) {
            metrics.push({ label: 'Lochia Amount', value: this.formatMetricValue(conditionData.lochia_amount) });
        }
        if (conditionData.lochia_color) {
            metrics.push({ label: 'Lochia Color', value: this.formatMetricValue(conditionData.lochia_color) });
        }
        if (conditionData.lochia_odor) {
            metrics.push({ label: 'Lochia Odor', value: this.formatMetricValue(conditionData.lochia_odor) });
        }
        
        // WOUND/INCISION
        if (conditionData.wound_condition) {
            metrics.push({ label: 'Incision Condition', value: this.formatMetricValue(conditionData.wound_condition) });
        }
        if (conditionData.wound_discharge_type) {
            metrics.push({ label: 'Wound Discharge Type', value: this.formatMetricValue(conditionData.wound_discharge_type) });
        }
        if (conditionData.wound_tenderness) {
            metrics.push({ label: 'Wound Tenderness', value: this.formatMetricValue(conditionData.wound_tenderness) });
        }
        
        // URINARY & BOWEL FUNCTION
        if (conditionData.urine_output) {
            metrics.push({ label: 'Urine Output', value: conditionData.urine_output + ' mL/24h' });
        }
        if (conditionData.urinary_retention !== undefined) {
            metrics.push({ label: 'Urinary Retention', value: conditionData.urinary_retention ? 'Yes' : 'No' });
        }
        if (conditionData.bowel_sounds) {
            metrics.push({ label: 'Bowel Sounds', value: this.formatMetricValue(conditionData.bowel_sounds) });
        }
        if (conditionData.flatus_passed !== undefined) {
            metrics.push({ label: 'Flatus Passed', value: conditionData.flatus_passed ? 'Yes' : 'No' });
        }
        if (conditionData.bowel_movement !== undefined) {
            metrics.push({ label: 'Bowel Movement', value: conditionData.bowel_movement ? 'Yes' : 'No' });
        }
        
        // MOBILITY
        if (conditionData.mobility_level) {
            metrics.push({ label: 'Mobility Level', value: this.formatMetricValue(conditionData.mobility_level) });
        }
        if (conditionData.ambulation_distance) {
            metrics.push({ label: 'Ambulation Distance', value: this.formatMetricValue(conditionData.ambulation_distance) });
        }
        
        // BREAST & LACTATION
        if (conditionData.breastfeeding !== undefined) {
            metrics.push({ label: 'Breastfeeding', value: conditionData.breastfeeding ? 'Yes' : 'No' });
        }
        if (conditionData.breast_engorgement) {
            metrics.push({ label: 'Breast Engorgement', value: this.formatMetricValue(conditionData.breast_engorgement) });
        }
        if (conditionData.breast_tenderness) {
            metrics.push({ label: 'Breast Tenderness', value: this.formatMetricValue(conditionData.breast_tenderness) });
        }
        if (conditionData.nipple_condition) {
            metrics.push({ label: 'Nipple Condition', value: this.formatMetricValue(conditionData.nipple_condition) });
        }
        if (conditionData.feeding_frequency) {
            metrics.push({ label: 'Feeding Frequency', value: this.formatMetricValue(conditionData.feeding_frequency) });
        }
        
        // ADDITIONAL NOTES
        if (conditionData.additional_notes) {
            metrics.push({ label: 'Notes', value: conditionData.additional_notes });
        }
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
                <span class="condition-badge cesarean">cesarean</span>
            </div>
            <div class="entry-content">
                <div class="key-metrics">
                    <h4>Key Metrics</h4>
                    ${this.formatMetricsHTML(keyMetrics)}
                </div>
                <div class="detailed-metrics">
                    <h4>Detailed Assessment</h4>
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
            return value.split('_').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
        }
        return value;
    }
}