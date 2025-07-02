<template>
  <div class="home-container">
    <header class="main-header">
      <div class="logo">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
        <span>GRC Platform</span>
      </div>
      <nav class="main-nav">
        <router-link to="/home" class="active">Dashboard</router-link>
        <router-link to="/policy/dashboard">Policies</router-link>
        <router-link to="/compliance/user-dashboard">Compliance</router-link>
        <router-link to="/risk/riskdashboard">Risk</router-link>
        <router-link to="/auditor/performance/userdashboard">Audits</router-link>
        <router-link to="/incident/dashboard">Incidents</router-link>
      </nav>
      <button @click="logout" class="logout-btn">Logout</button>
    </header>

    <main class="main-content">
      <section class="hero-section">
        <div class="hero-text">
            <h1>Unified GRC at Your Fingertips</h1>
            <p>
            Experience the future of Governance, Risk, and Compliance with a unified platform designed for agility, accuracy, and efficiency. Our GRC solution empowers MAU Bank to seamlessly manage audits, assess risks, enforce compliance, and monitor policies — all from a single intuitive interface.
            </p>
            <p>
            Secure. Scalable. Smart. Your unified GRC system is now just a login away.
            </p>
        <div class="card chart-card">
          <Bar :data="barChartData" :options="chartOptions" />
        </div>
        </div>
        
        <div class="card metrics-card">
          <div class="logo-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
            <span>GRC Platform</span>
          </div>
          <h2>42% decrease in compliance breaches</h2>
          <p>Public does not participate in payment for order flow as a source of revenue.</p>
        </div>

        <div class="card chart-card">
           <Line :data="lineChartData" :options="chartOptions" />
        </div>
      </section>

      <footer class="stats-footer">
        <div class="stat-item">
          <div class="stat-header">
            <span class="stat-value">39,000+</span>
            <div class="stat-icon-wrapper">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="stat-icon"><line x1="6" y1="3" x2="6" y2="15"></line><circle cx="18" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><path d="M18 9a9 9 0 0 1-9 9"></path></svg>
            </div>
          </div>
          <p>• Policies ready to be connected</p>
        </div>
        <div class="stat-item">
          <div class="stat-header">
            <span class="stat-value">180M+</span>
            <div class="stat-icon-wrapper">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="stat-icon"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            </div>
          </div>
          <p>• Happy global client</p>
        </div>
        <div class="stat-item">
          <div class="stat-header">
            <span class="stat-value">5.00</span>
            <div class="stat-icon-wrapper">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="stat-icon"><path d="M12 2 L14.5 9.5 L22 12 L14.5 14.5 L12 22 L9.5 14.5 L2 12 L9.5 9.5 Z"></path></svg>
            </div>
          </div>
          <p>• 10k+ rating</p>
        </div>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { Line, Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js';
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement);

const router = useRouter();
const user = ref(null);
const dashboardData = ref({
  totalPolicies: 0,
  totalIncidents: 0,
  totalRisks: 0,
  totalCompliances: 0
});

// Chart data - will be populated with real data
const lineChartData = ref({
  labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
  datasets: [
    {
      label: 'Incidents',
      backgroundColor: '#6a5acd',
      borderColor: '#6a5acd',
      data: [40, 39, 10, 40, 39, 80, 40],
      tension: 0.4,
    },
  ],
});

const barChartData = ref({
    labels: [ 'IT', 'Finance', 'HR', 'Operations', 'Marketing' ],
    datasets: [
        {
            label: 'Compliance Status',
            backgroundColor: ['#6a5acd', '#7b6bd2', '#8c7cd7', '#9d8ddc', '#aea0e1'],
            data: [95, 80, 60, 90, 75]
        }
    ]
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    y: {
        beginAtZero: true
    }
  }
};

// Fetch dashboard data
const fetchDashboardData = async () => {
  try {
    // Fetch various GRC metrics
    const [incidentsResponse, policiesResponse] = await Promise.all([
      axios.get('/api/incidents/counts/'),
      axios.get('/api/policy-dashboard/')
    ]);
    
    if (incidentsResponse.data) {
      dashboardData.value.totalIncidents = incidentsResponse.data.total || 0;
    }
    
    if (policiesResponse.data) {
      dashboardData.value.totalPolicies = policiesResponse.data.totalPolicies || 0;
    }
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
  }
};

