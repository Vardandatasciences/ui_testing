<template>
  <div class="dropdown-container">
    <button class="filter-btn" @click="toggleDropdown">
      <PhCalendar v-if="showCalendarIcon" :size="16" />
      <span class="text-content">
        <span class="dropdown-label">{{ config.label || config.name }}: </span>
        <span class="dropdown-value">{{ selectedLabel }}</span>
      </span>
      <PhCaretDown :size="16" />
    </button>
    <div v-if="isOpen" class="dropdown-menu">
      <div 
        v-for="option in config.values || config.options || []" 
        :key="option.value"
        class="dropdown-item"
        @click="selectOption(option)"
      >
        {{ option.label }}
      </div>
    </div>
  </div>
</template>

<script>
import { PhCalendar, PhCaretDown } from '@phosphor-icons/vue';

export default {
  name: 'CustomDropdown',
  components: {
    PhCalendar,
    PhCaretDown
  },
  props: {
    config: {
      type: Object,
      required: true
    },
    modelValue: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      isOpen: false
    }
  },
  computed: {
    selectedLabel() {
      const options = this.config.values || this.config.options || [];
      const selectedOption = options.find(option => option.value === this.modelValue);
      if (selectedOption) {
        return selectedOption.label;
      }
      return this.config.defaultValue || this.config.defaultLabel || 'Select...';
    },
    showCalendarIcon() {
      return (this.config.label || this.config.name) === 'Due Date';
    }
  },
  mounted() {
    // Add event listener for clicking outside
    document.addEventListener('click', this.closeDropdown);
  },
  // eslint-disable-next-line vue/no-deprecated-destroyed-lifecycle
  beforeDestroy() {
    // Remove event listener
    document.removeEventListener('click', this.closeDropdown);
  },
  methods: {
    toggleDropdown() {
      this.isOpen = !this.isOpen;
    },
    selectOption(option) {
      this.$emit('update:modelValue', option.value);
      this.$emit('change', option);
      this.isOpen = false;
    },
    // Close dropdown when clicking outside
    closeDropdown(event) {
      if (!event.target.closest('.dropdown-container')) {
        this.isOpen = false;
      }
    }
  }
}
</script>

<style scoped>
.dropdown-container {
  position: relative;
  display: inline-block;
  z-index: 100;
  font-family: var(--font-family, inherit);
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--dropdown-bg, white);
  border: 1px solid var(--dropdown-border, #ddd);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--dropdown-label-text, #333);
  transition: all 0.3s;
  width: 100%;
  min-width: 250px;
  height: 45px;
  justify-content: space-between;
  font-family: var(--font-family, inherit);
}

.filter-btn:hover {
  background: var(--dropdown-hover-bg, #f8f9fa);
  border-color: var(--dropdown-hover-border, #7B6FDD);
  box-shadow: 0 0 0 2px rgba(123, 111, 221, 0.1);
}

.text-content {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex: 1;
  font-family: var(--font-family, inherit);
}

.dropdown-label {
  color: var(--dropdown-label-text, #333);
  font-weight: 500;
  font-family: var(--font-family, inherit);
}

.dropdown-value {
  font-weight: 500;
  color: var(--dropdown-value-text, #7B6FDD);
  font-family: var(--font-family, inherit);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--dropdown-menu-bg, white);
  border: 1px solid var(--dropdown-border, #ddd);
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px var(--dropdown-menu-shadow, rgba(0, 0, 0, 0.1));
  z-index: 99999 !important;
  margin-top: 4px;
  width: 100%;
  min-width: 250px;
  max-width: 300px;
  font-family: var(--font-family, inherit);
}

.dropdown-item {
  padding: 10px 16px;
  cursor: pointer;
  font-size: 14px;
  color: var(--dropdown-item-text, #333);
  transition: background-color 0.2s;
  font-family: var(--font-family, inherit);
}

.dropdown-item:hover {
  background: var(--dropdown-item-hover-bg, #f8f9fa);
}

.dropdown-item:first-child {
  border-radius: 8px 8px 0 0;
}

.dropdown-item:last-child {
  border-radius: 0 0 8px 8px;
}
</style> 