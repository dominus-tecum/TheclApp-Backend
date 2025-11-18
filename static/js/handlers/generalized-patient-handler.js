// generalized-patient-handler.js - Web handler for generalized patient data
export class GeneralizedPatientHandler {
    getKeyMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // CRITICAL HEALTH INDICATORS
        if (conditionData.healthTrend) {
            metrics.push({ label: 'Health Trend', value: this.formatMetricValue(conditionData.healthTrend) });
        }
        if (conditionData.overallWellbeing !== undefined) {
            metrics.push({ label: 'Overall Wellbeing', value: conditionData.overallWellbeing + '/10' });
        }
        if (conditionData.primarySymptom && conditionData.primarySymptom.severity !== undefined) {
            metrics.push({ label: 'Symptom Severity', value: conditionData.primarySymptom.severity + '/10' });
        }
        
        // COMMON VITAL SIGNS (if available)
        if (commonData.temperature) {
            metrics.push({ label: 'Temperature', value: commonData.temperature + '°C' });
        }
        if (commonData.heart_rate) {
            metrics.push({ label: 'Heart Rate', value: commonData.heart_rate + ' bpm' });
        }
        if (commonData.blood_pressure_systolic && commonData.blood_pressure_diastolic) {
            metrics.push({ label: 'Blood Pressure', value: commonData.blood_pressure_systolic + '/' + commonData.blood_pressure_diastolic });
        }
        
        // STATUS INDICATOR
        if (entry.status) {
            metrics.push({ label: 'Status', value: this.formatMetricValue(entry.status) });
        }
        
