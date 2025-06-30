<template>
    <div class="dynamic-search-bar">
      <input
        v-model="inputValue"
        :placeholder="placeholder"
        class="dynamic-search-input"
        @input="onInput"
        @keyup.enter="onEnter"
      />
      <button v-if="inputValue" class="clear-btn" @click="clearInput">✕</button>
    </div>
  </template>
  
  <script>
  export default {
    name: 'DynamicSearchBar',
    props: {
      modelValue: {
        type: String,
        default: ''
      },
      placeholder: {
        type: String,
        default: 'Search...'
      }
    },
    data() {
      return {
        inputValue: this.modelValue
      }
    },
    watch: {
      modelValue(val) {
        this.inputValue = val;
      }
    },
    methods: {
      onInput() {
        this.$emit('update:modelValue', this.inputValue);
        this.$emit('input', this.inputValue);
      },
      onEnter() {
        this.$emit('search', this.inputValue);
      },
      clearInput() {
        this.inputValue = '';
        this.onInput();
      }
    }
  }
  </script>
  
  <style scoped>
  .dynamic-search-bar {
    position: relative;
    width: 100%;
    max-width: 500px;
    border-radius: 50px;
    margin: 0;
    display: flex;
    align-items: center;
    border: none;
    box-shadow: none;
    transition: all 0.3s;
  }
  

  .dynamic-search-input {
    width: 100%;
    height: 45px;
    padding: 10px 16px;
    border: none;
    border-radius: 50px;
    font-size: 16px;
    color: #333;
    outline: none;
    background: transparent;
  }
  
  .dynamic-search-input::placeholder {
    font-size: 16px;
  }
  
  .clear-btn {
    position: absolute;
    right: 8px;
    background: none;
    border: none;
    color: #888;
    font-size: 18px;
    cursor: pointer;
    padding: 0 6px;
    border-radius: 50%;
    transition: background 0.2s;
  }
  
  .clear-btn:hover {
    background: #eee;
    color: #d32f2f;
  }
  </style>