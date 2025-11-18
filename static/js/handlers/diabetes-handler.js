// diabetes-handler.js - ONLY knows diabetes fields
export class DiabetesHandler {
    getKeyMetrics(entry) {
        const conditionData = entry.condition_data || {};
        let metrics = [];
        
        // ONLY DIABETES FIELDS
        if (conditionData.blood_glucose) {
            metrics.push({ label: 'Blood Glucose', value: `${conditionData.blood_glucose} mg/dL` });
        }
        if (conditionData.insulin_dose) {
            metrics.push({ label: 'Insulin Dose', value: `${conditionData.insulin_dose} units` });
        }
        
        return metrics;
    }
    
    getDetailedMetrics(entry) {
        const conditionData = entry.condition_data || {};
        let metrics = [];
        
        // ONLY DIABETES FIELDS
        if (conditionData.blood_glucose) {
            metrics.push({ label: 'Blood Glucose', value: `${conditionData.blood_glucose} mg/dL` });
        }
        if (conditionData.insulin_dose) {
            metrics.push({ label: 'Insulin Dose', value: `${conditionData.insulin_dose} units` });
        }
        if (conditionData.insulin_type) {
            metrics.push({ label: 'Insulin Type', value: this.formatMetricValue(conditionData.insulin_type) });
        }
        if (conditionData.hypoglycemia_symptoms !== undefined) {
            metrics.push({ label: 'Hypoglycemia Symptoms', value: conditionData.hypoglycemia_symptoms ? 'Yes' : 'No' });
        }
        if (conditionData.diet_adherence) {
            metrics.push({ label: 'Diet Adherence', value: this.formatMetricValue(conditionData.diet_adherence) });
        }
        
        return metrics;
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