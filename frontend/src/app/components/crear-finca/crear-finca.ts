import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, FormGroup } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-crear-finca',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './crear-finca.html',
  styleUrl: './crear-finca.css'
})
export class CrearFincaComponent {
  form: FormGroup;
  enviando = false;
  error = '';

  constructor(
    private fb: FormBuilder,
    private api: ApiService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {
    this.form = this.fb.group({
      nombre: ['', Validators.required],
      municipio: ['', Validators.required],
      vereda: [''],
      departamento: ['Nariño', Validators.required],
      area_hectareas: ['', [Validators.required, Validators.min(0)]],
      latitud: [''],
      longitud: ['']
    });
  }

  onSubmit() {
    if (this.form.invalid) {
      Object.keys(this.form.controls).forEach(key => {
        this.form.get(key)?.markAsTouched();
      });
      return;
    }

    this.enviando = true;
    this.error = '';

    // Convertir los valores vacíos a null (Django lo espera así para los decimales)
    const payload = {
      ...this.form.value,
      area_hectareas: this.form.value.area_hectareas || null,
      latitud: this.form.value.latitud || null,
      longitud: this.form.value.longitud || null,
    };

    this.api.crearFinca(payload).subscribe({
      next: () => {
        this.router.navigate(['/dashboard/fincas']);
      },
      error: (err) => {
        console.error(err);
        this.error = 'Error al crear la finca. Revisa los datos.';
        this.enviando = false;
        this.cdr.detectChanges();
      }
    });
  }
}