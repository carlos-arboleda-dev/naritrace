import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { Router, RouterOutlet, RouterLink, RouterLinkActive, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs';
import { ApiService, Usuario } from '../../services/api';
import { IconComponent } from '../icon/icon';

const SECCIONES: Record<string, string> = {
  resumen: 'Resumen', lotes: 'Mis lotes', fincas: 'Mi finca',
  movimientos: 'Movimientos', documentos: 'Documentos', admin: 'Panel admin',
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

  usuario = signal<Usuario | null>(null);
  finca = signal<{ nombre: string; municipio: string; departamento: string } | null>(null);
  seccion = signal(this.seccionDe(this.router.url));

  nombre = computed(() => {
    const u = this.usuario();
    return u ? `${u.first_name} ${u.last_name}`.trim() || u.username : '';
  });
  iniciales = computed(() => {
    const u = this.usuario();
    if (!u) return '';
    const base = (u.first_name && u.last_name) ? `${u.first_name[0]}${u.last_name[0]}` : u.username.slice(0, 2);
    return base.toUpperCase();
  });
  esAdmin = computed(() => this.usuario()?.rol === 'administrador');

  ngOnInit() {
    this.router.events.pipe(filter(e => e instanceof NavigationEnd))
      .subscribe(() => this.seccion.set(this.seccionDe(this.router.url)));

    this.api.getMe().subscribe({
      next: u => { this.usuario.set(u); this.api.setUserRole(u.rol); },
      error: () => this.logout()   // token vencido o inválido
    });
    this.api.getEstadisticas().subscribe({
      next: e => this.finca.set(e.finca_principal),
      error: () => {}
    });
  }

  private seccionDe(url: string): string {
    const clave = url.split('?')[0].split('/')[2] ?? 'resumen';
    return SECCIONES[clave] ?? 'Resumen';
  }

  logout() {
    this.api.logout();
    this.router.navigate(['/login']);
  }
}
