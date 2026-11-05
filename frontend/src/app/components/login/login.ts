import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, FormGroup } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './login.html', // <-- Apunta al HTML
  styleUrl: './login.css'      // <-- Apunta al CSS
})
export class LoginComponent {
  form: FormGroup;
  loading = false;
  error = '';

  constructor(private fb: FormBuilder, private api: ApiService, private router: Router) {
    this.form = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });
  }

  onSubmit() {
    if (this.form.invalid) return;
    this.loading = true;
    
    this.api.login(this.form.value.username, this.form.value.password).subscribe({
      next: (res) => {
        localStorage.setItem('token', res.token);
        this.router.navigate(['/dashboard/lotes']); // Ojo: router.router es un error tipográfico, debe ser this.router.navigate
      },
      error: () => {
        this.error = 'Credenciales incorrectas. Verifica tu correo y contraseña.';
        this.loading = false;
      }
    });
  }
}