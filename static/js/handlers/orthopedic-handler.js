// orthopedic-handler.js - Reads ALL orthopedic surgery fields
export class OrthopedicHandler {
    getKeyMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // PAIN ASSESSMENT
        if (conditionData.pain_level !== undefined) {
            metrics.push({ label: 'Pain Level', value: conditionData.pain_level + '/10' });
        }
        if (conditionData.pain_location) {
            metrics.push({ label: 'Pain Location', value: conditionData.pain_location });
        }
        
        // NEUROVASCULAR STATUS
        if (conditionData.distal_pulse) {
            metrics.push({ label: 'Distal Pulse', value: this.formatMetricValue(conditionData.distal_pulse) });
        }
        if (conditionData.limb_color) {
            metrics.push({ label: 'Limb Color', value: this.formatMetricValue(conditionData.limb_color) });
        }
        
        // WOUND CONDITION
        if (conditionData.wound_condition) {
            metrics.push({ label: 'Wound Condition', value: this.formatMetricValue(conditionData.wound_condition) });
        }
        
        // MOBILITY
        if (conditionData.mobility_level) {
            metrics.push({ label: 'Mobility', value: this.formatMetricValue(conditionData.mobility_level) });
        }
        
        // TEMPERATURE
        if (commonData.temperature) {
            metrics.push({ label: 'Temperature', value: commonData.temperature + '°C' });
        }
        
