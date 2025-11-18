// abdominal-handler.js - Reads ALL abdominal fields
export class AbdominalHandler {
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
        
        // CONDITION SPECIFIC FIELDS
        if (conditionData.gi_function) {
            metrics.push({ label: 'Bowel Function', value: this.formatMetricValue(conditionData.gi_function) });
        }
        if (conditionData.appetite) {
            metrics.push({ label: 'Appetite', value: this.formatMetricValue(conditionData.appetite) });
        }
        if (conditionData.wound_condition) {
            metrics.push({ label: 'Wound Condition', value: this.formatMetricValue(conditionData.wound_condition) });
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
        
        // ABDOMINAL SPECIFIC FIELDS
        if (conditionData.gi_function) {
            metrics.push({ label: 'Bowel Function', value: this.formatMetricValue(conditionData.gi_function) });
        }
        if (conditionData.nausea_vomiting) {
            metrics.push({ label: 'Nausea/Vomiting', value: this.formatMetricValue(conditionData.nausea_vomiting) });
        }
        if (conditionData.appetite) {
            metrics.push({ label: 'Appetite', value: this.formatMetricValue(conditionData.appetite) });
        }
        if (conditionData.wound_condition) {
            metrics.push({ label: 'Incision/Wound Condition', value: this.formatMetricValue(conditionData.wound_condition) });
        }
        if (conditionData.mobility) {
            metrics.push({ label: 'Mobility Level', value: this.formatMetricValue(conditionData.mobility) });
        }
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
                <span class="condition-badge abdominal">abdominal</span>
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