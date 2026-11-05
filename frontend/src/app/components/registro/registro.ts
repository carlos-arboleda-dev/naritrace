import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, FormGroup } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-registro',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './registro.html',
  styleUrl: './registro.css'
})
export class RegistroComponent {
  form: FormGroup;
  loading = false;
  error = '';

  constructor(private fb: FormBuilder, private api: ApiService, private router: Router) {
    // Formulario basado en el Figma
    this.form = this.fb.group({
      rol: ['productor', Validators.required], // Por defecto productor
      nombre: ['', Validators.required],
      municipio: ['Buesaco, Nariño', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      celular: ['', Validators.required],
      password: ['', [Validators.required, Validators.minLength(8)]],
      terminos: [false, Validators.requiredTrue]
    });
  }

  onSubmit() {
    if (this.form.invalid) return;
    this.loading = true;
    this.error = '';

    const formValues = this.form.value;

    // Separar nombre y apellido (el backend espera first_name y last_name)
    const nombrePartes = formValues.nombre.trim().split(' ');
    const firstName = nombrePartes[0];
    const lastName = nombrePartes.length > 1 ? nombrePartes.slice(1).join(' ') : '';

    // Construir el payload para Django
    const payload = {
      username: formValues.email,  // Usamos el email como nombre de usuario
      email: formValues.email,
      password: formValues.password,
      first_name: firstName,
      last_name: lastName,
      rol: formValues.rol,
      telefono: formValues.celular,
      municipio: formValues.municipio
    };

    this.api.registrarUsuario(payload).subscribe({
      next: (res) => {
        // Registro exitoso, redirigimos al login
        this.router.navigate(['/login']);
      },
      error: (err) => {
        console.error('Error en registro:', err);
        // Mostrar mensajes de error del backend si los hay
        if (err.error) {
          const mensajes = Object.values(err.error).flat().join(' ');
          this.error = mensajes;
        } else {
          this.error = 'Error al crear la cuenta. Intenta de nuevo.';
        }
        this.loading = false;
      }
    });
  }
}
