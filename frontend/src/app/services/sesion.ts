import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, of, tap, catchError, map, throwError } from 'rxjs';
import { ApiService, Usuario } from './api';

export type Grupo = 'productor' | 'administrador' | 'distribuidor' | 'pendiente';

const INTERMEDIARIOS = ['distribuidor', 'acopiador', 'transportador'];

export function grupoDe(rol?: string | null): Grupo {
  if (rol === 'productor') return 'productor';
  if (rol === 'administrador') return 'administrador';
  if (rol && INTERMEDIARIOS.includes(rol)) return 'distribuidor';
  return 'pendiente';   // "cliente": aún no tiene un rol operativo aprobado
}

/** Usuario autenticado compartido por el menú, los paneles y los guards. */
@Injectable({ providedIn: 'root' })
export class SesionService {
  private api = inject(ApiService);

  usuario = signal<Usuario | null>(null);
  cargado = signal(false);
  grupo = computed(() => grupoDe(this.usuario()?.rol));
  nombre = computed(() => {
    const u = this.usuario();
    return u ? (`${u.first_name} ${u.last_name}`.trim() || u.username) : '';
  });
  iniciales = computed(() => {
    const u = this.usuario();
    if (!u) return '';
    return ((u.first_name && u.last_name) ? `${u.first_name[0]}${u.last_name[0]}` : u.username.slice(0, 2)).toUpperCase();
  });

  /** Carga el perfil una sola vez (los guards y las pantallas pueden llamarlo sin repetir la petición). */
  cargar(): Observable<Usuario> {
    const actual = this.usuario();
    if (actual) return of(actual);
    if (!this.api.isLoggedIn()) return throwError(() => new Error('sin sesión'));
    return this.api.getMe().pipe(tap(u => {
      this.usuario.set(u);
      this.cargado.set(true);
      this.api.setUserRole(u.rol);
    }));
  }

  recargar(): Observable<Usuario> {
    this.usuario.set(null);
    return this.cargar();
  }

  cerrar() {
    this.usuario.set(null);
    this.cargado.set(false);
    this.api.logout();
  }
}
