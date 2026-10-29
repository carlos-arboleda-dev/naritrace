import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-trazabilidad-publica',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="bg-light min-vh-100 py-5">
      <div class="container" style="max-width: 900px;">
        
        <!-- Header Público -->
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h4 class="text-success mb-0 fw-bold">NariTrace</h4>
          <a routerLink="/login" class="btn btn-outline-success btn-sm">Iniciar Sesión</a>
        </div>

        <div *ngIf="error" class="alert alert-danger">
          {{ error }}
        </div>

        <div *ngIf="lote" class="card shadow border-0">
          <!-- Banner principal -->
          <div class="card-header bg-success text-white p-4">
            <h2 class="mb-1">Historia de origen</h2>
            <p class="mb-0 opacity-75">Lote: {{ lote.codigo }}</p>
          </div>

          <div class="card-body p-4">
            <!-- Resumen del producto -->
            <div class="row mb-5 border-bottom pb-4">
              <div class="col-md-8">
                <h3 class="text-dark">{{ lote.producto.nombre }}</h3>
                <p class="text-muted mb-2">Variedad: {{ lote.variedad || 'No especificada' }}</p>
                <p class="mb-1"><strong>Cantidad:</strong> {{ lote.cantidad }} {{ lote.unidad }}</p>
                <p class="mb-1"><strong>Fecha de cosecha:</strong> {{ lote.fecha_cosecha }}</p>
                <p class="mb-0"><strong>Proceso:</strong> {{ lote.proceso || 'Estándar' }}</p>
              </div>
              <div class="col-md-4 text-md-end mt-3 mt-md-0">
                <div class="bg-light p-3 rounded">
                  <small class="text-muted d-block mb-1">Producido en</small>
                  <strong>{{ lote.finca.municipio }}, {{ lote.finca.departamento }}</strong>
                  <hr class="my-2">
                  <small class="text-muted d-block mb-1">Productor</small>
                  <strong>{{ lote.productor.nombre }}</strong>
                </div>
              </div>
            </div>

            <!-- Línea de tiempo -->
            <h4 class="mb-4">Recorrido del producto</h4>
            <div class="timeline">
              <div class="timeline-item" *ngFor="let evento of lote.linea_tiempo; let i = index">
                <div class="timeline-marker bg-success text-white">
                  {{ i + 1 }}
                </div>
                <div class="timeline-content card mb-3 border-0 shadow-sm bg-white">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <h6 class="mb-0 fw-bold text-success">{{ evento.tipo }}</h6>
                      <small class="text-muted">{{ evento.fecha | date:'dd/MM/yyyy HH:mm' }}</small>
                    </div>
                    <p class="mb-1"><strong>Responsable:</strong> {{ evento.actor }}</p>
                    <p class="mb-1" *ngIf="evento.origen && evento.destino">
                      <strong>Ruta:</strong> {{ evento.origen }} ➔ {{ evento.destino }}
                    </p>
                    <p class="mb-0 text-muted" *ngIf="evento.descripcion">{{ evento.descripcion }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Certificaciones (si hay) -->
            <div *ngIf="lote.certificaciones?.length > 0" class="mt-5">
              <h5 class="mb-3">Certificaciones</h5>
              <div class="d-flex gap-2 flex-wrap">
                <span *ngFor="let cert of lote.certificaciones" class="badge bg-success p-2">
                  {{ cert.tipo_display }}
                </span>
              </div>
            </div>

          </div>
        </div>

        <!-- Footer -->
        <div class="text-center mt-4 text-muted small">
          <p>Plataforma de trazabilidad agropecuaria - Nariño, Colombia.</p>
        </div>

      </div>
    </div>
  `,
  styles: [`
    .timeline {
      position: relative;
      padding-left: 30px;
    }
    .timeline::before {
      content: '';
      position: absolute;
      top: 0;
      bottom: 0;
      left: 15px;
      width: 2px;
      background-color: #198754;
    }
    .timeline-item {
      position: relative;
      margin-bottom: 20px;
    }
    .timeline-marker {
      position: absolute;
      left: -30px;
      width: 30px;
      height: 30px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 14px;
      z-index: 2;
      border: 3px solid white;
    }
    .timeline-content {
      margin-left: 20px;
    }
  `]
})
export class TrazabilidadPublicaComponent implements OnInit {
  lote: any = null;
  error = '';

  constructor(
    private route: ActivatedRoute,
    private api: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    const codigo = this.route.snapshot.paramMap.get('codigo');
    if (codigo) {
      this.cargarTrazabilidad(codigo);
    }
  }

  cargarTrazabilidad(codigo: string) {
    this.api.getTrazabilidadPublica(codigo).subscribe({
      next: (data) => {
        this.lote = data;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.error = 'No se encontró información para este código QR. Es posible que el lote no esté publicado.';
        this.cdr.detectChanges();
      }
    });
  }
}