import axios from 'axios'

const BASE_URL = 'https://wc2026-simulator-uiiv.onrender.com'

export const getOdds = () => axios.get(`${BASE_URL}/odds`)
export const getTeams = () => axios.get(`${BASE_URL}/teams`)
export const getTeam = (name) => axios.get(`${BASE_URL}/teams/${name}`)
export const getGroups = () => axios.get(`${BASE_URL}/groups`)
export const simulateMatch = (teamA, teamB) => 
  axios.get(`${BASE_URL}/simulate/${teamA}/${teamB}`)