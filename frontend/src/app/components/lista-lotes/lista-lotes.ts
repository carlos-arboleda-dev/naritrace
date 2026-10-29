import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router'; // <-- IMPORTANTE
import { ApiService, Lote } from '../../services/api';

@Component({
  selector: 'app-lista-lotes',
  standalone: true,
  imports: [CommonModule, RouterLink], // <-- AGREGAR RouterLink AQUÍ
  template: `
    <div class="p-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>Mis Lotes</h2>
        <a routerLink="/dashboard/lotes/nuevo" class="btn btn-success">+ Nuevo Lote</a>
      </div>

      <div *ngIf="cargando" class="text-center py-5 text-muted">
        Cargando lotes...
      </div>

      <div class="row" *ngIf="!cargando">
        <!-- Tarjeta de lote -->
        <div class="col-md-4 mb-3" *ngFor="let lote of lotes">
          <div class="card shadow-sm h-100 border-0">
            <div class="card-body">
              <h5 class="card-title text-success fw-bold">{{ lote.codigo }}</h5>
              <p class="card-text mb-1"><strong>{{ lote.producto_nombre }}</strong></p>
              <p class="card-text mb-1 text-muted">Finca: {{ lote.finca_nombre }}</p>
              <p class="card-text mb-3">{{ lote.cantidad }} {{ lote.unidad }}</p>
            </div>
            <div class="card-footer bg-white border-top-0 d-flex justify-content-between align-items-center pb-3">
              <span class="badge" 
                [ngClass]="lote.estado === 'publicado' ? 'bg-success' : 'bg-secondary'">
                {{ lote.estado_display }}
              </span>
              <!-- AQUÍ ESTÁ EL BOTÓN VER -->
              <a [routerLink]="['/dashboard/lotes', lote.id]" class="btn btn-sm btn-outline-success">
                Ver Lote
              </a>
            </div>
          </div>
        </div>

        <!-- Mensaje si está vacío -->
        <div *ngIf="lotes.length === 0" class="col-12 text-center py-5">
          <p class="text-muted">No tienes lotes registrados aún.</p>
          <a routerLink="/dashboard/lotes/nuevo" class="btn btn-success">Crear mi primer lote</a>
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
    this.cargarLotes();
  }

  cargarLotes() {
    this.cargando = true;
    this.api.getLotes().subscribe({
      next: (data: any) => { // <-- Usamos 'any' para aceptar el objeto paginado
        // Si el backend devuelve un objeto con 'results', extraemos eso
        if (data && data.results) {
          this.lotes = data.results;
        } else {
          this.lotes = data; // Por si acaso algún día quitas la paginación
        }
        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error cargando lotes', err);
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }
}