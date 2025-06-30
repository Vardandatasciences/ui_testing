<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="logo">
        <span>MAU</span>
        <span>BANK</span>
      </div>
      <span class="header-title">GRC</span>
    </div>
    <nav class="navigation">
      <ul>
        <li>
          <button @click="togglePolicyManagement" :class="{ 'open': policyManagementOpen }">
            <PhCaretDown v-if="policyManagementOpen" weight="fill" />
            <PhCaretRight v-else weight="fill" />
            <span>Policy Management</span>
          </button>
          <ul v-if="policyManagementOpen" class="submenu">
            <li><router-link to="/create-policy">Create Policy</router-link></li>
            <li><router-link to="/policy-approval">Policy Approval</router-link></li>
            <li><router-link to="/policy-list">Policy List</router-link></li>
            <li><router-link to="/list-view">List view</router-link></li>
          </ul>
        </li>
        <li>
          <a href="#">
            <PhCaretRight weight="fill" />
            <span>Compliance Management</span>
          </a>
        </li>
        <li>
          <a href="#">
            <PhCaretRight weight="fill" />
            <span>Incident Management</span>
          </a>
        </li>
        <li>
          <a href="#">
            <PhCaretRight weight="fill" />
            <span>Risk Management</span>
          </a>
        </li>
        <li>
          <a href="#">
            <PhCaretRight weight="fill" />
            <span>Audit Management</span>
          </a>
        </li>
      </ul>
    </nav>
    <div class="sidebar-footer">
      <ul>
        <li>
          <button @click="toggleTheme">
            <PhPaintBrush :size="20" />
            <span>Theme</span>
          </button>
        </li>
        <li>
          <a href="#">
            <PhUserCircle :size="20" />
            <span>User Profile</span>
          </a>
        </li>
      </ul>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue';
import { PhCaretDown, PhCaretRight, PhPaintBrush, PhUserCircle } from '@phosphor-icons/vue';
import './Sidebar_New.css';

const policyManagementOpen = ref(true);

function togglePolicyManagement() {
  policyManagementOpen.value = !policyManagementOpen.value;
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  let newTheme;
  if (currentTheme === 'dark') {
    newTheme = 'blue';
  } else if (currentTheme === 'blue') {
    newTheme = 'light';
  } else {
    newTheme = 'dark';
  }
  document.documentElement.setAttribute('data-theme', newTheme);
}
</script>