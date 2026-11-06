import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, FormGroup } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService, Producto, Finca } from '../../services/api';

@Component({
  selector: 'app-crear-lote',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './crear-lote.html',
  styleUrl: './crear-lote.css'
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
      cantidad: ['', [Validators.required, Validators.min(0.01)]],
      unidad: ['kg', Validators.required],
      fecha_cosecha: ['', Validators.required],
      proceso: [''],
      notas_produccion: ['']
    });
  }

  ngOnInit() {
    // Cargar productos y fincas
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
    if (this.form.invalid) {
      // Si el formulario es inválido, marcamos todos los campos como "tocados"
      // para que Angular muestre los errores en rojo.
      Object.keys(this.form.controls).forEach(key => {
        this.form.get(key)?.markAsTouched();
      });
      return;
    }
    
    this.enviando = true;
    this.error = '';

    const payload = { ...this.form.value };

    this.api.crearLote(payload).subscribe({
      next: (res) => {
        this.router.navigate(['/dashboard/lotes']);
      },
      error: (err) => {
        console.error(err);
        this.error = 'Error al crear el lote. Revisa los datos.';
        this.enviando = false;
        this.cdr.detectChanges();
      }
    });
  }
}