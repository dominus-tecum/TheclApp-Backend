// postnatal-handler.js - Reads ALL postnatal fields
export class PostnatalHandler {
    getKeyMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // MATERNAL KEY METRICS
        if (conditionData.lochia_flow && conditionData.lochia_flow !== 'none') {
            metrics.push({ label: 'Lochia', value: this.formatMetricValue(conditionData.lochia_flow) });
        }
        if (conditionData.breast_engorgement && conditionData.breast_engorgement !== 'none') {
            metrics.push({ label: 'Breast Engorgement', value: this.formatMetricValue(conditionData.breast_engorgement) });
        }
        if (conditionData.perineal_pain && conditionData.perineal_pain !== 'none') {
            metrics.push({ label: 'Perineal Pain', value: this.formatMetricValue(conditionData.perineal_pain) });
        }
        
        // INFANT KEY METRICS
        if (conditionData.feeding_method) {
            metrics.push({ label: 'Feeding', value: this.formatMetricValue(conditionData.feeding_method) });
        }
        if (conditionData.feeding_frequency) {
            metrics.push({ label: 'Feeds/Day', value: conditionData.feeding_frequency });
        }
        if (conditionData.wet_diapers) {
            metrics.push({ label: 'Wet Diapers', value: conditionData.wet_diapers });
        }
        if (conditionData.jaundice_level && conditionData.jaundice_level !== 'none') {
            metrics.push({ label: 'Jaundice', value: this.formatMetricValue(conditionData.jaundice_level) });
        }
        