const logout = async () => {
  try {
    // Call the logout API endpoint
    await axios.post('/api/logout/');
    
    // Clear authentication data
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('user');
    
    // Emit auth change event
    window.dispatchEvent(new Event('authChanged'));
    
    // Redirect to login
    router.push('/login');
  } catch (error) {
    console.error('Logout error:', error);
    
    // Even if the API call fails, still log out on the client side
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('user');
    window.dispatchEvent(new Event('authChanged'));
    router.push('/login');
  }
};

onMounted(() => {
  // Get user data from localStorage
  const userData = localStorage.getItem('user');
  if (userData) {
    user.value = JSON.parse(userData);
  }
  
  // Fetch dashboard data
  fetchDashboardData();
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.home-container {
  font-family: 'Inter', sans-serif;
  background-color: #f5f5f5;
  margin-left: 260px;
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background-color: #fff;
  padding: 1rem 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.logo {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 1.25rem;
}

.logo svg {
  color: #6a5acd;
  margin-right: 0.5rem;
}

.main-nav a {
  margin: 0 1rem;
  text-decoration: none;
  color: #555;
  font-weight: 500;
  position: relative;
  padding-bottom: 0.25rem;
  transition: color 0.3s;
}

.main-nav a:hover {
  color: #6a5acd;
}

.main-nav a.active {
  color: #6a5acd;
  font-weight: 600;
}

.main-nav a.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #6a5acd;
}

.logout-btn {
  background-color: #6a5acd;
  color: #fff;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: #5849b6;
}

.main-content {
  background-color: #fff;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

.hero-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  grid-template-rows: auto auto;
  gap: 1.5rem;
  align-items: flex-start;
}

.hero-text {
  grid-row: span 2;
}

.card {
  background-color: #f8f9fa;
  border-radius: 10px;
  padding: 1.5rem;
  border: 1px solid #eee;
  transition: transform 0.3s, box-shadow 0.3s;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.1);
}

.hero-text h1 {
  font-size: 2.25rem;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 1rem;
  color: #333;
}

.hero-text p {
  color: #555;
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.testimonial-card .rating {
  margin-bottom: 1rem;
  color: #555;
}

.testimonial-card .rating span {
  color: #facc15;
}

.testimonial-card p {
  font-size: 1rem;
  line-height: 1.5;
  margin-bottom: 1.5rem;
}

.user-profile {
  display: flex;
  align-items: center;
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 1rem;
}

.user-info .user-name {
  display: block;
  font-weight: 600;
}

.user-info .user-title {
  color: #555;
  font-size: 0.9rem;
}

.metrics-card .logo-title {
  display: flex;
  align-items: center;
  font-weight: 600;
  margin-bottom: 1rem;
}

.metrics-card .logo-title svg {
  color: #6a5acd;
  margin-right: 0.5rem;
}

.metrics-card h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #333;
}

.metrics-card p {
  color: #555;
  font-size: 0.9rem;
}

.chart-card {
  padding: 1rem;
  height: 250px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  font-weight: 600;
}

.chart-legend .legend-item {
  margin-left: 1rem;
  font-size: 0.8rem;
  color: #555;
  position: relative;
  padding-left: 12px;
}

.chart-legend .legend-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-item.this-month::before {
  background-color: #7E57C2;
}
.legend-item.last-month::before {
  background-color: #a9a9a9;
}

.chart-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    color: #888;
    margin-top: 0.5rem;
}

.stats-footer {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-top: 2.5rem;
  border-top: 1px solid #eee;
  padding-top: 2rem;
}

.stat-item {
  background-color: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 10px;
  padding: 1.5rem;
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.08);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
}

.stat-value::before {
  content: '';
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #6a5acd;
  margin-right: 0.75rem;
}

.stat-icon-wrapper {
  background-color: #f8f9fa;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.stat-icon {
  color: #6a5acd;
  width: 20px;
  height: 20px;
}

.stat-item p {
  color: #555;
  font-size: 0.9rem;
  margin: 0;
}

@media (max-width: 768px) {
  .hero-section {
    grid-template-columns: 1fr;
  }
  
  .hero-text {
    grid-row: auto;
  }
  
  .stats-footer {
    grid-template-columns: 1fr;
  }
}
</style> 