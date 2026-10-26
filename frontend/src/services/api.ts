import axios from 'axios';
export const api=axios.create({baseURL:import.meta.env.VITE_API_URL||'http://localhost:8000/api',timeout:10000,headers:{'Content-Type':'application/json'}});
export function apiMessage(error:unknown){if(axios.isAxiosError(error)){const detail=error.response?.data?.detail;if(typeof detail==='string')return detail;if(Array.isArray(detail))return detail[0]?.msg||'Revise os dados informados.';if(!error.response)return'Não foi possível conectar à API.'}return'Não foi possível concluir a operação.'}