        return metrics;
    }
    
    getDetailedMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // HEALTH TREND & OVERALL ASSESSMENT
        if (conditionData.healthTrend) {
            metrics.push({ label: 'Health Trend', value: this.formatMetricValue(conditionData.healthTrend) });
        }
        if (conditionData.overallWellbeing !== undefined) {
            metrics.push({ label: 'Overall Wellbeing', value: conditionData.overallWellbeing + '/10' });
        }
        
        // PRIMARY SYMPTOM DETAILS
        if (conditionData.primarySymptom) {
            if (conditionData.primarySymptom.severity !== undefined) {
                metrics.push({ label: 'Symptom Severity', value: conditionData.primarySymptom.severity + '/10' });
            }
            if (conditionData.primarySymptom.description) {
                metrics.push({ label: 'Symptom Description', value: conditionData.primarySymptom.description });
            }
        }
        
        // ADDITIONAL NOTES
        if (conditionData.notes) {
            metrics.push({ label: 'Additional Notes', value: conditionData.notes });
        }
        
        // COMMON VITAL SIGNS - COMPREHENSIVE
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
        
        // SUBMISSION INFORMATION
        if (entry.status) {
            metrics.push({ label: 'Clinical Status', value: this.formatMetricValue(entry.status) });
        }
        if (entry.submissionDate) {
            metrics.push({ label: 'Submission Date', value: new Date(entry.submissionDate).toLocaleDateString() });
        }
        if (entry.submittedAt) {
            metrics.push({ label: 'Submitted At', value: new Date(entry.submittedAt).toLocaleString() });
        }
        
        // PATIENT INFORMATION
        if (entry.patientName) {
            metrics.push({ label: 'Patient Name', value: entry.patientName });
        }
        if (entry.patientId) {
            metrics.push({ label: 'Patient ID', value: entry.patientId });
        }
        
        return metrics;
    }
    
    renderEntryHTML(entry) {
        const keyMetrics = this.getKeyMetrics(entry);
        const detailedMetrics = this.getDetailedMetrics(entry);
        const healthSummary = this.getHealthSummary(entry);
        
        return `
            <div class="entry-header">
                <h3>${entry.patientName || entry.patient_name || 'Unknown Patient'}</h3>
                <span class="condition-badge generalized">General Health Follow-up</span>
            </div>
            <div class="entry-content">
                ${healthSummary.length > 0 ? `
                    <div class="health-alerts">
                        <h4>Clinical Alerts</h4>
                        ${healthSummary.map(alert => `
                            <div class="alert-item">${alert}</div>
                        `).join('')}
                    </div>
                ` : ''}
                
                <div class="key-metrics">
                    <h4>Health Overview</h4>
                    ${this.formatMetricsHTML(keyMetrics)}
                </div>
                <div class="detailed-metrics">
                    <h4>Detailed Assessment</h4>
                    ${this.formatMetricsHTML(detailedMetrics)}
                </div>
            </div>
            <div class="entry-footer">
                <span class="timestamp">${new Date(entry.created_at || entry.submittedAt).toLocaleString()}</span>
                ${entry.submissionDate ? `<span class="submission-date">Submitted: ${entry.submissionDate}</span>` : ''}
                ${entry.conditionType ? `<span class="condition-type">Type: ${this.formatMetricValue(entry.conditionType)}</span>` : ''}
            </div>
        `;
    }
    
    formatMetricsHTML(metrics) {
        if (!metrics || metrics.length === 0) {
            return '<div class="no-metrics">No health metrics recorded</div>';
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
                'significantly_worse': 'Significantly Worse',
                'slightly_worse': 'Slightly Worse',
                'stable': 'Stable',
                'slightly_better': 'Slightly Better',
                'significantly_better': 'Significantly Better',
                'varies': 'Varies Day to Day',
                'urgent': 'Needs Attention',
                'monitor': 'Requires Monitoring',
                'good': 'Stable',
                'general_health': 'General Health'
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
    
    // Additional helper method for health status analysis
    getHealthSummary(entry) {
        const conditionData = entry.condition_data || {};
        const summary = [];
        
        // Health trend warnings
        if (conditionData.healthTrend === 'significantly_worse') {
            summary.push('Health trending significantly worse - requires immediate attention');
        } else if (conditionData.healthTrend === 'slightly_worse') {
            summary.push('Health trending slightly worse - close monitoring needed');
        }
        
        // Symptom severity alerts
        if (conditionData.primarySymptom && conditionData.primarySymptom.severity >= 9) {
            summary.push('Severe symptom level (9-10/10) reported');
        } else if (conditionData.primarySymptom && conditionData.primarySymptom.severity >= 6) {
            summary.push('Moderate symptom level (6-8/10) reported');
        }
        
        // Overall wellbeing concerns
        if (conditionData.overallWellbeing <= 2) {
            summary.push('Very low overall wellbeing (0-2/10) reported');
        } else if (conditionData.overallWellbeing <= 4) {
            summary.push('Low overall wellbeing (3-4/10) reported');
        }
        
        // Status-based alerts
        if (entry.status === 'urgent') {
            summary.push('Urgent status - immediate clinical review recommended');
        } else if (entry.status === 'monitor') {
            summary.push('Monitoring status - regular follow-up needed');
        }
        
        return summary;
    }
    
    // Method to determine urgency based on the same logic as React Native component
    determineUrgency(entry) {
        const conditionData = entry.condition_data || {};
        
        // Urgent criteria for general health
        if (conditionData.healthTrend === 'significantly_worse' || 
            (conditionData.primarySymptom && conditionData.primarySymptom.severity >= 9) ||
            conditionData.overallWellbeing <= 2) {
            return 'urgent';
        }
        
        // Monitor criteria
        if (conditionData.healthTrend === 'slightly_worse' || 
            (conditionData.primarySymptom && conditionData.primarySymptom.severity >= 6) ||
            conditionData.overallWellbeing <= 4) {
            return 'monitor';
        }
        
        return 'good';
    }
    
    // Helper to check for existing entries (mirrors React Native logic)
    async checkExistingEntry(patientId, date) {
        try {
            // This would typically make an API call
            const response = await fetch(`/api/health-progress/general-entries/${patientId}/${date}`);
            return response.exists;
        } catch (error) {
            console.error('Error checking existing entry:', error);
            return false;
        }
    }
}