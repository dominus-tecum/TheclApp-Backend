// urological-handler.js - Reads ALL urological fields
export class UrologicalHandler {
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
        
        // UROLOGICAL SPECIFIC FIELDS
        if (conditionData.urine_output) {
            metrics.push({ label: 'Urine Output', value: conditionData.urine_output + ' mL' });
        }
        if (conditionData.urine_color) {
            metrics.push({ label: 'Urine Color', value: this.formatMetricValue(conditionData.urine_color) });
        }
        if (conditionData.catheter_patency) {
            metrics.push({ label: 'Catheter Status', value: this.formatMetricValue(conditionData.catheter_patency) });
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
        if (commonData.oxygen_saturation) {
            metrics.push({ label: 'Oxygen Saturation', value: commonData.oxygen_saturation + '%' });
        }
        
        // URINE ASSESSMENT
        if (conditionData.urine_output) {
            metrics.push({ label: 'Urine Output (24h)', value: conditionData.urine_output + ' mL' });
        }
        if (conditionData.urine_color) {
            metrics.push({ label: 'Urine Color', value: this.formatMetricValue(conditionData.urine_color) });
        }
        if (conditionData.urine_clarity) {
            metrics.push({ label: 'Urine Clarity', value: this.formatMetricValue(conditionData.urine_clarity) });
        }
        if (conditionData.urine_odor) {
            metrics.push({ label: 'Urine Odor', value: this.formatMetricValue(conditionData.urine_odor) });
        }
        if (conditionData.urine_debris) {
            metrics.push({ label: 'Urine Debris', value: this.formatMetricValue(conditionData.urine_debris) });
        }
        
        // CATHETER & DRAIN MANAGEMENT
        if (conditionData.has_catheter !== undefined) {
            metrics.push({ label: 'Catheter in Place', value: conditionData.has_catheter ? 'Yes' : 'No' });
        }
        if (conditionData.catheter_patency) {
            metrics.push({ label: 'Catheter Patency', value: this.formatMetricValue(conditionData.catheter_patency) });
        }
        if (conditionData.catheter_drainage) {
            metrics.push({ label: 'Catheter Drainage', value: this.formatMetricValue(conditionData.catheter_drainage) });
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
        if (conditionData.insertion_site) {
            metrics.push({ label: 'Insertion Site', value: this.formatMetricValue(conditionData.insertion_site) });
        }
        
        // WOUND ASSESSMENT
        if (conditionData.wound_condition) {
            metrics.push({ label: 'Wound Condition', value: this.formatMetricValue(conditionData.wound_condition) });
        }
        if (conditionData.wound_tenderness) {
            metrics.push({ label: 'Wound Tenderness', value: this.formatMetricValue(conditionData.wound_tenderness) });
        }
        if (conditionData.dressing_condition) {
            metrics.push({ label: 'Dressing Condition', value: this.formatMetricValue(conditionData.dressing_condition) });
        }
        
        // GASTROINTESTINAL FUNCTION
        if (conditionData.nausea_level) {
            metrics.push({ label: 'Nausea Level', value: this.formatMetricValue(conditionData.nausea_level) });
        }
        if (conditionData.vomiting_episodes !== undefined) {
            metrics.push({ label: 'Vomiting Episodes', value: conditionData.vomiting_episodes });
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
        
        // HYDRATION & RENAL STATUS
        if (conditionData.oral_intake) {
            metrics.push({ label: 'Oral Intake', value: conditionData.oral_intake + ' mL' });
        }
        if (conditionData.iv_intake) {
            metrics.push({ label: 'IV Intake', value: conditionData.iv_intake + ' mL' });
        }
        if (conditionData.total_intake) {
            metrics.push({ label: 'Total Intake', value: conditionData.total_intake + ' mL' });
        }
        if (conditionData.fluid_balance) {
            metrics.push({ label: 'Fluid Balance', value: conditionData.fluid_balance + ' mL' });
        }
        if (conditionData.creatinine_level) {
            metrics.push({ label: 'Creatinine Level', value: conditionData.creatinine_level + ' mg/dL' });
        }
        if (conditionData.hydration_status) {
            metrics.push({ label: 'Hydration Status', value: this.formatMetricValue(conditionData.hydration_status) });
        }
        
        // ADDITIONAL NOTES
        if (conditionData.additional_notes) {
            metrics.push({ label: 'Additional Notes', value: conditionData.additional_notes });
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
                <span class="condition-badge urological">Urological</span>
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