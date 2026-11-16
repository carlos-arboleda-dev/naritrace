import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface LoginResponse {
  token: string;
}

export interface Lote {
  id: number;
  codigo: string | null;
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

export interface Pagina<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface FiltrosLotes {
  page?: number;
  page_size?: number;
  search?: string;
  estado?: string;
  producto?: string | number;
}

export interface Usuario {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  rol: string;
  rol_display: string;
}

export interface Producto {
  id: number;
  nombre: string;
  categoria?: string;
  categoria_display: string;
}

export interface Finca {
  id: number;
  nombre: string;
  municipio: string;
  vereda?: string;
  departamento?: string;
  latitud?: string | null;
  longitud?: string | null;
  area_hectareas?: string | null;
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
    localStorage.removeItem('rol');
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

  actualizarLote(id: number, data: any): Observable<any> {
    return this.http.patch<any>(`${this.API_URL}/lotes/${id}/`, data, { headers: this.getHeaders() });
  }

  publicarLote(id: number): Observable<any> {
    return this.http.post<any>(`${this.API_URL}/lotes/${id}/publicar/`, {}, { headers: this.getHeaders() });
  }


  /** Lotes paginados y filtrados (usado por el resumen del productor). */
  getLotesPagina(filtros: FiltrosLotes = {}): Observable<Pagina<Lote & { total_movimientos: number }>> {
    let params = new HttpParams();
    for (const [k, v] of Object.entries(filtros)) {
      if (v !== undefined && v !== null && v !== '') params = params.set(k, String(v));
    }
    return this.http.get<Pagina<Lote & { total_movimientos: number }>>(
      `${this.API_URL}/lotes/`, { headers: this.getHeaders(), params });
  }

  // ==================== PERFIL ====================
  getMe(): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.API_URL}/me/`, { headers: this.getHeaders() });
  }

  // ==================== PRODUCTOS Y FINCAS ====================
  getProductos(): Observable<Producto[]> {
    return this.http.get<Producto[]>(`${this.API_URL}/productos/`, { headers: this.getHeaders() });
  }

  getProductosLista(): Observable<Pagina<Producto>> {
    return this.http.get<Pagina<Producto>>(`${this.API_URL}/productos/?page_size=200`, { headers: this.getHeaders() });
  }

  getFincas(): Observable<Finca[]> {
    return this.http.get<Finca[]>(`${this.API_URL}/fincas/`, { headers: this.getHeaders() });
  }

  crearFinca(finca: any): Observable<any> {
    return this.http.post<any>(`${this.API_URL}/fincas/`, finca, { headers: this.getHeaders() });
  }

  // ==================== TRAZABILIDAD PÚBLICA ====================
  getTrazabilidadPublica(codigo: string): Observable<any> {
    // Este no lleva headers porque es público
    return this.http.get<any>(`${this.API_URL}/publico/trazabilidad/${codigo}/`);
  }

    // ==================== REGISTRO ====================
  registrarUsuario(data: any): Observable<any> {
    return this.http.post<any>(`${this.API_URL}/usuarios/registro/`, data);
  }

    // ==================== MOVIMIENTOS ====================
  crearMovimiento(data: any): Observable<any> {
    return this.http.post<any>(`${this.API_URL}/movimientos/`, data, { headers: this.getHeaders() });
  }

  getMovimientos(loteId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.API_URL}/movimientos/?lote=${loteId}`, { headers: this.getHeaders() });
  }

    // ==================== ESTADÍSTICAS (Admin) ====================
  getEstadisticas(): Observable<any> {
    return this.http.get<any>(`${this.API_URL}/estadisticas/`, { headers: this.getHeaders() });
  }

  // Guardar el rol del usuario al hacer login
  setUserRole(rol: string) {
    localStorage.setItem('rol', rol);
  }
  
  getUserRole(): string {
    return localStorage.getItem('rol') || 'cliente';
  }
}