import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { QRCodeComponent } from 'angularx-qrcode';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-detalle-lote',
  standalone: true,
  imports: [CommonModule, RouterLink, QRCodeComponent],
  template: `
    <div class="p-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>Detalle del Lote</h2>
        <a routerLink="/dashboard/lotes" class="btn btn-outline-secondary">Volver</a>
      </div>

      <div class="card shadow-sm p-4" style="max-width: 800px;" *ngIf="lote">
        <div class="row">
          <!-- Info -->
          <div class="col-md-7">
            <h4 class="text-success">{{ lote.codigo }}</h4>
            <p class="mb-1"><strong>Producto:</strong> {{ lote.producto.nombre }}</p>
            <p class="mb-1"><strong>Finca:</strong> {{ lote.finca.nombre }} ({{ lote.finca.municipio }})</p>
            <p class="mb-1"><strong>Cantidad:</strong> {{ lote.cantidad }} {{ lote.unidad }}</p>
            <p class="mb-1"><strong>Fecha Cosecha:</strong> {{ lote.fecha_cosecha }}</p>
            <p class="mb-1"><strong>Estado:</strong> <span class="badge bg-primary">{{ lote.estado_display }}</span></p>
          </div>

          <!-- QR -->
          <div class="col-md-5 text-center border-start">
            <h5>Escanea y verifica</h5>
            <qrcode [qrdata]="lote.qr_codigo" [width]="200" [errorCorrectionLevel]="'M'"></qrcode>
            <p class="mt-2 text-muted small">Este código es público.</p>
            
            <button *ngIf="lote.estado === 'borrador'" (click)="publicar()" class="btn btn-success w-100 mt-2">
              Publicar Lote
            </button>
          </div>
        </div>
      </div>
    </div>
  `
})
export class DetalleLoteComponent implements OnInit {
  lote: any = null;
  id!: number;

  constructor(
    private route: ActivatedRoute,
    private api: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.id = Number(this.route.snapshot.paramMap.get('id'));
    this.cargarLote();
  }

  cargarLote() {
    this.api.getLote(this.id).subscribe(data => {
      this.lote = data;
      this.cdr.detectChanges();
    });
  }

  publicar() {
    this.api.publicarLote(this.id).subscribe(() => {
      this.cargarLote(); // Recargar para ver el nuevo estado
    });
  }
}