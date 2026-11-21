import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { Router, RouterOutlet, RouterLink, RouterLinkActive, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs';
import { ApiService } from '../../services/api';
import { Grupo, SesionService } from '../../services/sesion';
import { IconComponent, NtIcon } from '../icon/icon';

interface ItemMenu { ruta: string; texto: string; icono: NtIcon; }

const MENUS: Record<Grupo, ItemMenu[]> = {
  productor: [
    { ruta: 'resumen', texto: 'Resumen', icono: 'resumen' },
    { ruta: 'lotes', texto: 'Mis lotes', icono: 'lotes' },
    { ruta: 'fincas', texto: 'Mi finca', icono: 'finca' },
    { ruta: 'movimientos', texto: 'Movimientos', icono: 'movimientos' },
    { ruta: 'documentos', texto: 'Documentos', icono: 'documentos' },
  ],
  administrador: [
    { ruta: 'resumen', texto: 'Resumen', icono: 'resumen' },
    { ruta: 'admin/productores', texto: 'Productores', icono: 'users' },
    { ruta: 'admin/lotes', texto: 'Lotes', icono: 'lotes' },
    { ruta: 'admin/municipios', texto: 'Municipios', icono: 'finca' },
    { ruta: 'admin/auditoria', texto: 'Auditoría', icono: 'shield' },
    { ruta: 'admin/solicitudes', texto: 'Solicitudes', icono: 'inbox' },
  ],
  distribuidor: [
    { ruta: 'resumen', texto: 'Centro de operaciones', icono: 'truck' },
    { ruta: 'inventario', texto: 'Inventario', icono: 'lotes' },
    { ruta: 'historial', texto: 'Historial', icono: 'clock' },
  ],
  pendiente: [{ ruta: 'resumen', texto: 'Mi solicitud', icono: 'inbox' }],
};

const SECCIONES: Record<string, string> = {
  resumen: 'Resumen', lotes: 'Mis lotes', fincas: 'Mi finca', movimientos: 'Movimientos', documentos: 'Documentos',
  productores: 'Productores', municipios: 'Municipios', auditoria: 'Auditoría', solicitudes: 'Solicitudes',
  inventario: 'Inventario', historial: 'Historial',
};

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, IconComponent],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class DashboardComponent implements OnInit {
  private api = inject(ApiService);
  private router = inject(Router);
  sesion = inject(SesionService);

  finca = signal<{ nombre: string; municipio: string; departamento: string } | null>(null);
  seccion = signal(this.seccionDe(this.router.url));

  menu = computed(() => MENUS[this.sesion.grupo()]);
  grupo = this.sesion.grupo;

  /** Encabezado "Espacio de trabajo" del menú, según el rol. */
  espacio = computed(() => {
    const u = this.sesion.usuario();
    switch (this.sesion.grupo()) {
      case 'administrador': return { titulo: 'Administración', sub: 'Nariño · Vista regional' };
      case 'distribuidor': return { titulo: 'Centro de operaciones', sub: [u?.rol_display, u?.municipio].filter(Boolean).join(' · ') };
      case 'productor': {
        const f = this.finca();
        return f ? { titulo: f.nombre, sub: `${f.municipio}, ${f.departamento}` } : { titulo: 'Sin finca registrada', sub: '' };
      }
      default: return { titulo: 'Tu cuenta', sub: 'Pendiente de aprobación' };
    }
  });
  migas = computed(() => {
    const raiz = { productor: 'Productor', administrador: 'Administración', distribuidor: this.sesion.usuario()?.rol_display ?? 'Distribución', pendiente: 'Cuenta' }[this.sesion.grupo()];
    return `${raiz} / ${this.seccion()}`;
  });

  ngOnInit() {
    this.router.events.pipe(filter(e => e instanceof NavigationEnd))
      .subscribe(() => this.seccion.set(this.seccionDe(this.router.url)));

    this.sesion.cargar().subscribe({
      next: () => {
        if (this.sesion.grupo() === 'productor') {
          this.api.getEstadisticas().subscribe({ next: e => this.finca.set(e.finca_principal), error: () => {} });
        }
      },
      error: () => this.logout()   // token vencido o inválido
    });
  }

  private seccionDe(url: string): string {
    const partes = url.split('?')[0].split('/');          // ['', 'dashboard', 'admin', 'lotes']
    const clave = partes[2] === 'admin' ? partes[3] : partes[2];
    return SECCIONES[clave ?? 'resumen'] ?? 'Resumen';
  }

  logout() {
    this.sesion.cerrar();
    this.router.navigate(['/login']);
  }
}