        return metrics;
    }
    
    getDetailedMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // DAYS POSTPARTUM
        if (entry.days_postpartum) {
            metrics.push({ label: 'Days Postpartum', value: entry.days_postpartum });
        }
        
        // MATERNAL VITAL SIGNS
        if (commonData.temperature) {
            metrics.push({ label: 'Maternal Temperature', value: commonData.temperature + '°C' });
        }
        if (commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic) {
            metrics.push({ label: 'Maternal BP', value: commonData.blood_pressure_systolic + '/' + commonData.blood_pressure_diastolic });
        }
        if (commonData.heart_rate) {
            metrics.push({ label: 'Maternal Heart Rate', value: commonData.heart_rate + ' bpm' });
        }
        
        // MATERNAL RECOVERY - LOCHIA
        if (conditionData.lochia_flow) {
            metrics.push({ label: 'Lochia Flow', value: this.formatMetricValue(conditionData.lochia_flow) });
        }
        if (conditionData.lochia_color && conditionData.lochia_flow !== 'none') {
            metrics.push({ label: 'Lochia Color', value: this.formatMetricValue(conditionData.lochia_color) });
        }
        
        // MATERNAL PAIN ASSESSMENT
        if (conditionData.perineal_pain && conditionData.perineal_pain !== 'none') {
            metrics.push({ label: 'Perineal Pain', value: this.formatMetricValue(conditionData.perineal_pain) });
        }
        if (conditionData.uterine_pain && conditionData.uterine_pain !== 'none') {
            metrics.push({ label: 'Uterine Pain', value: this.formatMetricValue(conditionData.uterine_pain) });
        }
        if (conditionData.c_section_pain && conditionData.c_section_pain !== 'none') {
            metrics.push({ label: 'C-Section Pain', value: this.formatMetricValue(conditionData.c_section_pain) });
        }
        
        // BREASTFEEDING ASSESSMENT
        if (conditionData.breast_engorgement && conditionData.breast_engorgement !== 'none') {
            metrics.push({ label: 'Breast Engorgement', value: this.formatMetricValue(conditionData.breast_engorgement) });
        }
        if (conditionData.nipple_pain && conditionData.nipple_pain !== 'none') {
            metrics.push({ label: 'Nipple Pain', value: this.formatMetricValue(conditionData.nipple_pain) });
        }
        
        // INCISION ASSESSMENT
        if (conditionData.incision_redness) {
            metrics.push({ label: 'Incision Redness', value: conditionData.incision_redness ? 'Yes' : 'No' });
        }
        if (conditionData.incision_discharge) {
            metrics.push({ label: 'Incision Discharge', value: conditionData.incision_discharge ? 'Yes' : 'No' });
        }
        
        // MATERNAL MENTAL HEALTH
        if (conditionData.maternal_energy) {
            metrics.push({ label: 'Maternal Energy', value: this.formatMetricValue(conditionData.maternal_energy) });
        }
        if (conditionData.support_system) {
            metrics.push({ label: 'Support System', value: this.formatMetricValue(conditionData.support_system) });
        }
        
        // EPDS SCORE CALCULATION
        const epdsScore = this.calculateEPDSScore(conditionData);
        if (epdsScore !== null) {
            metrics.push({ label: 'EPDS Score', value: epdsScore + '/24' });
            metrics.push({ label: 'Depression Risk', value: this.getEPDSRisk(epdsScore) });
        }
        
        // INFANT FEEDING
        if (conditionData.feeding_method) {
            metrics.push({ label: 'Feeding Method', value: this.formatMetricValue(conditionData.feeding_method) });
        }
        if (conditionData.feeding_frequency) {
            metrics.push({ label: 'Feeding Frequency', value: conditionData.feeding_frequency + ' times/day' });
        }
        if (conditionData.feeding_duration) {
            metrics.push({ label: 'Feeding Duration', value: conditionData.feeding_duration + ' minutes' });
        }
        if (conditionData.latching_quality) {
            metrics.push({ label: 'Latching Quality', value: this.formatMetricValue(conditionData.latching_quality) });
        }
        
        // INFANT DIAPER OUTPUT
        if (conditionData.wet_diapers) {
            metrics.push({ label: 'Wet Diapers', value: conditionData.wet_diapers + '/24h' });
        }
        if (conditionData.soiled_diapers) {
            metrics.push({ label: 'Soiled Diapers', value: conditionData.soiled_diapers + '/24h' });
        }
        if (conditionData.stool_color) {
            metrics.push({ label: 'Stool Color', value: this.formatMetricValue(conditionData.stool_color) });
        }
        if (conditionData.stool_consistency) {
            metrics.push({ label: 'Stool Consistency', value: this.formatMetricValue(conditionData.stool_consistency) });
        }
        
        // INFANT HEALTH
        if (conditionData.infant_temperature) {
            metrics.push({ label: 'Infant Temperature', value: conditionData.infant_temperature + '°C' });
        }
        if (conditionData.infant_heart_rate) {
            metrics.push({ label: 'Infant Heart Rate', value: conditionData.infant_heart_rate + ' bpm' });
        }
        if (conditionData.jaundice_level && conditionData.jaundice_level !== 'none') {
            metrics.push({ label: 'Jaundice Level', value: this.formatMetricValue(conditionData.jaundice_level) });
        }
        if (conditionData.umbilical_cord) {
            metrics.push({ label: 'Umbilical Cord', value: this.formatMetricValue(conditionData.umbilical_cord) });
        }
        if (conditionData.skin_condition && conditionData.skin_condition !== 'normal') {
            metrics.push({ label: 'Skin Condition', value: this.formatMetricValue(conditionData.skin_condition) });
        }
        
        // INFANT BEHAVIOR
        if (conditionData.infant_alertness) {
            metrics.push({ label: 'Infant Alertness', value: this.formatMetricValue(conditionData.infant_alertness) });
        }
        if (conditionData.sleep_pattern) {
            metrics.push({ label: 'Sleep Pattern', value: this.formatMetricValue(conditionData.sleep_pattern) });
        }
        if (conditionData.crying_level && conditionData.crying_level !== 'normal') {
            metrics.push({ label: 'Crying Level', value: this.formatMetricValue(conditionData.crying_level) });
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
        const epdsScore = this.calculateEPDSScore(entry.condition_data || {});
        
        return `
            <div class="entry-header">
                <h3>${entry.patient_name || 'Unknown Patient'}</h3>
                <span class="condition-badge postnatal">Postnatal</span>
                ${entry.infant_name ? `<span class="infant-name">Baby: ${entry.infant_name}</span>` : ''}
                ${entry.days_postpartum ? `<span class="days-postpartum">Day ${entry.days_postpartum}</span>` : ''}
                ${entry.condition_data?.high_risk ? `<span class="high-risk-badge">High Risk</span>` : ''}
            </div>
            <div class="entry-content">
                <div class="key-metrics">
                    <h4>Key Postnatal Metrics</h4>
                    ${this.formatMetricsHTML(keyMetrics)}
                </div>
                ${epdsScore !== null ? `
                <div class="epds-card ${epdsScore >= 10 ? 'epds-warning' : ''}">
                    <h4>Postpartum Depression Screening</h4>
                    <div class="epds-score">EPDS Score: ${epdsScore}/24</div>
                    <div class="epds-risk">${this.getEPDSRisk(epdsScore)}</div>
                </div>
                ` : ''}
                <div class="detailed-metrics">
                    <h4>Complete Postnatal Assessment</h4>
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
            return '<div class="no-metrics">No postnatal metrics available</div>';
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
            if (value === 'yes_often') return 'Yes, often';
            if (value === 'c_section') return 'C-Section';
            
            // Convert snake_case to Title Case
            return value.split('_').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
        }
        return value;
    }
    
    calculateEPDSScore(conditionData) {
        const scores = {
            mood_laugh: { yes: 0, sometimes: 1, no: 2 },
            mood_anxious: { no: 0, sometimes: 1, yes_often: 2 },
            mood_blame: { no: 0, sometimes: 1, yes_often: 2 },
            mood_panic: { no: 0, sometimes: 1, yes_often: 2 },
            mood_sleep: { no: 0, sometimes: 1, yes_often: 2 },
            mood_sad: { no: 0, sometimes: 1, yes_often: 2 },
            mood_crying: { no: 0, sometimes: 1, yes_often: 2 },
            mood_harm: { no: 0, sometimes: 1, yes_often: 2 }
        };
        
        try {
            return (
                scores.mood_laugh[conditionData.mood_laugh] +
                scores.mood_anxious[conditionData.mood_anxious] +
                scores.mood_blame[conditionData.mood_blame] +
                scores.mood_panic[conditionData.mood_panic] +
                scores.mood_sleep[conditionData.mood_sleep] +
                scores.mood_sad[conditionData.mood_sad] +
                scores.mood_crying[conditionData.mood_crying] +
                scores.mood_harm[conditionData.mood_harm]
            );
        } catch (error) {
            return null;
        }
    }
    
    getEPDSRisk(score) {
        if (score >= 13) return 'High Risk';
        if (score >= 10) return 'Possible';
        return 'Low Risk';
    }
    
    // Additional postnatal-specific methods
    getUrgencyLevel(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        
        const maternalTemp = parseFloat(commonData.temperature || '0');
        const systolicBP = parseInt(commonData.blood_pressure_systolic || '0');
        const diastolicBP = parseInt(commonData.blood_pressure_diastolic || '0');
        const infantTemp = parseFloat(conditionData.infant_temperature || '0');
        
        // URGENT: Immediate medical attention needed
        if (
            maternalTemp >= 38.0 ||
            systolicBP >= 140 || diastolicBP >= 90 ||
            conditionData.lochia_flow === 'heavy' ||
            conditionData.incision_redness || conditionData.incision_discharge ||
            conditionData.mood_harm === 'yes_often' ||
            infantTemp >= 38.0 ||
            conditionData.jaundice_level === 'severe' ||
            conditionData.umbilical_cord === 'red' || conditionData.umbilical_cord === 'discharge' ||
            conditionData.infant_alertness === 'lethargic' ||
            conditionData.wet_diapers < 3 || conditionData.soiled_diapers < 1
        ) {
            return 'urgent';
        }
        
        // MONITOR: Needs medical review
        if (
            maternalTemp >= 37.5 ||
            systolicBP >= 130 || diastolicBP >= 85 ||
            conditionData.lochia_flow === 'moderate' ||
            conditionData.perineal_pain === 'severe' || conditionData.c_section_pain === 'severe' ||
            conditionData.breast_engorgement === 'severe' ||
            conditionData.mood_sad === 'yes_often' || conditionData.mood_crying === 'yes_often' ||
            conditionData.jaundice_level === 'moderate' ||
            conditionData.feeding_frequency < 6
        ) {
            return 'monitor';
        }
        
        return 'good';
    }
    
    getSummary(entry) {
        const conditionData = entry.condition_data || {};
        let summary = [];
        
        if (conditionData.lochia_flow && conditionData.lochia_flow !== 'none') {
            summary.push(`Lochia: ${this.formatMetricValue(conditionData.lochia_flow)}`);
        }
        if (conditionData.feeding_method) {
            summary.push(`Feeding: ${this.formatMetricValue(conditionData.feeding_method)}`);
        }
        if (conditionData.wet_diapers) {
            summary.push(`Wet diapers: ${conditionData.wet_diapers}`);
        }
        if (conditionData.jaundice_level && conditionData.jaundice_level !== 'none') {
            summary.push(`Jaundice: ${this.formatMetricValue(conditionData.jaundice_level)}`);
        }
        
        return summary.length > 0 ? summary.join(' • ') : 'Normal postnatal progress';
    }
}