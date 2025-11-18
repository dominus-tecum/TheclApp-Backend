// prenatal-handler.js - Reads ALL prenatal fields
export class PrenatalHandler {
    getKeyMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // COMMON DATA FIELDS
        if (commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic) {
            metrics.push({ label: 'Blood Pressure', value: commonData.blood_pressure_systolic + '/' + commonData.blood_pressure_diastolic });
        }
        if (commonData.temperature) {
            metrics.push({ label: 'Temperature', value: commonData.temperature + '°C' });
        }
        if (commonData.heart_rate) {
            metrics.push({ label: 'Heart Rate', value: commonData.heart_rate + ' bpm' });
        }
        
        // PRENATAL SPECIFIC FIELDS - KEY METRICS
        if (conditionData.fetal_movement) {
            metrics.push({ label: 'Fetal Movement', value: this.formatMetricValue(conditionData.fetal_movement) });
        }
        if (conditionData.contractions) {
            metrics.push({ label: 'Contractions', value: conditionData.contractions ? 'Yes' : 'No' });
        }
        if (conditionData.vaginal_bleeding && conditionData.vaginal_bleeding !== 'none') {
            metrics.push({ label: 'Vaginal Bleeding', value: this.formatMetricValue(conditionData.vaginal_bleeding) });
        }
        
