import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { ApiService } from '../../services/api';
import { Router } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="d-flex vh-100">
      <!-- Sidebar -->
      <div class="bg-success text-white p-3 d-flex flex-column" style="width: 250px;">
        <h4 class="mb-4">NariTrace</h4>
        <ul class="nav nav-pills flex-column mb-auto">
          <li class="nav-item">
            <a routerLink="/dashboard/lotes" routerLinkActive="active" class="nav-link text-white">
              Mis Lotes
            </a>
          </li>
          <li class="nav-item">
            <a routerLink="/dashboard/fincas" routerLinkActive="active" class="nav-link text-white">
              Mis Fincas
            </a>
          </li>
        </ul>
        <hr>
        <button (click)="logout()" class="btn btn-outline-light btn-sm">Cerrar Sesión</button>
      </div>

      <!-- Contenido -->
      <div class="flex-grow-1 bg-light overflow-auto">
        <router-outlet></router-outlet>
      </div>
    </div>
  `,
  styles: [`
    .nav-link.active { background-color: rgba(255,255,255,0.2); font-weight: bold; }
  `]
})
export class DashboardComponent {
  constructor(private api: ApiService, private router: Router) {}

  logout() {
    this.api.logout();
    this.router.navigate(['/login']);
  }
}