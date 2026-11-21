import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

const API = 'http://127.0.0.1:8000/api';

export interface EventoAuditoria {
  id: number; fecha: string; usuario: string; accion: string; recurso: string; detalle: string; resultado: string;
}

/** Llamadas al panel de administración y al de operaciones (distribuidor). */
@Injectable({ providedIn: 'root' })
export class PanelApiService {
  private http = inject(HttpClient);

  private opciones(params: Record<string, string | number | undefined | null> = {}) {
    const token = localStorage.getItem('token');
    let p = new HttpParams();
    for (const [k, v] of Object.entries(params)) if (v !== undefined && v !== null && v !== '') p = p.set(k, String(v));
    return { headers: new HttpHeaders({ Authorization: token ? `Token ${token}` : '' }), params: p };
  }
  private get<T>(ruta: string, params = {}): Observable<T> { return this.http.get<T>(`${API}/${ruta}`, this.opciones(params)); }
  private post<T>(ruta: string, cuerpo: unknown = {}): Observable<T> { return this.http.post<T>(`${API}/${ruta}`, cuerpo, this.opciones()); }

  // ---------- administrador
  adminResumen(f: { desde?: string; hasta?: string; departamento?: string; municipio?: string }) { return this.get<any>('admin/resumen/', f); }
  adminAuditoria(f: Record<string, any>) { return this.get<any>('admin/auditoria/', f); }
  adminProductores(buscar = '') { return this.get<any[]>('admin/productores/', { buscar }); }
  adminVerificarProductor(id: number) { return this.post<any>(`admin/productores/${id}/verificar/`); }
  adminLotes(f: Record<string, any>) { return this.get<any[]>('admin/lotes/', f); }
  adminVerificarLote(id: number) { return this.get<any>(`admin/lotes/${id}/verificar/`); }
  adminMunicipios() { return this.get<any[]>('admin/municipios/'); }
  adminSolicitudes(estado = 'pendiente') { return this.get<any[]>('admin/solicitudes/', { estado }); }
  adminResolver(id: number, decision: 'aprobar' | 'rechazar', nota = '') { return this.post<any>(`admin/solicitudes/${id}/resolver/`, { decision, nota }); }
  adminCadena() { return this.get<any>('admin/cadena/'); }
  adminVerificarCadena() { return this.post<any>('admin/cadena/'); }

  // ---------- distribuidor / acopiador / transportador
  distResumen() { return this.get<any>('distribuidor/resumen/'); }
  distLotes(vista: string, buscar = '') { return this.get<any[]>('distribuidor/lotes/', { vista, buscar }); }
  distHistorial(tipo = '') { return this.get<any[]>('distribuidor/historial/', { tipo }); }
  buscarLote(codigo: string) { return this.get<any>(`operaciones/buscar/${encodeURIComponent(codigo.trim())}/`); }
  operar(cuerpo: { codigo: string; accion: string; destino?: string; descripcion?: string; tipo_envio?: string }) {
    return this.post<any>('operaciones/operar/', cuerpo);
  }

  // ---------- público
  verificarPublico(codigo: string) { return this.http.get<any>(`${API}/publico/trazabilidad/${encodeURIComponent(codigo)}/verificar/`); }
}