        return metrics;
    }
    
    getDetailedMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // MATERNAL VITAL SIGNS
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
        if (conditionData.weight) {
            metrics.push({ label: 'Weight', value: conditionData.weight + ' kg' });
        }
        
        // MATERNAL SYMPTOMS
        if (conditionData.edema && conditionData.edema !== 'none') {
            metrics.push({ label: 'Swelling (Edema)', value: this.formatMetricValue(conditionData.edema) });
        }
        if (conditionData.edema_location && conditionData.edema_location.length > 0) {
            metrics.push({ label: 'Swelling Location', value: conditionData.edema_location.map(loc => this.formatMetricValue(loc)).join(', ') });
        }
        if (conditionData.headache && conditionData.headache !== 'none') {
            metrics.push({ label: 'Headache', value: this.formatMetricValue(conditionData.headache) });
        }
        if (conditionData.visual_disturbances) {
            metrics.push({ label: 'Visual Disturbances', value: conditionData.visual_disturbances ? 'Yes' : 'No' });
        }
        if (conditionData.epigastric_pain) {
            metrics.push({ label: 'Upper Abdominal Pain', value: conditionData.epigastric_pain ? 'Yes' : 'No' });
        }
        if (conditionData.nausea_level && conditionData.nausea_level !== 'none') {
            metrics.push({ label: 'Nausea Level', value: this.formatMetricValue(conditionData.nausea_level) });
        }
        if (conditionData.vomiting_episodes > 0) {
            metrics.push({ label: 'Vomiting Episodes', value: conditionData.vomiting_episodes + ' times' });
        }
        
        // FETAL MOVEMENT
        if (conditionData.fetal_movement) {
            metrics.push({ label: 'Fetal Movement', value: this.formatMetricValue(conditionData.fetal_movement) });
        }
        if (conditionData.movement_count > 0) {
            metrics.push({ label: 'Kick Count', value: conditionData.movement_count + ' movements' });
        }
        if (conditionData.movement_duration) {
            metrics.push({ label: 'Movement Duration', value: conditionData.movement_duration + ' minutes' });
        }
        
        // CONTRACTIONS
        if (conditionData.contractions) {
            metrics.push({ label: 'Contractions Present', value: 'Yes' });
            if (conditionData.contraction_frequency) {
                metrics.push({ label: 'Contraction Frequency', value: conditionData.contraction_frequency + ' min apart' });
            }
            if (conditionData.contraction_duration) {
                metrics.push({ label: 'Contraction Duration', value: conditionData.contraction_duration + ' seconds' });
            }
            if (conditionData.contraction_intensity) {
                metrics.push({ label: 'Contraction Intensity', value: this.formatMetricValue(conditionData.contraction_intensity) });
            }
        }
        
        // VAGINAL SYMPTOMS
        if (conditionData.vaginal_bleeding && conditionData.vaginal_bleeding !== 'none') {
            metrics.push({ label: 'Vaginal Bleeding', value: this.formatMetricValue(conditionData.vaginal_bleeding) });
        }
        if (conditionData.bleeding_color && conditionData.vaginal_bleeding !== 'none') {
            metrics.push({ label: 'Bleeding Color', value: this.formatMetricValue(conditionData.bleeding_color) });
        }
        if (conditionData.fluid_leak) {
            metrics.push({ label: 'Fluid Leak', value: 'Yes' });
            if (conditionData.fluid_color) {
                metrics.push({ label: 'Fluid Color', value: this.formatMetricValue(conditionData.fluid_color) });
            }
            if (conditionData.fluid_amount) {
                metrics.push({ label: 'Fluid Amount', value: this.formatMetricValue(conditionData.fluid_amount) });
            }
        }
        
        // URINARY SYMPTOMS
        if (conditionData.urinary_frequency && conditionData.urinary_frequency !== 'normal') {
            metrics.push({ label: 'Urinary Frequency', value: this.formatMetricValue(conditionData.urinary_frequency) });
        }
        if (conditionData.dysuria && conditionData.dysuria !== 'none') {
            metrics.push({ label: 'Painful Urination', value: this.formatMetricValue(conditionData.dysuria) });
        }
        if (conditionData.urinary_incontinence) {
            metrics.push({ label: 'Urinary Incontinence', value: conditionData.urinary_incontinence ? 'Yes' : 'No' });
        }
        
        // GASTROINTESTINAL
        if (conditionData.appetite && conditionData.appetite !== 'normal') {
            metrics.push({ label: 'Appetite', value: this.formatMetricValue(conditionData.appetite) });
        }
        if (conditionData.heartburn && conditionData.heartburn !== 'none') {
            metrics.push({ label: 'Heartburn', value: this.formatMetricValue(conditionData.heartburn) });
        }
        if (conditionData.constipation && conditionData.constipation !== 'none') {
            metrics.push({ label: 'Constipation', value: this.formatMetricValue(conditionData.constipation) });
        }
        
        // MEDICATION COMPLIANCE
        if (conditionData.medications_taken !== undefined) {
            metrics.push({ label: 'Medications Taken', value: conditionData.medications_taken ? 'Yes' : 'No' });
        }
        if (conditionData.missed_medications) {
            metrics.push({ label: 'Missed Medications', value: conditionData.missed_medications });
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
                <span class="condition-badge prenatal">Prenatal</span>
                ${entry.condition_data?.gestational_age ? `<span class="gestational-age">${entry.condition_data.gestational_age}</span>` : ''}
                ${entry.condition_data?.high_risk ? `<span class="high-risk-badge">High Risk</span>` : ''}
            </div>
            <div class="entry-content">
                <div class="key-metrics">
                    <h4>Key Pregnancy Metrics</h4>
                    ${this.formatMetricsHTML(keyMetrics)}
                </div>
                <div class="detailed-metrics">
                    <h4>Complete Prenatal Assessment</h4>
                    ${this.formatMetricsHTML(detailedMetrics)}
                </div>
            </div>
            <div class="entry-footer">
                <span class="timestamp">${new Date(entry.created_at).toLocaleString()}</span>
                ${entry.condition_data?.status ? `<span class="status-indicator ${entry.condition_data.status}">${this.formatMetricValue(entry.condition_data.status)}</span>` : ''}
            </div>
        `;
    }
    
    formatMetricsHTML(metrics) {
        if (!metrics || metrics.length === 0) {
            return '<div class="no-metrics">No prenatal metrics available</div>';
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
            // Handle special cases first
            if (value === 'blood_tinged') return 'Blood-tinged';
            if (value === 'dayPost_op') return 'Days Post-Op';
            
            // Convert snake_case to Title Case
            return value.split('_').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
        }
        return value;
    }
    
    // Additional prenatal-specific methods
    getUrgencyLevel(entry) {
        const conditionData = entry.condition_data || {};
        
        // URGENT: Pre-eclampsia signs, heavy bleeding, absent fetal movement
        if (conditionData.blood_pressure_systolic >= 140 || 
            conditionData.blood_pressure_diastolic >= 90 ||
            conditionData.headache === 'severe' ||
            conditionData.visual_disturbances ||
            conditionData.epigastric_pain ||
            conditionData.vaginal_bleeding === 'heavy' ||
            conditionData.fetal_movement === 'absent') {
            return 'urgent';
        }
        
        // MONITOR: Moderate symptoms
        if (conditionData.blood_pressure_systolic >= 130 ||
            conditionData.blood_pressure_diastolic >= 85 ||
            conditionData.headache === 'moderate' ||
            conditionData.vaginal_bleeding === 'moderate' ||
            conditionData.fetal_movement === 'decreased' ||
            conditionData.contractions ||
            conditionData.vomiting_episodes >= 3) {
            return 'monitor';
        }
        
        return 'good';
    }
    
    getSummary(entry) {
        const conditionData = entry.condition_data || {};
        let summary = [];
        
        if (conditionData.fetal_movement) {
            summary.push(`Fetal movement: ${this.formatMetricValue(conditionData.fetal_movement)}`);
        }
        if (conditionData.contractions) {
            summary.push('Contractions present');
        }
        if (conditionData.vaginal_bleeding && conditionData.vaginal_bleeding !== 'none') {
            summary.push(`Vaginal bleeding: ${this.formatMetricValue(conditionData.vaginal_bleeding)}`);
        }
        
        return summary.length > 0 ? summary.join(' • ') : 'Normal prenatal progress';
    }
}