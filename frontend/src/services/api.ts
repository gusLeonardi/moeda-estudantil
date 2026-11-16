import axios from 'axios';
import { clearSession, readSession } from '../auth/session';
export const api=axios.create({baseURL:import.meta.env.VITE_API_URL||'http://localhost:8000/api',timeout:10000,headers:{'Content-Type':'application/json'}});
api.interceptors.request.use(config=>{const session=readSession();if(session)config.headers.Authorization=`Bearer ${session.access_token}`;return config;});
api.interceptors.response.use(response=>response,error=>{if(error.response?.status===401){clearSession();if(location.pathname!=='/login')location.assign('/login');}return Promise.reject(error);});
export function apiMessage(error:unknown){if(axios.isAxiosError(error)){const detail=error.response?.data?.detail;if(typeof detail==='string')return detail;if(Array.isArray(detail))return detail[0]?.msg||'Revise os dados informados.';if(!error.response)return'Não foi possível conectar à API.'}return'Não foi possível concluir a operação.'}