        return metrics;
    }
    
    getDetailedMetrics(entry) {
        const conditionData = entry.condition_data || {};
        const commonData = entry.common_data || {};
        let metrics = [];
        
        // PAIN ASSESSMENT SECTION
        metrics.push({ label: '--- PAIN ASSESSMENT ---', value: '', section: true });
        
        if (conditionData.pain_level !== undefined) {
            metrics.push({ label: 'Pain Level', value: conditionData.pain_level + '/10' });
        }
        if (conditionData.pain_location) {
            metrics.push({ label: 'Pain Location', value: conditionData.pain_location });
        }
        
        // NEUROVASCULAR STATUS SECTION
        metrics.push({ label: '--- LIMB NEUROVASCULAR STATUS ---', value: '', section: true });
        
        if (conditionData.limb_color) {
            metrics.push({ label: 'Limb Color', value: this.formatMetricValue(conditionData.limb_color) });
        }
        if (conditionData.limb_temperature) {
            metrics.push({ label: 'Limb Temperature', value: this.formatMetricValue(conditionData.limb_temperature) });
        }
        if (conditionData.capillary_refill) {
            metrics.push({ label: 'Capillary Refill', value: this.formatMetricValue(conditionData.capillary_refill) });
        }
        if (conditionData.limb_movement) {
            metrics.push({ label: 'Limb Movement', value: this.formatMetricValue(conditionData.limb_movement) });
        }
        if (conditionData.limb_sensation) {
            metrics.push({ label: 'Limb Sensation', value: this.formatMetricValue(conditionData.limb_sensation) });
        }
        if (conditionData.distal_pulse) {
            metrics.push({ label: 'Distal Pulse', value: this.formatMetricValue(conditionData.distal_pulse) });
        }
        
        // WOUND CONDITION SECTION
        metrics.push({ label: '--- WOUND CONDITION ---', value: '', section: true });
        
        if (conditionData.wound_condition) {
            metrics.push({ label: 'Wound Condition', value: this.formatMetricValue(conditionData.wound_condition) });
        }
        if (conditionData.wound_discharge_type) {
            metrics.push({ label: 'Discharge Type', value: this.formatMetricValue(conditionData.wound_discharge_type) });
        }
        if (conditionData.wound_swelling) {
            metrics.push({ label: 'Wound Swelling', value: this.formatMetricValue(conditionData.wound_swelling) });
        }
        
        // MOBILITY & WEIGHT-BEARING SECTION
        metrics.push({ label: '--- MOBILITY & WEIGHT-BEARING ---', value: '', section: true });
        
        if (conditionData.mobility_level) {
            metrics.push({ label: 'Mobility Level', value: this.formatMetricValue(conditionData.mobility_level) });
        }
        if (conditionData.weight_bearing_status) {
            metrics.push({ label: 'Weight-Bearing Status', value: this.formatMetricValue(conditionData.weight_bearing_status) });
        }
        if (conditionData.assistive_device && conditionData.assistive_device !== 'none') {
            metrics.push({ label: 'Assistive Device', value: this.formatMetricValue(conditionData.assistive_device) });
        }
        
        // VITAL SIGNS & DRAIN SECTION
        metrics.push({ label: '--- VITAL SIGNS & DRAIN ---', value: '', section: true });
        
        if (commonData.temperature) {
            metrics.push({ label: 'Temperature', value: commonData.temperature + '°C' });
        }
        if (conditionData.has_drain) {
            metrics.push({ label: 'Surgical Drain', value: 'Yes' });
            if (conditionData.drain_output) {
                metrics.push({ label: 'Drain Output', value: conditionData.drain_output + ' mL/24h' });
            }
            if (conditionData.drain_color) {
                metrics.push({ label: 'Drain Color', value: this.formatMetricValue(conditionData.drain_color) });
            }
        } else {
            metrics.push({ label: 'Surgical Drain', value: 'No' });
        }
        
        // ADDITIONAL NOTES SECTION
        metrics.push({ label: '--- ADDITIONAL NOTES ---', value: '', section: true });
        
        if (conditionData.additional_notes) {
            metrics.push({ label: 'Patient Notes', value: conditionData.additional_notes });
        }
        
        // STATUS
        if (conditionData.status) {
            metrics.push({ label: 'Overall Status', value: this.formatMetricValue(conditionData.status) });
        }
        
        return metrics;
    }
    
    renderEntryHTML(entry) {
        const keyMetrics = this.getKeyMetrics(entry);
        const detailedMetrics = this.getDetailedMetrics(entry);
        
        return `
            <div class="entry-header">
                <h3>${entry.patient_name || 'Unknown Patient'}</h3>
                <span class="condition-badge orthopedic">Orthopedic Surgery</span>
            </div>
            <div class="entry-content">
                <div class="key-metrics">
                    <h4>Key Orthopedic Metrics</h4>
                    ${this.formatMetricsHTML(keyMetrics)}
                </div>
                <div class="detailed-metrics">
                    <h4>Comprehensive Orthopedic Assessment</h4>
                    ${this.formatMetricsHTML(detailedMetrics)}
                </div>
            </div>
            <div class="entry-footer">
                <span class="timestamp">Submitted: ${new Date(entry.created_at).toLocaleString()}</span>
                ${entry.submission_date ? `<span class="submission-date">For: ${entry.submission_date}</span>` : ''}
                ${entry.day_post_op ? `<span class="days-post-op">Day ${entry.day_post_op} Post-Op</span>` : ''}
            </div>
        `;
    }
    
    formatMetricsHTML(metrics) {
        if (!metrics || metrics.length === 0) {
            return '<div class="no-metrics">No orthopedic metrics recorded</div>';
        }
        
        return metrics.map(metric => {
            if (metric.section) {
                return `<div class="metric-section">${metric.label}</div>`;
            }
            return `
                <div class="metric-item">
                    <span class="metric-label">${metric.label}:</span>
                    <span class="metric-value">${metric.value}</span>
                </div>
            `;
        }).join('');
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
    
    // Additional helper methods for orthopedic-specific data
    getNeurovascularStatus(entry) {
        const conditionData = entry.condition_data || {};
        return {
            limbColor: conditionData.limb_color,
            limbTemperature: conditionData.limb_temperature,
            capillaryRefill: conditionData.capillary_refill,
            limbMovement: conditionData.limb_movement,
            limbSensation: conditionData.limb_sensation,
            distalPulse: conditionData.distal_pulse
        };
    }
    
    getWoundAssessment(entry) {
        const conditionData = entry.condition_data || {};
        return {
            condition: conditionData.wound_condition,
            dischargeType: conditionData.wound_discharge_type,
            swelling: conditionData.wound_swelling
        };
    }
    
    getMobilityStatus(entry) {
        const conditionData = entry.condition_data || {};
        return {
            mobilityLevel: conditionData.mobility_level,
            weightBearing: conditionData.weight_bearing_status,
            assistiveDevice: conditionData.assistive_device
        };
    }
    
    getUrgencyStatus(entry) {
        return entry.condition_data?.status || 'unknown';
    }
    
    getDaysPostOp(entry) {
        return entry.day_post_op || 0;
    }
    
    // Method to check for critical neurovascular compromise
    hasNeurovascularCompromise(entry) {
        const neurovascular = this.getNeurovascularStatus(entry);
        return (
            neurovascular.distalPulse === 'absent' ||
            neurovascular.limbColor === 'blue' ||
            neurovascular.limbSensation === 'numbness' ||
            neurovascular.capillaryRefill === 'absent'
        );
    }
    
    // Method to check for infection signs
    hasInfectionSigns(entry) {
        const wound = this.getWoundAssessment(entry);
        return (
            wound.condition === 'odor' ||
            wound.dischargeType === 'purulent'
        );
    }
}