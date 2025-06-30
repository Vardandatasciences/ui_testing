/**
 * Popup Service Module
 * A centralized service for managing popups throughout the application
 */

import { ref } from 'vue';

// Popup state management
const popupState = ref({
  visible: false,
  type: 'info',
  heading: '',
  message: '',
  buttons: [],
  autoClose: 0,
  inputPlaceholder: 'Enter your comment...',
  selectOptions: [],
  selectedValue: ''
});

// Callback management
const popupCallbacks = ref(new Map());

/**
 * Popup Service
 * Provides methods for showing different types of popups and handling user interactions
 */
export const PopupService = {
  /**
   * Show a popup with custom configuration
   * @param {Object} config - Popup configuration
   * @param {string} config.type - Type of popup (info, success, error, warning, confirm, comment)
   * @param {string} config.heading - Popup heading
   * @param {string} config.message - Popup message
   * @param {Array} config.buttons - Array of button configurations
   * @param {number} config.autoClose - Auto close timeout in milliseconds
   */
  show(config) {
    popupState.value = { ...popupState.value, ...config, visible: true };
  },

  /**
   * Hide the current popup
   */
  hide() {
    popupState.value.visible = false;
  },

  /**
   * Get current popup state
   * @returns {Object} Current popup state
   */
  getState() {
    return popupState;
  },

  /**
   * Handle popup actions
   * @param {Object} params - Action parameters
   * @param {string} params.action - Action type
   * @param {string} params.comment - Comment text (for comment type popups)
   */
  handleAction({ action, comment }) {
    console.log('DEBUG PopupService: handleAction called with:', { action, comment });
    const callback = popupCallbacks.value.get(action);
    console.log('DEBUG PopupService: Found callback for action:', action, callback ? 'YES' : 'NO');
    if (callback) {
      console.log('DEBUG PopupService: Executing callback with comment:', comment);
      // Hide first, then execute callback to allow chained popups
      this.hide();
      console.log('DEBUG PopupService: Popup hidden');
      
      // Use setTimeout to allow the popup to close before the callback potentially shows another popup
      setTimeout(() => {
        callback(comment);
        console.log('DEBUG PopupService: Callback executed');
      }, 100);
      
      popupCallbacks.value.delete(action);
      console.log('DEBUG PopupService: Callback deleted');
    } else {
      this.hide();
      console.log('DEBUG PopupService: Popup hidden (no callback)');
    }
  },

  /**
   * Register callback for specific action
   * @param {string} action - Action type
   * @param {Function} callback - Callback function
   */
  onAction(action, callback) {
    popupCallbacks.value.set(action, callback);
  },

  /**
   * Show success popup
   * @param {string} message - Success message
   * @param {string} heading - Popup heading (default: 'Success')
   */
  success(message, heading = 'Success') {
    this.show({
      type: 'success',
      heading,
      message,
      buttons: [{ label: 'OK', action: 'ok', class: 'success' }]
    });
  },

  /**
   * Show error popup
   * @param {string} message - Error message
   * @param {string} heading - Popup heading (default: 'Error')
   */
  error(message, heading = 'Error') {
    this.show({
      type: 'error',
      heading,
      message,
      buttons: [{ label: 'OK', action: 'ok', class: 'error' }]
    });
  },

  /**
   * Show warning popup
   * @param {string} message - Warning message
   * @param {string} heading - Popup heading (default: 'Warning')
   */
  warning(message, heading = 'Warning') {
    this.show({
      type: 'warning',
      heading,
      message,
      buttons: [{ label: 'OK', action: 'ok', class: 'warning' }]
    });
  },

  /**
   * Show confirmation popup
   * @param {string} message - Confirmation message
   * @param {string} heading - Popup heading (default: 'Confirm')
   * @param {Function} onConfirm - Callback for confirmation
   * @param {Function} onCancel - Callback for cancellation
   */
  confirm(message, heading = 'Confirm', onConfirm, onCancel) {
    this.show({
      type: 'confirm',
      heading,
      message,
      buttons: [
        { label: 'Yes', action: 'yes', class: 'success' },
        { label: 'No', action: 'no', class: 'error' }
      ]
    });

    if (onConfirm) this.onAction('yes', onConfirm);
    if (onCancel) this.onAction('no', onCancel);
  },

  /**
   * Show comment popup
   * @param {string} message - Comment prompt message
   * @param {string} heading - Popup heading (default: 'Comment')
   * @param {Function} onSubmit - Callback for submission
   */
  comment(message, heading = 'Comment', onSubmit) {
    this.show({
      type: 'comment',
      heading,
      message,
      buttons: [
        { label: 'Submit', action: 'submit', class: 'success' },
        { label: 'Cancel', action: 'cancel', class: 'error' }
      ]
    });

    if (onSubmit) this.onAction('submit', onSubmit);
  },

  /**
   * Show select popup
   * @param {string} message - Selection prompt message
   * @param {string} heading - Popup heading (default: 'Select')
   * @param {Array} options - Array of {value, label} objects
   * @param {Function} onSubmit - Callback for submission
   */
  select(message, heading = 'Select', options, onSubmit) {
    this.show({
      type: 'select',
      heading,
      message,
      selectOptions: options,
      selectedValue: options.length > 0 ? options[0].value : '',
      buttons: [
        { label: 'Submit', action: 'submit', class: 'success' },
        { label: 'Cancel', action: 'cancel', class: 'error' }
      ]
    });

    if (onSubmit) this.onAction('submit', onSubmit);
  }
};

export default PopupService; 