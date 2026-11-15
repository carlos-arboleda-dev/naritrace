import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-admin-panel',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="p-4">
      <h2 class="fw-bold mb-1">Una mirada al territorio</h2>
      <p class="text-muted mb-4">Actividad regional, cobertura y registros de la plataforma - Nariño.</p>

      <div class="row mb-4" *ngIf="stats">
        <div class="col-md-4">
          <div class="card shadow-sm border-0 bg-white p-3">
            <small class="text-muted">Productores Activos</small>
            <h2 class="fw-bold text-success">{{ stats.productores_activos }}</h2>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card shadow-sm border-0 bg-white p-3">
            <small class="text-muted">Lotes Registrados</small>
            <h2 class="fw-bold text-success">{{ stats.lotes_publicados }}</h2>
          </div>
        </div>
      </div>

      <div class="card shadow-sm border-0 p-4 bg-white" *ngIf="stats">
        <h5 class="fw-bold mb-3">Lotes por Municipio</h5>
        <div *ngFor="let m of stats.lotes_por_municipio" class="mb-2 d-flex justify-content-between border-bottom pb-2">
          <span>{{ m.municipio }}</span>
          <span class="badge bg-success rounded-pill">{{ m.total }} lotes</span>
        </div>
      </div>
    </div>
  `
})
export class AdminPanelComponent implements OnInit {
  stats: any = null;

  constructor(private api: ApiService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.api.getEstadisticas().subscribe({
      next: (data) => {
        this.stats = data;
        this.cdr.detectChanges();
      },
      error: (err) => console.error('Error cargando stats', err)
    });
  }
}