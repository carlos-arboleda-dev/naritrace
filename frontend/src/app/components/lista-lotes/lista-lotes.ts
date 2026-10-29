import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, Lote } from '../../services/api';

@Component({
  selector: 'app-lista-lotes',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="p-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>Mis Lotes</h2>
        <button class="btn btn-success">+ Nuevo Lote</button>
      </div>

      <div *ngIf="cargando" class="text-center py-5">Cargando lotes...</div>

      <div class="row" *ngIf="!cargando">
        <div class="col-md-4 mb-3" *ngFor="let lote of lotes">
          <div class="card shadow-sm h-100">
            <div class="card-body">
              <h5 class="card-title text-success">{{ lote.codigo }}</h5>
              <p class="card-text mb-1"><strong>{{ lote.producto_nombre }}</strong> - {{ lote.variedad || 'Sin variedad' }}</p>
              <p class="card-text mb-1">{{ lote.cantidad }} {{ lote.unidad }}</p>
              <p class="card-text"><small class="text-muted">Finca: {{ lote.finca_nombre }}</small></p>
            </div>
            <div class="card-footer bg-white border-top-0">
              <span class="badge bg-secondary">{{ lote.estado_display }}</span>
            </div>
          </div>
        </div>
        <div *ngIf="lotes.length === 0" class="col-12 text-center py-5 text-muted">
          No tienes lotes registrados aún.
        </div>
      </div>
    </div>
  `
})
export class ListaLotesComponent implements OnInit {
  lotes: Lote[] = [];
  cargando = true;

  constructor(private api: ApiService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.api.getLotes().subscribe({
      next: (data) => {
        this.lotes = data;
        this.cargando = false;
        this.cdr.detectChanges(); // Forzar render por Angular 22 (Zoneless)
      },
      error: () => {
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }
}