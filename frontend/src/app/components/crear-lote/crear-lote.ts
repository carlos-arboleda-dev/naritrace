import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, FormGroup } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService, Producto, Finca } from '../../services/api';

@Component({
  selector: 'app-crear-lote',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  template: `
    <div class="p-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>Registrar Nuevo Lote</h2>
        <a routerLink="/dashboard/lotes" class="btn btn-outline-secondary">Volver</a>
      </div>

      <div class="card shadow-sm p-4" style="max-width: 800px;">
        <form [formGroup]="form" (ngSubmit)="onSubmit()">
          <div class="row mb-3">
            <div class="col-md-6">
              <label class="form-label">Producto</label>
              <select formControlName="producto" class="form-select">
                <option value="">Seleccione un producto</option>
                <option *ngFor="let p of productos" [value]="p.id">{{ p.nombre }}</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label">Finca de Origen</label>
              <select formControlName="finca" class="form-select">
                <option value="">Seleccione una finca</option>
                <option *ngFor="let f of fincas" [value]="f.id">{{ f.nombre }} - {{ f.municipio }}</option>
              </select>
            </div>
          </div>

          <div class="row mb-3">
            <div class="col-md-6">
              <label class="form-label">Variedad</label>
              <input type="text" formControlName="variedad" class="form-control" placeholder="Ej: Castillo">
            </div>
            <div class="col-md-3">
              <label class="form-label">Cantidad</label>
              <input type="number" formControlName="cantidad" class="form-control">
            </div>
            <div class="col-md-3">
              <label class="form-label">Unidad</label>
              <select formControlName="unidad" class="form-select">
                <option value="kg">Kilogramos</option>
                <option value="lb">Libras</option>
                <option value="unidades">Unidades</option>
              </select>
            </div>
          </div>

          <div class="row mb-3">
            <div class="col-md-6">
              <label class="form-label">Fecha de Cosecha</label>
              <input type="date" formControlName="fecha_cosecha" class="form-control">
            </div>
            <div class="col-md-6">
              <label class="form-label">Proceso</label>
              <input type="text" formControlName="proceso" class="form-control" placeholder="Ej: Lavado, Secado">
            </div>
          </div>

          <div class="mb-4">
            <label class="form-label">Notas de producción (Opcional)</label>
            <textarea formControlName="notas_produccion" class="form-control" rows="3"></textarea>
          </div>

          <div *ngIf="error" class="alert alert-danger">{{ error }}</div>

          <button type="submit" class="btn btn-success px-4" [disabled]="form.invalid || enviando">
            {{ enviando ? 'Guardando...' : 'Guardar Lote' }}
          </button>
        </form>
      </div>
    </div>
  `
})
export class CrearLoteComponent implements OnInit {
  form: FormGroup;
  productos: Producto[] = [];
  fincas: Finca[] = [];
  enviando = false;
  error = '';

  constructor(
    private fb: FormBuilder,
    private api: ApiService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {
    this.form = this.fb.group({
      producto: ['', Validators.required],
      finca: ['', Validators.required],
      variedad: [''],
      cantidad: ['', [Validators.required, Validators.min(0)]],
      unidad: ['kg', Validators.required],
      fecha_cosecha: ['', Validators.required],
      proceso: [''],
      notas_produccion: ['']
    });
  }

  ngOnInit() {
    this.api.getProductos().subscribe((data: any) => {
      this.productos = data.results ? data.results : data;
      this.cdr.detectChanges();
    });
    this.api.getFincas().subscribe((data: any) => {
      this.fincas = data.results ? data.results : data;
      this.cdr.detectChanges();
    });
}

  onSubmit() {
    if (this.form.invalid) return;
    this.enviando = true;
    this.error = '';

    this.api.crearLote(this.form.value).subscribe({
      next: (res) => {
        // Redirigir a la lista de lotes
        this.router.navigate(['/dashboard/lotes']);
      },
      error: (err) => {
        this.error = 'Error al crear el lote. Revisa los datos.';
        this.enviando = false;
        this.cdr.detectChanges();
      }
    });
  }
}