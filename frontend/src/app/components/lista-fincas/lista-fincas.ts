import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-lista-fincas',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="p-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>Mis Fincas</h2>
        <button class="btn btn-success" disabled>+ Nueva Finca (Próximamente)</button>
      </div>

      <div *ngIf="cargando" class="text-center py-5 text-muted">
        Cargando fincas...
      </div>

      <div class="row" *ngIf="!cargando">
        <div class="col-md-4 mb-3" *ngFor="let finca of fincas">
          <div class="card shadow-sm h-100 border-0">
            <div class="card-body">
              <h5 class="card-title text-success fw-bold">{{ finca.nombre }}</h5>
              <p class="card-text mb-1"><strong>{{ finca.municipio }}</strong></p>
              <p class="card-text text-muted small">{{ finca.departamento }}</p>
            </div>
          </div>
        </div>

        <div *ngIf="fincas.length === 0" class="col-12 text-center py-5">
          <p class="text-muted">No tienes fincas registradas aún.</p>
        </div>
      </div>
    </div>
  `
})
export class ListaFincasComponent implements OnInit {
  fincas: any[] = [];
  cargando = true;

  constructor(private api: ApiService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.cargarFincas();
  }

  cargarFincas() {
    this.cargando = true;
    this.api.getFincas().subscribe({
      next: (data: any) => {
        // Extraemos el array si viene paginado
        this.fincas = data.results ? data.results : data;
        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error cargando fincas', err);
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }
}