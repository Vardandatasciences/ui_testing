// popupUtils.js
// Utility functions for compliance-specific popup operations

import { PopupService } from '../../../modules/popup';

/**
 * Compliance Popup Utilities
 * Contains pre-configured popup functions specific to the Compliance module
 */
export const CompliancePopups = {
  /**
   * Show a popup for successful compliance creation
   * @param {Object} compliance - The created compliance data
   */
  complianceCreated(compliance) {
    const complianceId = compliance.compliance_id || compliance.ComplianceId;
    const message = `Compliance #${complianceId} created successfully and sent for review.`;
    PopupService.success(message, 'Compliance Created');
  },

  /**
   * Show a popup for successful compliance update
   * @param {Object} compliance - The updated compliance data
   */
  complianceUpdated(compliance) {
    const complianceId = compliance.compliance_id || compliance.ComplianceId;
    const message = `Compliance #${complianceId} updated successfully and sent for review.`;
    PopupService.success(message, 'Compliance Updated');
  },

  /**
   * Show a popup for successful compliance clone
   * @param {Object} compliance - The cloned compliance data
   */
  complianceCloned(compliance) {
    const complianceId = compliance.compliance_id || compliance.ComplianceId;
    const message = `Compliance #${complianceId} cloned successfully and sent for review.`;
    PopupService.success(message, 'Compliance Cloned');
  }
};