import axios from 'axios'

export default {
  namespaced: true,
  
  state: {
    incidents: [],
    selectedIncident: null
  },
  
  mutations: {
    SET_INCIDENTS(state, incidents) {
      state.incidents = incidents
    },
    SET_SELECTED_INCIDENT(state, incident) {
      state.selectedIncident = incident
    }
  },
  
  actions: {
    async acceptIncident({ commit }, incident) {
      try {
        // Call the accept incident API
        const response = await axios.post(`http://localhost:8000/api/incidents/${incident.IncidentId}/accept/`)
        // Update the incident in the store
        commit('SET_SELECTED_INCIDENT', response.data)
        return response.data
      } catch (error) {
        console.error('Error accepting incident:', error)
        throw error
      }
    },
    
    async rejectIncident({ commit }, incident) {
      try {
        // Call the reject incident API
        const response = await axios.post(`http://localhost:8000/api/incidents/${incident.IncidentId}/reject/`)
        // Update the incident in the store
        commit('SET_SELECTED_INCIDENT', response.data)
        return response.data
      } catch (error) {
        console.error('Error rejecting incident:', error)
        throw error
      }
    }
  }
} 