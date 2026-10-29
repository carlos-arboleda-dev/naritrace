import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface LoginResponse {
  token: string;
}

export interface Lote {
  id: number;
  codigo: string;
  producto_nombre: string;
  productor_nombre: string;
  finca_nombre: string;
  cantidad: string;
  unidad: string;
  estado: string;
  estado_display: string;
  fecha_cosecha: string;
  variedad?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private API_URL = 'http://127.0.0.1:8000/api';

  constructor(private http: HttpClient) {}

  // ==================== AUTENTICACIÓN ====================
  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': token ? `Token ${token}` : ''
    });
  }

  login(username: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.API_URL}/token/`, { username, password });
  }

  logout(): void {
    localStorage.removeItem('token');
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('token');
  }

  // ==================== LOTES ====================
  getLotes(): Observable<Lote[]> {
    return this.http.get<Lote[]>(`${this.API_URL}/lotes/`, { headers: this.getHeaders() });
  }

  getLote(id: number): Observable<any> {
    return this.http.get<any>(`${this.API_URL}/lotes/${id}/`, { headers: this.getHeaders() });
  }

  crearLote(data: any): Observable<any> {
    return this.http.post<any>(`${this.API_URL}/lotes/`, data, { headers: this.getHeaders() });
  }

  publicarLote(id: number): Observable<any> {
    return this.http.post<any>(`${this.API_URL}/lotes/${id}/publicar/`, {}, { headers: this.getHeaders() });
  }
}